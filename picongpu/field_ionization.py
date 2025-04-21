#!/usr/bin/env python
"""Field ionization models implemented in PIConGPU.

This file is part of PIConGPU.
Copyright 2019-2024 PIConGPU contributors
Authors: Marco Garten, Brian Marre
License: GPLv3+
"""


import numpy as np
import scipy.constants as sc


class FieldIonization:
    """Field ionization class, containing methods and units.

    A field ionization class that contains functions to calculate ionization
    rates, threshold fields and atomic units.
    """

    # dictionary of atomic units (AU) - values in SI units
    atomic_unit = {
        "electric field": sc.m_e**2 * sc.e**5 / (sc.hbar**4 * (4 * sc.pi * sc.epsilon_0) ** 3),
        "intensity": sc.m_e**4 / (8 * sc.pi * sc.alpha * sc.hbar**9) * sc.e**12 / (4 * sc.pi * sc.epsilon_0) ** 6,
        "energy": sc.m_e * sc.e**4 / (sc.hbar**2 * (4 * sc.pi * sc.epsilon_0) ** 2),
        "time": sc.hbar**3 * (4 * sc.pi * sc.epsilon_0) ** 2 / sc.m_e / sc.e**4,
    }

    def F_crit_BSI(self, Z, E_Ip):
        """Classical barrier suppression field strength.

        :param Z: charge state of the resulting ion
        :param E_Ip: ionization potential [unit: AU]

        :returns: critical field strength [unit: AU]
        """
        return E_Ip**2.0 / (4.0 * Z)

    def F_crit_BSIStarkShifted(self, E_Ip):
        """Barrier suppression field strength according to \
        Bauer 2010 - High Power Laser Matter Interaction, p. 276, Eq. (7.45).

        :param E_Ip: ionization potential [unit: AU]

        :returns: critical field strength [unit: AU]
        """
        return (np.sqrt(2.0) - 1.0) * E_Ip ** (3.0 / 2.0)

    def n_eff(self, Z, E_Ip):
        """Effective principal quantum number.

        Belongs to the ADK rate model.

        :param Z: charge state of the resulting ion
        :param E_Ip: ionization potential [unit: AU]

        :returns: effective principal quantum number
        """
        return Z / np.sqrt(2.0 * E_Ip)

    def ADKRate(self, Z, E_Ip, F, polarization="linear"):
        """Ammosov-Delone-Krainov ionization rate.

        A rate model, simplified by Stirling's approximation and setting the
        magnetic quantum number m=0 like in publication [DeloneKrainov1998].

        :param Z: charge state of the resulting ion
        :param E_Ip: ionization potential [unit: AU]
        :param F: field strength [unit: AU]
        :param polarization: laser polarization
                             ['linear' (default), 'circular']

        :returns: ionization rate [unit: 1/AU(time)]
        """
        pol = polarization
        if pol not in ["linear", "circular"]:
            raise NotImplementedError(
                "Cannot interpret polarization='{}'.\n".format(pol)
                + "So far, the only implemented options are: "
                + "['linear', 'circular']"
            )

        nEff = np.float64(self.n_eff(Z, E_Ip))
        D = ((4.0 * np.exp(1.0) * Z**3.0) / (F * nEff**4.0)) ** nEff

        rate = (F * D**2.0) / (8.0 * np.pi * Z) * np.exp(-(2.0 * Z**3.0) / (3.0 * nEff**3.0 * F))

        if pol == "linear":
            rate = rate * np.sqrt((3.0 * nEff**3.0 * F) / (np.pi * Z**3.0))

        # set nan values due to near-zero field strengths to zero
        rate = np.nan_to_num(rate)

        return rate

    def KeldyshRate(self, E_Ip, F):
        """Keldysh model ionization rate.

        :param E_Ip: ionization potential [unit: AU]
        :param F: field strength [unit: AU]

        :returns: ionization rate [unit: 1/AU(time)]
        """
        # characteristic exponential function argument
        charExpArg = np.sqrt((2.0 * E_Ip) ** 3) / F

        # ionization rate
        rate = (
            np.sqrt(6.0 * np.pi) / 2 ** (5.0 / 4.0) * E_Ip * np.sqrt(1.0 / charExpArg) * np.exp(-2.0 / 3.0 * charExpArg)
        )

        return rate

    @staticmethod
    def convert_a0_to_Intensity(E_in_a0, lambda_laser=800.0e-9):
        """Convert electric field in a0 to intensity in SI.

        :param E_in_a0: electric field [unit: a0]
        :param lambda_laser: laser wavelength [unit: m]

        :returns: intensity [unit: W/m^2]
        """
        E_in_SI = E_in_a0 * sc.m_e * sc.c * 2.0 * sc.pi * sc.c / (lambda_laser * sc.e)

        intensity = 0.5 * sc.c * sc.epsilon_0 * E_in_SI**2.0

        return intensity
    def convert_Intensity_to_a0(intensity, lambda_laser=800.0e-9):
        """Convert electric field in a0 to intensity in SI.

        :param intensity [unit: W/m^2]
        :param lambda_laser: laser wavelength [unit: m]

        :returns: E_in_a0: electric field [unit: a0]
        """
        E_in_SI= (intensity*(0.5 * sc.c * sc.epsilon_0 ))**(1/2) 
        
        E_in_a0=_in_SI/(c.m_e * sc.c * 2.0 * sc.pi * sc.c / (lambda_laser * sc.e))

        return E_in_a0
