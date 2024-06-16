import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui

st.set_page_config(layout="wide")


# Function to load data
@st.cache_data
def load_data(file):
    data = pd.read_csv(file)
    data = data.iloc[1:]  # Remove the first row
    return data


# Function to clean Variation column by removing specific rows
def clean_variation(data):
    keywords_to_delete = ['vco30', 'vco50', 'so30', 'so50']
    pattern = '|'.join(keywords_to_delete)
    data = data[~data['Seller SKU'].str.contains(pattern, case=False, na=False)]
    # Remove non-numeric characters and convert to numeric
    data['Variation'] = data['Variation'].str.extract('(\d+)').fillna(0).astype(int)
    return data


# Function to remove cancelled orders
def remove_cancelled_orders(data):
    data = data[~data['Cancelation/Return Type'].str.contains('cancel', case=False, na=False)]
    return data


# Function to count repeated customers
def count_repeated_customers(data):
    customer_counts = data['Buyer Username'].value_counts()
    repeated_customers = customer_counts[customer_counts > 1]
    return repeated_customers


# Function to plot purchase trends over time
def plot_purchase_trends(data):
    data['Created Time'] = pd.to_datetime(data['Created Time'], format="%d/%m/%Y %H:%M:%S", dayfirst=True).dt.to_period(
        'M')
    purchase_trends = data.groupby('Created Time').size().reset_index(name='Purchases')
    purchase_trends['Created Time'] = purchase_trends['Created Time'].astype(str)
    st.line_chart(purchase_trends, x='Created Time', y='Purchases', use_container_width=True)


# Function to plot purchase frequency chart
def plot_purchase_frequency(data, repeated_customers):
    purchase_frequency = data[data['Buyer Username'].isin(repeated_customers.index)][
        'Buyer Username'].value_counts().reset_index()
    purchase_frequency.columns = ['Buyer Username', 'Frequency']
    st.bar_chart(purchase_frequency.set_index('Buyer Username'), use_container_width=True)


# Main function to create the Streamlit app
def main():
    st.title('Joey Gummy Order Analytics')

    # File uploader
    uploaded_file = st.sidebar.file_uploader('Upload your CSV file', type=['csv'])

    if uploaded_file is not None:
        data = load_data(uploaded_file)

        # Clean and preprocess data
        data = clean_variation(data)
        data = remove_cancelled_orders(data)

        # Ensure 'Quantity' is an integer
        data['Quantity'] = pd.to_numeric(data['Quantity'], errors='coerce').fillna(0).astype(int)

        # Create a new column 'Total Items' and calculate the total sum
        data['Total Items'] = data['Variation'] * data['Quantity']
        total_items_sold = data['Total Items'].sum()

        # Calculate other metrics
        repeated_customers = count_repeated_customers(data)
        total_repeated_customers = len(repeated_customers)
        total_unique_customers = data['Buyer Username'].nunique()

        # Display metrics using metric cards
        cols = st.columns(3)
        with cols[0]:
            ui.metric_card(title="Total Repeated Customers", content=str(total_repeated_customers),
                           description="Total number of repeated customers", key="card1")
        with cols[1]:
            ui.metric_card(title="Total Unique Customers", content=str(total_unique_customers),
                           description="Total number of unique customers", key="card2")
        with cols[2]:
            ui.metric_card(title="Total Items Sold", content=str(total_items_sold),
                           description="Total number of items sold", key="card3")

        # Display data preview after all transformations
        st.subheader('Data Preview')
        num_rows = st.sidebar.number_input('Number of rows to display', min_value=1, max_value=len(data),
                                           value=len(data))
        st.dataframe(data.head(num_rows))

        # Purchase trends over time
        st.subheader('Purchase Trends Over Time')
        plot_purchase_trends(data)

        # Purchase frequency chart
        st.subheader('Purchase Frequency Chart')
        plot_purchase_frequency(data, repeated_customers)


if __name__ == '__main__':
    main()
