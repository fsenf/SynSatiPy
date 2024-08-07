import os, sys


def get_example_data(example_name, stored_on_server=True):

    """
    Get the example data.

    Parameters
    ----------
    example_name : str
        The name of the example data.
        Possible values are "era01", "icon01", "icon02".

    stored_on_server : bool, optional
        If the data is stored on the server. Default is True.
        Check the server name and set this parameter False if the server is unknown.
        Possible servers are "tropos", "dkrz".

    Returns
    -------
    fname : str
        The file name of the example data

    Notes
    -----
    The example data is stored on the server.
    """
    

    if stored_on_server:
        hostname = os.uname()[1]

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
            dirname = "/work/bb1262/data/era5/medi/2020"
            fname = f"{dirname}/era5-3d-medi-2020-09-15.nc"

    if example_name == "icon01":

        if server == "tropos":
            dirname = "/vols/fs1/store/senf/data/icon/ifces2/atlantic-cases/paulette/ifces2-atlanXL-20200907-exp021/POSTPROC/"
            fname = f"{dirname}/3d_full_base_DOM01_ML_20200912T000000Z_regrid7km.nc"

        elif server == "dkrz":
            dirname = "/work/bb1376/data/icon/atlantic-cases/paulette/ifces2-atlanXL-20200907-exp021/POSTPROC/"
            fname = f"{dirname}/3d_full_base_DOM01_ML_20200912T000000Z_regrid7km.nc"

    if example_name == "icon02":

        if server == "tropos":
            dirname = "/vols/fs1/store/senf/data/icon/ifces2/atlantic-cases/paulette/ifces2-atlanXL-20200907-exp021/POSTPROC/"
            fname = f"{dirname}/3d_full_base_DOM02_ML_20200912T000000Z_regrid7km.nc"

        elif server == "dkrz":
            dirname = "/work/bb1376/data/icon/atlantic-cases/paulette/ifces2-atlanXL-20200907-exp021/POSTPROC/"
            fname = f"{dirname}/3d_full_base_DOM02_ML_20200912T000000Z_regrid7km.nc"

    return fname


if __name__ == "__main__":

    print(get_example_data("era01"))

    print(get_example_data("icon01"))
