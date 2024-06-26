import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit_shadcn_ui as ui

st.set_page_config(page_title="Joey Gummy Order Analytics", layout="wide")


# Function to load data
@st.cache_data
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            data = pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            data = pd.read_excel(file)
        else:
            st.error("Unsupported file type. Please upload a CSV or XLSX file.")
            return None
        data = data.iloc[1:]  # Remove the first row
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


# Function to clean Variation column by removing specific rows
def clean_variation(data):
    try:
        keywords_to_delete = ['vco30', 'vco50', 'so30', 'so50']
        pattern = '|'.join(keywords_to_delete)
        data = data[~data['Seller SKU'].str.contains(pattern, case=False, na=False)]
        data['Variation'] = data['Variation'].str.extract('(\d+)').fillna(0).astype(int)
        return data
    except Exception as e:
        st.error(f"Error cleaning Variation column: {e}")
        return data


# Function to remove cancelled orders
def remove_cancelled_orders(data):
    try:
        data = data[~data['Cancelation/Return Type'].str.contains('cancel', case=False, na=False)]
        return data
    except Exception as e:
        st.error(f"Error removing cancelled orders: {e}")
        return data


# Function to count repeated customers
def count_repeated_customers(data):
    try:
        customer_counts = data['Buyer Username'].value_counts()
        repeated_customers = customer_counts[customer_counts > 1]
        return repeated_customers
    except Exception as e:
        st.error(f"Error counting repeated customers: {e}")
        return pd.Series()


# Function to plot purchase trends over time
def plot_purchase_trends(data):
    try:
        data['Created Time'] = pd.to_datetime(data['Created Time'], format="%d/%m/%Y %H:%M:%S",
                                              dayfirst=True).dt.to_period('M')
        purchase_trends = data.groupby('Created Time').size().reset_index(name='Purchases')
        purchase_trends['Created Time'] = purchase_trends['Created Time'].astype(str)
        fig = px.line(purchase_trends, x='Created Time', y='Purchases', title="Purchase Trends Over Time",
                      color_discrete_sequence=["#9EE6CF"])
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    except Exception as e:
        st.error(f"Error plotting purchase trends: {e}")


# Function to plot purchase frequency chart
def plot_purchase_frequency(data, repeated_customers):
    try:
        purchase_frequency = data[data['Buyer Username'].isin(repeated_customers.index)][
            'Buyer Username'].value_counts().reset_index()
        purchase_frequency.columns = ['Buyer Username', 'Frequency']
        fig = px.bar(purchase_frequency, x='Buyer Username', y='Frequency',
                     title="Purchase Frequency of Repeated Customers", color_discrete_sequence=["#9EE6CF"])
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    except Exception as e:
        st.error(f"Error plotting purchase frequency: {e}")


# Function to plot sales based on variation
def plot_variation_sales(data):
    try:
        allowed_variations = [1, 7, 15, 30]
        variation_sales = data[data['Variation'].isin(allowed_variations)].groupby('Variation')[
            'Total Items'].sum().reset_index()
        variation_sales['Total Orders'] = variation_sales['Total Items'] / variation_sales['Variation']

        fig = px.pie(variation_sales,
                     names='Variation',
                     values='Total Orders',
                     title="Total Orders Based on Variation",
                     color_discrete_sequence=px.colors.sequential.Teal)  # Use color scheme

        fig.update_traces(textinfo='percent+label', textfont_size=12)

        fig.update_layout(
            title_font=dict(size=24),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#FFFFFF")
        )
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    except Exception as e:
        st.error(f"Error plotting sales by variation: {e}")


# Function to plot sales by state
def plot_sales_by_state(data):
    try:
        state_sales = data.groupby('State')['Total Items'].sum().reset_index().sort_values(by='Total Items',
                                                                                           ascending=False)
        fig = px.bar(state_sales, x='State', y='Total Items', title="Sales by State",
                     color_discrete_sequence=["#9EE6CF"])
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    except Exception as e:
        st.error(f"Error plotting sales by state: {e}")


# Function to get the top state for orders
def get_top_state(data):
    try:
        top_state = data['State'].value_counts().idxmax()
        return top_state
    except Exception as e:
        st.error(f"Error getting top state for orders: {e}")
        return None


# Main function to create the Streamlit app
def main():
    st.title('Joey Gummy Order Analytics')
    st.sidebar.image("Time.jpg", width=200)

    uploaded_file = st.sidebar.file_uploader('Upload your CSV or XLSX file', type=['csv', 'xlsx'])

    if uploaded_file is not None:
        data = load_data(uploaded_file)

        if data is not None:
            with st.spinner('Processing data...'):
                data = clean_variation(data)
                data = remove_cancelled_orders(data)

                data['Quantity'] = pd.to_numeric(data['Quantity'], errors='coerce').fillna(0).astype(int)
                data['Total Items'] = data['Variation'] * data['Quantity']
                total_items_sold = data['Total Items'].sum()
                total_orders = data.shape[0]

                repeated_customers = count_repeated_customers(data)
                total_repeated_customers = len(repeated_customers)
                total_unique_customers = data['Buyer Username'].nunique()
                top_state = get_top_state(data)

            row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3, row1_3, row1_spacer4, row1_4, row1_spacer5, row1_5, row1_spacer6 = st.columns(
                (0.1, 2, 0.1, 2, 0.1, 2, 0.1, 2, 0.1, 2, 0.1))

            with row1_1:
                ui.metric_card(title="Total Repeated Customers", content=str(total_repeated_customers),
                               description="Total number of repeated customers", key="card1")
            with row1_2:
                ui.metric_card(title="Total Unique Customers", content=str(total_unique_customers),
                               description="Total number of unique customers", key="card2")
            with row1_3:
                ui.metric_card(title="Total Items Sold", content=str(total_items_sold),
                               description="Total number of items sold", key="card3")
            with row1_4:
                ui.metric_card(title="Total Orders", content=str(total_orders), description="Total number of orders",
                               key="card5")
            with row1_5:
                ui.metric_card(title="Top State for Orders", content=top_state,
                               description="State with the highest number of orders", key="card6")

            st.subheader("Data Preview")
            st.write(data.head())

            row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3 = st.columns((0.1, 2, 0.1, 2, 0.1))

            with row2_1:
                st.subheader("Purchase Trends Over Time")
                plot_purchase_trends(data)

            with row2_2:
                st.subheader("Purchase Frequency of Repeated Customers")
                plot_purchase_frequency(data, repeated_customers)

            row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.columns((0.1, 2, 0.1, 2, 0.1))

            with row3_1:
                st.subheader("Total Orders Based on Variation")
                plot_variation_sales(data)

            with row3_2:
                st.subheader("Sales by State")
                plot_sales_by_state(data)


if __name__ == "__main__":
    main()
