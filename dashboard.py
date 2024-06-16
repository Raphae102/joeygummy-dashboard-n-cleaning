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


# Function to count repeated customers and their purchase frequency
def count_repeated_customers(data):
    customer_counts = data['Buyer Username'].value_counts()
    repeated_customers = customer_counts[customer_counts > 1]
    return repeated_customers


# Function to plot purchase trends over time using LineChartColumn
def plot_purchase_trends(data):
    # Convert 'Created Time' to datetime and remove the time part
    data['Created Time'] = pd.to_datetime(data['Created Time'], format="%d/%m/%Y %H:%M:%S", dayfirst=True).dt.to_period(
        'M')
    purchase_trends = data.groupby('Created Time').size().reset_index(name='Purchases')
    purchase_trends['Created Time'] = purchase_trends['Created Time'].astype(str)

    st.line_chart(purchase_trends, x='Created Time', y='Purchases', width=0, height=0, use_container_width=True)


# Function to plot purchase frequency chart using BarChartColumn
def plot_purchase_frequency(data, repeated_customers):
    purchase_frequency = data[data['Buyer Username'].isin(repeated_customers.index)][
        'Buyer Username'].value_counts().reset_index()
    purchase_frequency.columns = ['Buyer Username', 'Frequency']

    st.bar_chart(purchase_frequency.set_index('Buyer Username'), width=0, height=0, use_container_width=True)


# Main function to create the Streamlit app
def main():
    st.title('Repeated Customers Dashboard')

    # File uploader
    uploaded_file = st.sidebar.file_uploader('Upload your CSV file', type=['csv'])

    if uploaded_file is not None:
        data = load_data(uploaded_file)
        # st.write('Data Preview:', data.head())

        # Count repeated customers
        repeated_customers = count_repeated_customers(data)

        # with left_column:
        # Display repeated customers and their purchase frequency
        st.subheader('Repeated Customers')

        # Display as a DataFrame with wider layout
        st.dataframe(repeated_customers.reset_index().rename(
            columns={'index': 'Buyer Username', 'Buyer Username': 'Frequency'}))

        # with right_column:
        # Display total number of repeated customers in metrics chart
        st.subheader('Total Repeated Customers')
        st.metric(label='Repeated Customers', value=len(repeated_customers))

        # Create columns for layout
        left_column, right_column = st.columns([1, 2])

        # Purchase trends over time
        st.subheader('Purchase Trends Over Time')
        plot_purchase_trends(data)

        # Purchase frequency chart
        st.subheader('Purchase Frequency Chart')
        plot_purchase_frequency(data, repeated_customers)

        # Detailed view of orders from repeated customers
        # st.subheader('Detailed Orders for Repeated Customers')
        # detailed_orders = data[data['Buyer Username'].isin(repeated_customers.index)]
        # st.write(detailed_orders)


if __name__ == '__main__':
    main()
