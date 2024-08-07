import numpy as np
import pylab as plt


def enhanced_colormap(vmin=200.0, vmed=240.0, vmax=300.0):
    """
    Creates enhanced colormap typical of IR BTs.

    Parameters
    ----------
    vmin : float, optional
        Minimum value for the colormap. Default is 200.0.
    vmed : float, optional
        Median value for the colormap. At this values shading jumps 
        from color to gray-scale. Default is 240.0.
    vmax : float, optional
        Maximum value for the colormap. Default is 300.0.

    Returns
    -------
    mymap : matplotlib.colors.LinearSegmentedColormap
        The generated colormap.
    """
    nfull = 256

    ngray = int(nfull * (vmax - vmed) / (vmax - vmin))
    ncol = nfull - ngray

    colors1 = plt.cm.gray_r(np.linspace(0.0, 1.0, ngray))
    colors2 = plt.cm.Spectral(np.linspace(0.0, 0.95, ncol))

    # combine them and build a new colormap
    colors = np.vstack((colors2, colors1))
    mymap = plt.matplotlib.colors.LinearSegmentedColormap.from_list(
        "enhanced_colormap", colors
    )

    return mymap

# make docstring for this function
def enhanced_wv62_cmap(vmin=200.0, vmed1=230.0, vmed2=240.0, vmax=260.0):
    """
    Creates enhanced colormap typical of WV62 BTs.

    Parameters
    ----------
    vmin : float, optional
        Minimum value for the colormap. Default is 200.0.
    vmed1 : float, optional
        First median value for the colormap. At this values shading jumps 
        from color to gray-scale. Default is 230.0.
    vmed2 : float, optional
        Second median value for the colormap. At this values shading jumps 
        from gray-scale to afmhot shadings. Default is 240.0.
    vmax : float, optional
        Maximum value for the colormap. Default is 260.0.

    Returns
    -------
    mymap : matplotlib.colors.LinearSegmentedColormap
        The generated colormap.
    """
    nfull = 256

    ncopp = int(nfull * (vmax - vmed2) / (vmax - vmin))
    ngray = int(nfull * (vmed2 - vmed1) / (vmax - vmin))
    ncol = nfull - (ncopp + ngray)

    colors1 = plt.cm.afmhot(np.linspace(0, 1.0, ncopp))
    colors2 = plt.cm.gray_r(np.linspace(0.0, 1.0, ngray))
    colors3 = plt.cm.Spectral(np.linspace(0, 1.0, ncol))

    # combine them and build a new colormap
    colors = np.vstack((colors3, colors2, colors1))
    mymap = plt.matplotlib.colors.LinearSegmentedColormap.from_list(
        "enhanced_wv62_cmap", colors
    )

    return mymap


