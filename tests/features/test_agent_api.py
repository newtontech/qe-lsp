import json
from lsprotocol.types import Diagnostic, DiagnosticSeverity, Position, Range
from qe_lsp.features.agent_api import (
    AgentAPIProvider,
    AgentAPISnapshot,
    describe_domain_language,
    lookup_keyword,
    lookup_namelist,
)


class TestSnapshot:
    def test_to_json(self):
        s = AgentAPISnapshot(uri="test", diagnostics=[{"line": 0}])
        assert json.loads(s.to_json())["uri"] == "test"


class TestProvider:
    def test_empty(self):
        snap = AgentAPIProvider().get_snapshot("")
        assert snap.diagnostics == []

    def test_with_diagnostics(self):
        diags = [
            Diagnostic(
                range=Range(start=Position(0, 0), end=Position(0, 0)),
                message="err",
                severity=DiagnosticSeverity.Error,
                source="test",
                code="X1",
            )
        ]
        snap = AgentAPIProvider().get_snapshot("test", diagnostics=diags)
        assert len(snap.diagnostics) == 1

    def test_outline(self):
        snap = AgentAPIProvider().get_outline_json("title test\n")
        assert "outline" in snap

    def test_metadata(self):
        snap = AgentAPIProvider().get_snapshot("test")
        assert snap.metadata["language"] == "quantum-espresso"

    def test_diags_json(self):
        r = AgentAPIProvider().get_diagnostics_json("test")
        assert "count" in r


class TestDescribeDomainLanguage:
    def test_returns_dict_with_required_top_level_keys(self):
        desc = describe_domain_language()
        assert isinstance(desc, dict)
        assert "namelists" in desc
        assert "cards" in desc
        assert "file_types" in desc
        assert desc["language"] == "quantum-espresso"

    def test_all_five_namelists_present(self):
        desc = describe_domain_language()
        namelists = desc["namelists"]
        for name in ("CONTROL", "SYSTEM", "ELECTRONS", "IONS", "CELL"):
            assert name in namelists, f"Missing namelist {name}"

    def test_namelist_has_description_and_keywords(self):
        desc = describe_domain_language()
        for nl_name, nl in desc["namelists"].items():
            assert "description" in nl, f"{nl_name} missing description"
            assert "keywords" in nl, f"{nl_name} missing keywords"
            for kw_name, kw in nl["keywords"].items():
                assert "type" in kw, f"{nl_name}.{kw_name} missing type"
                assert "description" in kw, f"{nl_name}.{kw_name} missing description"

    def test_control_calculation_keyword_has_enum(self):
        desc = describe_domain_language()
        calc_kw = desc["namelists"]["CONTROL"]["keywords"]["calculation"]
        assert "scf" in calc_kw["enum"]
        assert "vc-relax" in calc_kw["enum"]

    def test_cards_have_descriptions(self):
        desc = describe_domain_language()
        for card_name, card in desc["cards"].items():
            assert "description" in card, f"{card_name} missing description"

    def test_file_types_are_recognised_extensions(self):
        desc = describe_domain_language()
        assert ".in" in desc["file_types"]
        assert ".pw" in desc["file_types"]

    def test_return_value_is_fresh_copy(self):
        a = describe_domain_language()
        b = describe_domain_language()
        a["namelists"]["CONTROL"]["keywords"]["calculation"]["enum"].append("bogus")
        assert "bogus" not in describe_domain_language()["namelists"]["CONTROL"][
            "keywords"
        ]["calculation"]["enum"]


class TestLookupNamelist:
    def test_returns_schema_for_control(self):
        result = lookup_namelist("CONTROL")
        assert result is not None
        assert result["name"] == "CONTROL"
        assert "description" in result
        assert "keywords" in result
        assert isinstance(result["keywords"], dict)

    def test_case_insensitive_lookup(self):
        result = lookup_namelist("control")
        assert result is not None
        assert result["name"] == "CONTROL"

    def test_returns_none_for_unknown_namelist(self):
        assert lookup_namelist("BOGUS") is None

    def test_keyword_schemas_have_required_fields(self):
        result = lookup_namelist("CONTROL")
        assert result is not None
        for kw_name, kw in result["keywords"].items():
            assert "type" in kw, f"CONTROL.{kw_name} missing type"
            assert "description" in kw, f"CONTROL.{kw_name} missing description"
            assert "default_value" in kw, f"CONTROL.{kw_name} missing default_value"
            assert "valid_values" in kw, f"CONTROL.{kw_name} missing valid_values"
            assert "required" in kw, f"CONTROL.{kw_name} missing required"

    def test_enum_keyword_has_valid_values(self):
        result = lookup_namelist("CONTROL")
        assert result is not None
        calc_kw = result["keywords"]["calculation"]
        assert calc_kw["valid_values"] is not None
        assert "scf" in calc_kw["valid_values"]
        assert "vc-relax" in calc_kw["valid_values"]

    def test_non_enum_keyword_valid_values_is_none(self):
        result = lookup_namelist("CONTROL")
        assert result is not None
        prefix_kw = result["keywords"]["prefix"]
        assert prefix_kw["valid_values"] is None

    def test_all_five_namelists_found(self):
        for name in ("CONTROL", "SYSTEM", "ELECTRONS", "IONS", "CELL"):
            result = lookup_namelist(name)
            assert result is not None, f"Namelist {name} not found"
            assert result["name"] == name


class TestLookupKeyword:
    def test_returns_schema_for_calculation(self):
        result = lookup_keyword("CONTROL", "calculation")
        assert result is not None
        assert result["namelist"] == "CONTROL"
        assert result["name"] == "calculation"
        assert result["type"] == "string"
        assert result["valid_values"] is not None
        assert "scf" in result["valid_values"]

    def test_case_insensitive_namelist(self):
        result = lookup_keyword("system", "ecutwfc")
        assert result is not None
        assert result["namelist"] == "SYSTEM"
        assert result["type"] == "float"

    def test_returns_none_for_unknown_namelist(self):
        assert lookup_keyword("BOGUS", "something") is None

    def test_returns_none_for_unknown_keyword(self):
        assert lookup_keyword("CONTROL", "nonexistent_keyword") is None

    def test_non_enum_keyword_has_none_valid_values(self):
        result = lookup_keyword("CONTROL", "prefix")
        assert result is not None
        assert result["valid_values"] is None
        assert result["type"] == "string"

    def test_enum_keyword_has_valid_values_list(self):
        result = lookup_keyword("ELECTRONS", "diagonalization")
        assert result is not None
        assert result["valid_values"] is not None
        assert "david" in result["valid_values"]
        assert "cg" in result["valid_values"]

    def test_logical_keyword(self):
        result = lookup_keyword("CONTROL", "tprnfor")
        assert result is not None
        assert result["type"] == "logical"

    def test_required_field_exists(self):
        result = lookup_keyword("CONTROL", "calculation")
        assert result is not None
        assert "required" in result
        assert isinstance(result["required"], bool)

    def test_default_value_field_exists(self):
        result = lookup_keyword("CONTROL", "calculation")
        assert result is not None
        assert "default_value" in result

    def test_description_present(self):
        result = lookup_keyword("SYSTEM", "ecutwfc")
        assert result is not None
        assert "description" in result
        assert "cutoff" in result["description"].lower()
