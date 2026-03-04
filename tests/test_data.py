"""Tests for data module."""

from qe_lsp.data import (
    ALL_PARAMS,
    CARD_DOCS,
    CELL_PARAMS,
    CONTROL_PARAMS,
    ELECTRONS_PARAMS,
    IONS_PARAMS,
    NAMELIST_SUGGESTIONS,
    SYSTEM_PARAMS,
    format_card_hover,
    format_param_hover,
    get_card_doc,
    get_param_doc,
)


class TestControlParams:
    """Test CONTROL namelist parameters."""

    def test_calculation_param(self):
        """Test calculation parameter documentation."""
        assert "calculation" in CONTROL_PARAMS
        doc = CONTROL_PARAMS["calculation"]
        assert doc["required"] is True
        assert "type" in doc
        assert "values" in doc

    def test_prefix_param(self):
        """Test prefix parameter documentation."""
        assert "prefix" in CONTROL_PARAMS
        doc = CONTROL_PARAMS["prefix"]
        assert doc["type"] == "string"

    def test_verbosity_param(self):
        """Test verbosity parameter documentation."""
        assert "verbosity" in CONTROL_PARAMS
        doc = CONTROL_PARAMS["verbosity"]
        assert "values" in doc

    def test_all_control_params_have_description(self):
        """Test that all control params have descriptions."""
        for name, doc in CONTROL_PARAMS.items():
            assert "description" in doc, f"{name} missing description"
            assert "type" in doc, f"{name} missing type"


class TestSystemParams:
    """Test SYSTEM namelist parameters."""

    def test_ibrav_param(self):
        """Test ibrav parameter documentation."""
        assert "ibrav" in SYSTEM_PARAMS
        doc = SYSTEM_PARAMS["ibrav"]
        assert doc["required"] is True
        assert "values" in doc

    def test_nat_ntyp_params(self):
        """Test nat and ntyp parameters."""
        assert "nat" in SYSTEM_PARAMS
        assert "ntyp" in SYSTEM_PARAMS
        assert SYSTEM_PARAMS["nat"]["required"] is True
        assert SYSTEM_PARAMS["ntyp"]["required"] is True

    def test_ecutwfc_param(self):
        """Test ecutwfc parameter documentation."""
        assert "ecutwfc" in SYSTEM_PARAMS
        doc = SYSTEM_PARAMS["ecutwfc"]
        assert doc["type"] == "real"
        assert doc["required"] is True

    def test_all_system_params(self):
        """Test that all system params are properly documented."""
        for name, doc in SYSTEM_PARAMS.items():
            assert "description" in doc, f"{name} missing description"
            assert "type" in doc, f"{name} missing type"


class TestElectronsParams:
    """Test ELECTRONS namelist parameters."""

    def test_conv_thr_param(self):
        """Test conv_thr parameter documentation."""
        assert "conv_thr" in ELECTRONS_PARAMS
        doc = ELECTRONS_PARAMS["conv_thr"]
        assert "default" in doc

    def test_mixing_params(self):
        """Test mixing parameters."""
        assert "mixing_beta" in ELECTRONS_PARAMS
        assert "mixing_mode" in ELECTRONS_PARAMS

    def test_diagonalization_param(self):
        """Test diagonalization parameter."""
        assert "diagonalization" in ELECTRONS_PARAMS
        doc = ELECTRONS_PARAMS["diagonalization"]
        assert "values" in doc

    def test_all_electrons_params(self):
        """Test that all electrons params are properly documented."""
        for name, doc in ELECTRONS_PARAMS.items():
            assert "description" in doc, f"{name} missing description"


class TestIonsParams:
    """Test IONS namelist parameters."""

    def test_ion_dynamics_param(self):
        """Test ion_dynamics parameter documentation."""
        assert "ion_dynamics" in IONS_PARAMS
        doc = IONS_PARAMS["ion_dynamics"]
        assert "values" in doc

    def test_bfgs_params(self):
        """Test BFGS-related parameters."""
        assert "trust_radius_max" in IONS_PARAMS
        assert "trust_radius_min" in IONS_PARAMS
        assert "bfgs_ndim" in IONS_PARAMS


class TestCellParams:
    """Test CELL namelist parameters."""

    def test_cell_dynamics_param(self):
        """Test cell_dynamics parameter documentation."""
        assert "cell_dynamics" in CELL_PARAMS
        doc = CELL_PARAMS["cell_dynamics"]
        assert "values" in doc

    def test_press_param(self):
        """Test press parameter documentation."""
        assert "press" in CELL_PARAMS
        doc = CELL_PARAMS["press"]
        assert "default" in doc


class TestAllParams:
    """Test combined ALL_PARAMS dictionary."""

    def test_all_params_structure(self):
        """Test that ALL_PARAMS contains all namelists."""
        assert "control" in ALL_PARAMS
        assert "system" in ALL_PARAMS
        assert "electrons" in ALL_PARAMS
        assert "ions" in ALL_PARAMS
        assert "cell" in ALL_PARAMS

    def test_namelist_suggestions(self):
        """Test that NAMELIST_SUGGESTIONS matches ALL_PARAMS."""
        for namelist in ALL_PARAMS.keys():
            assert namelist in NAMELIST_SUGGESTIONS
            assert set(NAMELIST_SUGGESTIONS[namelist]) == set(ALL_PARAMS[namelist].keys())


class TestCardDocs:
    """Test CARD_DOCS dictionary."""

    def test_atomic_species_doc(self):
        """Test ATOMIC_SPECIES card documentation."""
        assert "ATOMIC_SPECIES" in CARD_DOCS
        doc = CARD_DOCS["ATOMIC_SPECIES"]
        assert "description" in doc
        assert "format" in doc

    def test_atomic_positions_doc(self):
        """Test ATOMIC_POSITIONS card documentation."""
        assert "ATOMIC_POSITIONS" in CARD_DOCS
        doc = CARD_DOCS["ATOMIC_POSITIONS"]
        assert "description" in doc

    def test_k_points_doc(self):
        """Test K_POINTS card documentation."""
        assert "K_POINTS" in CARD_DOCS
        doc = CARD_DOCS["K_POINTS"]
        assert "description" in doc

    def test_cell_parameters_doc(self):
        """Test CELL_PARAMETERS card documentation."""
        assert "CELL_PARAMETERS" in CARD_DOCS
        doc = CARD_DOCS["CELL_PARAMETERS"]
        assert "description" in doc

    def test_all_cards_have_description(self):
        """Test that all cards have descriptions."""
        for name, doc in CARD_DOCS.items():
            assert "description" in doc, f"{name} missing description"


class TestGetParamDoc:
    """Test get_param_doc function."""

    def test_get_existing_param(self):
        """Test getting documentation for existing parameter."""
        doc = get_param_doc("control", "calculation")
        assert doc is not None
        assert "description" in doc

    def test_get_nonexistent_param(self):
        """Test getting documentation for non-existent parameter."""
        doc = get_param_doc("control", "nonexistent")
        assert doc is None

    def test_get_param_case_insensitive_namelist(self):
        """Test that namelist name is case-insensitive."""
        doc_lower = get_param_doc("control", "calculation")
        doc_upper = get_param_doc("CONTROL", "calculation")
        assert doc_lower == doc_upper

    def test_get_param_from_invalid_namelist(self):
        """Test getting param from invalid namelist."""
        doc = get_param_doc("invalid", "param")
        assert doc is None


class TestGetCardDoc:
    """Test get_card_doc function."""

    def test_get_existing_card(self):
        """Test getting documentation for existing card."""
        doc = get_card_doc("ATOMIC_SPECIES")
        assert doc is not None
        assert "description" in doc

    def test_get_nonexistent_card(self):
        """Test getting documentation for non-existent card."""
        doc = get_card_doc("NONEXISTENT")
        assert doc is None

    def test_get_card_case_insensitive(self):
        """Test that card name is case-insensitive."""
        doc_upper = get_card_doc("ATOMIC_SPECIES")
        doc_lower = get_card_doc("atomic_species")
        assert doc_upper == doc_lower


class TestFormatParamHover:
    """Test format_param_hover function."""

    def test_format_basic_param(self):
        """Test formatting basic parameter."""
        param_doc = {
            "description": "Test description",
            "type": "string",
        }
        result = format_param_hover(param_doc)
        assert "Test description" in result
        assert "string" in result

    def test_format_param_with_default(self):
        """Test formatting parameter with default."""
        param_doc = {
            "description": "Test description",
            "type": "real",
            "default": 1.0,
        }
        result = format_param_hover(param_doc)
        assert "Default:" in result
        assert "1.0" in result

    def test_format_required_param(self):
        """Test formatting required parameter."""
        param_doc = {
            "description": "Test description",
            "type": "string",
            "required": True,
        }
        result = format_param_hover(param_doc)
        assert "Required parameter" in result

    def test_format_param_with_values(self):
        """Test formatting parameter with values."""
        param_doc = {
            "description": "Test description",
            "type": "string",
            "values": ["'value1'", "'value2'"],
        }
        result = format_param_hover(param_doc)
        assert "Possible values:" in result
        assert "'value1'" in result


class TestFormatCardHover:
    """Test format_card_hover function."""

    def test_format_basic_card(self):
        """Test formatting basic card."""
        card_doc = {
            "description": "Test description",
        }
        result = format_card_hover(card_doc)
        assert "Test description" in result

    def test_format_card_with_format(self):
        """Test formatting card with format."""
        card_doc = {
            "description": "Test description",
            "format": "FORMAT\n  data",
        }
        result = format_card_hover(card_doc)
        assert "Format:" in result
        assert "FORMAT" in result

    def test_format_card_with_example(self):
        """Test formatting card with example."""
        card_doc = {
            "description": "Test description",
            "example": "EXAMPLE\n  data",
        }
        result = format_card_hover(card_doc)
        assert "Example:" in result
        assert "EXAMPLE" in result

    def test_format_card_with_required_when(self):
        """Test formatting card with required_when."""
        card_doc = {
            "description": "Test description",
            "required_when": "some_condition",
        }
        result = format_card_hover(card_doc)
        assert "Required when:" in result
        assert "some_condition" in result
