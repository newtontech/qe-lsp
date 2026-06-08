"""Navigation providers: definition, hover, and references for QE inputs."""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from lsprotocol import types

from ..constants import QE_CARDS, QE_HOVER_DOCS, QE_NAMELISTS, QE_PARAM_DOCS
from ..parser import parse_qe_input


@dataclass(frozen=True)
class SymbolInfo:
    """A navigable symbol in a QE input file."""

    name: str
    kind: str  # "namelist", "card", "parameter", "variable"
    line: int
    character: int
    length: int


@dataclass
class SymbolIndex:
    """Index of navigable symbols within a single document."""

    symbols: Dict[str, List[SymbolInfo]] = field(default_factory=dict)

    def add(self, symbol: SymbolInfo) -> None:
        key = symbol.name.lower()
        self.symbols.setdefault(key, []).append(symbol)

    def lookup(self, name: str) -> List[SymbolInfo]:
        return self.symbols.get(name.lower(), [])


def build_symbol_index(text: str) -> SymbolIndex:
    """Parse the document and build a symbol index."""
    index = SymbolIndex()
    parsed = parse_qe_input(text)
    lines = text.splitlines()

    # Index namelists
    for name, line_number in parsed.namelist_lines.items():
        line = lines[line_number] if line_number < len(lines) else name
        char = line.upper().find(name.upper())
        if char < 0:
            char = 0
        index.add(SymbolInfo(name=name, kind="namelist", line=line_number, character=char, length=len(name)))

    # Index parameters inside namelists
    for namelist_name, parameters in parsed.namelists.items():
        for param_name, parameter in parameters.items():
            index.add(
                SymbolInfo(
                    name=param_name,
                    kind="parameter",
                    line=parameter.line,
                    character=parameter.character,
                    length=len(param_name),
                )
            )

    # Index cards
    for card_name, card_header in parsed.card_headers.items():
        line_number = _find_card_line(lines, card_name)
        if line_number is not None:
            index.add(
                SymbolInfo(
                    name=card_name,
                    kind="card",
                    line=line_number,
                    character=0,
                    length=len(card_name),
                )
            )

    # Index variable-like assignments for $ENV style references
    assignment_re = re.compile(
        r"([A-Za-z_][A-Za-z0-9_]*(?:\(\d+\))?)\s*=\s*('[^']*'|\"[^\"]*\"|[^\s,]+)"
    )
    for line_number, raw_line in enumerate(lines):
        for match in assignment_re.finditer(raw_line):
            var_name = match.group(1).lower()
            # Already indexed via parsed.namelists; skip duplicates
            existing = index.lookup(var_name)
            if not any(s.line == line_number and s.character == match.start(1) for s in existing):
                index.add(
                    SymbolInfo(
                        name=var_name,
                        kind="variable",
                        line=line_number,
                        character=match.start(1),
                        length=len(match.group(1)),
                    )
                )

    return index


def _find_card_line(lines: List[str], card_name: str) -> Optional[int]:
    """Find the line number where a card header appears."""
    for i, line in enumerate(lines):
        stripped = line.strip().upper()
        if stripped.startswith(card_name):
            return i
    return None


def _get_uri(params: object) -> str:
    """Extract the URI from LSP params."""
    text_document = getattr(params, "text_document", None)
    if text_document is None:
        return ""
    return getattr(text_document, "uri", "")


# ---------------------------------------------------------------------------
# Definition provider
# ---------------------------------------------------------------------------


def get_definition(text: str, line_number: int, character: int, uri: str) -> Optional[types.Location]:
    """Return the definition location for the symbol at the given position.

    Handles:
    - Namelist names (&CONTROL etc.) -> their declaration line
    - Card names (ATOMIC_SPECIES etc.) -> their declaration line
    - Parameters (ecutwfc, ibrav etc.) -> first assignment in the relevant namelist
    """
    index = build_symbol_index(text)
    word = _word_at_position(text, line_number, character)
    if not word:
        return None

    candidates = index.lookup(word)
    if not candidates:
        return None

    # Prefer the first occurrence (definition)
    target = candidates[0]
    return types.Location(
        uri=uri,
        range=types.Range(
            start=types.Position(line=target.line, character=target.character),
            end=types.Position(line=target.line, character=target.character + target.length),
        ),
    )


# ---------------------------------------------------------------------------
# Hover provider (enhanced)
# ---------------------------------------------------------------------------


def get_hover(text: str, line_number: int, character: int) -> Optional[types.Hover]:
    """Return hover documentation for the symbol at the given position.

    Handles:
    - Namelist and card section headers using QE_HOVER_DOCS
    - Parameters inside namelists using QE_PARAM_DOCS
    """
    word = _word_at_position(text, line_number, character)
    if not word:
        return None

    word_upper = word.upper()
    word_lower = word.lower()

    # Section-level hover (namelists and cards)
    if word_upper in QE_HOVER_DOCS:
        return types.Hover(
            contents=types.MarkupContent(
                kind=types.MarkupKind.Markdown,
                value=f"**{word_upper}**\n\n{QE_HOVER_DOCS[word_upper]}",
            )
        )

    # Determine which namelist we are inside
    namelist_name = _namelist_at_line(text, line_number)
    if namelist_name is not None:
        param_docs = QE_PARAM_DOCS.get(namelist_name.upper(), {})
        if word_lower in param_docs:
            return types.Hover(
                contents=types.MarkupContent(
                    kind=types.MarkupKind.Markdown,
                    value=f"**{word_lower}** ({namelist_name})\n\n{param_docs[word_lower]}",
                )
            )

    # Try all namelists for the parameter
    for nl_name, param_docs in QE_PARAM_DOCS.items():
        if word_lower in param_docs:
            return types.Hover(
                contents=types.MarkupContent(
                    kind=types.MarkupKind.Markdown,
                    value=f"**{word_lower}** ({nl_name})\n\n{param_docs[word_lower]}",
                )
            )

    return None


# ---------------------------------------------------------------------------
# References provider
# ---------------------------------------------------------------------------


def get_references(
    text: str,
    line_number: int,
    character: int,
    uri: str,
    include_declaration: bool = True,
) -> List[types.Location]:
    """Return all references to the symbol at the given position.

    Handles:
    - Namelist names -> all lines referencing that namelist
    - Card names -> all lines referencing that card
    - Parameters -> all assignment occurrences
    """
    index = build_symbol_index(text)
    word = _word_at_position(text, line_number, character)
    if not word:
        return []

    candidates = index.lookup(word)
    if not candidates:
        return []

    locations: List[types.Location] = []
    for symbol in candidates:
        if not include_declaration and symbol == candidates[0]:
            continue
        locations.append(
            types.Location(
                uri=uri,
                range=types.Range(
                    start=types.Position(line=symbol.line, character=symbol.character),
                    end=types.Position(line=symbol.line, character=symbol.character + symbol.length),
                ),
            )
        )
    return locations


# ---------------------------------------------------------------------------
# Document symbols provider
# ---------------------------------------------------------------------------


def get_document_symbols(text: str) -> List[types.DocumentSymbol]:
    """Return a hierarchical list of document symbols."""
    index = build_symbol_index(text)
    lines = text.splitlines()
    symbols: List[types.DocumentSymbol] = []

    # Namelists as top-level symbols with parameter children
    for name_upper in QE_NAMELISTS:
        matches = index.lookup(name_upper)
        if not matches:
            continue
        for sym in matches:
            children = _namelist_parameter_symbols(text, name_upper, sym.line, lines)
            end_line = _find_namelist_end(lines, sym.line)
            symbols.append(
                types.DocumentSymbol(
                    name=name_upper,
                    kind=types.SymbolKind.Class,
                    range=types.Range(
                        start=types.Position(line=sym.line, character=sym.character),
                        end=types.Position(line=end_line, character=0),
                    ),
                    selection_range=types.Range(
                        start=types.Position(line=sym.line, character=sym.character),
                        end=types.Position(line=sym.line, character=sym.character + sym.length),
                    ),
                    children=children or None,
                )
            )

    # Cards as top-level symbols
    for card_name in QE_CARDS:
        matches = index.lookup(card_name)
        if not matches:
            continue
        for sym in matches:
            symbols.append(
                types.DocumentSymbol(
                    name=card_name,
                    kind=types.SymbolKind.Struct,
                    range=types.Range(
                        start=types.Position(line=sym.line, character=0),
                        end=types.Position(line=sym.line, character=sym.length),
                    ),
                    selection_range=types.Range(
                        start=types.Position(line=sym.line, character=0),
                        end=types.Position(line=sym.line, character=sym.length),
                    ),
                )
            )

    return symbols


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _word_at_position(text: str, line_number: int, character: int) -> str:
    """Extract the word at a given line/character position."""
    lines = text.splitlines()
    if line_number < 0 or line_number >= len(lines):
        return ""
    line = lines[line_number]
    character = max(0, min(character, len(line)))
    start = character
    while start > 0 and not line[start - 1].isspace() and line[start - 1] not in "{,}=!":
        start -= 1
    end = character
    while end < len(line) and not line[end].isspace() and line[end] not in "{,}=!":
        end += 1
    return line[start:end].strip(",{}")


def _namelist_at_line(text: str, line_number: int) -> Optional[str]:
    """Determine which namelist contains the given line."""
    current: Optional[str] = None
    lines = text.splitlines()
    for i, raw_line in enumerate(lines):
        stripped = raw_line.split("!")[0].strip()
        if not stripped:
            continue
        if stripped.startswith("&"):
            upper_token = stripped.split()[0].upper()
            if upper_token in QE_NAMELISTS:
                current = upper_token
            else:
                current = None
            continue
        if stripped.startswith("/"):
            current = None
            continue
        if i == line_number:
            return current
    return None


def _find_namelist_end(lines: List[str], start_line: int) -> int:
    """Find the line containing '/' that closes a namelist starting at start_line."""
    for i in range(start_line + 1, len(lines)):
        stripped = lines[i].split("!")[0].strip()
        if stripped.startswith("/"):
            return i
    return len(lines) - 1


def _namelist_parameter_symbols(
    text: str, namelist_name: str, namelist_line: int, lines: List[str]
) -> List[types.DocumentSymbol]:
    """Build DocumentSymbol children for parameters inside a namelist."""
    parsed = parse_qe_input(text)
    params = parsed.namelists.get(namelist_name, {})
    symbols: List[types.DocumentSymbol] = []
    for param_name, parameter in params.items():
        symbols.append(
            types.DocumentSymbol(
                name=param_name,
                kind=types.SymbolKind.Field,
                range=types.Range(
                    start=types.Position(line=parameter.line, character=parameter.character),
                    end=types.Position(line=parameter.line, character=parameter.character + len(param_name)),
                ),
                selection_range=types.Range(
                    start=types.Position(line=parameter.line, character=parameter.character),
                    end=types.Position(line=parameter.line, character=parameter.character + len(param_name)),
                ),
            )
        )
    return symbols
