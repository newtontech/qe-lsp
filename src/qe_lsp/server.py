"""qe Language Server Protocol server wiring."""

from importlib import import_module
from typing import Any, Type, cast

from lsprotocol.types import (
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
)

from . import __version__
from .constants import SERVER_NAME
from .features.diagnostic import DiagnosticProvider
from .features.lint import LintProvider
from .registry import register_handlers


def _load_language_server() -> Type[Any]:
    try:
        return cast(Type[Any], import_module("pygls.lsp.server").LanguageServer)
    except ImportError:
        return cast(Type[Any], import_module("pygls.server").LanguageServer)


LanguageServer = _load_language_server()


def create_server(name: str = SERVER_NAME, version: str = __version__) -> Any:
    lsp_server = LanguageServer(name, version)
    register_handlers(lsp_server)

    # Attach diagnostic provider for live feedback loops
    lsp_server.diagnostic_provider = DiagnosticProvider(lsp_server)  # type: ignore[attr-defined]

    # Attach lint provider for schema-aware static checks
    lsp_server.lint_provider = LintProvider()  # type: ignore[attr-defined]

    # Document cache used by did_open / did_change handlers
    lsp_server.documents = {}  # type: ignore[attr-defined]

    @_register(lsp_server, TEXT_DOCUMENT_DID_OPEN)
    def did_open(params: DidOpenTextDocumentParams) -> None:
        uri = params.text_document.uri
        text = params.text_document.text
        lsp_server.documents[uri] = text  # type: ignore[attr-defined]
        diagnostics = lsp_server.diagnostic_provider.get_diagnostics(text)  # type: ignore[attr-defined]
        diagnostics.extend(lsp_server.lint_provider.lint(text))  # type: ignore[attr-defined]
        lsp_server.publish_diagnostics(uri, diagnostics)

    @_register(lsp_server, TEXT_DOCUMENT_DID_CHANGE)
    def did_change(params: DidChangeTextDocumentParams) -> None:
        uri = params.text_document.uri
        if params.content_changes:
            text = params.content_changes[-1].text
            lsp_server.documents[uri] = text  # type: ignore[attr-defined]
            diagnostics = lsp_server.diagnostic_provider.get_diagnostics(text)  # type: ignore[attr-defined]
            diagnostics.extend(lsp_server.lint_provider.lint(text))  # type: ignore[attr-defined]
            lsp_server.publish_diagnostics(uri, diagnostics)

    return lsp_server


def _register(server: Any, feature_name: str) -> Any:
    """Return the ``server.feature(feature_name)`` decorator."""
    return server.feature(feature_name)


server = create_server()


def main() -> None:
    server.start_io()


if __name__ == "__main__":
    main()
