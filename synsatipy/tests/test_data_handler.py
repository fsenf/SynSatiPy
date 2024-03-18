import pytest

from synsatipy.data_handler import DataHandler
from synsatipy.synsat_example_data import get_example_data


@pytest.mark.parametrize(
    "example_name",
    [
        ("era01"),
        ("icon01"),
    ],
)
def test_input_of_example_data(example_name):

    filename = get_example_data(example_name)

    d = DataHandler()
    d.open_data(filename)
