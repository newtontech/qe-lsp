"""Validation accuracy regression tests."""

from dataclasses import dataclass
from typing import List, Optional

from qe_lsp.handlers.diagnostic import diagnostic


@dataclass(frozen=True)
class ValidationCase:
    name: str
    text: str
    expected_fragments: List[str]
    unexpected_fragment: Optional[str] = None


VALIDATION_CASES = [
    ValidationCase("valid_control", "&CONTROL\ncalculation = 'scf'\n/\n", []),
    ValidationCase("unclosed_namelist", "&CONTROL\ncalculation = 'scf'\n", ["Unclosed"]),
    ValidationCase(
        "duplicate_parameter",
        "&CONTROL\ncalculation = 'scf'\ncalculation = 'nscf'\n/\n",
        ["Duplicate parameter calculation"],
    ),
    ValidationCase("ibrav_requires_cell", "&SYSTEM\nibrav = 0\n/\n", ["CELL_PARAMETERS"]),
    ValidationCase(
        "ibrav_ignores_a",
        "&SYSTEM\nibrav = 1\nA = 7.5\n/\n",
        ["ignored when ibrav is not 0"],
    ),
    ValidationCase(
        "norm_conserving_cutoff_ratio",
        "&SYSTEM\necutwfc = 60\necutrho = 120\n/\n",
        ["at least 4x ecutwfc"],
    ),
    ValidationCase(
        "paw_cutoff_ratio",
        "&SYSTEM\necutwfc = 60\necutrho = 300\n/\n" "ATOMIC_SPECIES\nO 15.999 O.paw.UPF\n",
        ["at least 8x ecutwfc"],
    ),
    ValidationCase(
        "high_mixing_beta",
        "&ELECTRONS\nmixing_beta = 0.9\n/\n",
        ["mixing_beta above 0.7"],
    ),
    ValidationCase(
        "pseudo_element_mismatch",
        "ATOMIC_SPECIES\nO 15.999 Si.pbe.UPF\n",
        ["does not appear to match element O"],
    ),
    ValidationCase(
        "mixed_functionals",
        "ATOMIC_SPECIES\nO 15.999 O.pbe.UPF\nSi 28.086 Si.lda.UPF\n",
        ["Mixed pseudopotential functional"],
    ),
    ValidationCase(
        "position_species_mismatch",
        "ATOMIC_SPECIES\nO 15.999 O.pbe.UPF\n" "ATOMIC_POSITIONS {crystal}\nSi 0.0 0.0 0.0\n",
        ["missing from ATOMIC_SPECIES"],
    ),
    ValidationCase(
        "crystal_position_bounds",
        "ATOMIC_SPECIES\nO 15.999 O.pbe.UPF\n" "ATOMIC_POSITIONS {crystal}\nO 1.2 0.0 0.0\n",
        ["between 0 and 1"],
    ),
    ValidationCase(
        "gamma_offset",
        "K_POINTS {gamma}\n1 1 1 0 0 1\n",
        ["non-zero offset"],
    ),
    ValidationCase(
        "coarse_automatic_grid",
        "K_POINTS {automatic}\n2 2 2 0 0 0\n",
        ["very coarse"],
    ),
    ValidationCase(
        "valid_species_and_positions",
        "ATOMIC_SPECIES\nO 15.999 O.pbe.UPF\n" "ATOMIC_POSITIONS {crystal}\nO 0.0 0.5 1.0\n",
        [],
        "missing from ATOMIC_SPECIES",
    ),
]


def test_validation_accuracy_cases():
    """Expected diagnostics should be present without known false positives."""
    true_positives = 0
    false_negatives = 0
    false_positives = 0

    for case in VALIDATION_CASES:
        messages = [item.message for item in diagnostic({"text": case.text})]
        for expected in case.expected_fragments:
            if any(expected in message for message in messages):
                true_positives += 1
            else:
                false_negatives += 1
        if case.unexpected_fragment and any(
            case.unexpected_fragment in message for message in messages
        ):
            false_positives += 1
        if not case.expected_fragments and messages:
            false_positives += 1

    precision = true_positives / max(true_positives + false_positives, 1)
    recall = true_positives / max(true_positives + false_negatives, 1)

    assert false_negatives == 0
    assert false_positives == 0
    assert precision >= 0.90
    assert recall >= 0.85
