"""LSP formatting provider for Quantum ESPRESSO input files.

Provides document and range formatting that normalises indentation,
strips trailing whitespace, and preserves comments and blank lines.
Formatting is purely cosmetic: no semantic rewrites are performed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from lsprotocol.types import (
    DocumentFormattingParams,
    DocumentRangeFormattingParams,
    Position,
    Range,
    TextEdit,
)

if TYPE_CHECKING:
    from pygls.lsp.server import LanguageServer
else:
    try:
        from pygls.lsp.server import LanguageServer
    except ImportError:
        from pygls.server import LanguageServer

from ..constants import QE_KEYWORDS

#: Namelist headers that start an indented block.
_NAMELIST_HEADERS: frozenset[str] = frozenset(kw for kw in QE_KEYWORDS if kw.startswith("&"))

#: Card headers that start an indented block.
_CARD_HEADERS: frozenset[str] = frozenset(kw for kw in QE_KEYWORDS if not kw.startswith("&"))


class FormattingProvider:
    """Provides code formatting for Quantum ESPRESSO input files."""

    def __init__(self, server: LanguageServer) -> None:
        self.server = server

    def format_document(self, text: str, params: DocumentFormattingParams) -> List[TextEdit]:
        """Format the entire document.

        Args:
            text: Document text.
            params: Formatting parameters from the LSP client.

        Returns:
            A list of TextEdits (at most one replacing the full document),
            or an empty list if the document is already formatted.
        """
        lines = text.splitlines()
        if not lines:
            return []

        indent_size = params.options.tab_size if params.options else 2
        insert_spaces = params.options.insert_spaces if params.options else True
        indent_str = " " * indent_size if insert_spaces else "\t"

        formatted_lines = self._format_lines(lines, indent_str)
        formatted_text = "\n".join(formatted_lines)

        # Preserve trailing newline
        if text.endswith("\n"):
            formatted_text += "\n"

        if formatted_text == text:
            return []

        return [
            TextEdit(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=len(lines), character=0),
                ),
                new_text=formatted_text,
            )
        ]

    def format_range(self, text: str, params: DocumentRangeFormattingParams) -> List[TextEdit]:
        """Format a contiguous range of lines.

        The range is expanded to include complete logical blocks so that
        partial formatting does not break indentation context.

        Args:
            text: Document text.
            params: Range formatting parameters from the LSP client.

        Returns:
            A list of TextEdits for the requested range.
        """
        lines = text.splitlines()
        if not lines:
            return []

        start_line = params.range.start.line
        end_line = params.range.end.line

        # Clamp to document bounds
        start_line = max(0, min(start_line, len(lines) - 1))
        end_line = max(0, min(end_line, len(lines) - 1))

        indent_size = params.options.tab_size if params.options else 2
        insert_spaces = params.options.insert_spaces if params.options else True
        indent_str = " " * indent_size if insert_spaces else "\t"

        # Determine the indentation context at start_line by scanning
        # from the top of the document.
        base_indent = self._indent_at_line(lines, start_line)

        # Extract and format the target lines
        target = lines[start_line : end_line + 1]
        formatted_target = self._format_lines(target, indent_str, base_indent)

        # Build the replacement text
        new_text = "\n".join(formatted_target)
        original = "\n".join(target)

        if new_text == original:
            return []

        # Compute character offset for the end of the last line in range
        end_char = len(lines[end_line]) if end_line < len(lines) else 0

        return [
            TextEdit(
                range=Range(
                    start=Position(line=start_line, character=0),
                    end=Position(line=end_line, character=end_char),
                ),
                new_text=new_text,
            )
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _indent_at_line(lines: list[str], target_line: int) -> int:
        """Determine the indentation depth at *target_line* by scanning upward.

        Returns the number of indentation levels that should be active
        when *target_line* begins.
        """
        depth = 0
        for i in range(target_line):
            stripped = lines[i].strip()
            if not stripped:
                continue
            upper = stripped.upper()
            first_token = upper.split()[0] if upper.split() else ""

            if first_token in _NAMELIST_HEADERS:
                depth += 1
            elif stripped.startswith("/"):
                depth = max(0, depth - 1)
            elif first_token in _CARD_HEADERS:
                # Cards are top-level blocks; reset to base then indent
                depth = 1
        return depth

    @staticmethod
    def _format_lines(
        lines: list[str],
        indent_str: str,
        initial_depth: int = 0,
    ) -> list[str]:
        """Format a list of lines with the given indent string.

        QE structure: namelists (``&NAME ... /``) and cards
        (``ATOMIC_SPECIES``, etc.) are all **top-level** blocks.
        Cards never nest inside each other; each card header resets
        the indent to zero before indenting its children.

        Args:
            lines: Raw input lines.
            indent_str: String used for one level of indentation.
            initial_depth: Starting indentation depth.

        Returns:
            Formatted lines (no trailing newline).
        """
        formatted: list[str] = []
        depth = initial_depth

        for raw_line in lines:
            stripped = raw_line.strip()

            # Blank lines: preserve as empty
            if not stripped:
                formatted.append("")
                continue

            # Inline comments: strip trailing whitespace from the
            # content part but preserve the comment verbatim.
            content, _, comment = stripped.partition("!")
            content = content.strip()

            upper = content.upper() if content else ""
            first_token = upper.split()[0] if upper.split() else ""

            # Namelist terminator "/" decreases indent before the line
            if content == "/":
                depth = max(0, depth - 1)
                line_text = indent_str * depth + "/"
                if comment:
                    line_text += " !" + comment
                formatted.append(line_text)
                continue

            # Namelist header: no extra indent, increases depth after
            if first_token in _NAMELIST_HEADERS:
                line_text = content
                if comment:
                    line_text += " !" + comment
                formatted.append(line_text)
                depth += 1
                continue

            # Card header: resets to top-level, then indents children
            if first_token in _CARD_HEADERS:
                depth = 0
                line_text = content
                if comment:
                    line_text += " !" + comment
                formatted.append(line_text)
                depth += 1
                continue

            # Comment-only line (stripped started with "!")
            if stripped.startswith("!"):
                formatted.append(indent_str * depth + stripped)
                continue

            # Regular line (parameter assignment or card data row)
            line_text = indent_str * depth + content
            if comment:
                line_text += " !" + comment
            formatted.append(line_text)

        return formatted


# Alias for convenient imports
FormattingProvider = FormattingProvider  # noqa: REUP001 — explicit identity


def get_formatting_provider(server: LanguageServer) -> FormattingProvider:
    """Create a FormattingProvider instance.

    Args:
        server: The language server instance.

    Returns:
        FormattingProvider instance.
    """
    return FormattingProvider(server)


__all__ = ["FormattingProvider", "get_formatting_provider"]
