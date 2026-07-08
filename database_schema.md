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

