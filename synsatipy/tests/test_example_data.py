import pytest

import synsatipy.synsat_example_data as synsat_example_data

def test_examble_data(  ):

    eraname = synsat_example_data.get_example_data( 'era01' )

    assert 'medi' in eraname

    iconname = synsat_example_data.get_example_data( 'icon01' )

    assert 'ifces2' in iconname

