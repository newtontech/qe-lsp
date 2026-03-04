"""qe-lsp - Language Server Protocol for Quantum ESPRESSO"""

__version__ = "0.1.0"

from typing import Any

from qe_lsp.data import (
    format_card_hover,
    format_param_hover,
    get_card_doc,
    get_param_doc,
)
from qe_lsp.parser import (
    Card,
    Namelist,
    QEInputFile,
    QELexer,
    QEParser,
    Token,
    TokenType,
    get_card_names,
    get_namelist_params,
    parse_qe_input,
)

# Alias for backward compatibility
get_parameter_doc = get_param_doc
QEInput = QEInputFile
parse = parse_qe_input


# Lazy import for server/main to avoid pygls initialization issues
def __getattr__(name: str) -> Any:
    if name == "server":
        from qe_lsp.server import _get_server

        return _get_server()
    elif name == "main":
        from qe_lsp.server import main

        return main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "__version__",
    "parse_qe_input",
    "parse",
    "get_parameter_doc",
    "get_param_doc",
    "get_namelist_params",
    "get_card_names",
    "get_card_doc",
    "QEInputFile",
    "QEInput",
    "Namelist",
    "Card",
    "QEParser",
    "QELexer",
    "Token",
    "TokenType",
    "server",
    "main",
    "format_param_hover",
    "format_card_hover",
]
