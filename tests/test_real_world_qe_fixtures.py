from pathlib import Path

import pytest

from qe_lsp.parser import parse_qe_input

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "qe_inputs"

FIXTURE_CASES = [
    pytest.param(
        "qe_test_suite_pw_scf_scf.in",
        {
            "namelists": {"&CONTROL", "&SYSTEM", "&ELECTRONS"},
            "cards": {"ATOMIC_SPECIES", "ATOMIC_POSITIONS", "K_POINTS"},
            "parameters": {
                "&CONTROL": {"calculation": "'scf'"},
                "&SYSTEM": {"ibrav": "2", "nat": "2", "ntyp": "1"},
            },
            "species": ["Si"],
            "card_lengths": {"ATOMIC_POSITIONS": 2, "K_POINTS": 3},
        },
        id="pw_scf_scf",
    ),
    pytest.param(
        "qe_test_suite_pw_metal_tetrahedra.in",
        {
            "namelists": {"&CONTROL", "&SYSTEM", "&ELECTRONS"},
            "cards": {"ATOMIC_SPECIES", "ATOMIC_POSITIONS", "K_POINTS"},
            "parameters": {
                "&CONTROL": {"calculation": "'scf'"},
                "&SYSTEM": {"occupations": "'tetrahedra-opt'", "nat": "1", "ntyp": "1"},
            },
            "species": ["Al"],
            "card_lengths": {"ATOMIC_POSITIONS": 1, "K_POINTS": 1},
        },
        id="pw_metal_tetrahedra",
    ),
    pytest.param(
        "qe_test_suite_pw_lattice_ibrav0_cell_parameters.in",
        {
            "namelists": {"&CONTROL", "&SYSTEM", "&ELECTRONS"},
            "cards": {
                "ATOMIC_SPECIES",
                "ATOMIC_POSITIONS",
                "CELL_PARAMETERS",
                "K_POINTS",
            },
            "parameters": {
                "&CONTROL": {"calculation": "'scf'"},
                "&SYSTEM": {"ibrav": "0", "nat": "2", "ntyp": "1"},
            },
            "species": ["H"],
            "card_lengths": {"ATOMIC_POSITIONS": 2, "CELL_PARAMETERS": 3, "K_POINTS": 0},
        },
        id="pw_lattice_ibrav0_cell_parameters",
    ),
    pytest.param(
        "qe_test_suite_pw_relax_relax.in",
        {
            "namelists": {"&CONTROL", "&SYSTEM", "&ELECTRONS", "&IONS"},
            "cards": {"ATOMIC_SPECIES", "ATOMIC_POSITIONS", "K_POINTS"},
            "parameters": {
                "&CONTROL": {"calculation": '"relax"'},
                "&SYSTEM": {"ibrav": "1", "nat": "2", "ntyp": "2"},
            },
            "species": ["O", "C"],
            "card_lengths": {"ATOMIC_POSITIONS": 2, "K_POINTS": 0},
        },
        id="pw_relax_relax",
    ),
]


@pytest.mark.parametrize("filename, expected", FIXTURE_CASES)
def test_public_qe_input_fixtures_parse_expected_namelists_and_cards(filename, expected):
    text = (FIXTURE_DIR / filename).read_text(encoding="utf-8")

    parsed = parse_qe_input(text)

    assert parsed.unclosed_namelist is None
    assert parsed.duplicate_parameters == []
    assert expected["namelists"].issubset(parsed.namelists)
    assert expected["cards"].issubset(parsed.cards)

    for namelist, parameters in expected["parameters"].items():
        for name, value in parameters.items():
            assert parsed.namelists[namelist][name].value == value

    assert [row.symbol for row in parsed.cards["ATOMIC_SPECIES"]] == expected["species"]
    for card, length in expected["card_lengths"].items():
        assert len(parsed.cards[card]) == length
