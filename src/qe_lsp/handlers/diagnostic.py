"""Diagnostic handler."""

from typing import Any, List

from lsprotocol import types

from qe_lsp.text import get_text
from qe_lsp.validation import validate_qe_input


def diagnostic(params: Any) -> List[types.Diagnostic]:
    text = get_text(params)
    if not text:
        return []

    return validate_qe_input(text)
