from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd
import gc
import sys

from config import INPUT_DB, OUTPUT_DB

from source_table.python.MAXID import maxid
from source_table.python.VLASS_NEIGHBORS import vlass_neighbors
from source_table.python.RACS_NEIGHBORS import racs_neighbors
from source_table.python.ADD_SIMBAD_FIELDS import add_simbad_fields

from name_table.python.NAME import name

from measurement_table.python.VLASS import vlass
from measurement_table.python.RACS import racs
from measurement_table.python.TMASS import tmass
from measurement_table.python.GAIA import gaia
from measurement_table.python.GALEX import galex
from measurement_table.python.CHANDRA import chandra
from measurement_table.python.ROSAT import rosat
from measurement_table.python.XMM import xmm

from class_table.python.CLASS import source_class


# ------------------------------------------------------------
# User inputs
# ------------------------------------------------------------

ra = 245.4470133276900
dec = -22.8862182469700

PORB = None
PORB_ERR = None

PSPIN = None
PSPIN_ERR = None


# ------------------------------------------------------------
# Prepare output database
# ------------------------------------------------------------

if not INPUT_DB.exists():
    raise FileNotFoundError(f"Input database not found: {INPUT_DB}")

OUTPUT_DB.parent.mkdir(parents=True, exist_ok=True)

if OUTPUT_DB.exists():
    OUTPUT_DB.unlink()

db_path = OUTPUT_DB

print("Created new updates-only database:")
print(f"  {OUTPUT_DB}")


# ------------------------------------------------------------
# Source Table
# ------------------------------------------------------------

primary_source_id = maxid() + 1

df_primary = pd.DataFrame({
    "PRIMARY_FLAG": [True],
    "RA": [ra],
    "DEC": [dec],
})

df_vlass_neighbors = vlass_neighbors(ra, dec)
df_vlass_neighbors["PRIMARY_FLAG"] = False

df_racs_neighbors = racs_neighbors(ra, dec)
df_racs_neighbors["PRIMARY_FLAG"] = False

df_source_interm = pd.concat(
    [df_primary, df_vlass_neighbors, df_racs_neighbors],
    ignore_index=True,
)

df_source = add_simbad_fields(df_source_interm)

df_source = df_source.dropna(subset=["SIMBAD_NAME"]).reset_index(drop=True)

mask_duplicate_neighbor = (
    (df_source["PRIMARY_FLAG"] == False)
    & df_source.duplicated(subset="SIMBAD_NAME", keep="first")
)

df_source = df_source.loc[~mask_duplicate_neighbor].reset_index(drop=True)


# ------------------------------------------------------------
# Remove neighbors already present in input database
# ------------------------------------------------------------

conn = sqlite3.connect(INPUT_DB)

try:
    df_current_names = pd.read_sql_query(
        """
        SELECT s.PRIMARY_FLAG, n.NAME
        FROM source_table AS s
        JOIN name_table AS n
            ON s.SOURCE_ID = n.SOURCE_ID
        WHERE s.PRIMARY_FLAG = 0
          AND n.DEFAULT_NAME = 1
        """,
        conn,
    )

finally:
    conn.close()

current_names = df_current_names["NAME"].dropna()

mask_existing_neighbor = (
    (df_source["PRIMARY_FLAG"] == False)
    & df_source["SIMBAD_NAME"].isin(current_names)
)

df_source = df_source.loc[~mask_existing_neighbor].reset_index(drop=True)

df_source["SOURCE_ID"] = np.arange(
    primary_source_id,
    primary_source_id + len(df_source),
)

df_source_for_name = df_source.copy()

df_source = df_source.drop(columns=["SIMBAD_NAME"])

print(f"New source rows: {len(df_source)}")


# ------------------------------------------------------------
# Name Table
# ------------------------------------------------------------

df_name = name(df_source_for_name)

print(f"New name rows: {len(df_name)}")


# ------------------------------------------------------------
# Measurement Table
# ------------------------------------------------------------

df_vlass_1 = pd.DataFrame()
df_vlass_23 = pd.DataFrame()
df_racs = pd.DataFrame()

for _, row in df_source.iterrows():

    source_id = row["SOURCE_ID"]
    ra_source = row["RA"]
    dec_source = row["DEC"]

    df_temp = vlass(1, source_id, ra_source, dec_source)
    df_vlass_1 = pd.concat([df_vlass_1, df_temp], ignore_index=True)

    df_temp = vlass(23, source_id, ra_source, dec_source)
    df_vlass_23 = pd.concat([df_vlass_23, df_temp], ignore_index=True)

    df_temp = racs(source_id, ra_source, dec_source)
    df_racs = pd.concat([df_racs, df_temp], ignore_index=True)

df_vlass = pd.concat([df_vlass_1, df_vlass_23], ignore_index=True)

df_primary_new = df_source[df_source["PRIMARY_FLAG"] == True].copy()

if len(df_primary_new) > 0:

    primary_row = df_primary_new.iloc[0]

    primary_id = primary_row["SOURCE_ID"]
    primary_ra = primary_row["RA"]
    primary_dec = primary_row["DEC"]

    df_tmass = tmass(primary_id, primary_ra, primary_dec)
    df_gaia = gaia(primary_id, primary_ra, primary_dec)
    df_galex = galex(primary_id, primary_ra, primary_dec)
    df_chandra = chandra(primary_id, primary_ra, primary_dec)
    df_rosat = rosat(primary_id, primary_ra, primary_dec)
    df_xmm = xmm(primary_id, primary_ra, primary_dec)

else:

    df_tmass = pd.DataFrame()
    df_gaia = pd.DataFrame()
    df_galex = pd.DataFrame()
    df_chandra = pd.DataFrame()
    df_rosat = pd.DataFrame()
    df_xmm = pd.DataFrame()

df_measurement = pd.concat(
    [
        df_vlass,
        df_racs,
        df_tmass,
        df_gaia,
        df_galex,
        df_chandra,
        df_rosat,
        df_xmm,
    ],
    ignore_index=True,
)

df_measurement = df_measurement.rename(columns={"CAT": "EPOCH"})

print(f"New measurement rows: {len(df_measurement)}")


# ------------------------------------------------------------
# Class Table
# ------------------------------------------------------------

if len(df_primary_new) > 0:
    df_class = source_class(primary_id, primary_ra, primary_dec)
else:
    df_class = pd.DataFrame()

print(f"New class rows: {len(df_class)}")


# ------------------------------------------------------------
# Period Table
# ------------------------------------------------------------

if len(df_primary_new) > 0:

    df_period = pd.DataFrame({
        "SOURCE_ID": [primary_id, primary_id],
        "TYPE": ["Orbital", "Spin"],
        "UNITS": ["Hours", "Seconds"],
        "PERIOD": [PORB, PSPIN],
        "PERIOD_ERROR": [PORB_ERR, PSPIN_ERR],
    })

else:

    df_period = pd.DataFrame(
        columns=[
            "SOURCE_ID",
            "TYPE",
            "UNITS",
            "PERIOD",
            "PERIOD_ERROR",
        ]
    )

print(f"New period rows: {len(df_period)}")


# ------------------------------------------------------------
# Add only new rows to output database
# ------------------------------------------------------------

tables = {
    "source_table": df_source,
    "name_table": df_name,
    "measurement_table": df_measurement,
    "class_table": df_class,
    "period_table": df_period,
}

conn = sqlite3.connect(db_path)

try:
    for table_name, df in tables.items():

        df = df.replace({np.nan: None})

        if len(df) == 0:
            print(f"Skipping {table_name}: no rows")
            continue

        df.to_sql(
            table_name,
            conn,
            if_exists="append",
            index=False,
        )

        print(f"Appended {len(df)} rows to {table_name}")

    conn.commit()

finally:
    conn.close()


# ------------------------------------------------------------
# Final cleanup
# ------------------------------------------------------------

gc.collect()

print("Update complete.")
print(f"Updated database written to: {OUTPUT_DB}")

sys.exit()