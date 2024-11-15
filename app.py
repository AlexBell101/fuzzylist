import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.title("Fuzzy Matching App with Flexible Column Selection and Improved Error Handling")

# File upload widgets
primary_file = st.file_uploader("Upload Primary List CSV", type="csv")
checklist_file = st.file_uploader("Upload Checklist CSV", type="csv")

# Function to read CSV with error handling
def read_csv_file(file):
    try:
        # Attempt to read file with default UTF-8 encoding
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        # Fallback to 'latin1' encoding if UTF-8 fails
        try:
            df = pd.read_csv(file, encoding='latin1')
        except Exception as e:
            st.error(f"Failed to read the file due to encoding issues: {e}")
            return None
    except pd.errors.EmptyDataError:
        st.error("The uploaded file appears to be empty or is not a valid CSV.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while reading the file: {e}")
        return None
    return df

if primary_file and checklist_file:
    # Load primary and checklist files
    primary_df = read_csv_file(primary_file)
    checklist_df = read_csv_file(checklist_file)

    # Ensure files are loaded correctly
    if primary_df is not None and checklist_df is not None:
        # Display data previews
        st.write("Primary List Preview:", primary_df.head())
        st.write("Checklist Preview:", checklist_df.head())

        # Check if dataframes have columns before proceeding
        if not primary_df.columns.empty and not checklist_df.columns.empty:
            # Select columns to use for matching
            primary_column = st.selectbox("Select column from Primary List to match", primary_df.columns)
            checklist_column = st.selectbox("Select column from Checklist to match", checklist_df.columns)

            # Only perform matching if columns are selected
            if primary_column and checklist_column:
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
                primary_names = primary_df[primary_column].astype(str).tolist()
                checklist_names = checklist_df[checklist_column].astype(str).tolist()

                matched_flags, matched_names = fuzzy_match(primary_names, checklist_names, threshold)
                
                # Add match results to primary dataframe
                primary_df['Matched'] = matched_flags
                primary_df['Matched Checklist Name'] = matched_names  # Optional: View matched name
                st.write("Matching Results:", primary_df)

                # Download matched results as CSV
                st.download_button("Download Results", primary_df.to_csv(index=False), "matched_results.csv")
            else:
                st.warning("Please select columns from both the primary and checklist files to match.")
        else:
            st.error("The uploaded files do not contain any columns. Please check the files.")
else:
    st.info("Please upload both the primary list and the checklist CSV files.")
