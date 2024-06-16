import streamlit as st
import pandas as pd
from data_cleaning import DataCleaner  # Assuming DataCleaner class is defined in data_cleaning.py


# Define your main function
def main():
    st.set_page_config(
        page_title="RPHL DATA ANALYSIS APP",
        page_icon='bar_chart',
        layout="wide")

    # Sidebar navigation
    st.sidebar.title('Navigation')
    page = st.sidebar.selectbox('Select Page', ['Data Cleaning', 'Data Visualization'])

    if page == 'Data Cleaning':
        data_cleaning_page()
    elif page == 'Data Visualization':
        data_visualization_page()


def data_cleaning_page():
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
        st.session_state.cleaned_data = data  # Initialize cleaned data with original data

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
        columns_to_delete = col3.multiselect(f"Select columns to delete: {len(data.columns)}", data.columns,
                                             key='delete_columns')
        keywords_to_delete = col4.text_input("Enter words to remove rows with them:", key='delete_rows_keywords')
        keywords_to_delete = [keyword.strip() for keyword in keywords_to_delete.split(',')]
        column_to_extract = col5.multiselect("Select column to extract integers from:", data.columns,
                                             key='extract_integers')

        # Perform data cleaning on button click
        if st.button("Perform Data Cleaning", key='clean_button'):
            if columns_to_delete or keywords_to_delete or column_to_extract:
                cleaner = DataCleaner()
                cleaner.set_data(st.session_state.cleaned_data)  # Set the data for cleaning
                cleaned_data = cleaner.perform_data_cleaning(
                    columns_to_delete,
                    keywords_to_delete,
                    column_to_extract
                )
                st.session_state.cleaned_data = cleaned_data

        # Display modified DataFrame
        col2.write("Modified DataFrame:")
        col2.write(st.session_state.cleaned_data)


def data_visualization_page():
    st.title("Data Visualization")
    if 'cleaned_data' in st.session_state:
        cleaned_data = st.session_state.cleaned_data
        st.write("Cleaned Data:")
        st.write(cleaned_data)
        # Add your data visualization code here using the cleaned_data


# Run the main function
if __name__ == "__main__":
    main()