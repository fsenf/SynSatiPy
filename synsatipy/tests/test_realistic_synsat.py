import os, tempfile


from synsatipy.synsat import SynSat


def test_synsat4nextgems():

    """
    Test the SynSat class with the nextGEMS data.
    """
    cat_path = "https://data.nextgems-h2020.eu/catalog.yaml"
    medi_extend = [-8, 45, 30, 45]
    time = "2021-07-01T0030"
    zoom = 5
    expname = "ngc4008a"
    version = "medi-v001"

    # init
    s = SynSat()
    isel = {"cell": slice(0, None, 4)}

    # data input
    nextgems_kws = dict(
        model="nextgems",
        zoom=zoom,
        time=time,
        extend=medi_extend,
        profile_dimensions=["time", "cell"],
    )
    s.load(cat_path, isel=isel, **nextgems_kws)

    s._options.Nthreads = 1
    s._options.NprofsPerCall = 4000
    s.Options.Verbose = False

    # run RTTOV
    s.run(chunked=True, synsat_snow_factor=1.0)

    # output
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".nc")

    s.save(f"{output_file.name}")
    os.unlink(output_file.name)
