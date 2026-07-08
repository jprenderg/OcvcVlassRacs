# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 11:55:16 2026

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

CACHE_DIR.mkdir(parents=True, exist_ok=True)

cache_dir = str(CACHE_DIR)

# ------------------------------------------------------------
# CASDA login
# ------------------------------------------------------------

casda = Casda()
casda.login(username=OPAL_USERNAME)


# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------

search_radius = 30 * u.arcmin      # CASDA search radius
cutout_radius = 2 * u.arcmin       # downloaded FITS cutout size

search_radius_pix = 120

peak_box_size = 5
half_box = peak_box_size // 2

threshold_mjy = 1.0
threshold_jy = threshold_mjy / 1000.0


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def get_2d_image(data):
    image = np.squeeze(data)

    if image.ndim == 2:
        return image
    else:
        return None


def is_valid_fits(path):
    try:
        with open(path, "rb") as f:
            return f.read(8).startswith(b"SIMPLE")
    except Exception:
        return False


def download_valid_fits(casda, urls, savedir, max_tries=3):
    for attempt in range(max_tries):

        files = casda.download_files(
            urls,
            savedir=savedir
        )

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


def get_racs_cutouts(ra_deg, dec_deg):
    """
    Query CASDA, find RACS-DR1 flux and RMS images,
    download cutouts, and return local paths.
    """

    coord = SkyCoord(
        ra=ra_deg * u.deg,
        dec=dec_deg * u.deg,
        frame="icrs"
    )

    result = casda.query_region(
        coord,
        radius=search_radius
    )

    public_data = casda.filter_out_unreleased(result)

    filenames = public_data["filename"].astype(str)

    flux_subset = public_data[
        (public_data["obs_collection"] == "The Rapid ASKAP Continuum Survey")
        & np.char.startswith(filenames, "RACS-DR1_")
        & np.char.endswith(filenames, "A.fits")
        & ~np.char.endswith(filenames, "_RMS.fits")
    ]

    if len(flux_subset) == 0:
        return None, None

    flux_selected = flux_subset[:1]
    flux_filename = str(flux_selected["filename"][0])

    rms_filename = flux_filename.replace(".fits", "_RMS.fits")

    rms_subset = public_data[
        public_data["filename"].astype(str) == rms_filename
    ]

    if len(rms_subset) == 0:
        return None, None

    rms_selected = rms_subset[:1]

    print("Flux file:", flux_filename)
    print("RMS file: ", rms_filename)

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
        return None, None

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
        return None, None

    return flux_path, rms_path


# ------------------------------------------------------------
# Main function
# ------------------------------------------------------------

def racs_neighbors(ra_deg, dec_deg):
    """
    Find RACS local-peak neighbors around input RA/DEC.

    Downloads RACS-DR1 flux and RMS cutouts from CASDA.

    Parameters
    ----------
    ra_deg : float
        RA in degrees.

    dec_deg : float
        DEC in degrees.

    Returns
    -------
    df_neighbors : pandas.DataFrame
        Columns:
            RA
            DEC
    """

    empty = pd.DataFrame(columns=["RA", "DEC"])

    if pd.isna(ra_deg) or pd.isna(dec_deg):
        return empty

    if not np.isfinite(ra_deg) or not np.isfinite(dec_deg):
        return empty

    # --------------------------------------------------------
    # Download RACS cutouts
    # --------------------------------------------------------

    try:
        fits_path_flux, fits_path_rms = get_racs_cutouts(
            ra_deg,
            dec_deg
        )
    except Exception as e:
        print(f"CASDA exception: {e}")
        return empty

    if fits_path_flux is None or fits_path_rms is None:
        return empty

    # --------------------------------------------------------
    # Open flux FITS
    # --------------------------------------------------------

    try:
        with fits.open(fits_path_flux, memmap=False) as hdul:
            data = hdul[0].data
            header = hdul[0].header.copy()

            image = get_2d_image(data)

            if image is None:
                return empty

    except Exception as e:
        print(f"Could not open flux FITS: {e}")
        return empty

    # --------------------------------------------------------
    # Open RMS FITS
    # --------------------------------------------------------

    try:
        with fits.open(fits_path_rms, memmap=False) as hdul_rms:
            data_rms = hdul_rms[0].data
            image_rms = get_2d_image(data_rms)

            if image_rms is None:
                return empty

    except Exception as e:
        print(f"Could not open RMS FITS: {e}")
        return empty

    if image.shape != image_rms.shape:
        return empty

    image_rows, image_columns = image.shape

    # --------------------------------------------------------
    # Build celestial WCS
    # --------------------------------------------------------

    try:
        mywcs = wcs.WCS(header).celestial

    except Exception as e:
        print(f"WCS exception: {e}")
        return empty

    # --------------------------------------------------------
    # Convert input RA/DEC to pixel
    # --------------------------------------------------------

    try:
        pix = mywcs.wcs_world2pix(
            [(ra_deg, dec_deg)],
            0
        )[0]

    except Exception:
        return empty

    if not np.isfinite(pix[0]) or not np.isfinite(pix[1]):
        return empty

    xpix = int(round(pix[0]))
    ypix = int(round(pix[1]))

    if (
        xpix < 0 or
        xpix >= image_columns or
        ypix < 0 or
        ypix >= image_rows
    ):
        return empty

    # --------------------------------------------------------
    # Define search region
    # --------------------------------------------------------

    y0 = max(half_box, ypix - search_radius_pix)
    y1 = min(image_rows - half_box, ypix + search_radius_pix + 1)

    x0 = max(half_box, xpix - search_radius_pix)
    x1 = min(image_columns - half_box, xpix + search_radius_pix + 1)

    if y1 <= y0 or x1 <= x0:
        return empty

    center = image[y0:y1, x0:x1]

    if center.size == 0:
        return empty

    if not np.isfinite(center).any():
        return empty

    yy, xx = np.mgrid[y0:y1, x0:x1]

    inside_radius = (
        (xx - xpix) ** 2 +
        (yy - ypix) ** 2
    ) <= search_radius_pix ** 2

    # --------------------------------------------------------
    # Find 5x5 local peaks above 1 mJy
    # --------------------------------------------------------

    peak_mask = (
        np.isfinite(center) &
        (center > threshold_jy) &
        inside_radius
    )

    for dy in range(-half_box, half_box + 1):
        for dx in range(-half_box, half_box + 1):

            if dy == 0 and dx == 0:
                continue

            neighbor_y0 = y0 + dy
            neighbor_y1 = y1 + dy
            neighbor_x0 = x0 + dx
            neighbor_x1 = x1 + dx

            if (
                neighbor_y0 < 0 or
                neighbor_x0 < 0 or
                neighbor_y1 > image_rows or
                neighbor_x1 > image_columns
            ):
                peak_mask[:, :] = False
                continue

            neighbor = image[
                neighbor_y0:neighbor_y1,
                neighbor_x0:neighbor_x1
            ]

            if neighbor.shape != center.shape:
                peak_mask[:, :] = False
                continue

            peak_mask &= center > neighbor

    peak_y = yy[peak_mask]
    peak_x = xx[peak_mask]

    if len(peak_x) == 0:
        return empty

    # --------------------------------------------------------
    # Bounds and edge checks
    # --------------------------------------------------------

    rms_rows, rms_columns = image_rms.shape

    good_peak = (
        np.isfinite(peak_x) &
        np.isfinite(peak_y) &
        (peak_x >= 0) &
        (peak_x < image_columns) &
        (peak_y >= 0) &
        (peak_y < image_rows) &
        (peak_x < rms_columns) &
        (peak_y < rms_rows) &
        (peak_x - half_box >= 0) &
        (peak_x + half_box < image_columns) &
        (peak_y - half_box >= 0) &
        (peak_y + half_box < image_rows) &
        (peak_x + half_box < rms_columns) &
        (peak_y + half_box < rms_rows)
    )

    peak_x = peak_x[good_peak].astype(int)
    peak_y = peak_y[good_peak].astype(int)

    if len(peak_x) == 0:
        return empty

    # --------------------------------------------------------
    # Require finite flux and RMS at peak pixels
    # --------------------------------------------------------

    peak_flux_mjy = image[peak_y, peak_x] * 1000.0
    peak_rms_mjy = image_rms[peak_y, peak_x] * 1000.0

    finite_flux_rms = (
        np.isfinite(peak_flux_mjy) &
        np.isfinite(peak_rms_mjy)
    )

    peak_x = peak_x[finite_flux_rms]
    peak_y = peak_y[finite_flux_rms]

    if len(peak_x) == 0:
        return empty

    # --------------------------------------------------------
    # Convert peak pixels back to RA/DEC
    # --------------------------------------------------------

    try:
        world = mywcs.wcs_pix2world(
            np.column_stack([peak_x, peak_y]),
            0
        )

    except Exception:
        return empty

    peak_ra = world[:, 0]
    peak_dec = world[:, 1]

    finite_world = (
        np.isfinite(peak_ra) &
        np.isfinite(peak_dec)
    )

    peak_ra = peak_ra[finite_world]
    peak_dec = peak_dec[finite_world]

    if len(peak_ra) == 0:
        return empty

    df_neighbors = pd.DataFrame({
        "RA": peak_ra,
        "DEC": peak_dec
    })

    return df_neighbors


# ------------------------------------------------------------
# Example
# ------------------------------------------------------------

# df_test = racs_neighbors(
#     268.815875, -29.5995
# )

# print(df_test)