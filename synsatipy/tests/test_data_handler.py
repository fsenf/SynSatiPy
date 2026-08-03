import pytest

from synsatipy.data_handler import DataHandler
from synsatipy.synsat_example_data import get_example_data


@pytest.mark.parametrize(
    "example_name, return_geofile",
    [
        ("era01", False),
        ("icon01", False),
        ("icon02", False),
        ("hamlite01", True),
    ],
)
def test_input_of_example_data(example_name, return_geofile):

    if return_geofile:
        filename, geofile = get_example_data(example_name, return_geofile=return_geofile)
    else:
        filename = get_example_data(example_name, return_geofile=return_geofile)
        geofile = None

    d = DataHandler()
    d.open_data(filename, geofile=geofile)
