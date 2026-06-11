import json
from lsprotocol.types import Diagnostic, DiagnosticSeverity, Position, Range
from qe_lsp.features.agent_api import (
    AgentAPIProvider,
    AgentAPISnapshot,
    describe_domain_language,
    get_examples,
    get_rule_manifest,
    lookup_keyword,
    lookup_namelist,
    next_token_suggestions,
    openqc_smoke,
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


# ------------------------------------------------------------------
# Tests for get_examples()
# ------------------------------------------------------------------

_ALL_CALC_TYPES = ["scf", "nscf", "relax", "vc-relax", "md", "phonon", "bands", "dos"]


class TestGetExamples:
    def test_returns_all_examples_when_no_type_given(self):
        examples = get_examples()
        assert len(examples) == 8

    def test_all_calculation_types_present(self):
        examples = get_examples()
        types = {ex["calculation_type"] for ex in examples}
        for ct in _ALL_CALC_TYPES:
            assert ct in types, f"Missing calculation type: {ct}"

    def test_each_example_has_required_keys(self):
        for ex in get_examples():
            assert "name" in ex
            assert "description" in ex
            assert "calculation_type" in ex
            assert "input_text" in ex

    def test_each_example_has_nonempty_input_text(self):
        for ex in get_examples():
            assert len(ex["input_text"].strip()) > 0

    def test_filter_by_scf(self):
        examples = get_examples("scf")
        assert len(examples) == 1
        assert examples[0]["calculation_type"] == "scf"

    def test_filter_by_vc_relax(self):
        examples = get_examples("vc-relax")
        assert len(examples) == 1
        assert examples[0]["calculation_type"] == "vc-relax"
        assert "CELL" in examples[0]["input_text"]

    def test_filter_by_phonon(self):
        examples = get_examples("phonon")
        assert len(examples) == 1
        assert "INPUTPH" in examples[0]["input_text"]

    def test_filter_by_dos(self):
        examples = get_examples("dos")
        assert len(examples) == 1
        assert "DOS" in examples[0]["input_text"]

    def test_filter_by_bands(self):
        examples = get_examples("bands")
        assert len(examples) == 1
        assert "K_POINTS crystal" in examples[0]["input_text"]

    def test_unknown_type_returns_empty(self):
        assert get_examples("bogus") == []

    def test_examples_are_fresh_copies(self):
        a = get_examples("scf")
        b = get_examples("scf")
        a[0]["input_text"] = "mutated"
        assert b[0]["input_text"] != "mutated"


# ------------------------------------------------------------------
# Tests for next_token_suggestions()
# ------------------------------------------------------------------


class TestNextTokenSuggestions:
    def test_empty_context_returns_namelist_suggestions(self):
        suggestions = next_token_suggestions("")
        assert len(suggestions) >= 1
        texts = [s["text"] for s in suggestions]
        assert any("&CONTROL" in t for t in texts)

    def test_control_namelist_suggests_keywords(self):
        suggestions = next_token_suggestions("&CONTROL\n")
        texts = [s["text"] for s in suggestions]
        assert any("calculation" in t for t in texts)
        assert any("prefix" in t for t in texts)
        assert any("pseudo_dir" in t for t in texts)

    def test_system_namelist_suggests_keywords(self):
        suggestions = next_token_suggestions("&SYSTEM\n")
        texts = [s["text"] for s in suggestions]
        assert any("nat" in t for t in texts)
        assert any("ecutwfc" in t for t in texts)

    def test_electrons_namelist_suggests_keywords(self):
        suggestions = next_token_suggestions("&ELECTRONS\n")
        texts = [s["text"] for s in suggestions]
        assert any("conv_thr" in t for t in texts)

    def test_ions_namelist_suggests_keywords(self):
        suggestions = next_token_suggestions("&IONS\n")
        texts = [s["text"] for s in suggestions]
        assert any("ion_dynamics" in t for t in texts)

    def test_cell_namelist_suggests_keywords(self):
        suggestions = next_token_suggestions("&CELL\n")
        texts = [s["text"] for s in suggestions]
        assert any("press" in t for t in texts)

    def test_after_namelist_end_suggests_cards(self):
        ctx = "&CONTROL\n  calculation = 'scf'\n/\n"
        suggestions = next_token_suggestions(ctx)
        texts = [s["text"] for s in suggestions]
        assert any("ATOMIC_SPECIES" in t for t in texts)
        assert any("K_POINTS" in t for t in texts)

    def test_after_atomic_species_suggests_placeholder(self):
        suggestions = next_token_suggestions("ATOMIC_SPECIES\n")
        assert len(suggestions) >= 1
        assert any("label" in s["text"] for s in suggestions)

    def test_after_atomic_positions_suggests_placeholder(self):
        suggestions = next_token_suggestions("ATOMIC_POSITIONS crystal\n")
        assert len(suggestions) >= 1
        assert any("label" in s["text"] for s in suggestions)

    def test_after_k_points_suggests_placeholder(self):
        suggestions = next_token_suggestions("K_POINTS automatic\n")
        assert len(suggestions) >= 1
        assert any("nk1" in s["text"] for s in suggestions)

    def test_calculation_assignment_suggests_values(self):
        ctx = "&CONTROL\n  calculation = '"
        suggestions = next_token_suggestions(ctx)
        texts = [s["text"] for s in suggestions]
        assert any("scf" in t for t in texts)
        assert any("vc-relax" in t for t in texts)
        assert any("md" in t for t in texts)

    def test_unrecognized_line_suggests_namelist_end(self):
        suggestions = next_token_suggestions("  some_random_text = 1\n")
        texts = [s["text"] for s in suggestions]
        assert any("/" in t for t in texts)

    def test_prefix_filter(self):
        suggestions = next_token_suggestions("&CONTROL\n", prefix="calc")
        assert len(suggestions) >= 1
        assert all(s["text"].startswith("calc") for s in suggestions)

    def test_prefix_filter_returns_empty_when_no_match(self):
        suggestions = next_token_suggestions("&CONTROL\n", prefix="zzz")
        assert suggestions == []

    def test_suggestions_have_required_keys(self):
        for s in next_token_suggestions("&CONTROL\n"):
            assert "text" in s
            assert "type" in s
            assert "description" in s

    def test_suggestion_types_are_strings(self):
        for s in next_token_suggestions("&SYSTEM\n"):
            assert isinstance(s["text"], str)
            assert isinstance(s["type"], str)
            assert isinstance(s["description"], str)


# ------------------------------------------------------------------
# Tests for get_rule_manifest()
# ------------------------------------------------------------------


class TestGetRuleManifest:
    def test_returns_non_empty_list(self):
        manifest = get_rule_manifest()
        assert isinstance(manifest, list)
        assert len(manifest) > 0

    def test_each_entry_has_required_keys(self):
        for entry in get_rule_manifest():
            assert "code" in entry
            assert "rule_id" in entry
            assert "severity" in entry
            assert "description" in entry

    def test_codes_follow_convention(self):
        """All codes should start with 'QE-' and use E/W/TE/TW prefixes."""
        for entry in get_rule_manifest():
            code = entry["code"]
            assert code.startswith("QE-"), f"Code {code} does not start with QE-"

    def test_severity_is_error_or_warning(self):
        for entry in get_rule_manifest():
            assert entry["severity"] in ("error", "warning")

    def test_rule_ids_use_dot_notation(self):
        for entry in get_rule_manifest():
            assert "." in entry["rule_id"], f"rule_id {entry['rule_id']} missing dot separator"

    def test_known_rules_present(self):
        """Verify that key rules we depend on are in the manifest."""
        codes = {e["code"] for e in get_rule_manifest()}
        assert "QE-E008" in codes  # missing_control
        assert "QE-E009" in codes  # bad_calculation
        assert "QE-W010" in codes  # conv_thr_loose
        assert "QE-W011" in codes  # ecutrho_inconsistent
        assert "QE-W012" in codes  # occupations_degauss_mismatch
        assert "QE-E013" in codes  # invalid_kpoints_card

    def test_returns_fresh_copy(self):
        a = get_rule_manifest()
        b = get_rule_manifest()
        a[0]["code"] = "MUTATED"
        assert b[0]["code"] != "MUTATED"

    def test_no_duplicate_codes(self):
        codes = [e["code"] for e in get_rule_manifest()]
        assert len(codes) == len(set(codes))

    def test_manifest_is_json_serialisable(self):
        manifest = get_rule_manifest()
        serialised = json.dumps(manifest)
        round_tripped = json.loads(serialised)
        assert round_tripped == manifest


# ------------------------------------------------------------------
# Tests for openqc_smoke()
# ------------------------------------------------------------------


class TestOpenqcSmoke:
    def test_smoke_passes(self):
        result = openqc_smoke()
        assert result["status"] == "pass", f"Smoke failed: {result['errors']}"

    def test_manifest_rule_count_positive(self):
        result = openqc_smoke()
        assert result["manifest_rule_count"] > 0

    def test_diagnostic_engine_ok(self):
        result = openqc_smoke()
        assert result["diagnostic_engine_ok"] is True

    def test_agent_api_ok(self):
        result = openqc_smoke()
        assert result["agent_api_ok"] is True

    def test_probe_results_non_empty(self):
        result = openqc_smoke()
        assert len(result["probe_results"]) > 0

    def test_all_probes_pass(self):
        result = openqc_smoke()
        for probe in result["probe_results"]:
            assert probe["status"] == "pass", (
                f"Probe '{probe['name']}' failed: expected {probe['expected_code']}, "
                f"got {probe.get('actual_codes', [])}"
            )

    def test_all_six_probes_present(self):
        result = openqc_smoke()
        probe_names = {p["name"] for p in result["probe_results"]}
        expected = {
            "missing_control",
            "bad_calculation",
            "conv_thr_loose",
            "ecutrho_inconsistent",
            "occupations_degauss_mismatch",
            "invalid_kpoints_card",
        }
        assert probe_names == expected

    def test_errors_list_empty_on_pass(self):
        result = openqc_smoke()
        assert result["errors"] == []

    def test_result_is_json_serialisable(self):
        result = openqc_smoke()
        serialised = json.dumps(result)
        round_tripped = json.loads(serialised)
        assert round_tripped["status"] == "pass"

    def test_probe_has_expected_code(self):
        result = openqc_smoke()
        for probe in result["probe_results"]:
            assert "expected_code" in probe
            assert probe["expected_code"].startswith("QE-")
