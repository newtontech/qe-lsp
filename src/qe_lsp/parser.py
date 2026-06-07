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
    parsed = ParsedInput()
    open_namelist: Optional[str] = None
    current_card: Optional[str] = None

    for line_number, raw_line in enumerate(text.splitlines()):
        line = strip_inline_comment(raw_line)
        if not line:
            continue

        upper_line = line.upper()
        first_token = upper_line.split()[0]

        if line.startswith("&"):
            open_namelist = first_token
            current_card = None
            parsed.namelists.setdefault(open_namelist, {})
            parsed.namelist_lines[open_namelist] = line_number
            continue

        if line.startswith("/") and open_namelist is not None:
            open_namelist = None
            continue

        if open_namelist is not None:
            for match in ASSIGNMENT_RE.finditer(line):
                name = match.group(1).lower()
                parameter = Parameter(
                    name=name,
                    value=match.group(2).strip(),
                    line=line_number,
                    character=match.start(1),
                )
                if name in parsed.namelists[open_namelist]:
                    parsed.duplicate_parameters.append(parameter)
                parsed.namelists[open_namelist][name] = parameter
            continue

        if first_token in {
            "ATOMIC_SPECIES",
            "ATOMIC_POSITIONS",
            "K_POINTS",
            "CELL_PARAMETERS",
        }:
            current_card = first_token
            parsed.cards.setdefault(current_card, [])
            parsed.card_headers[current_card] = upper_line
            continue

        if current_card is not None:
            parts = line.split()
            if parts:
                parsed.cards.setdefault(current_card, []).append(
                    CardRow(symbol=parts[0], values=parts[1:], line=line_number)
                )

    if open_namelist is not None:
        parsed.unclosed_namelist = Parameter(
            name=open_namelist,
            value="",
            line=parsed.namelist_lines.get(open_namelist, 0),
            character=0,
        )

    return parsed


def declared_species(parsed: ParsedInput) -> Set[str]:
    return {row.symbol for row in parsed.cards.get("ATOMIC_SPECIES", [])}
