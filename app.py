import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.title("Fuzzy Matching App - Improved File Handling and Parsing")

# File upload widgets
primary_file = st.file_uploader("Upload Primary List CSV (with Account Name, Owner, Region, and SFDC ID)", type="csv")
checklist_file = st.file_uploader("Upload Checklist CSV (with Account Name only)", type="csv")

# Function to read CSV with error handling
def read_csv_file(file, expected_columns=None):
    try:
        # Attempt to read file with default UTF-8 encoding
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        # Fallback to 'latin1' encoding if UTF-8 fails
        try:
            df = pd.read_csv(file, encoding='latin1')
        except Exception as e:
            st.error(f"Failed to read the file. Encoding issues encountered: {e}")
            return None
    except pd.errors.EmptyDataError:
        st.error("The uploaded file is empty or not a valid CSV.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while reading the file: {e}")
        return None

    # Check if expected columns are present, if provided
    if expected_columns:
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.error(f"The following required columns are missing from the uploaded file: {missing_columns}")
            return None

    return df

if primary_file and checklist_file:
    # Expected columns for validation
    primary_columns = ['Account Name', 'Account Owner', 'Sales Region', 'SFDC Account ID']
    checklist_columns = ['Account Name']

    # Read primary and checklist files with expected column validation
    primary_df = read_csv_file(primary_file, expected_columns=primary_columns)
    checklist_df = read_csv_file(checklist_file, expected_columns=checklist_columns)

    # Ensure files are loaded correctly
    if primary_df is not None and checklist_df is not None:
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

        primary_names = primary_df['Account Name'].tolist()
        checklist_names = checklist_df['Account Name'].tolist()

        matched_flags, matched_names = fuzzy_match(primary_names, checklist_names, threshold)
        
        # Add match results to primary dataframe
        primary_df['Matched'] = matched_flags
        primary_df['Matched Checklist Name'] = matched_names  # Optional: View matched name
        st.write("Matching Results:", primary_df)

        # Download matched results as CSV
        st.download_button("Download Results", primary_df.to_csv(index=False), "matched_results.csv")
else:
    st.info("Please upload both the primary list and the checklist CSV files.")
