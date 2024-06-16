import streamlit as st
import pandas as pd

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'intermediate_data' not in st.session_state:
    st.session_state.intermediate_data = None


@st.cache_data
def delete_columns_interactively(df, columns_to_delete):
    valid_columns = [col for col in columns_to_delete if col in df.columns]
    return df.drop(columns=valid_columns, axis=1)


@st.cache_data
def delete_rows_by_keyword(df, keywords):
    mask = df.apply(lambda row: any(keyword.lower() in str(row.values).lower() for keyword in keywords), axis=1)
    return df[~mask]


@st.cache_data
def extract_integers_from_string(df, columns):
    for col in columns:
        df[col] = df[col].astype(str).str.extract(r'(\d+)', expand=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


@st.cache_data
def perform_data_cleaning(df, columns_to_delete, keywords_to_delete, columns_to_extract):
    # Delete columns
    df_cleaned = delete_columns_interactively(df, columns_to_delete)

    # Delete rows by keywords
    df_cleaned = delete_rows_by_keyword(df_cleaned, keywords_to_delete)

    # Extract integers from string columns
    df_cleaned = extract_integers_from_string(df_cleaned, columns_to_extract)

    return df_cleaned


def main():
    st.set_page_config(
        page_title="RPHL DATA ANALYSIS APP",
        page_icon='bar_chart',
        layout="wide")
    st.title("Data Cleaning Tool")
    st.sidebar.image("Time.jpg", width=175)
    uploaded_file = st.sidebar.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file:
        file_extension = uploaded_file.name.split('.')[-1]
        if file_extension.lower() == 'csv':
            data = pd.read_csv(uploaded_file)
        elif file_extension.lower() == 'xlsx':
            data = pd.read_excel(uploaded_file)

        st.session_state.data = data
        st.session_state.intermediate_data = data

        st.markdown("### Original DataFrame vs Modified DataFrame")

        # Create columns for original and modified dataframes
        col1, col2 = st.columns(2)

        # Display original DataFrame
        with col1:
            st.write("Original DataFrame:")
            st.write(data)

        # Create UI for cleaning options side by side
        st.header("Data Cleaning Options")
        st.write("Use the options below to clean the data:")
        col3, col4, col5 = st.columns(3)
        columns_to_delete = col3.multiselect(f"Select columns to delete: {len(data.columns)}", data.columns, key='delete_columns')
        keywords_to_delete = col4.text_input("Enter words to remove rows with them:", key='delete_rows_keywords')
        keywords_to_delete = [keyword.strip() for keyword in keywords_to_delete.split(',')]
        column_to_extract = col5.multiselect("Select column to extract integers from:", data.columns,
                                             key='extract_integers')

        # Perform data cleaning
        if st.button("Perform Data Cleaning", key='clean_button'):
            if columns_to_delete or keywords_to_delete or column_to_extract:
                st.session_state.intermediate_data = perform_data_cleaning(
                    st.session_state.intermediate_data,
                    columns_to_delete,
                    keywords_to_delete,
                    column_to_extract
                )

        # Display modified DataFrame
        col2.write("Modified DataFrame:")
        col2.write(st.session_state.intermediate_data)


if __name__ == "__main__":
    main()
