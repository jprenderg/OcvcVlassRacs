# OCVC VLASS/RACS Catalog

The **OCVC VLASS/RACS Catalog** is a database of radio observations of known and candidate cataclysmic variables (CVs). It combines measurements from the **Very Large Array Sky Survey (VLASS)** and the **Rapid ASKAP Continuum Survey (RACS)** together with supplementary measurements from major optical, infrared, ultraviolet, X-ray, and astrometric surveys.

This repository contains:

- The OCVC VLASS/RACS catalog database.
- A CSV version of the Source Table.
- Python software for adding new sources to the catalog.
- Documentation describing the catalog and its database schema.

---

## Documentation

Complete documentation is provided in the docs/ directory and is published through the GitHub Pages site:

**https://jprenderg.github.io/OcvcVlassRacs/**

The documentation includes:

- Catalog overview
- Database field definitions
- Download instructions
- Catalog update instructions

---

## Downloads

The latest catalog data products include:

- SQLite database
- Source Table (CSV)

See the **Downloads** page in the documentation for the latest files.

---

## Updating the Catalog

The repository includes a Python utility for adding new sources and their associated measurements to the catalog.

The update utility never modifies the master database. Instead, new records are written to an output database for review by the catalog maintainer.

Complete instructions are provided in the **Updating the Catalog** section of the documentation.

---

## Repository Structure

```text
OcvcVlassRacs/
│
├── docs/                  Documentation website
│
├── downloads/
│   ├── OcvcVlassRacs.sqlite
│   └── OcvcVlassRacs_Source_Table.csv
│
├── input/                 Master catalog database
│
├── output/                Updated database created by the update utility
│
├── data/
│   ├── lookup/            Lookup tables
│   └── cache/             CASDA download cache
│
├── source_table/          Source table generation
├── measurement_table/     Measurement table generation
├── name_table/            Name table generation
├── class_table/           Class table generation
├── period_table/          Period table generation
│
├── update_database.py     Main update program
├── config.py              User configuration
├── requirements.txt       Python package requirements
├── mkdocs.yml             MkDocs configuration
└── README.md
```

---

## Citation

If you use the OCVC VLASS/RACS Catalog in your research, please cite the accompanying publication.