import streamlit as st
import pandas as pd
from data_cleaning import DataCleaner  # Assuming DataCleaner class is defined in data_cleaning.py


def main():
    st.set_page_config(
        page_title="RPHL DATA ANALYSIS APP",
        page_icon='bar_chart',
        layout="wide")

    st.markdown(
        """
        <style>
        .sidebar .sidebar-content {
            width: 300px;
        }
        .expander-content {
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0px 1px 6px rgba(0, 0, 0, 0.1);
            background-color: #f0f0f0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.image("Time.jpg", width=175)
    st.sidebar.title('Navigation')

    page = st.sidebar.radio('Select Page', ['Order Data Cleaning', 'Income Data Cleaning', 'Merge Cleaned Data'])

    if page == 'Order Data Cleaning':
        data_cleaning_page(data_type='order')
    elif page == 'Income Data Cleaning':
        data_cleaning_page(data_type='income')
    elif page == 'Merge Cleaned Data':
        merge_data_page()


def data_cleaning_page(data_type):
    st.title(f"{data_type.capitalize()} Data Cleaning Tool")

    if data_type == 'order':
        uploaded_file = st.sidebar.file_uploader("Choose a CSV or Excel file for Order Data", type=["csv", "xlsx"],
                                                 key='order_file')
    elif data_type == 'income':
        uploaded_file = st.sidebar.file_uploader("Choose a CSV or Excel file for Income Data", type=["csv", "xlsx"],
                                                 key='income_file')

    if uploaded_file:
        file_extension = uploaded_file.name.split('.')[-1]
        if file_extension.lower() == 'csv':
            data = pd.read_csv(uploaded_file)
        elif file_extension.lower() == 'xlsx':
            data = pd.read_excel(uploaded_file)

        st.session_state[f'{data_type}_data'] = data
        st.session_state[f'cleaned_{data_type}_data'] = data.copy()

        with st.expander("Show Column Names"):
            st.markdown("### Column Names")
            col_names = ", ".join(f"`{col}`" for col in data.columns)
            st.info(f"{col_names}")

        st.markdown(f"### Original {data_type.capitalize()} DataFrame vs Modified DataFrame")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"Original {data_type.capitalize()} DataFrame:")
            st.write(data)

        st.header(f"{data_type.capitalize()} Data Cleaning Options")
        st.write(f"Use the options below to clean the {data_type} data:")
        col3, col4, col5, col6, col7 = st.columns(5)

        # Column-related features
        columns_to_delete = col3.multiselect(f"Select columns to delete:", data.columns,
                                             key=f'delete_{data_type}_columns')
        columns_to_extract = col4.multiselect(f"Select columns to extract integers from:", data.columns,
                                              key=f'extract_{data_type}_integers')

        # Row-related features
        predefined_keywords = ["ml", "add_more"]  # Add more predefined keywords
        keywords_to_delete = col5.multiselect(f"Select words to remove rows with:", predefined_keywords,
                                              key=f'delete_{data_type}_keywords')

        first_n_rows = col6.number_input(f"Enter number of first rows to delete:", min_value=0, value=0,
                                         key=f'delete_{data_type}_first_n_rows')
        last_n_rows = col7.number_input(f"Enter number of last rows to delete:", min_value=0, value=0,
                                        key=f'delete_{data_type}_last_n_rows')

        if st.button(f"Perform {data_type.capitalize()} Data Cleaning", key=f'clean_{data_type}_button'):
            cleaner = DataCleaner()
            cleaner.set_data(st.session_state[f'cleaned_{data_type}_data'])

            # Display the number of instances before data cleaning
            st.write(f"Number of instances before {data_type.capitalize()} Data Cleaning: {len(cleaner.df)}")

            if columns_to_delete:
                cleaner.delete_columns_interactively(columns_to_delete)
            if keywords_to_delete:
                cleaner.delete_rows_by_keyword(keywords_to_delete)
            if columns_to_extract:
                cleaner.extract_integers_from_string(columns_to_extract)
            if first_n_rows > 0:
                cleaner.delete_first_n_rows(first_n_rows)
            if last_n_rows > 0:
                cleaner.delete_last_n_rows(last_n_rows)

            st.session_state[f'cleaned_{data_type}_data'] = cleaner.df

            # Display the number of instances after data cleaning
            st.write(f"Number of instances after {data_type.capitalize()} Data Cleaning: {len(cleaner.df)}")

            with col2:
                st.write(f"Cleaned {data_type.capitalize()} DataFrame:")
                st.write(cleaner.df)


def merge_data_page():
    st.title("Merge Cleaned Data")

    if 'cleaned_order_data' in st.session_state and 'cleaned_income_data' in st.session_state:
        cleaned_order_data = st.session_state['cleaned_order_data']
        cleaned_income_data = st.session_state['cleaned_income_data']

        merge_col = st.selectbox("Select column to merge from Cleaned Order Data:", cleaned_order_data.columns)

        if st.button("Merge DataFrames"):
            merged_data = pd.concat([cleaned_income_data, cleaned_order_data[[merge_col]]], axis=1)

            st.write("Merged DataFrame:")
            st.write(merged_data)
    else:
        st.write("Please clean both Order and Income data first before merging.")


if __name__ == "__main__":
    main()
