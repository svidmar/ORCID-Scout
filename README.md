# ORCID Scout
<img src="orcid_scout_logo.png" alt="ORCID Scout logo" width="200"/>

ORCID Scout is a Streamlit application designed to identify ORCID iDs based on Scopus Author IDs and verify institutional affiliation using a ROR ID.

## Features

- Upload a CSV or Excel file containing Scopus Author IDs
- Retrieve ORCID iDs using the Scopus API
- Check institutional affiliation based on ROR ID via the ORCID Public API
- Export results as a CSV

## Requirements

- Python 3.8 or higher
- Scopus API key
- Required Python packages:

```bash
pip install streamlit pandas requests
```
## Access Notes

To use this tool, you must have:

- An active **Scopus subscription**
- A valid **Scopus API key** from [Elsevier Developer Portal](https://dev.elsevier.com/)
- Access to the Scopus API from a **whitelisted IP address** (typically your institution’s IP range)

## Usage

1. Run the app locally:

```bash
streamlit run orcid_scout.py
```

2. Open your browser at `http://localhost:8501`

## Input File Format

The input file must contain a column with Scopus Author IDs. Example:

```
author_id
57431700700
7004212771
57188837200
```

## Output

The app will display a table with:
- Scopus Author ID
- Name (from Scopus)
- ORCID iD (if found)
- Affiliation match (Yes/No) based on the provided ROR ID

Results can be downloaded as a CSV file.

## Notes

- The tool respects a maximum of 3 requests per second to the Scopus API, however note the weekly quota.
- The ORCID iDs retrieved from Scopus may not always be accurate. Manual verification is recommended.
- ORCID best practice: Don’t write ORCID iDs directly to your system. Instead, nudge researchers to register and authenticate their ORCID via your system using the ORCID OAuth process to ensure accuracy, avoid misattribution, and gain permission to update their record.

## Author

Søren Vidmar  
Aalborg University  
Email: sv@aub.aau.dk  
ORCID: https://orcid.org/0000-0003-3055-6053  
GitHub: https://github.com/svidmar
