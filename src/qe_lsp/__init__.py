"""qe-lsp - Language Server Protocol for qe."""

from importlib.metadata import PackageNotFoundError, version

from .constants import SERVER_NAME

try:
    __version__ = version(SERVER_NAME)
except PackageNotFoundError:
    __version__ = "0.1.1"
