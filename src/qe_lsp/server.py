"""qe Language Server Protocol server wiring."""

from importlib import import_module
from typing import Any, Type, cast

from . import __version__
from .constants import SERVER_NAME
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
    return lsp_server


server = create_server()


def main() -> None:
    server.start_io()


if __name__ == "__main__":
    main()
