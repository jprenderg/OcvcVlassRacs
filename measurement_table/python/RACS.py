# -*- coding: utf-8 -*-
"""
Created on Wed May 27 12:01:55 2026

@author: Joe
"""

import os
import time
import numpy as np
import pandas as pd
from astropy import units as u
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy import wcs
from astroquery.casda import Casda

from config import CACHE_DIR, OPAL_USERNAME

# ------------------------------------------------------------
# User settings
# ------------------------------------------------------------


cache_dir = CACHE_DIR
os.makedirs(cache_dir, exist_ok=True)

# ------------------------------------------------------------
# CASDA login
# ------------------------------------------------------------

casda = Casda()
casda.login(username=OPAL_USERNAME)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def make_output(source_id, measurement=None, error=None):
    return pd.DataFrame([{
        "SOURCE_ID": source_id,
        "OBSERVATORY": "ASKAP",
        "CAT": "RACS-DR1",
        "BAND": "887.5 MHz",
        "UNITS": "mJy",
        "MEASUREMENT": measurement,
        "ERROR": error
    }])


def is_valid_fits(path):
    try:
        with open(path, "rb") as f:
            return f.read(8).startswith(b"SIMPLE")
    except Exception:
        return False


def download_valid_fits(casda, urls, savedir, max_tries=3):
    last_files = None

    for attempt in range(max_tries):

        files = casda.download_files(
            urls,
            savedir=savedir
        )

        last_files = files

        fits_files = [
            f for f in files
            if str(f).lower().endswith(".fits")
        ]

        for path in fits_files:

            if is_valid_fits(path):
                return path

            try:
                os.remove(path)
            except Exception:
                pass

        time.sleep(5)

    return None


# ------------------------------------------------------------
# Main function
# ------------------------------------------------------------

def racs(source_id, ra_deg, dec_deg):

    search_radius = 30 * u.arcmin
    cutout_radius = 1 * u.arcmin
    dim = 5

    measurement = None
    error = None

    coord = SkyCoord(
        ra=ra_deg * u.deg,
        dec=dec_deg * u.deg,
        frame="icrs"
    )

    try:
        # --------------------------------------------------------
        # Query CASDA near coordinate
        # --------------------------------------------------------

        result = casda.query_region(
            coord,
            radius=search_radius
        )

        public_data = casda.filter_out_unreleased(result)

        filenames = public_data["filename"].astype(str)

        # --------------------------------------------------------
        # Select RACS DR1 flux image
        # Example: RACS-DR1_0202-37A.fits
        # --------------------------------------------------------

        flux_subset = public_data[
            (public_data["obs_collection"] == "The Rapid ASKAP Continuum Survey")
            & np.char.startswith(filenames, "RACS-DR1_")
            & np.char.endswith(filenames, "A.fits")
            & ~np.char.endswith(filenames, "_RMS.fits")
        ]

        if len(flux_subset) == 0:
            print("No RACS DR1 flux FITS image found.")
            return make_output(source_id)

        flux_selected = flux_subset[:1]
        flux_filename = str(flux_selected["filename"][0])

        # --------------------------------------------------------
        # Find matching RMS image
        # Example:
        # RACS-DR1_0202-37A.fits
        # RACS-DR1_0202-37A_RMS.fits
        # --------------------------------------------------------

        rms_filename = flux_filename.replace(".fits", "_RMS.fits")

        rms_subset = public_data[
            public_data["filename"].astype(str) == rms_filename
        ]

        if len(rms_subset) == 0:
            print(f"No matching RMS FITS image found: {rms_filename}")
            return make_output(source_id)

        rms_selected = rms_subset[:1]

        print("Flux file:", flux_filename)
        print("RMS file: ", rms_filename)

        # --------------------------------------------------------
        # Download flux cutout
        # --------------------------------------------------------

        flux_urls = casda.cutout(
            flux_selected,
            coordinates=coord,
            radius=cutout_radius
        )

        flux_path = download_valid_fits(
            casda,
            flux_urls,
            cache_dir
        )

        if flux_path is None:
            print("No valid flux FITS file downloaded.")
            return make_output(source_id)

        # --------------------------------------------------------
        # Download RMS cutout
        # --------------------------------------------------------

        rms_urls = casda.cutout(
            rms_selected,
            coordinates=coord,
            radius=cutout_radius
        )

        rms_path = download_valid_fits(
            casda,
            rms_urls,
            cache_dir
        )

        if rms_path is None:
            print("No valid RMS FITS file downloaded.")
            return make_output(source_id)

        # --------------------------------------------------------
        # Measure flux from flux image
        # --------------------------------------------------------

        with fits.open(flux_path, memmap=False) as hdul:

            flux_data = hdul[0].data
            flux_header = hdul[0].header.copy()

            flux_image = np.squeeze(flux_data)
            flux_wcs = wcs.WCS(flux_header).celestial

            pix = flux_wcs.wcs_world2pix(
                [(ra_deg, dec_deg)],
                0
            )[0]

            xpix = int(round(pix[0]))
            ypix = int(round(pix[1]))

            nrows, ncols = flux_image.shape

            y0 = ypix - dim
            y1 = ypix + dim
            x0 = xpix - dim
            x1 = xpix + dim

            if not (
                0 <= xpix < ncols
                and 0 <= ypix < nrows
                and x0 >= 0
                and y0 >= 0
                and x1 <= ncols
                and y1 <= nrows
            ):
                print("Flux cutout lies outside image.")
                return make_output(source_id)

            flux_cutout = flux_image[y0:y1, x0:x1]

            max_y_cutout, max_x_cutout = np.unravel_index(
                np.nanargmax(flux_cutout),
                flux_cutout.shape
            )

            y_flux = y0 + max_y_cutout
            x_flux = x0 + max_x_cutout

            measurement = float(flux_image[y_flux, x_flux] * 1000.0)

            flux_peak_sky = flux_wcs.wcs_pix2world(
                [(x_flux, y_flux)],
                0
            )[0]

            peak_ra = flux_peak_sky[0]
            peak_dec = flux_peak_sky[1]

        # --------------------------------------------------------
        # Measure RMS at same sky position as max-flux pixel
        # --------------------------------------------------------

        with fits.open(rms_path, memmap=False) as hdul:

            rms_data = hdul[0].data
            rms_header = hdul[0].header.copy()

            rms_image = np.squeeze(rms_data)
            rms_wcs = wcs.WCS(rms_header).celestial

            rms_pix = rms_wcs.wcs_world2pix(
                [(peak_ra, peak_dec)],
                0
            )[0]

            x_rms = int(round(rms_pix[0]))
            y_rms = int(round(rms_pix[1]))

            rms_rows, rms_cols = rms_image.shape

            if 0 <= x_rms < rms_cols and 0 <= y_rms < rms_rows:
                error = float(rms_image[y_rms, x_rms] * 1000.0)
            else:
                print("RMS coordinate lies outside RMS image.")
                return make_output(source_id)

    except Exception as e:
        print(f"ASKAP exception for SOURCE_ID {source_id}: {e}")
        return make_output(source_id)

    return make_output(
        source_id,
        measurement=measurement,
        error=error
    )


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------

# unique_id = 1
# ra_deg = 0.0370542
# dec_deg = -77.3388

# temp = racs(unique_id, ra_deg, dec_deg)

# print(temp)