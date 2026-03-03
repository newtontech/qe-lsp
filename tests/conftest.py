"""Pytest configuration and fixtures for qe-lsp tests."""

import pytest

SAMPLE_QE_INPUT = """
&control
    calculation = 'scf'
    prefix = 'silicon'
    pseudo_dir = './'
    outdir = './tmp/'
    tstress = .true.
    tprnfor = .true.
    verbosity = 'high'
/

&system
    ibrav = 2
    celldm(1) = 10.20
    nat = 2
    ntyp = 1
    ecutwfc = 30.0
    occupations = 'smearing'
    degauss = 0.01
    smearing = 'gaussian'
/

&electrons
    conv_thr = 1.0d-8
    mixing_beta = 0.7
    diagonalization = 'david'
/

ATOMIC_SPECIES
 Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS alat
 Si   0.000000000   0.000000000   0.000000000
 Si   0.250000000   0.250000000   0.250000000

K_POINTS automatic
 6 6 6 0 0 0

CELL_PARAMETERS alat
  0.0   0.5   0.5
  0.5   0.0   0.5
  0.5   0.5   0.0
"""


MINIMAL_QE_INPUT = """
&control
    calculation = 'scf'
    prefix = 'test'
    pseudo_dir = './'
    outdir = './'
/

&system
    ibrav = 1
    nat = 1
    ntyp = 1
    ecutwfc = 20.0
/

ATOMIC_SPECIES
 H  1.008  H.pbe-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS alat
 H   0.0   0.0   0.0

K_POINTS gamma
"""


INVALID_QE_INPUT = """
&control
    calculation = 'scf'
    prefix = 'test'
/

&unknown_namelist
    param = 1.0
/

UNKNOWN_CARD
 some data

&system
    ibrav = 1
    nat = 1
/
"""


EMPTY_QE_INPUT = ""


COMMENT_ONLY_INPUT = """
! This is a comment
# This is also a comment
! celldm(1) = 10.0
"""


@pytest.fixture
def sample_qe_input():
    """Return a sample QE input file."""
    return SAMPLE_QE_INPUT


@pytest.fixture
def minimal_qe_input():
    """Return a minimal QE input file."""
    return MINIMAL_QE_INPUT


@pytest.fixture
def invalid_qe_input():
    """Return an invalid QE input file."""
    return INVALID_QE_INPUT


@pytest.fixture
def empty_qe_input():
    """Return an empty QE input file."""
    return EMPTY_QE_INPUT


@pytest.fixture
def comment_only_input():
    """Return a comment-only QE input file."""
    return COMMENT_ONLY_INPUT
