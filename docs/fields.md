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

## Summary_Table

| Field | Description |
|---|---|
| `SOURCE_ID` | Unique source identifier. There is a many-to-one correspondence between rows and `SOURCE_ID` values in this table. |
| `RA` | Right ascension, in degrees. |
| `DEC` | Declination, in degrees. |
| `NAME` | Default SIMBAD Name. |
| `PORB` | Estimated orbital period. |
| `GAIA_G_MAG` | G-band magnitude from Gaia mission. |
| `RACS_FLUX` | Flux from the RACS survey conducted with the ASKAP telescope. |
| `VLASS_MAX_FLUX` | Flux from the VLASS survey conducted with the VLA telescope. Maximum over epochs.|
| `VLASS_NUM_DETECTIONS` | Number of epochs in which a VLASS flux was detected.|