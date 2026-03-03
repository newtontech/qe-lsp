"""Quantum ESPRESSO input file parser.

This module provides parsing capabilities for Quantum ESPRESSO input files (.in).
It supports parsing of namelists and cards commonly used in QE calculations.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple


class TokenType(Enum):
    """Token types for QE input files."""

    NAMELIST_START = auto()
    NAMELIST_END = auto()
    CARD_NAME = auto()
    PARAMETER = auto()
    VALUE = auto()
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    COMMENT = auto()
    NEWLINE = auto()
    EOF = auto()


@dataclass
class Token:
    """Represents a token in the input file."""

    type: TokenType
    value: str
    line: int
    column: int


@dataclass
class Namelist:
    """Represents a QE namelist (e.g., &control, &system)."""

    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    line_start: int = 0
    line_end: int = 0


@dataclass
class Card:
    """Represents a QE card (e.g., ATOMIC_SPECIES, K_POINTS)."""

    name: str
    options: Optional[str] = None
    data: List[List[str]] = field(default_factory=list)
    line_start: int = 0
    line_end: int = 0


@dataclass
class QEInputFile:
    """Represents a parsed QE input file."""

    namelists: Dict[str, Namelist] = field(default_factory=dict)
    cards: Dict[str, Card] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)


class QELexer:
    """Lexer for tokenizing QE input files."""

    # Common QE namelists
    NAMELISTS = {
        "control",
        "system",
        "electrons",
        "ions",
        "cell",
        "press_ai",
        "wannier",
        "inputph",
        "inputpp",
    }

    # Common QE cards
    CARDS = {
        "ATOMIC_SPECIES",
        "ATOMIC_POSITIONS",
        "K_POINTS",
        "CELL_PARAMETERS",
        "OCCUPATIONS",
        "ATOMIC_FORCES",
        "CONSTRAINTS",
        "COLLECTIVE_VARS",
        "ATOMIC_VELOCITIES",
    }

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def error(self, msg: str) -> None:
        """Record a lexer error."""
        raise SyntaxError(f"Line {self.line}, Column {self.column}: {msg}")

    def advance(self) -> str:
        """Advance to the next character."""
        if self.pos >= len(self.text):
            return ""
        char = self.text[self.pos]
        self.pos += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def peek(self, offset: int = 0) -> str:
        """Peek at the current or future character without advancing."""
        pos = self.pos + offset
        if pos >= len(self.text):
            return ""
        return self.text[pos]

    def skip_whitespace(self) -> None:
        """Skip whitespace characters except newlines."""
        while (ch := self.peek()) and ch in " \t\r":
            self.advance()

    def skip_comment(self) -> None:
        """Skip a comment line."""
        if self.peek() == "!":
            while self.peek() not in "\n" and self.peek():
                self.advance()

    def read_string(self) -> Token:
        """Read a quoted string."""
        start_line = self.line
        start_col = self.column
        quote = self.advance()  # opening quote
        value = ""
        while self.peek() != quote and self.peek():
            if self.peek() == "\\":
                self.advance()
            value += self.advance()
        if self.peek() == quote:
            self.advance()  # closing quote
        return Token(TokenType.STRING, value, start_line, start_col)

    def read_number(self) -> Token:
        """Read a number (integer or float)."""
        start_line = self.line
        start_col = self.column
        value = ""
        # Handle leading sign
        if self.peek() in "+-":
            value += self.advance()
        while (ch := self.peek()) and (ch.isdigit() or ch in ".eEdD"):
            value += self.advance()
            # Handle exponent sign
            if ch.lower() in "ed" and self.peek() in "+-":
                value += self.advance()
        # Handle Fortran scientific notation (1d-10, 2e5)
        value = value.lower().replace("d", "e")
        return Token(TokenType.NUMBER, value, start_line, start_col)

    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start_line = self.line
        start_col = self.column
        value = ""

        # Check for boolean values starting with . (e.g., .true., .false.)
        if self.peek() == ".":
            # Try to read a boolean
            bool_val = ""
            while (ch := self.peek()) and (ch.isalpha() or ch == "."):
                bool_val += self.advance()
            if bool_val.lower() in (".true.", ".false.", ".true", ".false"):
                return Token(TokenType.BOOLEAN, bool_val.lower(), start_line, start_col)
            # Not a boolean, return what we have as parameter
            return Token(TokenType.PARAMETER, bool_val, start_line, start_col)

        # Check if this is a namelist starting with &
        is_namelist = False
        if self.peek() == "&":
            value += self.advance()  # consume '&'
            is_namelist = True

        # Read the identifier
        while (ch := self.peek()) and (ch.isalnum() or ch in "_-"):
            value += self.advance()

        # Handle empty identifier
        if not value or (is_namelist and len(value) == 1):
            return Token(TokenType.PARAMETER, value, start_line, start_col)

        # Check for boolean values (must check before namelist)
        if value.lower() in ("t", "f"):
            return Token(TokenType.BOOLEAN, value.lower(), start_line, start_col)

        # Check for namelist
        if is_namelist and value[1:].lower() in self.NAMELISTS:
            return Token(TokenType.NAMELIST_START, value[1:].lower(), start_line, start_col)

        # Check for card
        if value.upper() in self.CARDS:
            return Token(TokenType.CARD_NAME, value.upper(), start_line, start_col)

        return Token(TokenType.PARAMETER, value, start_line, start_col)

    def tokenize(self) -> List[Token]:
        """Tokenize the entire input."""
        while self.pos < len(self.text):
            self.skip_whitespace()

            # Handle comments
            if self.peek() == "!":
                self.skip_comment()
                continue

            # Handle newlines
            if self.peek() == "\n":
                self.tokens.append(Token(TokenType.NEWLINE, "\n", self.line, self.column))
                self.advance()
                continue

            # Handle end of namelist
            if self.peek() == "/":
                self.tokens.append(Token(TokenType.NAMELIST_END, "/", self.line, self.column))
                self.advance()
                continue

            # Handle strings
            if self.peek() in "\"'":
                self.tokens.append(self.read_string())
                continue

            # Handle numbers (including those starting with . like .5)
            if self.peek().isdigit() or (self.peek() == "." and self.peek(1).isdigit()):
                self.tokens.append(self.read_number())
                continue

            # Handle namelists starting with &
            if self.peek() == "&":
                self.tokens.append(self.read_identifier())
                continue

            # Handle identifiers and keywords
            if self.peek().isalpha():
                self.tokens.append(self.read_identifier())
                continue

            # Handle boolean values starting with .
            if self.peek() == ".":
                self.tokens.append(self.read_identifier())
                continue

            # Handle operators and punctuation
            if self.peek() == "=":
                self.tokens.append(Token(TokenType.VALUE, "=", self.line, self.column))
                self.advance()
                continue

            if self.peek() == ",":
                self.advance()
                continue

            if self.peek() == "(":
                # Handle array indices like celldm(1)
                self.advance()
                while self.peek() and self.peek() != ")":
                    self.advance()
                if self.peek() == ")":
                    self.advance()
                continue

            if self.peek() == ")":
                self.advance()
                continue

            # Skip unknown characters
            self.advance()

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens


class QEParser:
    """Parser for Quantum ESPRESSO input files."""

    # Required parameters for each namelist
    REQUIRED_PARAMS = {
        "control": ["calculation", "prefix", "outdir"],
        "system": ["ibrav", "nat", "ntyp", "ecutwfc"],
    }

    # Parameter documentation
    PARAM_DOCS = {
        "calculation": "Type of calculation: scf, nscf, bands, relax, md, vc-relax, vc-md",
        "prefix": "Prefix for input/output files",
        "outdir": "Directory for temporary files",
        "ibrav": "Bravais lattice index (0-14)",
        "nat": "Number of atoms in the unit cell",
        "ntyp": "Number of types of atoms",
        "ecutwfc": "Kinetic energy cutoff for wavefunctions (Ry)",
        "ecutrho": "Kinetic energy cutoff for charge density (Ry)",
        "conv_thr": "Convergence threshold for SCF (Ry)",
        "diagonalization": "Diagonalization method: david, cg, ppcg",
        "mixing_mode": "Mixing mode: plain, TF, local-TF",
        "mixing_beta": "Mixing factor for self-consistency",
        "electron_maxstep": "Maximum number of SCF iterations",
        "nspin": "Spin polarization: 1 (no), 2 (yes), 4 (non-collinear)",
        "starting_magnetization": "Starting magnetic moment",
        "occupations": "Occupation function: smearing, fixed, from_input",
        "smearing": "Smearing method: gaussian, methfessel-paxton, marzari-vanderbilt, fermi-dirac",
        "degauss": "Gaussian spreading (Ry)",
    }

    def __init__(self, text: str):
        self.text = text
        self.lexer = QELexer(text)
        self.tokens: List[Token] = []
        self.pos = 0
        self.errors: List[Dict[str, Any]] = []

    def error(self, msg: str, token: Optional[Token] = None) -> None:
        """Record a parser error."""
        if token is None:
            token = self.current()
        self.errors.append(
            {"message": msg, "line": token.line, "column": token.column, "severity": "error"}
        )

    def current(self) -> Token:
        """Get the current token."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1] if self.tokens else Token(TokenType.EOF, "", 0, 0)

    def advance(self) -> Token:
        """Advance to the next token."""
        token = self.current()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Optional[Token]:
        """Expect a specific token type."""
        if self.current().type == token_type:
            return self.advance()
        return None

    def parse_value(self) -> Any:
        """Parse a value (string, number, boolean, or array)."""
        token = self.current()

        if token.type == TokenType.STRING:
            self.advance()
            return token.value

        if token.type == TokenType.NUMBER:
            self.advance()
            try:
                if "." in token.value or "e" in token.value.lower():
                    return float(token.value)
                return int(token.value)
            except ValueError:
                return token.value

        if token.type == TokenType.BOOLEAN:
            self.advance()
            return token.value in (".true.", "t", ".true")

        if token.type == TokenType.PARAMETER:
            self.advance()
            return token.value

        return None

    def parse_namelist(self) -> Optional[Namelist]:
        """Parse a namelist section."""
        start_token = self.current()
        if start_token.type != TokenType.NAMELIST_START:
            return None

        name = start_token.value
        line_start = start_token.line
        self.advance()

        namelist = Namelist(name=name, line_start=line_start)
        current_param = None

        while self.current().type not in (TokenType.NAMELIST_END, TokenType.EOF):
            if self.current().type == TokenType.NEWLINE:
                self.advance()
                continue

            if self.current().type == TokenType.PARAMETER:
                current_param = self.current().value.lower()
                namelist.parameters[current_param] = None
                self.advance()

                # Expect '='
                if self.current().type == TokenType.VALUE:
                    self.advance()
                    # Parse the value
                    value = self.parse_value()
                    if value is not None:
                        namelist.parameters[current_param] = value
                    else:
                        self.error(f"Expected value for parameter '{current_param}'")
                else:
                    # Value might be missing '=' - try to parse anyway
                    pass

            elif self.current().type == TokenType.COMMENT:
                self.advance()
            else:
                self.advance()

        # Consume '/'
        if self.current().type == TokenType.NAMELIST_END:
            self.advance()

        namelist.line_end = self.current().line
        return namelist

    def parse_card_data(self, card_name: str) -> List[List[str]]:
        """Parse card data lines."""
        data = []

        while self.current().type not in (
            TokenType.CARD_NAME,
            TokenType.NAMELIST_START,
            TokenType.EOF,
        ):
            if self.current().type == TokenType.NEWLINE:
                self.advance()
                continue

            if self.current().type == TokenType.COMMENT:
                self.advance()
                continue

            # Read a line of data
            line_data = []
            while self.current().type not in (
                TokenType.NEWLINE,
                TokenType.CARD_NAME,
                TokenType.NAMELIST_START,
                TokenType.EOF,
            ):
                if self.current().type == TokenType.COMMENT:
                    break
                if self.current().type in (
                    TokenType.STRING,
                    TokenType.NUMBER,
                    TokenType.PARAMETER,
                    TokenType.BOOLEAN,
                ):
                    line_data.append(str(self.current().value))
                self.advance()

            if line_data:
                data.append(line_data)

            if self.current().type == TokenType.NEWLINE:
                self.advance()

        return data

    def parse_card(self) -> Optional[Card]:
        """Parse a card section."""
        start_token = self.current()
        if start_token.type != TokenType.CARD_NAME:
            return None

        name = start_token.value
        line_start = start_token.line
        self.advance()

        # Check for options (e.g., ATOMIC_POSITIONS {crystal})
        options = None
        if self.current().type == TokenType.PARAMETER:
            options = self.current().value
            self.advance()

        # Skip newline after card name
        if self.current().type == TokenType.NEWLINE:
            self.advance()

        data = self.parse_card_data(name)

        card = Card(
            name=name,
            options=options,
            data=data,
            line_start=line_start,
            line_end=self.current().line,
        )

        return card

    def validate(self, result: QEInputFile) -> None:
        """Validate the parsed input file."""
        # Check for required namelists
        if "control" not in result.namelists:
            self.errors.append(
                {
                    "message": "Missing required namelist '&control'",
                    "line": 1,
                    "column": 1,
                    "severity": "error",
                }
            )

        if "system" not in result.namelists:
            self.errors.append(
                {
                    "message": "Missing required namelist '&system'",
                    "line": 1,
                    "column": 1,
                    "severity": "error",
                }
            )

        # Check for required parameters in each namelist
        for namelist_name, required in self.REQUIRED_PARAMS.items():
            if namelist_name in result.namelists:
                namelist = result.namelists[namelist_name]
                for param in required:
                    if param not in namelist.parameters:
                        self.errors.append(
                            {
                                "message": f"Missing required parameter '{param}' in &{namelist_name}",
                                "line": namelist.line_start,
                                "column": 1,
                                "severity": "error",
                            }
                        )

    def parse(self) -> QEInputFile:
        """Parse the input file."""
        result = QEInputFile()

        # Tokenize
        self.tokens = self.lexer.tokenize()
        self.pos = 0

        while self.current().type != TokenType.EOF:
            if self.current().type == TokenType.NEWLINE:
                self.advance()
                continue

            if self.current().type == TokenType.NAMELIST_START:
                namelist = self.parse_namelist()
                if namelist:
                    result.namelists[namelist.name] = namelist
                continue

            if self.current().type == TokenType.CARD_NAME:
                card = self.parse_card()
                if card:
                    result.cards[card.name] = card
                continue

            # Skip unknown tokens
            self.advance()

        # Validate
        self.validate(result)
        result.errors = self.errors

        return result


def parse_qe_input(text: str) -> QEInputFile:
    """Parse a Quantum ESPRESSO input file.

    Args:
        text: The content of the input file

    Returns:
        QEInputFile object containing parsed namelists and cards
    """
    parser = QEParser(text)
    return parser.parse()


def get_parameter_doc(param: str) -> Optional[str]:
    """Get documentation for a parameter.

    Args:
        param: The parameter name

    Returns:
        Documentation string or None if not found
    """
    return QEParser.PARAM_DOCS.get(param.lower())


def get_namelist_params(namelist: str) -> List[str]:
    """Get list of known parameters for a namelist.

    Args:
        namelist: The namelist name (e.g., 'control', 'system')

    Returns:
        List of parameter names
    """
    # This is a simplified list - in practice, you'd want a comprehensive database
    params_by_namelist = {
        "control": [
            "calculation",
            "title",
            "verbosity",
            "restart_mode",
            "outdir",
            "wfcdir",
            "prefix",
            "disk_io",
            "pseudo_dir",
            "tstress",
            "tprnfor",
            "dt",
            "nstep",
            "iprint",
            "tabps",
            "max_seconds",
            "etot_conv_thr",
            "forc_conv_thr",
            "tefield",
            "dipfield",
            "lelfield",
            "lorbm",
            "lberry",
            "gdir",
            "nppstr",
            "lfcpopt",
            "gate",
            "trism",
        ],
        "system": [
            "ibrav",
            "celldm",
            "A",
            "B",
            "C",
            "cosAB",
            "cosAC",
            "cosBC",
            "nat",
            "ntyp",
            "nbnd",
            "tot_charge",
            "starting_charge",
            "tot_magnetization",
            "starting_magnetization",
            "nspin",
            "ecutwfc",
            "ecutrho",
            "ecutfock",
            "nr1",
            "nr2",
            "nr3",
            "nr1s",
            "nr2s",
            "nr3s",
            "nosym",
            "nosym_evc",
            "noinv",
            "no_t_rev",
            "force_symmorphic",
            "use_all_frac",
            "occupations",
            "degauss",
            "smearing",
            "one_atom_occupations",
            "spinorbit",
            "noncolin",
            "lspinorb",
            "lforcet",
            "starting_spin_angle",
            "angle1",
            "angle2",
            "constrained_magnetization",
            "B_field",
            "fixed_magnetization",
            "lambda",
            "report",
            "lscfpert",
            "esm_bc",
            "esm_w",
            "esm_efield",
            "esm_nfit",
            "fcp_mu",
            "vdw_corr",
            "london",
            "london_s6",
            "london_c6",
            "london_rvdw",
            "london_rcut",
            "ts_vdw_econv_thr",
            "xdm",
            "xdm_a1",
            "xdm_a2",
            "space_group",
            "origin_choice",
            "rhombohedral",
            "zmon",
            "realxz",
            "block",
            "block_1",
            "block_2",
            "block_height",
        ],
        "electrons": [
            "electron_maxstep",
            "scf_must_converge",
            "conv_thr",
            "adaptive_thr",
            "conv_thr_init",
            "conv_thr_multi",
            "mixing_mode",
            "mixing_beta",
            "mixing_ndim",
            "mixing_fixed_ns",
            "diagonalization",
            "ortho_para",
            "diago_thr_init",
            "diago_cg_maxiter",
            "diago_ppcg_maxiter",
            "diago_david_ndim",
            "diago_full_acc",
            "efield",
            "efield_cart",
            "efield_phase",
            "startingpot",
            "startingwfc",
            "tqr",
            "real_space",
        ],
        "ions": [
            "ion_dynamics",
            "ion_positions",
            "pot_extrapolation",
            "wfc_extrapolation",
            "remove_rigid_rot",
            "ion_temperature",
            "tempw",
            "tolp",
            "delta_t",
            "nraise",
            "refold_pos",
            "upscale",
            "bfgs_ndim",
            "trust_radius_max",
            "trust_radius_min",
            "trust_radius_ini",
            "w_1",
            "w_2",
            "fire_alpha_init",
            "fire_fmax",
        ],
        "cell": [
            "cell_dynamics",
            "press",
            "wmass",
            "cell_factor",
            "press_conv_thr",
            "cell_dofree",
            "protate",
        ],
    }
    return params_by_namelist.get(namelist.lower(), [])


def get_card_names() -> List[str]:
    """Get list of valid card names.

    Returns:
        List of card names
    """
    return list(QELexer.CARDS)


def get_word_at_position(text: str, line: int, column: int) -> Tuple[Optional[str], int, int]:
    """Get the word at a specific position in the text.

    Args:
        text: The text content
        line: 0-based line number
        column: 0-based column number

    Returns:
        Tuple of (word, start_col, end_col) or (None, 0, 0) if not found
    """
    lines = text.split("\n")
    if line >= len(lines):
        return None, 0, 0

    line_text = lines[line]
    if column >= len(line_text):
        return None, 0, 0

    # Find word boundaries
    start = column
    while start > 0 and line_text[start - 1].isalnum():
        start -= 1

    end = column
    while end < len(line_text) and line_text[end].isalnum():
        end += 1

    word = line_text[start:end] if start < end else None
    return word, start, end


# Alias for compatibility
parse = parse_qe_input
