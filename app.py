import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.title("Fuzzy Matching App - Primary and Checklist Matching")

# File upload widgets
primary_file = st.file_uploader("Upload Primary List CSV (with Account Name, Owner, Region, and SFDC ID)", type="csv")
checklist_file = st.file_uploader("Upload Checklist CSV (with Account Name only)", type="csv")

if primary_file and checklist_file:
    # Read uploaded files into dataframes
    primary_df = pd.read_csv(primary_file)
    checklist_df = pd.read_csv(checklist_file)

    # Display data previews
    st.write("Primary List Preview:", primary_df.head())
    st.write("Checklist Preview:", checklist_df.head())

    # Set matching threshold
    threshold = st.slider("Set Similarity Threshold", 0, 100, 80)

    # Function to perform fuzzy matching
    def fuzzy_match(primary_names, checklist_names, threshold=80):
        matched_flags = []
        matched_names = []
        for name in primary_names:
            match, score = process.extractOne(name, checklist_names, scorer=fuzz.ratio)
            if score >= threshold:
                matched_flags.append("Matched")
                matched_names.append(match)  # Optional: Store matched name
            else:
                matched_flags.append("Not Matched")
                matched_names.append(None)
        return matched_flags, matched_names

    st.write("Performing fuzzy matching...")

    # Perform fuzzy matching
    primary_names = primary_df['Account Name'].tolist()
    checklist_names = checklist_df['Account Name'].tolist()

    matched_flags, matched_names = fuzzy_match(primary_names, checklist_names, threshold)
    
    # Add match results to primary dataframe
    primary_df['Matched'] = matched_flags
    primary_df['Matched Checklist Name'] = matched_names  # Optional: View matched name
    st.write("Matching Results:", primary_df)

    # Download matched results as CSV
    st.download_button("Download Results", primary_df.to_csv(index=False), "matched_results.csv")
