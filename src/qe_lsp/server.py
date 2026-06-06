"""qe Language Server Protocol implementation."""

from importlib import import_module
from typing import Any

from lsprotocol import types


def _load_language_server() -> Any:
    try:
        return import_module("pygls.lsp.server").LanguageServer
    except ImportError:
        return import_module("pygls.server").LanguageServer


LanguageServer = _load_language_server()

QE_KEYWORDS = [
    "&CONTROL",
    "&SYSTEM",
    "&ELECTRONS",
    "&IONS",
    "&CELL",
    "ATOMIC_SPECIES",
    "ATOMIC_POSITIONS",
    "K_POINTS",
    "CELL_PARAMETERS",
]

QE_HOVER_DOCS = {
    "&CONTROL": "Calculation control namelist for Quantum ESPRESSO inputs.",
    "&SYSTEM": "System definition namelist, including cell, atoms, cutoffs, and occupations.",
    "&ELECTRONS": "Electronic minimization namelist for convergence and mixing settings.",
}

server = LanguageServer("qe-lsp", "0.1.0")


def _get_attr(params, name, default=None):
    if params is None:
        return default
    if isinstance(params, dict):
        return params.get(name, default)
    return getattr(params, name, default)


def _get_position(params):
    position = _get_attr(params, "position", {})
    if isinstance(position, dict):
        return position.get("line", 0), position.get("character", 0)
    return _get_attr(position, "line", 0), _get_attr(position, "character", 0)


def _get_text(params):
    text = _get_attr(params, "text")
    if text is not None:
        return text

    text_document = _get_attr(params, "text_document")
    return _get_attr(text_document, "text")


def _word_at_position(text, line_number, character):
    lines = text.splitlines()
    if line_number < 0 or line_number >= len(lines):
        return ""

    line = lines[line_number]
    character = max(0, min(character, len(line)))
    start = character
    while start > 0 and not line[start - 1].isspace():
        start -= 1
    end = character
    while end < len(line) and not line[end].isspace():
        end += 1
    return line[start:end].strip(",")


def _strip_inline_comment(line):
    return line.split("!", 1)[0].strip()


@server.feature("textDocument/completion")
def completion(params):
    return [
        types.CompletionItem(
            label=keyword,
            kind=types.CompletionItemKind.Keyword,
            detail="Quantum ESPRESSO input keyword",
        )
        for keyword in QE_KEYWORDS
    ]


@server.feature("textDocument/hover")
def hover(params):
    text = _get_text(params)
    if not text:
        return None

    line_number, character = _get_position(params)
    keyword = _word_at_position(text, line_number, character).upper()
    if keyword not in QE_HOVER_DOCS:
        return None

    return types.Hover(
        contents=types.MarkupContent(
            kind=types.MarkupKind.Markdown,
            value=f"**{keyword}**\n\n{QE_HOVER_DOCS[keyword]}",
        )
    )


@server.feature("textDocument/diagnostic")
def diagnostic(params):
    text = _get_text(params)
    if not text:
        return []

    diagnostics = []
    open_namelist = None
    open_line = 0
    for line_number, raw_line in enumerate(text.splitlines()):
        line = _strip_inline_comment(raw_line)
        if not line:
            continue
        if line.startswith("&"):
            open_namelist = line.split()[0].upper()
            open_line = line_number
            continue
        if line.startswith("/") and open_namelist is not None:
            open_namelist = None

    if open_namelist is not None:
        diagnostics.append(
            types.Diagnostic(
                range=types.Range(
                    start=types.Position(line=open_line, character=0),
                    end=types.Position(line=open_line, character=len(open_namelist)),
                ),
                severity=types.DiagnosticSeverity.Error,
                message=f"Unclosed namelist {open_namelist}; expected '/'.",
                source="qe-lsp",
            )
        )

    return diagnostics


def main():
    server.start_io()


if __name__ == "__main__":
    main()
