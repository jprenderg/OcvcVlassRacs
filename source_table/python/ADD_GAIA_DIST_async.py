# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 09:05:38 2026

@author: Joe
"""

from astroquery.gaia import Gaia
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
import pandas as pd
import logging


logging.getLogger("astroquery").setLevel(logging.ERROR)


def add_gaia_dist(df_source_interm):
    """
    Adds the following columns to df_source_interm:

        DISTANCE
        DISTANCE_ERROR

    Distances are calculated in kpc from the Gaia parallax:

        DISTANCE = 1 / parallax

    where parallax is in milliarcseconds.

    The nearest Gaia source within 2 arcseconds is used.
    """

    df_source_interm = df_source_interm.copy().reset_index(drop=True)

    # --------------------------------------------------------
    # Create output columns
    # --------------------------------------------------------

    for col in [
        "DISTANCE",
        "DISTANCE_ERROR"
    ]:
        if col not in df_source_interm.columns:
            df_source_interm[col] = np.nan

    # --------------------------------------------------------
    # Settings
    # --------------------------------------------------------

    search_radius_arcsec = 2.0

    Gaia.ROW_LIMIT = 1

    # --------------------------------------------------------
    # Process rows
    # --------------------------------------------------------

    for i in range(len(df_source_interm)):

        print(f"Processing {i + 1} of {len(df_source_interm)}")

        ra = df_source_interm.at[i, "RA"]
        dec = df_source_interm.at[i, "DEC"]

        if pd.isna(ra) or pd.isna(dec):
            continue

        coord = SkyCoord(
            ra=float(ra) * u.deg,
            dec=float(dec) * u.deg,
            frame="icrs"
        )

        try:

            job = Gaia.cone_search_async(
                coord,
                radius=search_radius_arcsec * u.arcsec
            )

            result = job.get_results()

            if result is None or len(result) == 0:
                continue

            row = result[0]

            parallax = row["parallax"]
            parallax_error = row["parallax_error"]

            if np.ma.is_masked(parallax):
                continue

            parallax = float(parallax)

            # A simple inverse-parallax distance is only valid
            # for a positive parallax.
            if parallax <= 0:
                continue

            # Parallax in mas gives distance directly in kpc.
            distance = 1.0 / parallax

            df_source_interm.at[i, "DISTANCE"] = distance

            if not np.ma.is_masked(parallax_error):

                parallax_error = float(parallax_error)

                if np.isfinite(parallax_error):

                    distance_error = (
                        parallax_error / parallax**2
                    )

                    df_source_interm.at[
                        i,
                        "DISTANCE_ERROR"
                    ] = distance_error

        except Exception as e:
            print(f"Row {i}: {e}")

    return df_source_interm