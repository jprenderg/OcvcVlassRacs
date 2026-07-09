Source_Table fields:
SOURCE_ID (unique id – one to one correspondence between rows and SOURCE_ID in this table)
PRIMARY_FLAG (1 if primary source; 0 if radio-loud nearby neighbor. Identified neighbors are all sources with at least one ASKAP/VLASS observation >= 1 mJy and within 5 arcminutes of a primary source)
RA (deg)
DEC (deg) 
MAJOR_AXIS (major axis of the coordinate uncertainty ellipse; arcseconds)
MINOR_AXIS  (minor axis of the coordinate uncertainty ellipse; arcseconds)
POSITION ANGLE  (position angle of the major axis; deg)
DISTANCE (kpc)
DISTANCE_ERROR (kpc)

Name_Table fields:
SOURCE_ID (unique id – many to one correspondence between rows and SOURCE_ID in this table)
NAME (SIMBAD_NAME)
DEFAULT_NAME (1 if SIMBAD default name; 0 for alternate names)

Measurement_Table fields:
SOURCE_ID (unique id – many to one correspondence between rows and SOURCE_ID in this table)
OBSERVATORY (self-explanatory)
EPOCH (epoch or catalog if applicable)
BAND (frequency band)
UNITS (self-explanatory)
MEASUREMENT (self-explanatory)
ERROR (self-explanatory)
POS_ERROR (positive error if errors are asymmetric)
NEG_ERROR (negative error if errors are asymmetric)

Class_Table fields:
SOURCE_ID (unique id – many to one correspondence between rows and SOURCE_ID in this table)
CLASS (SIMBAD class)
DEFAULT_CLASS (1 if SIMBAD default class; 0 for alternate names)

Period_Table fields:
SOURCE_ID (unique id – many to one correspondence between rows and SOURCE_ID in this table)
TYPE (spin or orbital)
UNITS (self-explanatory)
PERIOD (self-explanatory)
PERIOD_ERROR (self-explanatory)

# Catalog Fields

This page summarizes the fields included in the OCVC VLASS/RACS catalog database tables.

## Source_Table

| Field | Description |
|---|---|
| `SOURCE_ID` | Unique source identifier. There is a one-to-one correspondence between rows and `SOURCE_ID` values in this table. |
| `PRIMARY_FLAG` | `1` if the source is a primary catalog source; `0` if the source is a radio-loud nearby neighbor. Identified neighbors are sources with at least one ASKAP/VLASS observation >= 1 mJy and within 5 arcminutes of a primary source. |
| `RA` | Right ascension, in degrees. |
| `DEC` | Declination, in degrees. |
| `MAJOR_AXIS` | Major axis of the coordinate uncertainty ellipse, in arcseconds. |
| `MINOR_AXIS` | Minor axis of the coordinate uncertainty ellipse, in arcseconds. |
| `POSITION_ANGLE` | Position angle of the major axis, in degrees. |
| `DISTANCE` | Distance, in kpc. |
| `DISTANCE_ERROR` | Distance error, in kpc. |

## Name_Table

| Field | Description |
|---|---|
| `SOURCE_ID` | Unique source identifier. There is a many-to-one correspondence between rows and `SOURCE_ID` values in this table. |
| `NAME` | Source name, usually the SIMBAD name. |
| `DEFAULT_NAME` | `1` if this is the default SIMBAD name; `0` for alternate names. |

## Measurement_Table

| Field | Description |
|---|---|
| `SOURCE_ID` | Unique source identifier. There is a many-to-one correspondence between rows and `SOURCE_ID` values in this table. |
| `OBSERVATORY` | Observatory associated with the measurement. |
| `EPOCH` | Epoch or catalog, if applicable. |
| `BAND` | Frequency band or observing band. |
| `UNITS` | Measurement units. |
| `MEASUREMENT` | Measurement value. |
| `ERROR` | Measurement error, when a symmetric error is available. |
| `POS_ERROR` | Positive error, when errors are asymmetric. |
| `NEG_ERROR` | Negative error, when errors are asymmetric. |

## Class_Table

| Field | Description |
|---|---|
| `SOURCE_ID` | Unique source identifier. There is a many-to-one correspondence between rows and `SOURCE_ID` values in this table. |
| `CLASS` | SIMBAD source class. |
| `DEFAULT_CLASS` | `1` if this is the default SIMBAD class; `0` for alternate classes. |

## Period_Table

| Field | Description |
|---|---|
| `SOURCE_ID` | Unique source identifier. There is a many-to-one correspondence between rows and `SOURCE_ID` values in this table. |
| `TYPE` | Period type, usually spin or orbital. |
| `UNITS` | Period units. |
| `PERIOD` | Period value. |
| `PERIOD_ERROR` | Period error. |