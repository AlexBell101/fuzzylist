import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.title("Fuzzy Matching App - Enhanced File Handling and Parsing")

# File upload widgets
primary_file = st.file_uploader("Upload Primary List CSV (with Account Name, Owner, Region, and SFDC ID)", type="csv")
checklist_file = st.file_uploader("Upload Checklist CSV (with Account Name only)", type="csv")

# Function to read CSV with error handling
def read_csv_file(file):
    try:
        # Read CSV, assuming there is a header; if none, infer columns
        df = pd.read_csv(file, encoding='utf-8', on_bad_lines='skip')
        if df.empty:
            st.warning("The uploaded file is empty. Please upload a valid CSV file.")
            return None
        return df
    except UnicodeDecodeError:
        st.warning("UTF-8 encoding failed. Trying 'latin1' encoding...")
        try:
            df = pd.read_csv(file, encoding='latin1', on_bad_lines='skip')
            if df.empty:
                st.warning("The uploaded file is empty or unreadable. Please check the file.")
                return None
            return df
        except Exception as e:
            st.error(f"Failed to read the file with 'latin1' encoding. Error: {e}")
            return None
    except pd.errors.EmptyDataError:
        st.error("The uploaded file appears to have no data or is not a valid CSV.")
        return None
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        return None

if primary_file and checklist_file:
    # Read primary and checklist files
    primary_df = read_csv_file(primary_file)
    checklist_df = read_csv_file(checklist_file)

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

        # Check if 'Account Name' column exists in both DataFrames
        if 'Account Name' in primary_df.columns and 'Account Name' in checklist_df.columns:
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
            st.error("One or both files are missing the required 'Account Name' column.")
else:
    st.info("Please upload both the primary list and the checklist CSV files.")
