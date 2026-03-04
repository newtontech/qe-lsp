"""Documentation generation utilities for QE-LSP.

This module provides utilities for generating formatted documentation
for Quantum ESPRESSO parameters and cards, used by the LSP server
for hover tooltips and completion descriptions.
"""

from __future__ import annotations

from .data import CARD_DOCS, PARAMETER_DOCS, get_card_doc, get_parameter_doc


class DocFormatter:
    """Format documentation for LSP features."""

    @staticmethod
    def format_parameter_doc(param: str, namelist: str) -> str | None:
        """Format parameter documentation for hover tooltip.

        Args:
            param: Parameter name
            namelist: Namelist name (e.g., 'control', 'system')

        Returns:
            Formatted markdown documentation or None if not found
        """
        doc = get_parameter_doc(namelist, param)
        if doc is None:
            return None

        return f"**{param}** (in &{namelist})\n\n{doc}"

    @staticmethod
    def format_card_doc(card: str) -> str | None:
        """Format card documentation for hover tooltip.

        Args:
            card: Card name (e.g., 'ATOMIC_SPECIES')

        Returns:
            Formatted markdown documentation or None if not found
        """
        doc = get_card_doc(card)
        if doc is None:
            return None

        return f"**{card}** card\n\n{doc}"

    @staticmethod
    def format_namelist_doc(namelist: str) -> str:
        """Format namelist documentation.

        Args:
            namelist: Namelist name (e.g., 'control')

        Returns:
            Formatted markdown documentation
        """
        return f"**{namelist}** namelist\n\nQuantum ESPRESSO input namelist."


# Convenience functions
def get_formatted_parameter_doc(param: str, namelist: str) -> str | None:
    """Get formatted documentation for a parameter."""
    return DocFormatter.format_parameter_doc(param, namelist)


def get_formatted_card_doc(card: str) -> str | None:
    """Get formatted documentation for a card."""
    return DocFormatter.format_card_doc(card)


def get_formatted_namelist_doc(namelist: str) -> str:
    """Get formatted documentation for a namelist."""
    return DocFormatter.format_namelist_doc(namelist)


# Export commonly used functions
__all__ = [
    "DocFormatter",
    "get_formatted_parameter_doc",
    "get_formatted_card_doc",
    "get_formatted_namelist_doc",
    "get_parameter_doc",
    "get_card_doc",
    "PARAMETER_DOCS",
    "CARD_DOCS",
]
