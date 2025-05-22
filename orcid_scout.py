from ctypes import alignment
import streamlit as st
import pandas as pd
import requests
import time

# Page config
st.set_page_config(page_title="ORCID Scout", layout="centered")

# Title

st.markdown("""
<div style='text-align: center;'>
    <h1 style='margin-top: 0;'>ORCID Scout</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; font-size: 1.1rem; color: gray;'>Use Scopus Author IDs to find and verify ORCID iDs</p>", unsafe_allow_html=True)

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Scopus API Key", type="password")
    target_ror = st.text_input("Institution ROR ID (optional)", placeholder="https://ror.org/03yrm5c26")
    st.markdown("---")
    st.markdown("🔗 [Scopus API Rate Limits](https://dev.elsevier.com/api_key_settings.html)", unsafe_allow_html=True)
    st.image("orcid_scout_logo.png", width=200)

# Description and instructions
with st.expander("ℹ️ About this tool"):
    st.markdown("""
    **Purpose:**
    ORCID Scout helps identify missing ORCID iDs in internal systems by using known **Scopus Author IDs**. It also verifies if the ORCID profile lists an affiliation with a specific institution, using a **ROR ID**.

    **🔧 How to use it:**
    1. Enter a Scopus API key
    2. Enter the ROR ID of the institution (optional)
    3. Upload a CSV or Excel file with Scopus Author IDs
    4. Click **Start Lookup**

    ⚠️ ORCID iDs from Scopus are not always correct. Verify results before importing into internal systems — preferably with the researcher.
    """)

# File upload
uploaded_file = st.file_uploader("Upload a CSV or Excel file with Scopus Author IDs", type=["csv", "xlsx"])

def check_orcid_affiliation(orcid_url, target_ror):
    orcid_id = orcid_url.split("/")[-1]
    target_ror = target_ror.strip().lower()
    url = f"https://pub.orcid.org/v3.0/{orcid_id}"
    headers = {"Accept": "application/json"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return "Error"
        data = r.json()
        employments = data.get("activities-summary", {}).get("employments", {})
        affiliation_groups = employments.get("affiliation-group") or []
        if not affiliation_groups:
            return "No employment data"
        for group in affiliation_groups:
            summaries = group.get("summaries", [])
            for summary_container in summaries:
                summary = summary_container.get("employment-summary", {})
                org = summary.get("organization", {})
                disamb = org.get("disambiguated-organization", {})
                if disamb.get("disambiguation-source") == "ROR":
                    ror_id = disamb.get("disambiguated-organization-identifier", "").strip().lower()
                    if ror_id == target_ror:
                        return "✔️ Yes"
        return "❌ No"
    except Exception:
        return "Error"

if uploaded_file and api_key and target_ror:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    author_id_column = st.selectbox("Select the column with Scopus Author IDs", df.columns)

    if st.button("🔍 Start Lookup"):
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, row in df.iterrows():
            author_id = row[author_id_column]
            url = f"https://api.elsevier.com/content/author?author_id={author_id}&apiKey={api_key}"
            headers = {"Accept": "application/json"}

            orcid = None
            full_name = None
            affiliation_status = "Not checked"

            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    profile = data.get('author-retrieval-response', [{}])[0]
                    full_name = profile.get('author-profile', {}).get('preferred-name', {}).get('indexed-name')
                    orcid_raw = profile.get('coredata', {}).get('orcid')
                    orcid = f"https://orcid.org/{orcid_raw}" if orcid_raw else None

                    if orcid:
                        affiliation_status = check_orcid_affiliation(orcid, target_ror)
                else:
                    full_name = f"Error {response.status_code}"
            except Exception as e:
                full_name = "Error"
                orcid = f"Exception: {str(e)}"

            results.append({
                "author_id": author_id,
                "name": full_name,
                "orcid": orcid if orcid else "Not found",
                "affiliated": affiliation_status
            })

            progress_bar.progress((i + 1) / len(df))
            status_text.text(f"Processed {i + 1} of {len(df)}")
            time.sleep(0.34)  # 3 requests per second

        results_df = pd.DataFrame(results)

        # Render results as HTML table
        st.success("✅ Lookup completed!")
        st.markdown("### Results")

        table_html = """
        <table>
            <thead>
                <tr>
                    <th>Author ID</th>
                    <th>Name</th>
                    <th>ORCID</th>
                    <th>Affiliated to institution (via ROR ID)</th>
                </tr>
            </thead>
            <tbody>
        """

        for _, row in results_df.iterrows():
            author_id = row["author_id"]
            name = row["name"]
            orcid = row["orcid"]
            affiliated = row["affiliated"]

            if isinstance(orcid, str) and orcid.startswith("https://orcid.org/"):
                orcid_link = f'<a href="{orcid}" target="_blank">{orcid}</a>'
            else:
                orcid_link = orcid

            table_html += f"<tr><td>{author_id}</td><td>{name}</td><td>{orcid_link}</td><td>{affiliated}</td></tr>"

        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)

        # Download as CSV
        csv = results_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Results as CSV", csv, file_name="orcid_scout_results.csv", mime="text/csv")

# Footer 
st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 0.9rem; line-height: 1.6;'>
    <p><strong>Created by Søren Vidmar</strong></p>
    <p>
        🔗 <a href='https://orcid.org/0000-0003-3055-6053' target='_blank'>ORCID</a> |
        🏫 Aalborg University |
        📧 <a href='mailto:sv@aub.aau.dk'>sv@aub.aau.dk</a> |
        🏗 <a href='https://github.com/svidmar' target='_blank'>GitHub</a>
    </p>
</div>
""", unsafe_allow_html=True)        
