import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.title("Fuzzy Matching App with Visible Matching Quality Slider")

# File upload widgets
primary_file = st.file_uploader("Upload Primary List CSV", type="csv")
checklist_file = st.file_uploader("Upload Checklist CSV", type="csv")

# Function to read CSV files with specified encoding
def read_csv_file(file, header_option='infer', encoding='utf-8'):
    try:
        df = pd.read_csv(file, encoding=encoding, header=header_option)
    except UnicodeDecodeError:
        st.warning("UTF-8 encoding failed. Trying 'latin1' encoding...")
        try:
            df = pd.read_csv(file, encoding='latin1', header=header_option)
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
    # Load primary and checklist files with 'latin1' encoding as needed
    primary_df = read_csv_file(primary_file, header_option=0, encoding='latin1')
    checklist_df = read_csv_file(checklist_file, header_option=0, encoding='utf-8')  # Assuming checklist uses 'utf-8'

    # Ensure files are loaded correctly
    if primary_df is not None and checklist_df is not None:
        # Display data previews
        st.write("Primary List Preview:", primary_df.head())
        st.write("Checklist Preview:", checklist_df.head())

        # Check if DataFrames have columns before proceeding
        if not primary_df.columns.empty and not checklist_df.columns.empty:
            # Use only string representation for column names to avoid issues
            primary_columns = primary_df.columns.astype(str)
            checklist_columns = checklist_df.columns.astype(str)

            # Select columns to use for matching
            primary_column = st.selectbox("Select column from Primary List to match", primary_columns)
            checklist_column = st.selectbox("Select column from Checklist to match", checklist_columns)

            # Slider for setting matching threshold (moved outside button condition)
            threshold = st.slider("Set Matching Quality Threshold", 0, 100, 80)

            # Button to trigger matching
            if st.button("Run Matching"):
                # Ensure selected columns are not empty
                if primary_df[primary_column].notna().any() and checklist_df[checklist_column].notna().any():
                    # Convert columns to string and clean up missing values
                    primary_names = primary_df[primary_column].astype(str).fillna("").tolist()
                    checklist_names = checklist_df[checklist_column].astype(str).fillna("").tolist()

                    # Debug: Print sample data for validation
                    st.write("Sample of primary names:", primary_names[:5])
                    st.write("Sample of checklist names:", checklist_names[:5])

                    # Function to perform fuzzy matching with enhanced tuple handling
                    def fuzzy_match(primary_names, checklist_names, threshold=80):
                        matched_flags = []
                        matched_names = []
                        for name in primary_names:
                            # Clean and validate the input string
                            if not isinstance(name, str) or name.strip() == "":
                                matched_flags.append("Not Matched")
                                matched_names.append(None)
                                continue
                            try:
                                # Extract match and handle cases with variable tuple sizes
                                match_result = process.extractOne(name, checklist_names, scorer=fuzz.ratio)
                                if match_result:
                                    match = match_result[0]  # Get the matched string
                                    score = match_result[1]  # Get the score
                                    if len(match_result) > 2:
                                        st.write(f"Additional metadata detected for '{name}': {match_result[2:]}")
                                    if score >= threshold:
                                        matched_flags.append("Matched")
                                        matched_names.append(match)  # Store matched name
                                    else:
                                        matched_flags.append("Not Matched")
                                        matched_names.append(None)
                                else:
                                    matched_flags.append("Not Matched")
                                    matched_names.append(None)
                            except Exception as e:
                                st.error(f"Error during matching for '{name}': {e}")
                                matched_flags.append("Error")
                                matched_names.append(None)
                        return matched_flags, matched_names

                    st.write("Performing fuzzy matching...")

                    # Perform fuzzy matching
                    matched_flags, matched_names = fuzzy_match(primary_names, checklist_names, threshold)
                    
                    # Add match results to primary dataframe
                    primary_df['Matched'] = matched_flags
                    primary_df['Matched Checklist Name'] = matched_names  # Optional: View matched name
                    st.write("Matching Results:", primary_df)

                    # Download matched results as CSV
                    st.download_button("Download Results", primary_df.to_csv(index=False), "matched_results.csv")
                else:
                    st.error("Selected columns contain no data to match. Please check your data.")
            else:
                st.info("Click 'Run Matching' to start the matching process.")
        else:
            st.error("The uploaded files do not contain any columns. Please check the files.")
else:
    st.info("Please upload both the primary list and the checklist CSV files.")
