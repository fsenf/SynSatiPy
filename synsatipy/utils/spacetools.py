import numpy as np

######################################################################
######################################################################


def lonlat2azizen(lon, lat, lon0 = 0.0):

    '''
    Calculates satellite zenith and azimuth given lon / lat. Assumes
    sub-satellite longitude at `lon0` degree E.


    Parameters
    ----------
    lon : float or numpy array
        longitude
   
    lat : float or numpy array 
        latitude
    
    lon0 : float, optional
        longitude of sub-satellite point. The default is 0.0.
        This is the longitude of the satellite at zenith.


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
    lam, phi = np.deg2rad(lon - lon0), np.deg2rad(lat)
    

# calculate angle on great circle between pixel and (0,0) ............
    delta = np.arccos( np.cos(phi) * np.cos (lam) )


# azimuth angle ......................................................
    azi = np.arccos( np.sin(phi) / np.sin(delta))
    

# missing side of triangle ...........................................
    D = np.sqrt( R**2 + H**2 - 2 * H * R * np.cos(delta) )


# angle in the triangle on the opposite side of the height of satellite
# angle larger than 90 deg -> use second argument of sine
    gamma = pi - np.arcsin( H / D * np.sin(delta) )

# zenith angle .......................................................
    #    zen = pi - gamma
    zen = np.where( np.cos(delta) - R/H < 0, pi/2, pi - gamma)

    
    np.nan_to_num(azi, copy=False)
    np.nan_to_num(zen, copy=False)

    return np.rad2deg(azi), np.rad2deg(zen)

######################################################################
######################################################################
