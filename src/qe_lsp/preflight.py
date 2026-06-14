"""Universal generated-input preflight capabilities.

This module implements the four fleet-wide preflight capabilities called out in
``newtontech/qe-lsp#85`` against a *generic artifact-role model*, so the checks
generalize to any backend in the scientific LSP fleet instead of being wired to
MatMaster submission policy:

* ``version-aware-keywords``  - explicit runtime/version assumption metadata and
  keyword-availability validation derived from the builtin keyword set, never
  guessed.
* ``cross-artifact-graph``   - resolves the case as a graph of artifacts with
  stable roles (primary-input, structure, kpoints, pseudopotential, lattice).
  For Quantum ESPRESSO the structure/kpoints/lattice roles are in-file cards of
  the primary ``pw.x`` input (``ATOMIC_POSITIONS``/``K_POINTS``/
  ``CELL_PARAMETERS``), while the pseudopotential role is the one true
  cross-file artifact (external ``.UPF`` files referenced per species in the
  ``ATOMIC_SPECIES`` card). The same role set generalizes to the rest of the
  fleet (VASP/CP2K/ABINIT/...).
* ``code-actions``           - normalizes repair hints/actions on every
  diagnostic and exposes a blocking gate the agent CLI can run as
  ``check --fail-on-blocking``.
* ``fleet-regression-fixtures`` - ``fleet_manifest`` returns a machine-readable
  description of the preflight surface (codes, capabilities, fixture
  expectations) so the parent ``bohrium_skills`` probe/report workflow can
  consume regression evidence without re-deriving it.

The diagnostics emitted here are plain dictionaries (not the legacy
``Diagnostic`` dataclass) so they can carry the richer ``DiagnosticEnvelope/v1``
fields (``source_provenance``, ``domain_tags``, ``facts``, ``artifact_roles``,
``version_assumption``, ``actions``) directly.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .parser import ParsedInput, parse_qe_input

# --- Artifact-role model ---------------------------------------------------

# Generic roles. These are intentionally software-agnostic: every fleet backend
# can map its native files/sections onto this same small role set, which is
# what lets the parent router consume cross-file checks without learning
# MatMaster specifics. For QE the primary ``pw.x`` input file holds the in-file
# structure/kpoints/lattice cards; only pseudopotentials are real external
# artifacts (the third column of ``ATOMIC_SPECIES``). The graph records both
# kinds uniformly.
ROLE_PRIMARY_INPUT = "primary-input"
ROLE_STRUCTURE = "structure"
ROLE_KPOINTS = "kpoints"
ROLE_PSEUDOPOTENTIAL = "pseudopotential"
ROLE_ORBITAL = "orbital"
ROLE_LATTICE = "lattice"

ALL_ROLES = (
    ROLE_PRIMARY_INPUT,
    ROLE_STRUCTURE,
    ROLE_KPOINTS,
    ROLE_PSEUDOPOTENTIAL,
    ROLE_ORBITAL,
    ROLE_LATTICE,
)

# Conservative workflow threshold used by the warning-level ecutwfc check. QE
# documents ecutwfc in Rydberg. The actual cutoff is overridable via the
# preflight intent contract; this is only the default fleet baseline, not a
# MatMaster policy.
DEFAULT_ECUTWFC_WARNING_RY = 50.0

# Codes reserved for the universal preflight surface. They use the ``QE6xx``
# band so they sort after existing rule codes (QE0xx/1xx) and stay identifiable
# as cross-fleet preflight findings.
CODE_MISSING_INPUT = "QE601"
CODE_MISSING_STRUCTURE = "QE602"
CODE_MISSING_LATTICE = "QE603"
CODE_NTYP_SPECIES_MISMATCH = "QE604"
CODE_UNRESOLVED_PSEUDO = "QE605"
CODE_MISSING_PSEUDOS = "QE606"
CODE_LOW_ECUTWFC = "QE607"
CODE_SUSPICIOUS_KPOINTS = "QE608"
CODE_VERSION_ASSUMPTION = "QE609"
CODE_UNKNOWN_KEYWORD_VERSION = "QE610"


@dataclass(frozen=True)
class ArtifactNode:
    """A node in the cross-artifact graph.

    ``role`` is one of the fleet-generic roles above; ``path`` is the resolved
    filesystem path (may be a non-existent reference, which is itself a
    finding) or, for in-file QE cards, the primary input path; ``exists``
    records whether the artifact is present; ``source`` records where the
    reference originated so consumers can trace provenance.
    """

    role: str
    path: Path
    exists: bool
    source: str
    referenced_from: tuple[str, int] | None = None
    detail: dict[str, Any] | None = None


@dataclass
class ArtifactGraph:
    """Generic cross-artifact graph built from a parsed case directory."""

    case_dir: Path
    nodes: list[ArtifactNode] = field(default_factory=list)

    def by_role(self, role: str) -> list[ArtifactNode]:
        return [node for node in self.nodes if node.role == role]

    def to_json(self) -> list[dict[str, Any]]:
        """Serialize the graph for the parent probe/report workflow."""

        def _node_json(node: ArtifactNode) -> dict[str, Any]:
            payload: dict[str, Any] = {
                "role": node.role,
                "path": str(node.path),
                "exists": node.exists,
                "source": node.source,
            }
            if node.referenced_from is not None:
                payload["referenced_from"] = {
                    "path": node.referenced_from[0],
                    "line": node.referenced_from[1],
                }
            if node.detail:
                payload["detail"] = node.detail
            return payload

        return sorted(
            (_node_json(node) for node in self.nodes),
            key=lambda item: (item["role"], item["path"]),
        )


def _find_primary_input(case_dir: Path) -> Path | None:
    """Locate the primary Quantum ESPRESSO input file in a case directory.

    QE pw.x conventionally reads its input from ``.pwi``/``.in`` files (or a
    file named ``pw.in``/``qe.in``). We pick the first match so the graph has a
    stable primary node; if none of those exist we fall back to the most
    generic ``*.in`` so ad-hoc naming still works.
    """
    for pattern in ("*.pwi", "*.pw", "pw.in", "qe.in", "pw.x.in", "*.in"):
        for candidate in sorted(case_dir.glob(pattern)):
            if candidate.is_file():
                return candidate
    return None


def _system_param(parsed: ParsedInput, name: str) -> tuple[str, int] | None:
    """Return (value, line) for a ``&SYSTEM`` keyword, or None when absent."""
    system = parsed.namelists.get("&SYSTEM", {})
    entry = system.get(name)
    if entry is None:
        return None
    return entry.value, entry.line + 1


def _control_param(parsed: ParsedInput, name: str) -> tuple[str, int] | None:
    control = parsed.namelists.get("&CONTROL", {})
    entry = control.get(name)
    if entry is None:
        return None
    return entry.value, entry.line + 1


def _has_system_param(parsed: ParsedInput, name: str) -> bool:
    return name in parsed.namelists.get("&SYSTEM", {})


def _card_line(parsed: ParsedInput, card: str) -> int:
    rows = parsed.cards.get(card, [])
    return (rows[0].line + 1) if rows else 1


def _atomic_species_files(parsed: ParsedInput) -> list[tuple[str, str, int]]:
    """Return ``[(symbol, pseudo_filename, line), ...]`` from ATOMIC_SPECIES.

    Each ATOMIC_SPECIES row is ``<symbol> <mass> <pseudo_file>``; the third
    column is the cross-file pseudopotential reference.
    """
    out: list[tuple[str, str, int]] = []
    for row in parsed.cards.get("ATOMIC_SPECIES", []):
        values = row.values
        if not values:
            continue
        symbol = row.symbol
        # Mass may be omitted in some malformed inputs; the pseudo filename is
        # conventionally the last column.
        if len(values) >= 2:
            pseudo = values[-1]
            out.append((symbol, pseudo, row.line + 1))
        elif len(values) == 1:
            # Only mass, no pseudo file declared.
            out.append((symbol, "", row.line + 1))
    return out


def _resolve_dir(case_dir: Path, declared: str | None) -> Path:
    if not declared:
        return case_dir
    candidate = Path(declared)
    if candidate.is_absolute():
        return candidate
    return case_dir / candidate


def build_artifact_graph(
    case_dir: Path,
    parsed: ParsedInput,
    input_path: Path,
) -> ArtifactGraph:
    """Build the cross-artifact graph from a parsed QE pw.x input.

    The model is generic: it records roles + resolved paths + provenance. The
    same shape generalizes to other fleet backends because it never bakes in
    MatMaster/Bohrium runtime concepts (no input_dir, no image, no session).
    """
    case_dir = case_dir.resolve()
    graph = ArtifactGraph(case_dir=case_dir)

    graph.nodes.append(
        ArtifactNode(
            role=ROLE_PRIMARY_INPUT,
            path=input_path,
            exists=input_path.exists(),
            source="case-root",
        )
    )

    # In-file structure card (ATOMIC_POSITIONS) + the &SYSTEM structural keys.
    has_positions = bool(parsed.cards.get("ATOMIC_POSITIONS"))
    has_system_struct = any(_has_system_param(parsed, key) for key in ("nat", "ntyp"))
    structure_exists = has_positions or has_system_struct
    structure_line = _card_line(parsed, "ATOMIC_POSITIONS") if has_positions else 1
    graph.nodes.append(
        ArtifactNode(
            role=ROLE_STRUCTURE,
            path=input_path,
            exists=structure_exists,
            source="pwi:ATOMIC_POSITIONS/&SYSTEM",
            referenced_from=(str(input_path), structure_line),
            detail={
                "has_atomic_positions": has_positions,
                "has_system_struct": has_system_struct,
            },
        )
    )

    # In-file kpoints card.
    has_kpoints = bool(parsed.cards.get("K_POINTS"))
    kpt_line = _card_line(parsed, "K_POINTS")
    graph.nodes.append(
        ArtifactNode(
            role=ROLE_KPOINTS,
            path=input_path,
            exists=has_kpoints,
            source="pwi:K_POINTS",
            referenced_from=(str(input_path), kpt_line),
            detail={"has_k_points": has_kpoints},
        )
    )

    # In-file lattice: CELL_PARAMETERS when ibrav=0, or ibrav>0 + celldm/a.
    ibrav_entry = _system_param(parsed, "ibrav")
    ibrav_value: int | None = None
    if ibrav_entry is not None:
        try:
            ibrav_value = int(float(re.split(r"[\s,]", ibrav_entry[0])[0]))
        except (ValueError, IndexError):
            ibrav_value = None
    has_cell_parameters = bool(parsed.cards.get("CELL_PARAMETERS"))
    has_bravais_lattice = ibrav_value is not None and ibrav_value > 0
    lattice_exists = has_cell_parameters or has_bravais_lattice
    lattice_line = _card_line(parsed, "CELL_PARAMETERS") if has_cell_parameters else 1
    graph.nodes.append(
        ArtifactNode(
            role=ROLE_LATTICE,
            path=input_path,
            exists=lattice_exists,
            source="pwi:CELL_PARAMETERS/ibrav",
            referenced_from=(str(input_path), lattice_line),
            detail={
                "ibrav": ibrav_value,
                "has_cell_parameters": has_cell_parameters,
            },
        )
    )

    # Pseudopotential references (the only true cross-file artifact for QE).
    pseudo_dir_value = _control_param(parsed, "pseudo_dir")
    pseudo_dir_str = pseudo_dir_value[0].strip("'\"") if pseudo_dir_value else None
    for symbol, filename, line in _atomic_species_files(parsed):
        if not filename:
            continue
        resolved = _resolve_dir(case_dir, pseudo_dir_str) / filename
        graph.nodes.append(
            ArtifactNode(
                role=ROLE_PSEUDOPOTENTIAL,
                path=resolved,
                exists=resolved.exists(),
                source=f"pwi:ATOMIC_SPECIES:{symbol}",
                referenced_from=(str(input_path), line),
                detail=(
                    {"declared_dir": pseudo_dir_str, "symbol": symbol}
                    if pseudo_dir_str
                    else {"symbol": symbol}
                ),
            )
        )

    return graph


# --- Preflight diagnostics -------------------------------------------------


def preflight_diagnostics(
    case_dir: Path,
    *,
    intent: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], ArtifactGraph]:
    """Run universal generated-input preflight checks.

    Returns a tuple of (diagnostics, artifact_graph). Diagnostics are envelope
    dicts carrying the full ``DiagnosticEnvelope/v1`` field set so the agent
    CLI can emit them directly without re-shaping.
    """
    case_dir = case_dir.resolve()
    input_path = _find_primary_input(case_dir)
    if input_path is None:
        # No primary input at all: emit a single blocking finding and return
        # an empty graph. The legacy single-file lint path still flags
        # unsupported files; this finding is the preflight-specific view.
        empty_graph = ArtifactGraph(case_dir=case_dir)
        finding = _diag(
            code=CODE_MISSING_INPUT,
            severity="error",
            message=(
                "primary-input artifact not found: expected a .pwi/.in pw.x "
                "input file in the case directory"
            ),
            path=case_dir / "<missing-input>",
            line=1,
            category="cross-file reference",
            confidence=0.97,
            blocking=True,
            source_provenance={
                "role": ROLE_PRIMARY_INPUT,
                "reason": "no .pwi/.in file in case directory",
            },
            fix_hints=[
                "Add a pw.x input file (.pwi/.in) to the case directory",
            ],
            actions=[
                {
                    "kind": "create_artifact",
                    "role": ROLE_PRIMARY_INPUT,
                    "target": str(case_dir / "pw.in"),
                    "safe_to_auto_apply": False,
                }
            ],
            facts={"case_dir": str(case_dir)},
            artifact_roles=[ROLE_PRIMARY_INPUT],
            domain_tags=["cross-file", "blocking"],
        )
        return [finding], empty_graph

    text = input_path.read_text(encoding="utf-8", errors="ignore")
    parsed = parse_qe_input(text)
    graph = build_artifact_graph(case_dir, parsed, input_path)

    version_assumption = resolve_version_assumption(intent)
    diagnostics: list[dict[str, Any]] = []
    diagnostics.extend(_structure_diagnostics(graph, parsed, input_path))
    diagnostics.extend(_lattice_diagnostics(graph, parsed, input_path))
    diagnostics.extend(_kpoints_presence_diagnostics(graph, parsed, input_path))
    diagnostics.extend(_ntyp_species_diagnostics(parsed, input_path))
    diagnostics.extend(_pseudos_diagnostics(graph, parsed, input_path))
    diagnostics.extend(_unresolved_pseudo_diagnostics(graph))
    diagnostics.extend(_low_ecutwfc_diagnostics(parsed, input_path, intent))
    diagnostics.extend(_suspicious_kpoints_diagnostics(parsed, input_path))
    diagnostics.extend(_version_keyword_diagnostics(parsed, input_path, version_assumption))
    diagnostics.extend(_version_assumption_diagnostic(version_assumption, intent, input_path))

    return (
        sorted(
            diagnostics,
            key=lambda item: (
                item.get("range", {}).get("start", {}).get("line", 0),
                item.get("range", {}).get("start", {}).get("character", 0),
                item["code"],
            ),
        ),
        graph,
    )


def _diag(
    *,
    code: str,
    severity: str,
    message: str,
    path: Path,
    line: int = 1,
    column: int = 1,
    category: str,
    confidence: float,
    blocking: bool,
    source_provenance: dict[str, Any],
    fix_hints: list[str],
    actions: list[dict[str, Any]] | None = None,
    facts: dict[str, Any] | None = None,
    artifact_roles: list[str] | None = None,
    domain_tags: list[str] | None = None,
    version_assumption: dict[str, Any] | None = None,
    manual_ref: str | None = None,
    intent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a single normalized preflight diagnostic.

    Carries every field the issue acceptance criteria require (``code``,
    ``severity``, ``path``/``range``, ``blocking``, ``category``,
    ``source_provenance``, ``fix_hints``/``actions``) plus the richer envelope
    fields (``facts``, ``artifact_roles``, ``domain_tags``,
    ``version_assumption``) used by the parent fleet probe.
    """
    line0 = max(line - 1, 0)
    col0 = max(column - 1, 0)
    payload: dict[str, Any] = {
        "code": code,
        "severity": severity,
        "message": message,
        "file": str(path),
        "line": line,
        "column": column,
        "category": category,
        "confidence": confidence,
        "source": "qe-preflight",
        "range": {
            "start": {"line": line0, "character": col0},
            "end": {"line": line0, "character": col0 + 1},
        },
        "blocking": blocking,
        "fix_hints": fix_hints,
        "source_provenance": source_provenance,
    }
    if actions:
        payload["actions"] = actions
    if facts:
        payload["facts"] = facts
    if artifact_roles:
        payload["artifact_roles"] = artifact_roles
    if domain_tags:
        payload["domain_tags"] = domain_tags
    if version_assumption:
        payload["version_assumption"] = version_assumption
    if manual_ref:
        payload["manual_ref"] = manual_ref
    if intent:
        payload["intent"] = intent
    return payload


def _structure_diagnostics(
    graph: ArtifactGraph, parsed: ParsedInput, input_path: Path
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for node in graph.by_role(ROLE_STRUCTURE):
        if node.exists:
            continue
        ref = node.referenced_from or (str(input_path), 1)
        out.append(
            _diag(
                code=CODE_MISSING_STRUCTURE,
                severity="error",
                message=(
                    "structure section missing: pw.x input declares no "
                    "ATOMIC_POSITIONS card (and no nat/ntyp in &SYSTEM)"
                ),
                path=node.path,
                line=ref[1],
                category="cross-file reference",
                confidence=0.95,
                blocking=True,
                source_provenance={
                    "role": ROLE_STRUCTURE,
                    "referenced_from": {"path": ref[0], "line": ref[1]},
                    "declared_in": node.source,
                },
                fix_hints=[
                    "Add an ATOMIC_POSITIONS card listing the atom coordinates",
                    "And set nat/ntyp in &SYSTEM to match the structure",
                ],
                actions=[
                    {
                        "kind": "insert_card",
                        "card": "ATOMIC_POSITIONS",
                        "target": str(node.path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={
                    "has_atomic_positions": (node.detail or {}).get("has_atomic_positions", False),
                    "has_system_struct": (node.detail or {}).get("has_system_struct", False),
                },
                artifact_roles=[ROLE_STRUCTURE, ROLE_PRIMARY_INPUT],
                domain_tags=["cross-file", "blocking"],
            )
        )
    return out


def _lattice_diagnostics(
    graph: ArtifactGraph, parsed: ParsedInput, input_path: Path
) -> list[dict[str, Any]]:
    """Flag a missing lattice when ibrav=0 has no CELL_PARAMETERS card.

    QE requires explicit cell vectors when ``ibrav=0``; without them pw.x fails
    at startup. We surface this as a blocking cross-artifact finding.
    """
    out: list[dict[str, Any]] = []
    ibrav_entry = _system_param(parsed, "ibrav")
    ibrav_value: int | None = None
    if ibrav_entry is not None:
        try:
            ibrav_value = int(float(re.split(r"[\s,]", ibrav_entry[0])[0]))
        except (ValueError, IndexError):
            ibrav_value = None
    has_cell_parameters = bool(parsed.cards.get("CELL_PARAMETERS"))
    # Only block when ibrav is explicitly 0 (free cell) and no vectors given.
    # When ibrav is unset QE defaults to 0, so we still flag a missing lattice
    # unless a CELL_PARAMETERS card is present.
    free_cell = ibrav_value == 0 or (ibrav_value is None and not has_cell_parameters)
    if free_cell and not has_cell_parameters:
        line = ibrav_entry[1] if ibrav_entry is not None else 1
        out.append(
            _diag(
                code=CODE_MISSING_LATTICE,
                severity="error",
                message=(
                    "lattice section missing: ibrav=0 (or unset) requires a "
                    "CELL_PARAMETERS card with explicit cell vectors"
                ),
                path=input_path,
                line=line,
                category="cross-file reference",
                confidence=0.95,
                blocking=True,
                source_provenance={
                    "role": ROLE_LATTICE,
                    "referenced_from": {"path": str(input_path), "line": line},
                    "ibrav": ibrav_value,
                },
                fix_hints=[
                    "Add a CELL_PARAMETERS card with three cell vectors",
                    "Or set ibrav>0 in &SYSTEM and the matching celldm/a",
                ],
                actions=[
                    {
                        "kind": "insert_card",
                        "card": "CELL_PARAMETERS",
                        "target": str(input_path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={"ibrav": ibrav_value, "has_cell_parameters": has_cell_parameters},
                artifact_roles=[ROLE_LATTICE, ROLE_PRIMARY_INPUT],
                domain_tags=["cross-file", "blocking"],
            )
        )
    return out


def _kpoints_presence_diagnostics(
    graph: ArtifactGraph, parsed: ParsedInput, input_path: Path
) -> list[dict[str, Any]]:
    """Flag a missing K_POINTS card as a non-blocking warning.

    pw.x requires a K_POINTS card for scf/nscf/bands/relax; its absence is a
    startup error in practice, but some inputs are intentionally built up
    incrementally, so we surface this as a non-blocking warning rather than a
    hard block.
    """
    out: list[dict[str, Any]] = []
    for node in graph.by_role(ROLE_KPOINTS):
        if node.exists:
            continue
        ref = node.referenced_from or (str(input_path), 1)
        out.append(
            _diag(
                code=CODE_SUSPICIOUS_KPOINTS,
                severity="warning",
                message=(
                    "K_POINTS card missing: pw.x requires a K_POINTS card; "
                    "its absence is a startup error for scf/nscf/bands/relax"
                ),
                path=node.path,
                line=ref[1],
                category="preflight/runtime-risk",
                confidence=0.8,
                blocking=False,
                source_provenance={
                    "role": ROLE_KPOINTS,
                    "referenced_from": {"path": ref[0], "line": ref[1]},
                    "declared_in": node.source,
                },
                fix_hints=[
                    "Add a K_POINTS card (e.g. automatic with a grid)",
                    "Or confirm the input is intentionally incomplete",
                ],
                actions=[
                    {
                        "kind": "insert_card",
                        "card": "K_POINTS",
                        "target": str(node.path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={"has_k_points": False},
                artifact_roles=[ROLE_KPOINTS, ROLE_PRIMARY_INPUT],
                domain_tags=["preflight", "runtime-risk"],
            )
        )
    return out


def _ntyp_species_diagnostics(parsed: ParsedInput, input_path: Path) -> list[dict[str, Any]]:
    """Cross-check &SYSTEM ntyp against the ATOMIC_SPECIES row count.

    This is the generic "declared count vs evidence count" cross-artifact
    check; for QE the species list is the ATOMIC_SPECIES card.
    """
    out: list[dict[str, Any]] = []
    ntyp_entry = _system_param(parsed, "ntyp")
    species_rows = _atomic_species_files(parsed)
    species_count = len(species_rows)
    if ntyp_entry is None:
        # ntyp unset: QE can sometimes infer it, but we surface the assumption
        # so the parent probe knows it was made.
        if species_count:
            out.append(
                _diag(
                    code=CODE_NTYP_SPECIES_MISMATCH,
                    severity="information",
                    message=("ntyp is unset; pw.x will infer it from the " "ATOMIC_SPECIES card"),
                    path=input_path,
                    line=1,
                    category="semantic consistency",
                    confidence=0.8,
                    blocking=False,
                    source_provenance={
                        "role": ROLE_PRIMARY_INPUT,
                        "reason": "ntyp keyword absent from &SYSTEM",
                    },
                    fix_hints=[f"Set ntyp={species_count} to make the assumption explicit"],
                    actions=[
                        {
                            "kind": "set_keyword",
                            "namelist": "&SYSTEM",
                            "keyword": "ntyp",
                            "value": str(species_count),
                            "target": str(input_path),
                            "safe_to_auto_apply": False,
                        }
                    ],
                    facts={"inferred_ntyp": species_count},
                    artifact_roles=[ROLE_PRIMARY_INPUT, ROLE_STRUCTURE],
                    domain_tags=["cross-file", "assumption"],
                )
            )
        return out
    try:
        declared = int(float(re.split(r"[\s,]", ntyp_entry[0])[0]))
    except (ValueError, IndexError):
        return []
    if declared != species_count:
        line = ntyp_entry[1]
        species_symbols = [row[0] for row in species_rows]
        out.append(
            _diag(
                code=CODE_NTYP_SPECIES_MISMATCH,
                severity="error",
                message=(
                    f"ntyp={declared} does not match the {species_count} "
                    "species declared in the ATOMIC_SPECIES card"
                ),
                path=input_path,
                line=line,
                category="semantic consistency",
                confidence=0.96,
                blocking=True,
                source_provenance={
                    "role": ROLE_PRIMARY_INPUT,
                    "cross_referenced_role": ROLE_STRUCTURE,
                    "parsed_ntyp": declared,
                    "parsed_species": species_symbols,
                },
                fix_hints=[
                    f"Set ntyp={species_count} to match ATOMIC_SPECIES",
                    "Or correct the ATOMIC_SPECIES card to match ntyp",
                ],
                actions=[
                    {
                        "kind": "set_keyword",
                        "namelist": "&SYSTEM",
                        "keyword": "ntyp",
                        "value": str(species_count),
                        "target": str(input_path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={
                    "declared_ntyp": declared,
                    "species_count": species_count,
                    "species": species_symbols,
                },
                artifact_roles=[ROLE_PRIMARY_INPUT, ROLE_STRUCTURE],
                domain_tags=["cross-file", "blocking"],
            )
        )
    return out


def _pseudos_diagnostics(
    graph: ArtifactGraph, parsed: ParsedInput, input_path: Path
) -> list[dict[str, Any]]:
    """Flag inputs that declare a structure but no pseudopotential references.

    QE reads pseudopotential filenames from the third column of the
    ``ATOMIC_SPECIES`` card (and optionally their directory from the
    ``pseudo_dir`` control keyword). A structure-declaring input without any
    pseudopotential reference will fail at runtime, so we surface it as a
    blocking cross-artifact finding.
    """
    out: list[dict[str, Any]] = []
    has_positions = bool(parsed.cards.get("ATOMIC_POSITIONS"))
    species_rows = _atomic_species_files(parsed)
    has_pseudo_refs = any(filename for _, filename, _ in species_rows)
    if (has_positions or species_rows) and not has_pseudo_refs:
        line = species_rows[0][2] if species_rows else 1
        out.append(
            _diag(
                code=CODE_MISSING_PSEUDOS,
                severity="error",
                message=(
                    "pseudopotential artifact missing: structure is declared "
                    "but the ATOMIC_SPECIES card lists no pseudopotential files"
                ),
                path=input_path,
                line=line,
                category="cross-file reference",
                confidence=0.9,
                blocking=True,
                source_provenance={
                    "role": ROLE_PSEUDOPOTENTIAL,
                    "reason": "no pseudopotential filename in any ATOMIC_SPECIES row",
                },
                fix_hints=[
                    "Add the pseudopotential filename as the third column of "
                    "each ATOMIC_SPECIES row",
                ],
                actions=[
                    {
                        "kind": "set_keyword",
                        "card": "ATOMIC_SPECIES",
                        "target": str(input_path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={"has_atomic_positions": has_positions, "species_rows": len(species_rows)},
                artifact_roles=[ROLE_PSEUDOPOTENTIAL, ROLE_PRIMARY_INPUT],
                domain_tags=["cross-file", "blocking"],
            )
        )
    return out


def _unresolved_pseudo_diagnostics(graph: ArtifactGraph) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for node in graph.by_role(ROLE_PSEUDOPOTENTIAL):
        if node.exists:
            continue
        ref = node.referenced_from or (str(node.path), 1)
        out.append(
            _diag(
                code=CODE_UNRESOLVED_PSEUDO,
                severity="warning",
                message=(
                    f"pseudopotential artifact referenced from ATOMIC_SPECIES "
                    f"cannot be resolved: {node.path.name}"
                ),
                path=node.path,
                line=ref[1],
                category="cross-file reference",
                confidence=0.85,
                blocking=False,
                source_provenance={
                    "role": ROLE_PSEUDOPOTENTIAL,
                    "declared_in": node.source,
                    "declared_dir": (node.detail or {}).get("declared_dir"),
                    "referenced_from": {"path": ref[0], "line": ref[1]},
                },
                fix_hints=[
                    f"Place {node.path.name} in the declared directory",
                    "Or correct pseudo_dir in &CONTROL",
                ],
                actions=[
                    {
                        "kind": "resolve_artifact",
                        "role": ROLE_PSEUDOPOTENTIAL,
                        "target": str(node.path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={"unresolved_path": str(node.path)},
                artifact_roles=[ROLE_PSEUDOPOTENTIAL],
                domain_tags=["cross-file", "workspace-resolve"],
            )
        )
    return out


def _low_ecutwfc_diagnostics(
    parsed: ParsedInput, input_path: Path, intent: dict[str, Any] | None
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    ecut_entry = _system_param(parsed, "ecutwfc")
    if ecut_entry is None:
        return out
    try:
        ecut = float(re.split(r"[\s,]", ecut_entry[0])[0])
    except (ValueError, IndexError):
        return out
    threshold = float((intent or {}).get("ecutwfc_warning_ry", DEFAULT_ECUTWFC_WARNING_RY))
    high_accuracy = bool((intent or {}).get("high_accuracy_production", False))
    if ecut < threshold:
        message = (
            f"ecutwfc={ecut} Ry is below the conservative workflow threshold " f"({threshold} Ry)"
        )
        if high_accuracy:
            message += "; intent marks this as high-accuracy production input"
        line = ecut_entry[1]
        out.append(
            _diag(
                code=CODE_LOW_ECUTWFC,
                severity="warning",
                message=message,
                path=input_path,
                line=line,
                category="preflight/runtime-risk",
                confidence=0.8,
                blocking=False,
                source_provenance={
                    "role": ROLE_PRIMARY_INPUT,
                    "keyword": "ecutwfc",
                    "threshold_source": (
                        "intent" if "ecutwfc_warning_ry" in (intent or {}) else "default"
                    ),
                },
                fix_hints=[
                    f"Raise ecutwfc to at least {threshold} Ry",
                    "Or document the lower cutoff in the intent contract",
                ],
                actions=[
                    {
                        "kind": "set_keyword",
                        "namelist": "&SYSTEM",
                        "keyword": "ecutwfc",
                        "value": str(threshold),
                        "target": str(input_path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={
                    "ecutwfc": ecut,
                    "threshold": threshold,
                    "high_accuracy_production": high_accuracy,
                },
                artifact_roles=[ROLE_PRIMARY_INPUT],
                domain_tags=["preflight", "runtime-risk"],
            )
        )
    return out


def _suspicious_kpoints_diagnostics(parsed: ParsedInput, input_path: Path) -> list[dict[str, Any]]:
    """Flag a 1-point axis in an automatic K_POINTS grid.

    The automatic form is ``K_POINTS automatic\nnk1 nk2 nk3 k1 k2 k3``. A grid
    with a 1-point axis risks silently inaccurate results for low-dimensional
    systems, so we surface it as a non-blocking warning.
    """
    out: list[dict[str, Any]] = []
    header = (parsed.card_headers.get("K_POINTS") or "").upper()
    rows = parsed.cards.get("K_POINTS", [])
    if not rows or not header:
        return out
    # Only the automatic form declares an explicit nk1/nk2/nk3 grid.
    is_automatic = "AUTOMATIC" in header
    if not is_automatic:
        return out
    first = rows[0]
    # The parser stores the first token of each card row as ``symbol`` and the
    # remainder as ``values``. For the K_POINTS automatic card the whole line
    # is the grid + shift (nk1 nk2 nk3 k1 k2 k3), so we recombine them.
    grid_tokens = [first.symbol, *first.values][:3]
    if len(grid_tokens) < 3:
        return out
    try:
        grid = [int(float(tok)) for tok in grid_tokens]
    except ValueError:
        return out
    if any(component <= 1 for component in grid):
        line = first.line + 1
        out.append(
            _diag(
                code=CODE_SUSPICIOUS_KPOINTS,
                severity="warning",
                message=(
                    f"k-point grid {grid} contains a 1-point axis; "
                    "under-sampling risks silently inaccurate results for "
                    "low-dimensional systems"
                ),
                path=input_path,
                line=line,
                category="preflight/runtime-risk",
                confidence=0.7,
                blocking=False,
                source_provenance={
                    "role": ROLE_KPOINTS,
                    "grid": grid,
                    "card": "K_POINTS",
                },
                fix_hints=[
                    "Increase the sparse k-point axis",
                    "Or confirm the system is genuinely low-dimensional",
                ],
                actions=[
                    {
                        "kind": "set_keyword",
                        "card": "K_POINTS",
                        "value": " ".join(str(max(c, 2)) for c in grid),
                        "target": str(input_path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={"grid": grid, "card": "K_POINTS"},
                artifact_roles=[ROLE_KPOINTS],
                domain_tags=["preflight", "runtime-risk"],
            )
        )
    return out


# --- version-aware-keywords ------------------------------------------------


def resolve_version_assumption(intent: dict[str, Any] | None) -> dict[str, Any]:
    """Resolve the explicit runtime/version assumption for this preflight run.

    When the exact runtime/image version is unknown we record that fact
    explicitly rather than guessing, per the issue's version-assumptions
    acceptance criterion. The intent contract can override
    ``software_version`` (e.g. ``qe >=7.2``); otherwise we fall back to the
    schema version the builtin keyword set was authored against.
    """
    intent = intent or {}
    software_version = intent.get("software_version")
    runtime_image = intent.get("runtime_image")
    assumption: dict[str, Any] = {
        "software": "qe",
        "software_version": software_version or "unknown",
        "runtime_image": runtime_image or "unknown",
        "schema_source": intent.get("schema_source", "qe-lsp builtin"),
        # The fallback is intentional and explicit so consumers never have to
        # guess whether ``unknown`` means "not checked" or "could not determine".
        "exact_runtime_known": bool(software_version or runtime_image),
    }
    if software_version or runtime_image:
        assumption["declared_by"] = "intent"
    else:
        assumption["declared_by"] = "fallback"
    return assumption


# Keywords introduced or only valid for recent QE versions, with the minimal
# version each one requires. This is the version-aware schema that drives
# CODE_UNKNOWN_KEYWORD_VERSION: when a keyword is used below its introduction
# version, the parent probe can act on the mismatch. The versions below are
# conservative public-reference milestones from the QE pw.x manual.
_VERSIONED_KEYWORDS: dict[str, str] = {
    # Each value documents the minimal QE version that introduced / stabilized
    # the keyword, so preflight can flag inputs that rely on it without
    # declaring a compatible runtime version.
    "vdw_kernel_table": "qe >=5.0",
    "london": "qe >=5.0",
    "ts_vdw": "qe >=5.0",
    "xdm": "qe >=5.4",
    "q2_sigma": "qe >=6.0",
    "space_group": "qe >=6.0",
    "gate": "qe >=6.4",
    "tot_charge": "qe >=6.4",
    "assume_isolated": "qe >=5.1",
}


def _version_keyword_diagnostics(
    parsed: ParsedInput,
    input_path: Path,
    version_assumption: dict[str, Any],
) -> list[dict[str, Any]]:
    """Flag keywords whose declared availability is newer than the runtime assumption.

    This is the version-aware-keywords capability: when an input uses a keyword
    that requires a newer QE version than the intent/runtime declares, we
    surface an explicit version mismatch so the parent probe can fail early
    rather than discovering the incompatibility at runtime.
    """
    out: list[dict[str, Any]] = []
    declared_version = version_assumption.get("software_version", "unknown")
    exact_known = version_assumption.get("exact_runtime_known", False)
    # Aggregate keyword presence across all namelists so we catch a versioned
    # keyword no matter which namelist it appears in.
    present: dict[str, tuple[str, int]] = {}
    for namelist, params in parsed.namelists.items():
        for name, param in params.items():
            if name in _VERSIONED_KEYWORDS and name not in present:
                present[name] = (namelist, param.line + 1)
    for keyword, required in _VERSIONED_KEYWORDS.items():
        if keyword not in present:
            continue
        # Only emit when the runtime version is declared AND older than the
        # keyword requirement. When the version is unknown we leave the generic
        # CODE_VERSION_ASSUMPTION information diagnostic to carry that fact, so
        # we never guess at an incompatibility we cannot evidence.
        if not exact_known:
            continue
        if not _version_lt(declared_version, required):
            continue
        namelist, line = present[keyword]
        out.append(
            _diag(
                code=CODE_UNKNOWN_KEYWORD_VERSION,
                severity="error",
                message=(
                    f"keyword {keyword} requires {required} but the declared "
                    f"runtime version is {declared_version}"
                ),
                path=input_path,
                line=line,
                category="schema",
                confidence=0.9,
                blocking=True,
                source_provenance={
                    "role": ROLE_PRIMARY_INPUT,
                    "keyword": keyword,
                    "namelist": namelist,
                    "schema_source": version_assumption.get("schema_source"),
                },
                fix_hints=[
                    f"Raise the declared runtime version to at least {required}",
                    f"Or remove {keyword} from {namelist}",
                ],
                actions=[
                    {
                        "kind": "remove_keyword",
                        "keyword": keyword,
                        "namelist": namelist,
                        "target": str(input_path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={
                    "keyword": keyword,
                    "required_version": required,
                    "declared_version": declared_version,
                    "namelist": namelist,
                },
                artifact_roles=[ROLE_PRIMARY_INPUT],
                domain_tags=["schema", "version-aware", "blocking"],
                version_assumption=version_assumption,
                manual_ref=version_assumption.get("schema_source"),
            )
        )
    return out


def _version_lt(declared: str, required: str) -> bool:
    """Best-effort ``declared < required`` comparison for version strings.

    Both inputs are of the form ``qe >=X.Y``. We extract the leading numeric
    tuple from each and compare element-wise. Returns False if either side
    cannot be parsed, so we never fabricate a version mismatch.
    """

    def _tuple(text: str) -> tuple[int, ...]:
        match = re.search(r"(\d+(?:\.\d+)*)", text)
        if not match:
            return ()
        return tuple(int(part) for part in match.group(1).split("."))

    d = _tuple(declared)
    r = _tuple(required)
    if not d or not r:
        return False
    length = max(len(d), len(r))
    d_padded = d + (0,) * (length - len(d))
    r_padded = r + (0,) * (length - len(r))
    return d_padded < r_padded


def _version_assumption_diagnostic(
    version_assumption: dict[str, Any],
    intent: dict[str, Any] | None,
    input_path: Path,
) -> list[dict[str, Any]]:
    """Emit an explicit information diagnostic when the runtime version is unknown.

    This makes the version assumption machine-readable in the diagnostic stream
    itself (not just metadata) so the parent probe can surface it without
    parsing the envelope top-level.
    """
    if version_assumption["exact_runtime_known"]:
        return []
    return [
        _diag(
            code=CODE_VERSION_ASSUMPTION,
            severity="information",
            message=(
                "Exact Quantum ESPRESSO runtime/image version is unknown; "
                "preflight validated against the builtin schema keyword set"
            ),
            path=input_path,
            line=1,
            category="preflight/runtime-risk",
            confidence=1.0,
            blocking=False,
            source_provenance={
                "role": ROLE_PRIMARY_INPUT,
                "reason": "software_version and runtime_image not declared in intent",
            },
            fix_hints=[
                "Declare software_version/runtime_image in the intent contract",
            ],
            actions=[],
            facts={
                "software_version": version_assumption["software_version"],
                "runtime_image": version_assumption["runtime_image"],
                "schema_source": version_assumption["schema_source"],
            },
            artifact_roles=[ROLE_PRIMARY_INPUT],
            domain_tags=["version-aware", "assumption"],
            version_assumption=version_assumption,
            intent=dict(intent) if intent else None,
        )
    ]


# --- fleet-regression-fixtures --------------------------------------------


def fleet_manifest(
    *,
    fixtures: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a machine-readable preflight manifest for the parent fleet.

    The parent ``bohrium_skills`` probe/report workflow consumes this to know
    which preflight codes exist, which capabilities are implemented, and which
    fixtures exercise them. Keeping it as data (not README prose) means the
    fleet regression evidence stays in sync with the implementation.
    """
    codes = {
        CODE_MISSING_INPUT: {
            "severity": "error",
            "category": "cross-file reference",
            "blocking": True,
            "capability": "cross-artifact-graph",
            "summary": "primary-input artifact missing from workspace",
        },
        CODE_MISSING_STRUCTURE: {
            "severity": "error",
            "category": "cross-file reference",
            "blocking": True,
            "capability": "cross-artifact-graph",
            "summary": "ATOMIC_POSITIONS card / &SYSTEM structure keys missing",
        },
        CODE_MISSING_LATTICE: {
            "severity": "error",
            "category": "cross-file reference",
            "blocking": True,
            "capability": "cross-artifact-graph",
            "summary": "ibrav=0 without a CELL_PARAMETERS card",
        },
        CODE_NTYP_SPECIES_MISMATCH: {
            "severity": "error",
            "category": "semantic consistency",
            "blocking": True,
            "capability": "cross-artifact-graph",
            "summary": "ntyp does not match the ATOMIC_SPECIES row count",
        },
        CODE_MISSING_PSEUDOS: {
            "severity": "error",
            "category": "cross-file reference",
            "blocking": True,
            "capability": "cross-artifact-graph",
            "summary": "structure declared but no pseudopotential filenames",
        },
        CODE_UNRESOLVED_PSEUDO: {
            "severity": "warning",
            "category": "cross-file reference",
            "blocking": False,
            "capability": "cross-artifact-graph",
            "summary": "pseudopotential file cannot be resolved",
        },
        CODE_LOW_ECUTWFC: {
            "severity": "warning",
            "category": "preflight/runtime-risk",
            "blocking": False,
            "capability": "version-aware-keywords",
            "summary": "ecutwfc below conservative workflow threshold",
        },
        CODE_SUSPICIOUS_KPOINTS: {
            "severity": "warning",
            "category": "preflight/runtime-risk",
            "blocking": False,
            "capability": "cross-artifact-graph",
            "summary": "k-point grid has a 1-point axis or is undeclared",
        },
        CODE_VERSION_ASSUMPTION: {
            "severity": "information",
            "category": "preflight/runtime-risk",
            "blocking": False,
            "capability": "version-aware-keywords",
            "summary": "exact runtime version unknown; fallback schema used",
        },
        CODE_UNKNOWN_KEYWORD_VERSION: {
            "severity": "error",
            "category": "schema",
            "blocking": True,
            "capability": "version-aware-keywords",
            "summary": "keyword requires a newer runtime than declared",
        },
    }
    capabilities = {
        "version-aware-keywords": {
            "status": "available",
            "evidence_codes": [
                CODE_UNKNOWN_KEYWORD_VERSION,
                CODE_VERSION_ASSUMPTION,
                CODE_LOW_ECUTWFC,
            ],
        },
        "cross-artifact-graph": {
            "status": "available",
            "roles": list(ALL_ROLES),
            "evidence_codes": [
                CODE_MISSING_INPUT,
                CODE_MISSING_STRUCTURE,
                CODE_MISSING_LATTICE,
                CODE_NTYP_SPECIES_MISMATCH,
                CODE_MISSING_PSEUDOS,
                CODE_UNRESOLVED_PSEUDO,
                CODE_SUSPICIOUS_KPOINTS,
            ],
        },
        "code-actions": {
            "status": "available",
            "blocking_gate": "qe-lsp-tool check --fail-on-blocking",
            "evidence_codes": list(codes.keys()),
        },
        "fleet-regression-fixtures": {
            "status": "available",
            "fixtures": list(fixtures) if fixtures else [],
        },
    }
    return {
        "software": "qe",
        "preflight_envelope": "DiagnosticEnvelope/v1",
        "artifact_roles": list(ALL_ROLES),
        "capabilities": capabilities,
        "codes": codes,
    }
