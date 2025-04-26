import sqlite3
import pandas as pd
import streamlit as st
import random
from datetime import datetime, timedelta
import altair as alt  # For Altair charts

# Function to fetch user-specific transactions from the database
def fetch_user_transactions(user_email):
    conn = sqlite3.connect("users_data.db")
    query = "SELECT * FROM transactions WHERE user_email = ?"
    c = conn.cursor()
    c.execute(query, (user_email,))
    rows = c.fetchall()
    conn.close()
    
    # Convert fetched data into a pandas DataFrame
    df = pd.DataFrame(rows, columns=["id", "user_email", "date", "transaction_type", "payment_gateway", "transaction_state", "merchant_category", "amount", "is_fraud"])
    return df

# Function to generate random transaction data for other features
def generate_random_transactions(start_date, end_date, num_transactions):
    transaction_types = ["Credit", "Debit"]
    payment_gateways = ["UPI", "Debit Card", "Credit Card", "Wallet"]
    merchant_categories = ["Brand Vouchers and OTT", "Home delivery", "Utilities", "Investment", "Travel bookings", "Purchases", "Other"]
    
    data = []
    for _ in range(num_transactions):
        transaction_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        transaction_type = random.choice(transaction_types)
        payment_gateway = random.choice(payment_gateways)
        merchant_category = random.choice(merchant_categories)
        amount = round(random.uniform(10, 500), 2)
        is_fraud = random.choice([0, 1])
        transaction_state = random.choice([
            "Maharashtra", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", 
            "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Manipur", "Meghalaya", 
            "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
            "Uttar Pradesh", "Uttarakhand", "West Bengal", "Other"
        ])
        
        data.append([transaction_date, transaction_type, payment_gateway, transaction_state, merchant_category, amount, is_fraud])
    
    df = pd.DataFrame(data, columns=["date", "transaction_type", "payment_gateway", "transaction_state", "merchant_category", "amount", "is_fraud"])
    return df

# Set up the page layout
st.set_page_config(page_title="PayGuard-AI Dashboard", layout="wide")

# -------------------- AUTH0 LOGIN VERIFICATION --------------------
if "user_info" not in st.session_state:
    st.error("You need to be logged in to access the dashboard.")
    st.stop()

user = st.session_state.user_info
st.sidebar.success(f"👤 Welcome, {user['name']} | {user['email']}")

# -------------------- TITLE AND HEADER --------------------
st.markdown("<h1 style='text-align: center; color: white;'>🔐 PayGuard-AI Dashboard</h1>", unsafe_allow_html=True)
st.markdown(
    f"""
    <h2 style='color:#4B8BBE; text-align: center;'>Welcome, {user['name']}! Here’s your transaction dashboard.</h2>
    <p style="font-size:1.1em; text-align: center;">Monitor your UPI transactions, view fraud detection results, and analyze your transaction history.</p>
    """,
    unsafe_allow_html=True
)

# Fetch transactions for the logged-in user
df = fetch_user_transactions(user['email'])

# -------------------- TRANSACTION DATA ANALYSIS --------------------
st.markdown("### 📊 Transaction Overview")
if df.empty:
    st.warning("No transactions found for your account.")
else:
    st.write(f"#### You have a total of **{len(df)}** transactions.")
    st.write("#### Latest Transactions")
    st.dataframe(df.tail(5), width=800, height=300)

    # -------------------- FRAUD DETECTION RESULTS --------------------
    st.markdown("### 🚨 Fraud Detection Results")
    if df['is_fraud'].dtype == 'object' and df['is_fraud'].apply(lambda x: isinstance(x, bytes)).any():
        st.warning("Some 'is_fraud' entries appear to be in bytes format. Converting them to strings.")
        df['is_fraud'] = df['is_fraud'].apply(lambda x: x.decode() if isinstance(x, bytes) else x)

    fraud_counts = df['is_fraud'].value_counts().reset_index()
    fraud_counts.columns = ['Fraud Status', 'Count']
    fraud_counts_chart = fraud_counts.set_index('Fraud Status')['Count']
    
    # Apply color in Altair (Blue for fraud (1), Red for non-fraud (0))
    fraud_chart = alt.Chart(fraud_counts).mark_bar().encode(
        x='Fraud Status',
        y='Count',
        color=alt.Color('Fraud Status', scale=alt.Scale(domain=[0, 1], range=['#FF6347', '#1E90FF']))
    )
    st.altair_chart(fraud_chart)

# Generate random transaction data
start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 1, 1)
num_transactions = 500  # Number of transactions to generate
df_random = generate_random_transactions(start_date, end_date, num_transactions)

# -------------------- TRANSACTION TIMELINE --------------------
st.markdown("### ⏳ Transaction Timeline")

# Convert 'date' column to datetime (just in case)
df_random['date'] = pd.to_datetime(df_random['date'])

# Group by month and year, summing the transaction amounts
df_random['month_year'] = df_random['date'].dt.to_period('M')
df_monthly = df_random.groupby('month_year')['amount'].sum().reset_index()

# Line chart of total amount over time using Streamlit's built-in line_chart
st.line_chart(df_monthly.set_index('month_year')['amount'])

# -------------------- TOP MERCHANT CATEGORIES --------------------
st.markdown("### 🛒 Top Merchant Categories")

# Get top merchant categories by transaction count
category_counts = df_random['merchant_category'].value_counts().reset_index()
category_counts.columns = ['Merchant Category', 'Count']

# Apply different shades of blue for each merchant category
category_chart = alt.Chart(category_counts).mark_bar().encode(
    x='Merchant Category',
    y='Count',
    color=alt.Color('Merchant Category', scale=alt.Scale(scheme='blues'))
)
st.altair_chart(category_chart)

# -------------------- TRANSACTION STATES --------------------
st.markdown("### 📝 Transaction States Distribution")
transaction_states = [
    "Maharashtra", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", 
    "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Manipur", "Meghalaya", 
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Other"
]

# Count transaction states
state_counts = df['transaction_state'].value_counts().reset_index()
state_counts.columns = ['Transaction State', 'Count']

# Include any unmatched states in the "Other" category
state_counts['Transaction State'] = state_counts['Transaction State'].apply(
    lambda x: x if x in transaction_states else "Other"
)

# Aggregate the "Other" state
state_counts = state_counts.groupby('Transaction State').sum().reset_index()

# Apply random colors using Altair
state_chart = alt.Chart(state_counts).mark_bar().encode(
    x='Transaction State',
    y='Count',
    color=alt.Color('Transaction State', scale=alt.Scale(range=[f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(len(state_counts))]))
)
st.altair_chart(state_chart)

# -------------------- ACCOUNT SETTINGS --------------------
st.sidebar.header("🔧 Account Settings")
if st.sidebar.button("Logout"):
    del st.session_state.user_info
    st.experimental_rerun()
