import socket


def get_example_data(example_name, stored_on_server=True, return_geofile=False):

    """
    Get the example data.

    Parameters
    ----------
    example_name : str
        The name of the example data.
        Possible values are "era01", "icon01", "icon02", "hamlite01".

    stored_on_server : bool, optional
        If the data is stored on the server. Default is True.
        Check the server name and set this parameter False if the server is unknown.
        Possible servers are "tropos", "dkrz".

    return_geofile : bool, optional
        If True, return the path to the geofile as well. Default is False.
        
    Returns
    -------
    fname : str
        The file name of the example data. If <return_geofile> is True, a tuple
        (fname, geofile) is returned, where <geofile> is the path to the geofile.

    Notes
    -----
    The example data is stored on the server.
    """

    if return_geofile:
        geofile = None

    if stored_on_server:
        hostname = socket.getfqdn()

        if "tropos.de" in hostname:
            server = "tropos"

        elif "dkrz.de" in hostname:
            server = "dkrz"

        else:
            raise ValueError("Server is unknown. <stored_on_server> must be set False!")

    if example_name == "era01":

        if server == "tropos":
            dirname = "/vols/fs1/store/senf/data/era5/medi/2020"
            fname = f"{dirname}/era5-3d-medi-2020-09-15.nc"

        elif server == "dkrz":
            dirname = "/work/bb1376/data/synsatipy/example-data/era5"
            fname = f"{dirname}/era5-3d-medi-2020-09-15.nc"

    if example_name == "icon01":

        if server == "tropos":
            dirname = "/vols/fs1/store/senf/data/icon/ifces2/atlantic-cases/paulette/ifces2-atlanXL-20200907-exp021/POSTPROC/"
            fname = f"{dirname}/3d_full_base_DOM01_ML_20200912T000000Z_regrid7km.nc"

        elif server == "dkrz":
            dirname = "/work/bb1376/data/synsatipy/example-data/ifces2"
            fname = f"{dirname}/3d_full_base_DOM01_ML_20200912T000000Z_regrid7km.nc"

    if example_name == "icon02":

        if server == "tropos":
            dirname = "/vols/fs1/store/senf/data/icon/ifces2/atlantic-cases/paulette/ifces2-atlanXL-20200907-exp021/POSTPROC/"
            fname = f"{dirname}/3d_full_base_DOM02_ML_20200912T000000Z_regrid7km.nc"

        elif server == "dkrz":
            dirname = "/work/bb1376/data/synsatipy/example-data/ifces2"
            fname = f"{dirname}/3d_full_base_DOM02_ML_20200912T000000Z_regrid7km.nc"


    if example_name == 'hamlite01':


        if server == "dkrz":
            dirname = "/work/bb1376/data/synsatipy/example-data/hamlite"
            fname = f"{dirname}/lam_hra_2025_atm_3d_dyn_ml_20250530T030000Z.nc"
            geofile = f"{dirname}/hra_DOM01.nc"
    
    if return_geofile:
        return fname, geofile
    else:
        return fname


if __name__ == "__main__":

    print(get_example_data("era01"))

    print(get_example_data("icon01"))
