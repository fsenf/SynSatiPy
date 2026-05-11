import os
import pytest

import synsatipy.synsat_example_data as synsat_example_data


def test_examble_data():

    eraname = synsat_example_data.get_example_data("era01")

    assert "medi" in eraname

    iconname = synsat_example_data.get_example_data("icon01")

    assert "ifces2" in iconname

    hamlitename = synsat_example_data.get_example_data("hamlite01")

    assert "hamlite" in hamlitename

@pytest.mark.parametrize("example_name", ["era01", "icon01", "icon02", "hamlite01"])
def test_example_data_file_exists(example_name):
    """Check that the path returned by get_example_data points to an existing file."""
    fname = synsat_example_data.get_example_data(example_name)
    assert os.path.isfile(fname), f"Example data file not found: {fname}"
