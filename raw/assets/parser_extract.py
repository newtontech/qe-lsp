"""Small Quantum ESPRESSO input parser for validation."""

from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional, Set

from .text import strip_inline_comment

ASSIGNMENT_RE = re.compile(
    r"([A-Za-z_][A-Za-z0-9_]*(?:\(\d+\))?)\s*=\s*('[^']*'|\"[^\"]*\"|[^\s,]+)"
)


@dataclass
class Parameter:
    name: str
    value: str
    line: int
    character: int


@dataclass
class CardRow:
    symbol: str
    values: List[str]
    line: int


@dataclass
class ParsedInput:
    namelists: Dict[str, Dict[str, Parameter]] = field(default_factory=dict)
    duplicate_parameters: List[Parameter] = field(default_factory=list)
    namelist_lines: Dict[str, int] = field(default_factory=dict)
    unclosed_namelist: Optional[Parameter] = None
    cards: Dict[str, List[CardRow]] = field(default_factory=dict)
    card_headers: Dict[str, str] = field(default_factory=dict)


def normalize_value(value: str) -> str:
    return value.strip().strip("'\"").lower()


def parse_number(value: str) -> Optional[float]:
    try:
        return float(normalize_value(value).replace("d", "e"))
    except ValueError:
        return None


def parse_qe_input(text: str) -> ParsedInput:
