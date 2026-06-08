"""Feature registry for pygls handlers."""

from typing import Any, Callable, List, Protocol, Tuple

from .handlers.code_action import code_action
from .handlers.completion import completion
from .handlers.diagnostic import diagnostic
from .handlers.hover import hover

Handler = Callable[[Any], Any]


class SupportsFeatureRegistration(Protocol):
    def feature(self, feature_name: str) -> Callable[[Handler], Handler]: ...


def default_handlers() -> List[Tuple[str, Handler]]:
    return [
        ("textDocument/completion", completion),
        ("textDocument/hover", hover),
        ("textDocument/diagnostic", diagnostic),
        ("textDocument/codeAction", code_action),
    ]


def register_handlers(server: SupportsFeatureRegistration) -> None:
    for feature_name, handler in default_handlers():
        server.feature(feature_name)(handler)
