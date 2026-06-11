import json
from lsprotocol.types import Diagnostic, DiagnosticSeverity, Position, Range
from qe_lsp.features.agent_api import (
    AgentAPIProvider,
    AgentAPISnapshot,
    describe_domain_language,
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
