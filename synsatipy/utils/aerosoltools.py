import numpy as np
import xarray as xr

_default_aerosol_config = {
    "num_qca": {
        "radius": 8e-08,
        "density": 1993.0,
        "sigma": 1.59,
        "CAMS_OPAC_name": '"SOOT"',
        "target_name": "qca",
    },
    "num_qsu": {
        "radius": 1.4e-07,
        "density": 1859.0,
        "sigma": 1.59,
        "CAMS_OPAC_name": '"SULP"',
        "target_name": "qsu",
    },
    "num_qss": {
        "radius": 8.5e-07,
        "density": 2165.0,
        "sigma": 2.0,
        "CAMS_OPAC_name": '"SSA2"',
        "target_name": "qss",
    },
    "num_qdu": {
        "radius": 6e-07,
        "density": 2650.0,
        "sigma": 2.0,
        "CAMS_OPAC_name": '"DUS2"',
        "target_name": "qdu",
    },
}


def get_aerosol_particle_mass(r_geometric, sigma, rho):
    """
    Compute the mass of a single aerosol particle from lognormal size distribution parameters.

    Assumes a lognormal number size distribution. The volumetric (mass-equivalent)
    radius is derived from the geometric mean radius using the third moment of the
    lognormal distribution, and the particle mass is then obtained from its volume
    and material density.

    Parameters
    ----------
    r_geometric : float or array_like
        Geometric mean radius of the lognormal size distribution [m].
    sigma : float or array_like
        Geometric standard deviation of the lognormal size distribution
        (dimensionless, > 1).
    rho : float or array_like
        Material (bulk) density of the aerosol species [kg m⁻³].

    Returns
    -------
    m_particle : float or numpy.ndarray
        Mass of a single aerosol particle [kg].

    Notes
    -----
    The volumetric radius is computed as:

    .. math::

        r_{\\mathrm{vol}} = r_{\\mathrm{geo}} \\cdot \\exp\\!\\left(\\frac{3}{2} \\ln^2 \\sigma\\right)

    and the particle mass as:

    .. math::

        m = \\frac{4}{3} \\pi r_{\\mathrm{vol}}^3 \\cdot \\rho

    Examples
    --------
    >>> get_aerosol_particle_mass(r_geometric=0.1e-6, sigma=1.5, rho=1800.0)
    """
    # --- Lognormal parameters ---
    ln_sigma = np.log(sigma)
    moment3_factor = np.exp(1.5 * ln_sigma**2)
    r_vol = r_geometric * moment3_factor  # Volumetric Radius

    # --- Single-particle mass ---
    volume = (4.0 / 3.0) * np.pi * r_vol**3  # [m3]
    m_particle = volume * rho  # [kg]
    return m_particle


#####################################################################
#####################################################################


def convert_hamlite_numberconc_in_massconc(hamlite, config):
    """
    Convert HAMLite aerosol number concentrations to mass concentrations.

    Iterates over the aerosol species defined in ``config``, computes the
    single-particle mass from lognormal size distribution parameters, and
    multiplies by the number concentration to obtain mass concentration.

    Parameters
    ----------
    hamlite : xarray.Dataset
        HAMLite model dataset containing aerosol number concentration fields.
        Variable names must match the keys in ``config``.
    config : dict
        Configuration dictionary for aerosol species. Each key is the name of
        an aerosol variable in ``hamlite``, and the corresponding value is a
        dict with the following entries:

        radius : float
            Geometric mean radius of the lognormal size distribution [m].
        sigma : float
            Geometric standard deviation of the lognormal size distribution
            (dimensionless, > 1).
        density : float
            Material (bulk) density of the aerosol species [kg m⁻³].
            Note: key is spelled ``'denisty'`` in the current implementation
            (typo preserved for backwards compatibility).
        target_name : str
            Name of the output variable in the returned dataset.

    Returns
    -------
    hamlite_mass : xarray.Dataset
        Dataset with the same structure as ``hamlite`` but with aerosol
        variables converted to mass concentration [kg m⁻³].

    Notes
    -----
    Species present in ``config`` but absent from ``hamlite`` are silently
    skipped. The conversion is:

    .. math::

        c_{\\mathrm{mass}} = N \\cdot m_{\\mathrm{particle}}

    where :math:`N` is the number concentration [m⁻³] and
    :math:`m_{\\mathrm{particle}}` is computed by
    :func:`get_aerosol_particle_mass`.

    Examples
    --------
    >>> config = {
    ...     "so4_a1": {
    ...         "radius": 0.1e-6, "sigma": 1.5,
    ...         "denisty": 1800.0, "target_name": "aer_so4"
    ...     }
    ... }
    >>> hamlite_mass = convert_hamlite_numberconc_in_massconc(hamlite, config)
    """

    hamlite_mass = xr.Dataset()

    for aerosol_name in config:

        print(f"Processing aerosol species '{aerosol_name}'...")
        # get particle props
        radius = config[aerosol_name]["radius"]
        sigma = config[aerosol_name]["sigma"]
        density = config[aerosol_name]["density"]
        target_name = config[aerosol_name]["target_name"]

        # get particle mass
        aerosol_particle_mass = get_aerosol_particle_mass(radius, sigma, density)

        # do conversion
        if aerosol_name in hamlite:
            hamlite_mass[target_name] = hamlite[aerosol_name] * aerosol_particle_mass

    return hamlite_mass


######################################################################
######################################################################

def target_name_list( config ):
    """
    Get the list of target variable names from the aerosol config.

    Parameters
    ----------
    config : dict
        Configuration dictionary for aerosol species. Each key is the name of
        an aerosol variable, and the corresponding value is a dict with a
        'target_name' entry.    

    Returns
    -------
    target_names : list of str
        List of target variable names for the aerosol species defined in the config.

    """

    target_names = [ config[aerosol_name]["target_name"] for aerosol_name in config ]

    return target_names