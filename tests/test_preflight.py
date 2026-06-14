from __future__ import annotations

import json
from pathlib import Path

import pytest

from qe_lsp import tool
from qe_lsp.preflight import (
    ALL_ROLES,
    CODE_LOW_ECUTWFC,
    CODE_MISSING_INPUT,
    CODE_MISSING_LATTICE,
    CODE_MISSING_PSEUDOS,
    CODE_MISSING_STRUCTURE,
    CODE_NTYP_SPECIES_MISMATCH,
    CODE_SUSPICIOUS_KPOINTS,
    CODE_UNKNOWN_KEYWORD_VERSION,
    CODE_UNRESOLVED_PSEUDO,
    CODE_VERSION_ASSUMPTION,
    DEFAULT_ECUTWFC_WARNING_RY,
    ArtifactGraph,
    build_artifact_graph,
    fleet_manifest,
    resolve_version_assumption,
)
from qe_lsp.tool import (
    _looks_like_workspace,
    check_path,
    manifest_path,
    preflight_path,
)

FIXTURES = Path(__file__).parent / "fixtures" / "preflight"

# Envelope fields the issue acceptance criteria require on failing fixtures.
REQUIRED_FAILING_FIELDS = {
    "code",
    "severity",
    "path",
    "range",
    "blocking",
    "category",
    "source_provenance",
}


def _envelope_codes(payload: dict) -> set[str]:
    return {item["code"] for item in payload["diagnostics"]}


# --- Envelope shape --------------------------------------------------------


def test_agent_check_payload_carries_diagnostic_envelope_v1(capsys) -> None:
    # exercise the real CLI path so the capabilities block is attached
    rc = tool.main(["check", str(FIXTURES / "ntyp_mismatch")])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["diagnostic_envelope"] == "v1"
    assert payload["diagnostic_engine"] == "1.0"
    assert payload["software"] == "qe"
    # capabilities block is attached by the CLI wrapper
    assert payload["capabilities"]["operation"] == "check"
    # version assumption is surfaced at top level so the parent probe can branch
    assert "version_assumption" in payload
    assert payload["version_assumption"]["software"] == "qe"
    # cross-artifact graph is serialized for the fleet report workflow
    assert isinstance(payload.get("artifacts"), list)
    assert payload["artifacts"]


def test_failing_diagnostics_carry_required_envelope_fields() -> None:
    payload = preflight_path(FIXTURES / "ntyp_mismatch")
    failing = [
        item for item in payload["diagnostics"] if item["code"] == CODE_NTYP_SPECIES_MISMATCH
    ]
    assert failing, "ntyp mismatch fixture must emit QE604"
    item = failing[0]
    for field in REQUIRED_FAILING_FIELDS:
        assert field in item, f"missing required envelope field: {field}"
    # Richer envelope fields used by the parent fleet probe
    assert item["confidence"] >= 0.0
    assert "actions" in item and item["actions"]
    assert "fix_hints" in item and item["fix_hints"]
    assert "facts" in item
    assert item["facts"]["declared_ntyp"] == 1
    assert item["facts"]["species_count"] == 2
    assert "artifact_roles" in item
    # range is a proper LSP-style start/end object
    assert item["range"]["start"]["line"] >= 0
    assert "character" in item["range"]["start"]


# --- Fixture behavior ------------------------------------------------------


@pytest.mark.parametrize(
    "fixture, expected_ok, must_include",
    [
        ("valid_pw", True, set()),
        ("ntyp_mismatch", False, {CODE_NTYP_SPECIES_MISMATCH}),
        ("missing_cell_parameters", False, {CODE_MISSING_LATTICE}),
        ("missing_pseudos", False, {CODE_MISSING_PSEUDOS}),
        ("low_ecutwfc", True, {CODE_LOW_ECUTWFC}),
        ("suspicious_kpoints", True, {CODE_SUSPICIOUS_KPOINTS}),
        ("missing_kpoints", True, {CODE_SUSPICIOUS_KPOINTS}),
        ("keyword_version_mismatch", False, {CODE_UNKNOWN_KEYWORD_VERSION}),
    ],
)
def test_preflight_fixture_expectations(
    fixture: str,
    expected_ok: bool,
    must_include: set[str],
) -> None:
    payload = preflight_path(FIXTURES / fixture)
    codes = _envelope_codes(payload)
    assert (
        payload["ok"] is expected_ok
    ), f"{fixture}: expected ok={expected_ok}, got codes={sorted(codes)}"
    assert must_include <= codes, f"{fixture}: expected codes {must_include}, got {sorted(codes)}"


def test_valid_pw_fixture_has_no_blocking_or_error_diagnostics() -> None:
    payload = preflight_path(FIXTURES / "valid_pw")
    assert payload["summary"]["errors"] == 0
    assert payload["summary"]["blocking"] == 0
    # valid fixture must not carry the preflight error codes
    error_codes = {
        CODE_MISSING_INPUT,
        CODE_MISSING_STRUCTURE,
        CODE_MISSING_LATTICE,
        CODE_NTYP_SPECIES_MISMATCH,
        CODE_MISSING_PSEUDOS,
        CODE_UNKNOWN_KEYWORD_VERSION,
    }
    assert not (_envelope_codes(payload) & error_codes)


def test_low_ecutwfc_is_non_blocking_warning_with_threshold_fact() -> None:
    payload = preflight_path(FIXTURES / "low_ecutwfc")
    item = next(d for d in payload["diagnostics"] if d["code"] == CODE_LOW_ECUTWFC)
    assert item["severity"] == "warning"
    assert item["blocking"] is False
    assert item["facts"]["ecutwfc"] == 20.0
    assert item["facts"]["threshold"] == DEFAULT_ECUTWFC_WARNING_RY


def test_low_ecutwfc_intent_override_changes_threshold(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "pw.in").write_text(
        "&CONTROL\n/\n&SYSTEM\n  ibrav = 0\n  nat = 1\n  ntyp = 1\n  ecutwfc = 40\n/\n"
        "&ELECTRONS\n/\n"
        "ATOMIC_SPECIES\n  Si 28.085 Si.UPF\n"
        "ATOMIC_POSITIONS crystal\n  Si 0.0 0.0 0.0\n"
        "K_POINTS automatic\n  4 4 4 0 0 0\n"
        "CELL_PARAMETERS angstrom\n  1 0 0\n  0 1 0\n  0 0 1\n",
        encoding="utf-8",
    )
    (case / "Si.UPF").write_text("<UPF/>", encoding="utf-8")
    # No intent: default threshold 50 -> ecutwfc 40 is below -> warning fires.
    base = preflight_path(case)
    assert CODE_LOW_ECUTWFC in _envelope_codes(base)

    cfg = case / ".qe-lsp"
    cfg.mkdir()
    (cfg / "intent.json").write_text(json.dumps({"ecutwfc_warning_ry": 30.0}), encoding="utf-8")
    overridden = preflight_path(case)
    assert CODE_LOW_ECUTWFC not in _envelope_codes(overridden)


# --- version-aware-keywords ------------------------------------------------


def test_version_assumption_unknown_when_intent_absent() -> None:
    assumption = resolve_version_assumption(None)
    assert assumption["exact_runtime_known"] is False
    assert assumption["declared_by"] == "fallback"
    assert assumption["software_version"] == "unknown"


def test_version_assumption_known_when_intent_declares_version() -> None:
    assumption = resolve_version_assumption(
        {"software_version": "qe >=7.2", "runtime_image": "img:7.2"}
    )
    assert assumption["exact_runtime_known"] is True
    assert assumption["declared_by"] == "intent"
    assert assumption["software_version"] == "qe >=7.2"


def test_version_assumption_information_diagnostic_when_unknown(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "pw.in").write_text(
        "&CONTROL\n/\n&SYSTEM\n  ibrav = 0\n  nat = 1\n  ntyp = 1\n  ecutwfc = 80\n/\n"
        "&ELECTRONS\n/\n"
        "ATOMIC_SPECIES\n  Si 28.085 Si.UPF\n"
        "ATOMIC_POSITIONS crystal\n  Si 0.0 0.0 0.0\n"
        "K_POINTS automatic\n  4 4 4 0 0 0\n"
        "CELL_PARAMETERS angstrom\n  1 0 0\n  0 1 0\n  0 0 1\n",
        encoding="utf-8",
    )
    (case / "Si.UPF").write_text("<UPF/>", encoding="utf-8")
    payload = preflight_path(case)
    item = next(
        (d for d in payload["diagnostics"] if d["code"] == CODE_VERSION_ASSUMPTION),
        None,
    )
    assert item is not None
    assert item["severity"] == "information"
    assert item["blocking"] is False
    assert item["version_assumption"]["exact_runtime_known"] is False


def test_version_assumption_silent_when_intent_declares_version(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "pw.in").write_text(
        "&CONTROL\n/\n&SYSTEM\n  ibrav = 0\n  nat = 1\n  ntyp = 1\n  ecutwfc = 80\n/\n"
        "&ELECTRONS\n/\n"
        "ATOMIC_SPECIES\n  Si 28.085 Si.UPF\n"
        "ATOMIC_POSITIONS crystal\n  Si 0.0 0.0 0.0\n"
        "K_POINTS automatic\n  4 4 4 0 0 0\n"
        "CELL_PARAMETERS angstrom\n  1 0 0\n  0 1 0\n  0 0 1\n",
        encoding="utf-8",
    )
    (case / "Si.UPF").write_text("<UPF/>", encoding="utf-8")
    cfg = case / ".qe-lsp"
    cfg.mkdir()
    (cfg / "intent.json").write_text(json.dumps({"software_version": "qe >=7.2"}), encoding="utf-8")
    payload = preflight_path(case)
    assert CODE_VERSION_ASSUMPTION not in _envelope_codes(payload)
    assert payload["version_assumption"]["exact_runtime_known"] is True


def test_keyword_version_mismatch_carries_version_assumption() -> None:
    payload = preflight_path(FIXTURES / "keyword_version_mismatch")
    item = next(d for d in payload["diagnostics"] if d["code"] == CODE_UNKNOWN_KEYWORD_VERSION)
    # The fixture declares qe >=5.0 and uses `gate`, which requires >=6.4.
    assert item["facts"]["keyword"] == "gate"
    assert item["facts"]["required_version"] == "qe >=6.4"
    assert "version-aware" in item["domain_tags"]
    assert "version_assumption" in item


# --- cross-artifact-graph --------------------------------------------------


def test_artifact_graph_uses_generic_roles() -> None:
    from qe_lsp.parser import parse_qe_input

    case_dir = (FIXTURES / "valid_pw").resolve()
    text = (case_dir / "pw.in").read_text(encoding="utf-8")
    parsed = parse_qe_input(text)
    graph = build_artifact_graph(case_dir, parsed, case_dir / "pw.in")
    roles = {node.role for node in graph.nodes}
    assert roles <= set(ALL_ROLES)
    # primary-input, structure, kpoints, lattice are always present
    for required in ("primary-input", "structure", "kpoints", "lattice"):
        assert graph.by_role(required), f"missing required role: {required}"
    # serialized graph is JSON-friendly and stable
    serialized = graph.to_json()
    assert isinstance(serialized, list)
    assert all("role" in node and "path" in node and "exists" in node for node in serialized)


def test_missing_lattice_records_ibrav_fact() -> None:
    payload = preflight_path(FIXTURES / "missing_cell_parameters")
    item = next(d for d in payload["diagnostics"] if d["code"] == CODE_MISSING_LATTICE)
    prov = item["source_provenance"]
    assert prov["role"] == "lattice"
    # ibrav=0 was the declared free-cell mode
    assert item["facts"]["ibrav"] == 0


def test_unresolved_pseudopotential_is_warning(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "pw.in").write_text(
        "&CONTROL\n  pseudo_dir = './'\n/\n&SYSTEM\n  ibrav = 0\n  nat = 1\n  ntyp = 1\n"
        "  ecutwfc = 80\n/\n&ELECTRONS\n/\n"
        "ATOMIC_SPECIES\n  Si 28.085 Si_missing.UPF\n"
        "ATOMIC_POSITIONS crystal\n  Si 0.0 0.0 0.0\n"
        "K_POINTS automatic\n  4 4 4 0 0 0\n"
        "CELL_PARAMETERS angstrom\n  1 0 0\n  0 1 0\n  0 0 1\n",
        encoding="utf-8",
    )
    payload = preflight_path(case)
    item = next(
        (d for d in payload["diagnostics"] if d["code"] == CODE_UNRESOLVED_PSEUDO),
        None,
    )
    assert item is not None
    assert item["severity"] == "warning"
    assert item["artifact_roles"] == ["pseudopotential"]


def test_suspicious_kpoints_warning_on_single_point_axis() -> None:
    payload = preflight_path(FIXTURES / "suspicious_kpoints")
    item = next(
        (d for d in payload["diagnostics"] if d["code"] == CODE_SUSPICIOUS_KPOINTS),
        None,
    )
    assert item is not None
    assert item["severity"] == "warning"
    assert item["facts"]["grid"] == [1, 4, 4]


def test_missing_kpoints_card_emits_non_blocking_warning() -> None:
    payload = preflight_path(FIXTURES / "missing_kpoints")
    item = next(
        (d for d in payload["diagnostics"] if d["code"] == CODE_SUSPICIOUS_KPOINTS),
        None,
    )
    assert item is not None
    assert item["severity"] == "warning"
    assert item["blocking"] is False


def test_missing_primary_input_emits_blocking_finding(tmp_path: Path) -> None:
    case = tmp_path / "empty"
    case.mkdir()
    payload = preflight_path(case)
    item = next(
        (d for d in payload["diagnostics"] if d["code"] == CODE_MISSING_INPUT),
        None,
    )
    assert item is not None
    assert item["severity"] == "error"
    assert item["blocking"] is True


# --- code-actions / blocking gate -----------------------------------------


def test_check_fail_on_blocking_exits_nonzero_on_failing_fixture() -> None:
    rc = tool.main(["check", str(FIXTURES / "ntyp_mismatch"), "--fail-on-blocking"])
    assert rc == 1


def test_check_fail_on_blocking_exits_zero_on_valid_fixture(capsys) -> None:
    rc = tool.main(["check", str(FIXTURES / "valid_pw"), "--fail-on-blocking"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True


def test_preflight_subcommand_emits_envelope(capsys) -> None:
    rc = tool.main(["preflight", str(FIXTURES / "low_ecutwfc")])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["operation"] == "preflight"
    assert payload["diagnostic_envelope"] == "v1"
    assert payload["capabilities"]["operation"] == "preflight"


def test_preflight_fail_on_blocking_exits_nonzero() -> None:
    rc = tool.main(["preflight", str(FIXTURES / "ntyp_mismatch"), "--fail-on-blocking"])
    assert rc == 1


def test_actions_present_on_blocking_diagnostics() -> None:
    payload = preflight_path(FIXTURES / "ntyp_mismatch")
    blocking = [d for d in payload["diagnostics"] if d["blocking"]]
    assert blocking
    for item in blocking:
        assert item.get("actions"), f"blocking diagnostic {item['code']} must carry actions"
        assert all("kind" in action for action in item["actions"])


# --- fleet-regression-fixtures / manifest ---------------------------------


def test_manifest_lists_all_four_capabilities() -> None:
    manifest = manifest_path(FIXTURES / "valid_pw")
    capabilities = manifest["capabilities"]
    for cap in (
        "version-aware-keywords",
        "cross-artifact-graph",
        "code-actions",
        "fleet-regression-fixtures",
    ):
        assert cap in capabilities, f"missing capability: {cap}"
        assert capabilities[cap]["status"] == "available"
    # artifact roles are the generic fleet model, not MatMaster policy
    assert set(manifest["artifact_roles"]) == set(ALL_ROLES)
    assert manifest["preflight_envelope"] == "DiagnosticEnvelope/v1"


def test_manifest_without_path_still_describes_surface() -> None:
    manifest = manifest_path(None)
    assert set(manifest["codes"])
    assert manifest["capabilities"]["code-actions"]["blocking_gate"]


def test_manifest_merges_fixture_expectations() -> None:
    manifest = manifest_path(FIXTURES / "valid_pw")
    fixtures = manifest["capabilities"]["fleet-regression-fixtures"]["fixtures"]
    names = {item["name"] for item in fixtures}
    assert {
        "valid_pw",
        "ntyp_mismatch",
        "missing_cell_parameters",
        "missing_pseudos",
        "low_ecutwfc",
        "suspicious_kpoints",
        "missing_kpoints",
        "keyword_version_mismatch",
    } <= names


def test_fleet_manifest_helper_pure_data() -> None:
    manifest = fleet_manifest(fixtures=[{"name": "x", "expect_ok": True}])
    assert manifest["capabilities"]["fleet-regression-fixtures"]["fixtures"] == [
        {"name": "x", "expect_ok": True}
    ]
    # every code entry is self-describing for the parent probe
    for body in manifest["codes"].values():
        assert body["severity"] in {"error", "warning", "information", "hint"}
        assert "capability" in body
        assert "summary" in body


def test_fixture_expectations_match_actual_preflight() -> None:
    """The fleet manifest's declared fixture expectations must match reality.

    This is the regression-evidence contract: the parent ``bohrium_skills``
    probe consumes the manifest and replays these fixtures, so the declared
    expectations have to agree with what the preflight actually emits.
    """
    manifest = manifest_path(FIXTURES / "valid_pw")
    repo_root = Path(__file__).resolve().parent.parent
    for fixture in manifest["capabilities"]["fleet-regression-fixtures"]["fixtures"]:
        payload = preflight_path(repo_root / fixture["path"])
        assert payload["ok"] is fixture["expect_ok"], (
            f"{fixture['name']}: manifest expects ok={fixture['expect_ok']}, "
            f"got ok={payload['ok']}"
        )
        if fixture["expect_codes"]:
            assert set(fixture["expect_codes"]) <= _envelope_codes(payload), (
                f"{fixture['name']}: expected codes {fixture['expect_codes']}, "
                f"got {sorted(_envelope_codes(payload))}"
            )


# --- workspace detection ---------------------------------------------------


def test_looks_like_workspace_requires_qe_input(tmp_path: Path) -> None:
    assert _looks_like_workspace(tmp_path) is False
    (tmp_path / "pw.in").write_text("&CONTROL\n/\n", encoding="utf-8")
    assert _looks_like_workspace(tmp_path) is True


def test_check_on_single_input_file_does_not_run_preflight(tmp_path: Path) -> None:
    # A bare pw.in with no case-directory context must keep the legacy
    # single-file behavior and NOT flood with blocking missing-artifact
    # preflight errors.
    input_path = tmp_path / "pw.in"
    input_path.write_text("&CONTROL\n/\n", encoding="utf-8")
    payload = check_path(input_path)
    preflight_codes = {
        CODE_MISSING_INPUT,
        CODE_MISSING_STRUCTURE,
        CODE_MISSING_LATTICE,
    }
    assert not (_envelope_codes(payload) & preflight_codes)


def test_check_on_full_workspace_merges_preflight() -> None:
    payload = check_path(FIXTURES / "ntyp_mismatch")
    codes = _envelope_codes(payload)
    assert CODE_NTYP_SPECIES_MISMATCH in codes
    assert payload["diagnostic_envelope"] == "v1"


def test_artifact_graph_is_json_serializable_for_fleet_report() -> None:
    payload = preflight_path(FIXTURES / "valid_pw")
    # artifacts must round-trip through json.dumps cleanly for the parent probe
    serialized = json.dumps(payload["artifacts"], sort_keys=True)
    assert "primary-input" in serialized
    assert "structure" in serialized


def test_artifact_graph_class_smoke() -> None:
    graph = ArtifactGraph(case_dir=Path("/tmp"))
    assert graph.nodes == []
    assert graph.by_role("structure") == []
    assert graph.to_json() == []
