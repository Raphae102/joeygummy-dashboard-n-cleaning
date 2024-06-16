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

# Function to remove non-numeric characters from Variation and convert to int
def clean_variation(data):
    data['Variation'] = data['Variation'].str.replace(r'\D+', '', regex=True)
    data['Variation'] = pd.to_numeric(data['Variation'], errors='coerce').fillna(0).astype(int)
    return data

# Function to update Variation column based on specific values
def update_variation(data):
    keywords_to_replace = ['vco30', 'vco50', 'so30', 'so50']
    data.loc[data['Variation'].isin(keywords_to_replace), 'Variation'] = 1
    return data

# Function to count repeated customers and their purchase frequency
def count_repeated_customers(data):
    customer_counts = data['Buyer Username'].value_counts()
    repeated_customers = customer_counts[customer_counts > 1]
    return repeated_customers

# Function to plot purchase trends over time using LineChartColumn
def plot_purchase_trends(data):
    # Convert 'Created Time' to datetime and remove the time part
    data['Created Time'] = pd.to_datetime(data['Created Time'], format="%d/%m/%Y %H:%M:%S", dayfirst=True).dt.to_period('M')
    purchase_trends = data.groupby('Created Time').size().reset_index(name='Purchases')
    purchase_trends['Created Time'] = purchase_trends['Created Time'].astype(str)

    st.line_chart(purchase_trends, x='Created Time', y='Purchases', width=0, height=0, use_container_width=True)

# Function to plot purchase frequency chart using BarChartColumn
def plot_purchase_frequency(data, repeated_customers):
    purchase_frequency = data[data['Buyer Username'].isin(repeated_customers.index)]['Buyer Username'].value_counts().reset_index()
    purchase_frequency.columns = ['Buyer Username', 'Frequency']

    st.bar_chart(purchase_frequency.set_index('Buyer Username'), width=0, height=0, use_container_width=True)

# Main function to create the Streamlit app
def main():
    st.title('Joey Gummy Order')

    # File uploader
    uploaded_file = st.sidebar.file_uploader('Upload your CSV file', type=['csv'])

    if uploaded_file is not None:
        data = load_data(uploaded_file)

        # Remove non-numeric characters from Variation and convert to int
        data = clean_variation(data)

        # Update Variation column for specific values
        data = update_variation(data)

        # Ensure 'Quantity' is also an integer
        data['Quantity'] = data['Quantity'].astype(int)

        # Calculate total items sold
        data['Total Items'] = data['Variation'] * data['Quantity']
        total_items_sold = data['Total Items'].sum()

        # Count repeated customers
        repeated_customers = count_repeated_customers(data)

        # Calculate metrics
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

        # Display data preview
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
