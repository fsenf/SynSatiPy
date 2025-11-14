import pytest
import numpy as np
from synsat_test import SynSatTest


@pytest.mark.parametrize("instrument_config", [
    # Test SEVIRI with default channels
    {"instrument": "seviri", "msg_number": 3, "channels": (5, 6, 7)},
    # Test ABI with default channels
    {"instrument": "abi", "goes_number": 16, "channels": (13, 14, 15)},
    # Test FCI with default channels
    {"instrument": "fci", "mtg_number": 1, "channels": (13, 14, 15)},
])
def test_instrument_workflow(instrument_config):
    """
    Test different instruments using SynSatTest's predefined profiles.
    
    Parameters
    ----------
    instrument_config : dict
        Configuration for the instrument to test
    """
    # Extract test parameters
    instrument = instrument_config["instrument"]
    channels = instrument_config["channels"]
    
    # Prepare kwargs
    kwargs = {"synsat_instrument": instrument, "synsat_channel_list": channels}
    
    # Add instrument-specific configuration
    if instrument == "seviri":
        kwargs["synsat_msg_number"] = instrument_config["msg_number"]
    elif instrument == "abi":
        kwargs["synsat_goes_number"] = instrument_config["goes_number"]
    elif instrument == "fci":
        kwargs["synsat_mtg_number"] = instrument_config["mtg_number"]
    
    # Initialize SynSatTest with the specified instrument
    s = SynSatTest(**kwargs)
    
    # Verify instrument was loaded correctly
    assert s.synsat.instrument.upper() == instrument.upper()
    
    # Verify channels configuration
    assert s.synsat.chan_list_instrument == channels
    assert s.synsat.nchan_instrument == len(channels)
    
    # Run the workflow using predefined profiles
    s.run_workflow()
    
    # Verify that results were produced
    assert s.BtRefl is not None
    assert s.BtRefl.shape[1] == len(channels)
    
    # Check that values are within a reasonable range
    # For brightness temperatures (K)
    bt_indices = [i for i, ch in enumerate(s.synsat.channels) if ch.startswith("bt")]
    if bt_indices:
        bt_values = s.BtRefl[:, bt_indices]
        assert np.all(bt_values > 180)  # Very cold temps
        assert np.all(bt_values < 340)  # Very hot temps
    
    # For reflectances (unitless)
    refl_indices = [i for i, ch in enumerate(s.synsat.channels) if ch.startswith("rho")]
    if refl_indices:
        refl_values = s.BtRefl[:, refl_indices]
        assert np.all(refl_values >= 0)  # Non-negative
        assert np.all(refl_values <= 1)  # Max reflectance


def test_load_seviri_default_channels():
    """
    Tests loading the SEVIRI instrument with default channel list.
    
    Verifies that SEVIRI can be loaded without errors and
    the default channels are set correctly.
    """
    # Initialize with default SEVIRI instrument
    s = SynSatTest(synsat_instrument="seviri")
    
    # Check if instrument was loaded correctly
    assert s.synsat.instrument == "SEVIRI"
    
    # Default channel list for SEVIRI should be (5, 6, 7, 9, 10, 11)
    assert s.synsat.chan_list_instrument == (5, 6, 7, 9, 10, 11)
    assert s.synsat.nchan_instrument == 6
    
    # Check that coefficient files were found
    assert "rtcoef_msg" in s.FileCoef


def test_load_seviri_single_channel():
    """
    Tests loading the SEVIRI instrument with a single channel.
    
    Verifies that SEVIRI can be loaded with a custom channel list
    containing just one channel.
    """
    # Initialize with SEVIRI instrument and only channel 9
    s = SynSatTest(synsat_instrument="seviri", synsat_channel_list=(9,))
    
    # Check if instrument was loaded correctly
    assert s.synsat.instrument == "SEVIRI"
    
    # Custom channel list should be just (9,)
    assert s.synsat.chan_list_instrument == (9,)
    assert s.synsat.nchan_instrument == 1
    
    # Check channels attribute contains the right variable
    assert "bt108" in s.synsat.channels


def test_load_abi_default_channels():
    """
    Tests loading the ABI instrument with default channel list.
    
    Verifies that ABI can be loaded without errors and
    the default channels are set correctly.
    """
    # Initialize with ABI instrument
    s = SynSatTest(synsat_instrument="abi")
    
    # Check if instrument was loaded correctly
    assert s.synsat.instrument == "ABI"
    
    # Default channel list for ABI should be (7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
    assert s.synsat.chan_list_instrument == (7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
    assert s.synsat.nchan_instrument == 10
    
    # Check that coefficient files were found
    assert "rtcoef_goes" in s.FileCoef


def test_load_abi_single_channel():
    """
    Tests loading the ABI instrument with a single channel.
    
    Verifies that ABI can be loaded with a custom channel list
    containing just one channel.
    """
    # Initialize with ABI instrument and only channel 13 (10.3 µm - Clean IR Longwave Window)
    s = SynSatTest(synsat_instrument="abi", synsat_channel_list=(13,))
    
    # Check if instrument was loaded correctly
    assert s.synsat.instrument == "ABI"
    
    # Custom channel list should be just (13,)
    assert s.synsat.chan_list_instrument == (13,)
    assert s.synsat.nchan_instrument == 1
    
    # Check channels attribute contains the right variable
    assert "bt103" in s.synsat.channels


def test_load_fci_default_channels():
    """
    Tests loading the FCI instrument with default channel list.
    
    Verifies that FCI can be loaded without errors and
    the default channels are set correctly.
    """
    # Initialize with FCI instrument
    s = SynSatTest(synsat_instrument="fci")
    
    # Check if instrument was loaded correctly
    assert s.synsat.instrument == "FCI"
    
    # Default channel list for FCI should be (9, 10, 11, 12, 13, 14, 15, 16)
    
    assert s.synsat.chan_list_instrument == (9, 10, 11, 12, 13, 14, 15, 16)
    assert s.synsat.nchan_instrument == 8
    
    # Check that coefficient files were found
    assert "rtcoef_mtg" in s.FileCoef


def test_load_fci_single_channel():
    """
    Tests loading the FCI instrument with a single channel.
    
    Verifies that FCI can be loaded with a custom channel list
    containing just one channel.
    """
    # Initialize with FCI instrument and only channel 14 (10.50 µm - Clean IR Window)
    s = SynSatTest(synsat_instrument="fci", synsat_channel_list=(14,))
    
    # Check if instrument was loaded correctly
    assert s.synsat.instrument == "FCI"
    
    # Custom channel list should be just (14,)
    assert s.synsat.chan_list_instrument == (14,)
    assert s.synsat.nchan_instrument == 1
    
    # Check channels attribute contains the right variable
    assert "bt105" in s.synsat.channels
