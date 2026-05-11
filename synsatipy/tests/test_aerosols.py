import pytest
from synsat_test import SynSatTest


def test_modis_aerosol_init_defaults():
    """
    Test that MODIS initialises correctly with use_aerosols=True.

    Checks that:
    - the instrument loads without error
    - AddAerosl RTTOV option is set
    - use_aerosols flag is stored on synsat attributes
    """
    s = SynSatTest(
        synsat_instrument="modis",
        synsat_modis_satellite="terra",
        synsat_use_aerosols=True,
    )

    assert s.synsat.instrument.startswith("MODIS")
    assert s.Options.AddAerosl is True
    assert s.synsat.use_aerosols is True


def test_modis_no_aerosol_init_defaults():
    """
    Test that MODIS initialises correctly with use_aerosols=False (default).

    Checks that AddAerosl is off and use_aerosols is False.
    """
    s = SynSatTest(synsat_instrument="modis")

    assert s.synsat.use_aerosols is False
    assert s.Options.AddAerosl is False



