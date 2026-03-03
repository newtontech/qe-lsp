"""
Quantum ESPRESSO Language Server Protocol implementation
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    Diagnostic,
    DiagnosticSeverity,
    DocumentSymbol,
    DocumentSymbolParams,
    Hover,
    HoverParams,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
    SymbolKind,
    TextDocumentPositionParams,
)

if TYPE_CHECKING:
    from pygls.server import LanguageServer
    from pygls.workspace import Document

_server_instance = None


def _get_server() -> "LanguageServer":
    """Lazy initialization of the language server."""
    global _server_instance
    if _server_instance is None:
        from pygls.server import LanguageServer

        _server_instance = LanguageServer("qe-lsp", "0.1.0")
        _setup_features(_server_instance)
    return _server_instance



def _get_word_at_position(doc: "Document", position: Position) -> tuple[str, Range]:
    """Get the word at the given position."""
    lines = doc.source.split("\n")
    if position.line >= len(lines):
        return "", Range(position, position)

    line = lines[position.line]
    start = position.character
    end = position.character

    while start > 0 and (line[start - 1].isalnum() or line[start - 1] in "_-"):
        start -= 1

    while end < len(line) and (line[end].isalnum() or line[end] in "_-"):
        end += 1

    word = line[start:end]
    word_range = Range(
        Position(line=position.line, character=start), Position(line=position.line, character=end)
    )
    return word, word_range


def _get_namelist_at_position(doc: "Document", position: Position) -> str | None:
    """Determine which namelist the position is in."""
    lines = doc.source.split("\n")[: position.line + 1]
    current_namelist = None

    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        if line_lower.startswith("&") and not line_lower.startswith("&end"):
            name_part = line_lower[1:].split()[0] if len(line_lower) > 1 else ""
            current_namelist = name_part if name_part else None
        elif line_lower.startswith("/") or line_lower == "&end":
            if i < position.line:
                current_namelist = None

    return current_namelist


def _completion_handler(
    params: CompletionParams | TextDocumentPositionParams,
) -> CompletionList | None:
    """Provide completion items."""
    srv = _get_server()
    doc = srv.workspace.get_text_document(params.text_document.uri)
    position = params.position

    word, _ = _get_word_at_position(doc, position)
    namelist = _get_namelist_at_position(doc, position)

    items = []

    if namelist:
        from .parser import get_namelist_params

        valid_params = get_namelist_params(namelist)

        for param in valid_params:
            if word.lower() in param.lower():
                items.append(
                    CompletionItem(
                        label=param,
                        kind=CompletionItemKind.Property,
                        detail=f"Parameter in &{namelist}",
                        insert_text=f"{param} = ",
                    )
                )
    else:
        namelists = ["control", "system", "electrons", "ions", "cell"]
        for nl in namelists:
            if word.lower() in nl.lower():
                items.append(
                    CompletionItem(
                        label=f"&{nl}",
                        kind=CompletionItemKind.Class,
                        detail="Namelist",
                        insert_text=f"&{nl}\n\n/",
                    )
                )

        cards = ["ATOMIC_SPECIES", "ATOMIC_POSITIONS", "K_POINTS", "CELL_PARAMETERS"]
        for card in cards:
            if word.upper() in card or word.lower() in card.lower():
                items.append(
                    CompletionItem(
                        label=card,
                        kind=CompletionItemKind.Interface,
                        detail="Card",
                    )
                )

    return CompletionList(is_incomplete=False, items=items)


def _hover_handler(params: HoverParams | TextDocumentPositionParams) -> Hover | None:
    """Provide hover information."""
    srv = _get_server()
    doc = srv.workspace.get_text_document(params.text_document.uri)
    position = params.position

    word, _ = _get_word_at_position(doc, position)
    if not word:
        return None

    namelist = _get_namelist_at_position(doc, position)

    if namelist:
        from .data import get_parameter_doc

        doc_text = get_parameter_doc(namelist, word)
        if doc_text:
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown, value=f"**{word}** (in &{namelist})\n\n{doc_text}"
                )
            )

    if word.lower() in ["control", "system", "electrons", "ions", "cell"]:
        return Hover(
            contents=MarkupContent(
                kind=MarkupKind.Markdown,
                value=f"**{word}** namelist\n\nQuantum ESPRESSO input namelist.",
            )
        )

    if word.upper() in ["ATOMIC_SPECIES", "ATOMIC_POSITIONS", "K_POINTS", "CELL_PARAMETERS"]:
        from .data import get_card_doc, format_card_hover

        card_doc = get_card_doc(word)
        if card_doc:
            doc_text = format_card_hover(card_doc)
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown, value=f"**{word}** card\n\n{doc_text}"
                )
            )

    return None


def _diagnostic_handler(params: Any) -> list[Diagnostic]:
    """Provide diagnostics for the document."""
    srv = _get_server()
    doc = srv.workspace.get_text_document(params.text_document.uri)

    from .parser import parse

    result = parse(doc.source)

    diagnostics = []
    for error in result.errors:
        severity = (
            DiagnosticSeverity.Error
            if error.get("severity") == "error"
            else DiagnosticSeverity.Warning
        )
        diagnostics.append(
            Diagnostic(
                range=Range(
                    Position(line=error.get("line", 1) - 1, character=error.get("column", 1) - 1),
                    Position(line=error.get("line", 1) - 1, character=error.get("column", 1)),
                ),
                message=error.get("message", ""),
                severity=severity,
                source="qe-lsp",
            )
        )

    return diagnostics


def _document_symbol_handler(params: DocumentSymbolParams) -> list[DocumentSymbol]:
    """Provide document symbols (outline)."""
    srv = _get_server()
    doc = srv.workspace.get_text_document(params.text_document.uri)

    from .parser import parse

    result = parse(doc.source)

    symbols = []

    for name, namelist in result.namelists.items():
        children = []
        for param_name in namelist.parameters.keys():
            children.append(
                DocumentSymbol(
                    name=param_name,
                    kind=SymbolKind.Property,
                    range=Range(
                        Position(line=namelist.line_start - 1, character=0),
                        Position(line=namelist.line_start - 1, character=100),
                    ),
                    selection_range=Range(
                        Position(line=namelist.line_start - 1, character=0),
                        Position(line=namelist.line_start - 1, character=100),
                    ),
                )
            )

        symbols.append(
            DocumentSymbol(
                name=f"&{name}",
                kind=SymbolKind.Class,
                range=Range(
                    Position(line=namelist.line_start - 1, character=0),
                    Position(line=namelist.line_end - 1, character=10),
                ),
                selection_range=Range(
                    Position(line=namelist.line_start - 1, character=0),
                    Position(line=namelist.line_start - 1, character=len(name) + 1),
                ),
                children=children,
            )
        )

    for name, card in result.cards.items():
        symbols.append(
            DocumentSymbol(
                name=name,
                kind=SymbolKind.Interface,
                range=Range(
                    Position(line=card.line_start - 1, character=0),
                    Position(line=card.line_end - 1, character=100),
                ),
                selection_range=Range(
                    Position(line=card.line_start - 1, character=0),
                    Position(line=card.line_start - 1, character=len(name)),
                ),
            )
        )

    return symbols


def _setup_features(srv: "LanguageServer") -> None:
    """Setup LSP features on the server."""
    srv.feature("textDocument/completion")(_completion_handler)
    srv.feature("textDocument/hover")(_hover_handler)
    srv.feature("textDocument/diagnostic")(_diagnostic_handler)
    srv.feature("textDocument/documentSymbol")(_document_symbol_handler)


# For testing purposes - expose handlers
def completion(params: Any) -> CompletionList | None:
    return _completion_handler(params)


def hover(params: Any) -> Hover | None:
    return _hover_handler(params)


def diagnostic(params: Any) -> list[Diagnostic]:
    return _diagnostic_handler(params)


def document_symbol(params: Any) -> list[DocumentSymbol]:
    return _document_symbol_handler(params)


# Helper for testing - get server instance
def _get_server_for_testing() -> "LanguageServer":
    """Get the server instance for testing purposes."""
    return _get_server()


def main() -> None:
    """Start the language server."""
    srv = _get_server()
    srv.start_io()


if __name__ == "__main__":
    main()
