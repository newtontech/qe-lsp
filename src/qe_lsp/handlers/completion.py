"""Completion handler."""

from typing import Any, List

from lsprotocol import types

from qe_lsp.constants import QE_KEYWORDS


def completion(params: Any) -> List[types.CompletionItem]:
    return [
        types.CompletionItem(
            label=keyword,
            kind=types.CompletionItemKind.Keyword,
            detail="Quantum ESPRESSO input keyword",
        )
        for keyword in QE_KEYWORDS
    ]
