"""Tests for navigation features: definition, hover, references, symbols."""

import pytest
from lsprotocol import types

from qe_lsp.features.navigation import (
    build_symbol_index,
    get_definition,
    get_document_symbols,
    get_hover,
    get_references,
)
from qe_lsp.handlers.definition import definition
from qe_lsp.handlers.document_symbol import document_symbol
from qe_lsp.handlers.hover import hover
from qe_lsp.handlers.references import references


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_INPUT = """\
&CONTROL
  calculation = 'scf'
  title = 'test'
/
&SYSTEM
  ibrav = 1
  celldm(1) = 7.5
  nat = 2
  ntyp = 1
  ecutwfc = 60
  ecutrho = 480
/
&ELECTRONS
  conv_thr = 1d-8
  mixing_beta = 0.7
/
ATOMIC_SPECIES
Si 28.086 Si.pbe.UPF
ATOMIC_POSITIONS {crystal}
Si 0.0 0.0 0.0
Si 0.25 0.25 0.25
K_POINTS {automatic}
4 4 4 0 0 0
"""
# Line index:
#  0: &CONTROL
#  1:   calculation = 'scf'
#  2:   title = 'test'
#  3: /
#  4: &SYSTEM
#  5:   ibrav = 1
#  6:   celldm(1) = 7.5
#  7:   nat = 2
#  8:   ntyp = 1
#  9:   ecutwfc = 60
# 10:   ecutrho = 480
# 11: /
# 12: &ELECTRONS
# 13:   conv_thr = 1d-8
# 14:   mixing_beta = 0.7
# 15: /
# 16: ATOMIC_SPECIES
# 17: Si 28.086 Si.pbe.UPF
# 18: ATOMIC_POSITIONS {crystal}
# 19: Si 0.0 0.0 0.0
# 20: Si 0.25 0.25 0.25
# 21: K_POINTS {automatic}
# 22: 4 4 4 0 0 0

MULTI_NAMELIST_INPUT = """\
&CONTROL
  calculation = 'relax'
/
&SYSTEM
  ibrav = 0
  nat = 1
  ntyp = 1
  ecutwfc = 40
/
&IONS
  ion_dynamics = 'bfgs'
/
&CELL
  cell_dynamics = 'bfgs'
  press = 0.0
/
CELL_PARAMETERS {angstrom}
2.715 2.715 0.0
0.0 2.715 2.715
2.715 0.0 2.715
ATOMIC_POSITIONS {crystal}
Si 0.0 0.0 0.0
"""
# Line index:
#  0: &CONTROL
#  1:   calculation = 'relax'
#  2: /
#  3: &SYSTEM
#  4:   ibrav = 0
#  5:   nat = 1
#  6:   ntyp = 1
#  7:   ecutwfc = 40
#  8: /
#  9: &IONS
# 10:   ion_dynamics = 'bfgs'
# 11: /
# 12: &CELL
# 13:   cell_dynamics = 'bfgs'
# 14:   press = 0.0
# 15: /
# 16: CELL_PARAMETERS {angstrom}
# 17: 2.715 2.715 0.0
# 18: 0.0 2.715 2.715
# 19: 2.715 0.0 2.715
# 20: ATOMIC_POSITIONS {crystal}
# 21: Si 0.0 0.0 0.0


class Params:
    """Minimal LSP-params stand-in for handler tests."""

    def __init__(self, text: str, line: int = 0, character: int = 0, uri: str = "file:///test.in"):
        self.text = text
        self.position = {"line": line, "character": character}
        self.text_document = type("TD", (), {"uri": uri})()
        self.context = type("Ctx", (), {"include_declaration": True})()


# ===========================================================================
# Symbol index
# ===========================================================================


class TestSymbolIndex:
    def test_index_namelists(self) -> None:
        index = build_symbol_index(SAMPLE_INPUT)
        control = index.lookup("&CONTROL")
        assert len(control) == 1
        assert control[0].kind == "namelist"
        assert control[0].line == 0

    def test_index_cards(self) -> None:
        index = build_symbol_index(SAMPLE_INPUT)
        species = index.lookup("ATOMIC_SPECIES")
        assert len(species) == 1
        assert species[0].kind == "card"

    def test_index_parameters(self) -> None:
        index = build_symbol_index(SAMPLE_INPUT)
        ecutwfc = index.lookup("ecutwfc")
        assert len(ecutwfc) >= 1
        assert ecutwfc[0].kind in ("parameter", "variable")

    def test_index_unknown_returns_empty(self) -> None:
        index = build_symbol_index(SAMPLE_INPUT)
        assert index.lookup("nonexistent") == []


# ===========================================================================
# Go-to-definition
# ===========================================================================


class TestDefinition:
    def test_namelist_definition(self) -> None:
        # &CONTROL at line 0
        result = get_definition(SAMPLE_INPUT, 0, 2, "file:///test.in")
        assert result is not None
        assert isinstance(result, types.Location)
        assert result.range.start.line == 0
        assert result.range.start.character == 0

    def test_parameter_definition(self) -> None:
        # ecutwfc at line 9
        result = get_definition(SAMPLE_INPUT, 9, 2, "file:///test.in")
        assert result is not None
        assert result.range.start.line == 9

    def test_card_definition(self) -> None:
        # ATOMIC_SPECIES at line 16
        result = get_definition(SAMPLE_INPUT, 16, 2, "file:///test.in")
        assert result is not None
        assert result.range.start.line == 16

    def test_unknown_position_returns_none(self) -> None:
        # Blank line 3 (/) at character 0 - not a known symbol
        result = get_definition(SAMPLE_INPUT, 3, 0, "file:///test.in")
        assert result is None

    def test_handler_delegates(self) -> None:
        params = Params(SAMPLE_INPUT, line=0, character=2)
        result = definition(params)
        assert result is not None
        assert isinstance(result, types.Location)

    def test_empty_text_returns_none(self) -> None:
        result = get_definition("", 0, 0, "file:///test.in")
        assert result is None

    def test_handler_empty_text(self) -> None:
        result = definition(Params("", line=0, character=0))
        assert result is None


# ===========================================================================
# Hover
# ===========================================================================


class TestHover:
    def test_hover_namelist_section(self) -> None:
        # &CONTROL at line 0
        result = get_hover(SAMPLE_INPUT, 0, 2)
        assert result is not None
        assert isinstance(result.contents, types.MarkupContent)
        assert "&CONTROL" in result.contents.value

    def test_hover_card(self) -> None:
        # ATOMIC_SPECIES at line 16
        result = get_hover(SAMPLE_INPUT, 16, 2)
        assert result is not None
        assert "ATOMIC_SPECIES" in result.contents.value

    def test_hover_parameter_ecutwfc(self) -> None:
        # ecutwfc at line 9
        result = get_hover(SAMPLE_INPUT, 9, 2)
        assert result is not None
        assert "ecutwfc" in result.contents.value.lower()

    def test_hover_mixing_beta(self) -> None:
        # mixing_beta at line 14
        result = get_hover(SAMPLE_INPUT, 14, 2)
        assert result is not None
        assert "mixing_beta" in result.contents.value.lower()

    def test_hover_unknown_returns_none(self) -> None:
        # whitespace-only position
        result = get_hover("   \n   \n", 0, 0)
        assert result is None

    def test_hover_handler(self) -> None:
        # ecutwfc at line 9 via handler
        params = Params(SAMPLE_INPUT, line=9, character=2)
        result = hover(params)
        assert result is not None
        assert isinstance(result, types.Hover)
        assert "ecutwfc" in result.contents.value.lower()

    def test_hover_handler_empty(self) -> None:
        result = hover(Params("", line=0, character=0))
        assert result is None

    def test_hover_ion_dynamics(self) -> None:
        # ion_dynamics at line 10 in MULTI_NAMELIST_INPUT
        result = get_hover(MULTI_NAMELIST_INPUT, 10, 2)
        assert result is not None
        assert "ion_dynamics" in result.contents.value.lower()

    def test_hover_cell_dynamics(self) -> None:
        # cell_dynamics at line 13 in MULTI_NAMELIST_INPUT
        result = get_hover(MULTI_NAMELIST_INPUT, 13, 2)
        assert result is not None
        assert "cell_dynamics" in result.contents.value.lower()

    def test_hover_system_parameter(self) -> None:
        # ibrav at line 5
        result = get_hover(SAMPLE_INPUT, 5, 2)
        assert result is not None
        assert "ibrav" in result.contents.value.lower()

    def test_hover_conv_thr(self) -> None:
        # conv_thr at line 13
        result = get_hover(SAMPLE_INPUT, 13, 2)
        assert result is not None
        assert "conv_thr" in result.contents.value.lower()


# ===========================================================================
# References
# ===========================================================================


class TestReferences:
    def test_references_namelist(self) -> None:
        # &CONTROL at line 0
        result = get_references(SAMPLE_INPUT, 0, 2, "file:///test.in")
        assert len(result) >= 1
        assert all(isinstance(loc, types.Location) for loc in result)

    def test_references_parameter(self) -> None:
        # ecutwfc appears once at line 9
        result = get_references(SAMPLE_INPUT, 9, 2, "file:///test.in")
        assert len(result) >= 1

    def test_references_card(self) -> None:
        # ATOMIC_SPECIES at line 16
        result = get_references(SAMPLE_INPUT, 16, 2, "file:///test.in")
        assert len(result) >= 1
        assert result[0].range.start.line == 16

    def test_references_unknown_returns_empty(self) -> None:
        result = get_references("no symbols here", 0, 3, "file:///test.in")
        assert result == []

    def test_references_exclude_declaration(self) -> None:
        # With include_declaration=False, skip the first (definition) occurrence
        result = get_references(SAMPLE_INPUT, 0, 2, "file:///test.in", include_declaration=False)
        # &CONTROL only appears once, so excluding declaration gives empty
        assert len(result) == 0

    def test_references_handler(self) -> None:
        params = Params(SAMPLE_INPUT, line=0, character=2)
        result = references(params)
        assert len(result) >= 1
        assert all(isinstance(loc, types.Location) for loc in result)

    def test_references_handler_empty(self) -> None:
        result = references(Params("", line=0, character=0))
        assert result == []


# ===========================================================================
# Document symbols
# ===========================================================================


class TestDocumentSymbols:
    def test_symbols_include_namelists(self) -> None:
        symbols = get_document_symbols(SAMPLE_INPUT)
        names = [s.name for s in symbols]
        assert "&CONTROL" in names
        assert "&SYSTEM" in names
        assert "&ELECTRONS" in names

    def test_symbols_include_cards(self) -> None:
        symbols = get_document_symbols(SAMPLE_INPUT)
        names = [s.name for s in symbols]
        assert "ATOMIC_SPECIES" in names
        assert "ATOMIC_POSITIONS" in names
        assert "K_POINTS" in names

    def test_namelists_have_parameter_children(self) -> None:
        symbols = get_document_symbols(SAMPLE_INPUT)
        control = next(s for s in symbols if s.name == "&CONTROL")
        assert control.children is not None
        child_names = [c.name for c in control.children]
        assert "calculation" in child_names
        assert "title" in child_names

    def test_system_namelist_children(self) -> None:
        symbols = get_document_symbols(SAMPLE_INPUT)
        system = next(s for s in symbols if s.name == "&SYSTEM")
        assert system.children is not None
        child_names = [c.name for c in system.children]
        assert "ibrav" in child_names
        assert "ecutwfc" in child_names
        assert "ecutrho" in child_names

    def test_symbol_kinds(self) -> None:
        symbols = get_document_symbols(SAMPLE_INPUT)
        for sym in symbols:
            if sym.name.startswith("&"):
                assert sym.kind == types.SymbolKind.Class
            else:
                assert sym.kind == types.SymbolKind.Struct

    def test_empty_input_no_symbols(self) -> None:
        symbols = get_document_symbols("")
        assert symbols == []

    def test_handler(self) -> None:
        params = Params(SAMPLE_INPUT)
        result = document_symbol(params)
        assert len(result) > 0
        assert all(isinstance(s, types.DocumentSymbol) for s in result)

    def test_handler_empty(self) -> None:
        result = document_symbol(Params(""))
        assert result == []

    def test_multi_namelist_symbols(self) -> None:
        symbols = get_document_symbols(MULTI_NAMELIST_INPUT)
        names = [s.name for s in symbols]
        assert "&CONTROL" in names
        assert "&SYSTEM" in names
        assert "&IONS" in names
        assert "&CELL" in names
        assert "CELL_PARAMETERS" in names


# ===========================================================================
# Integration: handler registration
# ===========================================================================


class TestServerRegistration:
    def test_server_registers_definition(self) -> None:
        from qe_lsp.server import server

        features = server.lsp.fm.features
        assert "textDocument/definition" in features

    def test_server_registers_references(self) -> None:
        from qe_lsp.server import server

        features = server.lsp.fm.features
        assert "textDocument/references" in features

    def test_server_registers_document_symbol(self) -> None:
        from qe_lsp.server import server

        features = server.lsp.fm.features
        assert "textDocument/documentSymbol" in features

    def test_server_registers_hover(self) -> None:
        from qe_lsp.server import server

        features = server.lsp.fm.features
        assert "textDocument/hover" in features
