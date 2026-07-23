# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 14:50:34 2026

@author: Joe
"""

import sqlite3
import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))
from config import MASTER_DB
from config import OUTPUT_DB

# ------------------------------------------------------------
# Inputs
# ------------------------------------------------------------

db_path = OUTPUT_DB

ra_in = 245.4470133276900
dec_in = -22.8862182469700


# ------------------------------------------------------------
# Open database
# ------------------------------------------------------------

conn = sqlite3.connect(db_path)

# ------------------------------------------------------------
# Load source_table and find closest SOURCE_ID
# ------------------------------------------------------------

df_source_all = pd.read_sql_query(
    """
    SELECT
        SOURCE_ID,
        PRIMARY_FLAG,
        RA,
        DEC,
        MAJOR_AXIS,
        MINOR_AXIS,
        POSITION_ANGLE,
        DISTANCE,
        DISTANCE_ERROR
    FROM source_table
    WHERE RA IS NOT NULL
      AND DEC IS NOT NULL
    """,
    conn
)

target = SkyCoord(ra=ra_in * u.deg, dec=dec_in * u.deg, frame="icrs")

coords = SkyCoord(
    ra=df_source_all["RA"].astype(float).values * u.deg,
    dec=df_source_all["DEC"].astype(float).values * u.deg,
    frame="icrs"
)

sep_arcsec = target.separation(coords).arcsec
idx = int(np.argmin(sep_arcsec))

source_id = int(df_source_all.iloc[idx]["SOURCE_ID"])
closest_sep = float(sep_arcsec[idx])

print("\nClosest SOURCE_ID:")
print("SOURCE_ID =", source_id)
print("Separation arcsec =", closest_sep)

# ------------------------------------------------------------
# Print source_table row
# ------------------------------------------------------------

df_source = pd.read_sql_query(
    """
    SELECT *
    FROM source_table
    WHERE SOURCE_ID = ?
    """,
    conn,
    params=(source_id,)
)

print("\nSource_Table row:")
print(df_source.to_string(index=False))

# ------------------------------------------------------------
# Print nearby non-primary sources (within 5 arcminutes)
# ------------------------------------------------------------

search_radius_arcsec = 300.0
search_radius_deg = search_radius_arcsec / 3600.0

ra0 = float(df_source.iloc[0]["RA"])
dec0 = float(df_source.iloc[0]["DEC"])

cos_dec = np.cos(np.radians(dec0))

ra_min = ra0 - search_radius_deg / cos_dec
ra_max = ra0 + search_radius_deg / cos_dec
dec_min = dec0 - search_radius_deg
dec_max = dec0 + search_radius_deg

df_neighbors = pd.read_sql_query(
    """
    SELECT *
    FROM source_table
    WHERE PRIMARY_FLAG = 0
      AND RA BETWEEN ? AND ?
      AND DEC BETWEEN ? AND ?
    """,
    conn,
    params=(ra_min, ra_max, dec_min, dec_max)
)

if len(df_neighbors) > 0:

    c_primary = SkyCoord(
        ra=ra0 * u.deg,
        dec=dec0 * u.deg
    )

    c_neighbors = SkyCoord(
        ra=df_neighbors["RA"].astype(float).values * u.deg,
        dec=df_neighbors["DEC"].astype(float).values * u.deg
    )

    df_neighbors["SEPARATION_ARCSEC"] = (
        c_primary.separation(c_neighbors).arcsecond
    )

    df_neighbors = df_neighbors[
        (df_neighbors["SEPARATION_ARCSEC"] <= search_radius_arcsec) &
        (df_neighbors["SOURCE_ID"] != source_id)
    ]

    df_neighbors = df_neighbors.sort_values(
        "SEPARATION_ARCSEC"
    ).reset_index(drop=True)

print("\nNearby PRIMARY_FLAG = 0 sources (within 5 arcminutes):")

if len(df_neighbors) == 0:
    print("None found.")
else:
    print(df_neighbors.to_string(index=False))




# ------------------------------------------------------------
# Print all related table rows
# ------------------------------------------------------------

tables = [
    ("Name_Table", "name_table", "DEFAULT_NAME DESC, NAME"),
    ("Measurement_Table", "measurement_table", "OBSERVATORY, EPOCH, BAND"),
    ("Class_Table", "class_table", "DEFAULT_CLASS DESC, CLASS"),
    ("Period_Table", "period_table", "TYPE, PERIOD"),
]

for label, table_name, order_by in tables:

    print("\n" + "-" * 80)
    print(label)
    print("-" * 80)

    df = pd.read_sql_query(
        f"""
        SELECT *
        FROM {table_name}
        WHERE SOURCE_ID = ?
        ORDER BY {order_by}
        """,
        conn,
        params=(source_id,)
    )

    if len(df) == 0:
        print("No rows found.")
    else:
        print(df.to_string(index=False))

# ------------------------------------------------------------
# Close database
# ------------------------------------------------------------

conn.close()