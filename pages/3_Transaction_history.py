import streamlit as st
import sqlite3
import pandas as pd

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Transaction History", layout="wide")

# -------------------- FETCH DATA FROM DB --------------------
def get_all_transactions():
    conn = sqlite3.connect("users_data.db")
    cursor = conn.cursor()

    # Fetch all transactions from the database
    cursor.execute("""
        SELECT id, user_email, date, transaction_type, payment_gateway, 
               transaction_state, merchant_category, amount, is_fraud 
        FROM transactions
    """)
    transactions = cursor.fetchall()
    conn.close()

    # If transactions are found, return them as a dataframe
    columns = ['id', 'user_email', 'date', 'transaction_type', 'payment_gateway', 
               'transaction_state', 'merchant_category', 'amount', 'is_fraud']
    return pd.DataFrame(transactions, columns=columns)

# Fetch data from DB
all_transactions = get_all_transactions()

# -------------------- PAGE UI --------------------
st.title("🔍 Transaction History")
st.markdown("""
    View your transaction history with fraud detection results.
    You can browse through the transactions and see details.
""")

# Sidebar Search Filters
st.sidebar.title("Search Transaction")

# Transaction ID search (mandatory)
transaction_id = st.sidebar.text_input("Enter Transaction ID", "")

# Filter options in the sidebar
transaction_type = st.sidebar.selectbox("Select Transaction Type", ["All", "Refund", "Bank Transfer", "Subscription", "Purchase", "Investment", "Other"])
payment_gateway = st.sidebar.selectbox("Select Payment Gateway", ["All", "SamplePay", "UPI Pay", "Dummy Bank", "Alpha Bank", "Other"])
transaction_state = st.sidebar.selectbox("Select Transaction State", ["All", "Maharashtra", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Other"])
merchant_category = st.sidebar.selectbox("Select Merchant Category", ["All", "Brand Vouchers and OTT", "Home delivery", "Utilities", "Investment", "Travel bookings", "Purchases", "Other"])

# Search button
search_button = st.sidebar.button("Search")

# Filter the data based on search criteria
filtered_transactions = all_transactions

# Apply filters only if search is clicked
if search_button:
    # Filter by Transaction ID if provided
    if transaction_id:
        filtered_transactions = filtered_transactions[filtered_transactions['id'] == int(transaction_id)]
    
    # Filter by Transaction Type
    if transaction_type != "All":
        filtered_transactions = filtered_transactions[filtered_transactions['transaction_type'] == transaction_type]
    
    # Filter by Payment Gateway
    if payment_gateway != "All":
        filtered_transactions = filtered_transactions[filtered_transactions['payment_gateway'] == payment_gateway]
    
    # Filter by Transaction State
    if transaction_state != "All":
        filtered_transactions = filtered_transactions[filtered_transactions['transaction_state'] == transaction_state]
    
    # Filter by Merchant Category
    if merchant_category != "All":
        filtered_transactions = filtered_transactions[filtered_transactions['merchant_category'] == merchant_category]

# -------------------- DISPLAYING TRANSACTIONS --------------------
if not filtered_transactions.empty:
    # Display filtered transactions in a card-like format
    for _, row in filtered_transactions.iterrows():
        with st.container():
            # Two columns for transaction info
            col1, col2 = st.columns(2)

            # Column 1: Transaction ID, Date, and Transaction Type
            with col1:
                st.markdown(f"**Transaction ID:** {row['id']}")
                # Display date as it was in the DB (no formatting)
                st.markdown(f"**Date:** {row['date']}")
                st.markdown(f"**Transaction Type:** {row['transaction_type']}")

            # Column 2: Payment Gateway, State, and Merchant Category
            with col2:
                st.markdown(f"**Payment Gateway:** {row['payment_gateway']}")
                st.markdown(f"**State:** {row['transaction_state']}")
                st.markdown(f"**Merchant Category:** {row['merchant_category']}")

            # Display amount in the bottom right with lighter green, larger and bolder
            st.markdown(f"**<span style='color:#66FF66; font-size: 22px; font-weight: bold;'>{row['amount']} ₹</span>**", unsafe_allow_html=True)

            st.markdown("---")
else:
    st.error("No transactions found with the given filters.")
