VLASS_RACS_Update
Overview

VLASS_RACS_Update puts a new source and its associated measurements into an SQLite database.

The program never modifies the master database.  The owner will periodically review additions and update the master database accordingly. The output database file should be sent as a link (e.g., google drive, OneDrive) to the owner at jprenderg@outlook.com.

Requirements
Python 3.11 or later
An OPAL account with access to CASDA
Internet connection
The Python packages listed in requirements.txt

Install the required packages:
pip install -r requirements.txt

Project Structure

VLASS_RACS_Update/
|
+-- update_database.py
+-- config.py
+-- requirements.txt
+-- README.md
|
+-- data/
|   +-- lookup/
|   +-- cache/
|
+-- input/
|   +-- VLASS_RACS_Master.db
|
+-- output/
|   +-- VLASS_RACS_Updated.db
|
+-- source_table/
+-- name_table/
+-- measurement_table/
+-- class_table/
+-- period_table/
|

OPAL / CASDA Login
Some measurements require downloading data from the CASDA archive.
Before running the program, edit config.py and enter your OPAL username:
OPAL_USERNAME = "your_email@example.com"
When the program runs, you will be prompted for your OPAL password in the terminal or console.
Your password is never stored by this project.

Running the Program
Open update_database.py.
Near the beginning of the file is a section labelled User Inputs.
Enter the information for the source you wish to add, including:

Right Ascension (RA)
Declination (Dec)
Orbital period (optional)
Orbital period uncertainty (optional)
Spin period (optional)
Spin period uncertainty (optional)

Run the program:
python update_database.py

The program:
Creates new entries for:
Source Table
Name Table
Measurement Table
Class Table
Period Table
Appends the new records to:
output/VLASS_RACS_Updated.db

New SOURCE_ID values are assigned automatically.

Database Schema
Content of tables and field descriptions are listed in database_schema.md.

Output
After the program finishes, the update to the database is located at:
output/VLASS_RACS_Updated.db

Cache
Downloaded CASDA files are stored in:
data/cache/casda/
This cache allows previously downloaded files to be reused, reducing download time on future runs.