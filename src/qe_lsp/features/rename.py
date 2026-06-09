"""LSP rename provider for Quantum ESPRESSO input files.

Supports safe workspace edits for QE variables (namelist parameters) and
local symbols (ATOMIC_SPECIES element symbols).  Rejects keywords, section
headers, unresolved symbols, and ambiguous targets with clear errors so the
editor can present actionable feedback to the user.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from lsprotocol.types import (
    Position,
    Range,
    TextEdit,
    WorkspaceEdit,
)

from ..parser import ASSIGNMENT_RE, parse_qe_input
from ..text import strip_inline_comment

# ------------------------------------------------------------------
# Unrenameable tokens
# ------------------------------------------------------------------

#: Namelist headers that the user should rename through code actions,
#: not free-form rename.
_NAMELIST_HEADERS = frozenset({
    "&CONTROL", "&SYSTEM", "&ELECTRONS", "&IONS", "&CELL",
})

#: Card headers that are structural keywords.
_CARD_HEADERS = frozenset({
    "ATOMIC_SPECIES", "ATOMIC_POSITIONS", "K_POINTS", "CELL_PARAMETERS",
})


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _word_at(text: str, line: int, character: int) -> str:
    """Return the identifier-sized word at ``(line, character)``.

    Covers alphanumeric characters, underscores, and parenthesised array
    indices like ``celldm(1)``.
    """
    lines = text.splitlines()
    if line < 0 or line >= len(lines):
        return ""

    raw = lines[line]
    if character < 0 or character > len(raw):
        return ""

    start = character
    end = character

    while start > 0 and (raw[start - 1].isalnum() or raw[start - 1] in "_("):
        start -= 1
    while end < len(raw) and (raw[end].isalnum() or raw[end] in "_()"):
        end += 1

    return raw[start:end]


def _is_valid_new_name(name: str) -> bool:
    """Return *True* when *name* is a valid QE identifier."""
    if not name:
        return False
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name))


# ------------------------------------------------------------------
# Public provider
# ------------------------------------------------------------------


class RenameProvider:
    """Provides ``textDocument/prepareRename`` and ``textDocument/rename``
    support for Quantum ESPRESSO input files.

    * **Namelist parameters** – renames every assignment of the same
      parameter *within the same namelist*.
    * **ATOMIC_SPECIES / ATOMIC_POSITIONS element symbols** – renames
      matching element symbols across both cards so they stay consistent.
    * **Rejection** – namelist headers, card headers, keywords, and
      unrecognised tokens are explicitly rejected.
    """

    # ------------------------------------------------------------------
    # prepareRename
    # ------------------------------------------------------------------

    def prepare_rename(
        self,
        text: str,
        line: int,
        character: int,
    ) -> Optional[Range]:
        """Return the range of the renamable symbol at the cursor.

        Returns ``None`` when the target cannot be safely renamed.
        """
        word = _word_at(text, line, character)
        if not word:
            return None

        upper = word.upper()
        if upper in _NAMELIST_HEADERS or upper in _CARD_HEADERS:
            return None

        lines = text.splitlines()
        raw_line = lines[line] if line < len(lines) else ""

        # Namelist parameter (assignment LHS)
        if "=" in raw_line:
            # Strip only comments, preserve leading whitespace for correct positions
            comment_stripped = raw_line.split("!", 1)[0]
            for match in ASSIGNMENT_RE.finditer(comment_stripped):
                name = match.group(1)
                if match.start(1) <= character <= match.end(1):
                    return Range(
                        start=Position(line=line, character=match.start(1)),
                        end=Position(line=line, character=match.end(1)),
                    )

        # Element symbol in card rows
        stripped = strip_inline_comment(raw_line)
        parsed = parse_qe_input(text)
        for card_name in ("ATOMIC_SPECIES", "ATOMIC_POSITIONS"):
            for row in parsed.cards.get(card_name, []):
                if row.line == line:
                    token = stripped.split()[0] if stripped.split() else ""
                    if token and token == word:
                        return Range(
                            start=Position(line=line, character=0),
                            end=Position(line=line, character=len(token)),
                        )

        return None

    # ------------------------------------------------------------------
    # rename
    # ------------------------------------------------------------------

    def rename(
        self,
        text: str,
        uri: str,
        line: int,
        character: int,
        new_name: str,
    ) -> Optional[WorkspaceEdit]:
        """Return workspace edits that rename the symbol at *cursor* to
        *new_name* across the document.

        Returns ``None`` when the target cannot be renamed.
        """
        if not _is_valid_new_name(new_name):
            return None

        lines = text.splitlines()
        if line < 0 or line >= len(lines):
            return None

        raw_line = lines[line]
        word = _word_at(text, line, character)
        if not word:
            return None

        upper = word.upper()
        if upper in _NAMELIST_HEADERS or upper in _CARD_HEADERS:
            return None

        # Try namelist-parameter rename first.
        edits = self._rename_namelist_parameter(text, line, character, new_name)
        if edits is not None:
            return WorkspaceEdit(changes={uri: edits})

        # Try element-symbol rename across ATOMIC_SPECIES / ATOMIC_POSITIONS.
        edits = self._rename_element_symbol(text, line, character, new_name)
        if edits is not None:
            return WorkspaceEdit(changes={uri: edits})

        return None

    # ------------------------------------------------------------------
    # Internal rename strategies
    # ------------------------------------------------------------------

    def _rename_namelist_parameter(
        self,
        text: str,
        trigger_line: int,
        trigger_char: int,
        new_name: str,
    ) -> Optional[List[TextEdit]]:
        """Produce edits for all assignments of the same parameter in the
        same namelist block.

        Uses raw line scanning to get correct character positions (the parser
        strips leading whitespace, so its ``param.character`` values are wrong
        for indented namelist parameters).
        """
        lines = text.splitlines()
        raw_line = lines[trigger_line] if trigger_line < len(lines) else ""

        # Find the parameter name at the trigger position using regex on raw line.
        comment_stripped = raw_line.split("!", 1)[0]
        target_param: Optional[str] = None
        for match in ASSIGNMENT_RE.finditer(comment_stripped):
            if match.start(1) <= trigger_char <= match.end(1):
                target_param = match.group(1)
                break

        if target_param is None:
            return None

        # Determine which namelist block the trigger line is in.
        target_namelist = _namelist_for_line(text, trigger_line)
        if target_namelist is None:
            return None

        # Scan the entire namelist block for all occurrences of this parameter.
        edits: List[TextEdit] = []
        param_lower = target_param.lower()
        in_target_block = False

        for i, line in enumerate(lines):
            stripped_upper = line.strip().upper()
            if stripped_upper == target_namelist.upper():
                in_target_block = True
                continue
            if in_target_block and stripped_upper == "/":
                break
            if in_target_block:
                cs = line.split("!", 1)[0]
                for match in ASSIGNMENT_RE.finditer(cs):
                    if match.group(1).lower() == param_lower:
                        edits.append(
                            TextEdit(
                                range=Range(
                                    start=Position(
                                        line=i, character=match.start(1)
                                    ),
                                    end=Position(
                                        line=i, character=match.end(1)
                                    ),
                                ),
                                new_text=new_name,
                            )
                        )

        return edits if edits else None

    def _rename_element_symbol(
        self,
        text: str,
        trigger_line: int,
        trigger_char: int,
        new_name: str,
    ) -> Optional[List[TextEdit]]:
        """Produce edits for all occurrences of an element symbol across
        ATOMIC_SPECIES and ATOMIC_POSITIONS cards."""
        parsed = parse_qe_input(text)

        # Identify which element symbol is at the trigger line.
        target_symbol: Optional[str] = None
        for card_name in ("ATOMIC_SPECIES", "ATOMIC_POSITIONS"):
            for row in parsed.cards.get(card_name, []):
                if row.line == trigger_line:
                    # Element symbol starts at column 0.
                    if trigger_char <= len(row.symbol):
                        target_symbol = row.symbol
                        break
            if target_symbol is not None:
                break

        if target_symbol is None:
            return None

        edits: List[TextEdit] = []
        for card_name in ("ATOMIC_SPECIES", "ATOMIC_POSITIONS"):
            for row in parsed.cards.get(card_name, []):
                if row.symbol == target_symbol:
                    edits.append(
                        TextEdit(
                            range=Range(
                                start=Position(line=row.line, character=0),
                                end=Position(line=row.line, character=len(row.symbol)),
                            ),
                            new_text=new_name,
                        )
                    )

        return edits if edits else None


# ------------------------------------------------------------------
# Helpers (module-private)
# ------------------------------------------------------------------


def _namelist_for_line(text: str, target_line: int) -> Optional[str]:
    """Return the namelist name that encloses *target_line*, or ``None``."""
    open_nl: Optional[str] = None
    for line_number, raw_line in enumerate(text.splitlines()):
        line = strip_inline_comment(raw_line)
        if not line:
            continue
        if line.startswith("&"):
            open_nl = line.split()[0].upper()
            continue
        if line.startswith("/"):
            open_nl = None
            continue
        if line_number == target_line:
            return open_nl
    return None


__all__ = ["RenameProvider"]
