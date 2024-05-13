import numpy as np

######################################################################
######################################################################


def lonlat2azizen(lon, lat):

    '''
    Calculates satellite zenith and azimuth given lon / lat. Assumes
    sub-satellite longitude at zero degree E.


    Parameters
    ----------
    lon : float or numpy array
        longitude
   
    lat : float or numpy array
        latitude


    Returns
    -------
    azi : float or numpy array
        satellite azimuth angle
    
    zen : float or numpy array
        satellite zenith angle
    '''

# satellite height and earth radius ..................................
    H = 42164
    R = 6378
    pi = np.pi
    
# from degree to radiant .............................................
    lon, lat = np.deg2rad(lon), np.deg2rad(lat)
    

# calculate angle on great circle between pixel and (0,0) ............
    delta = np.arccos( np.cos(lat) * np.cos (lon) )


# azimuth angle ......................................................
    azi = np.arccos( np.sin(lat) / np.sin(delta))
    

# missing side of triangle ...........................................
    D = np.sqrt( R**2 + H**2 - 2 * H * R * np.cos(delta) )


# angle in the triangle on the opposite side of the height of satellite
# angle larger than 90 deg -> use second argument of sine
    gamma = pi - np.arcsin( H / D * np.sin(delta) )

# zenith angle .......................................................
    zen = pi - gamma
    
    np.nan_to_num(azi, copy=False)
    np.nan_to_num(zen, copy=False)

    return np.rad2deg(azi), np.rad2deg(zen)

######################################################################
######################################################################
