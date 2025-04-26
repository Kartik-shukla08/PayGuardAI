import streamlit as st
import sqlite3
import pandas as pd
import pickle
import xgboost
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from auth0_component import login_button


def log_transaction_to_db(user_email, row):
    conn = sqlite3.connect("users_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (
            user_email, date, transaction_type, payment_gateway,
            transaction_state, merchant_category, amount, is_fraud
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_email,
        row["Date"],
        row["Transaction_Type"],
        row["Payment_Gateway"],
        row["Transaction_State"],
        row["Merchant_Category"],
        row["amount"],
        row["fraud"]
    ))
    conn.commit()
    conn.close()

# Set page config first
st.set_page_config(page_title="PayGuard-AI", layout="wide")

# -------------------- AUTH0 LOGIN START --------------------
if "user_info" not in st.session_state:
    # Add a CSS style for the gradient background
    st.markdown("""
        <style>
        .gradient-background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 50% 30%, #4B8BBE, #1E3A8A);
            z-index: -1;
            opacity: 0.7;
        }
        </style>
        <div class="gradient-background"></div>
        
        <div style='text-align: center; padding: 3rem;'>
            <img src='https://cdn-icons-png.flaticon.com/512/2058/2058414.png' width='100' style='filter: invert(1);' />
            <h1 style='font-size: 3em; color: white;'>🔐 Welcome to <span style="color:#4B8BBE">PayGuard AI</span></h1>
            <h3 style='color: white;'>Secure AI-Powered UPI Fraud Detection</h3>
            <p style='max-width: 600px; margin: auto; font-size: 1.2em; color: white;'>
                Analyze, detect, and defend your UPI transactions against fraud with real-time machine learning insights.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Create columns for centering
    col1, col2, col3 = st.columns([1, 1.2, 1])
    # Display the image in the middle column with a specific width
    with col2:
        st.image("upi_secure.png", caption="Most accurate fraud detection", width=400)

    st.markdown("""
        <div style='padding: 2rem 3rem; text-align: center;'>
            <ul style='list-style-type: none; font-size: 1.1em;'>
                <h3>🔒 Bank-level security with encrypted insights</h3>
                <h3>⚡ Instant ML-driven fraud detection</h3>
                <h3>📊 Intuitive dashboards & bulk CSV upload</h3>
            </ul>
        </div>
        <div style='text-align: center; margin: 30px;'>
            <div style='display: flex; justify-content: center;'>
    """, unsafe_allow_html=True)

    # client_id = st.secrets["auth0"]["client_id"]
    # domain = st.secrets["auth0"]["domain"]
    # user_info = login_button(client_id, domain=domain)

    client_id = st.secrets["auth0"]["client_id"]
    domain = st.secrets["auth0"]["domain"]
    st.markdown("""
            <div style='margin: 20px; padding: 10px; background-color: #1E7E92; border-radius: 5px; color: white; font-size: 1.2em; text-align: center;'>
                <h3>🔑 Login to your account</h3>
            </div>
        """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 0.8, 1])
    with col2:
       
        user_info = login_button(client_id, domain=domain)

    st.markdown("""</div></div>
        <hr>
        <center style='color:gray'>🔗 <a href='#'>About</a> • <a href='#'>Contact</a> • <a href='#'>Privacy Policy</a></center>
    """, unsafe_allow_html=True)

    if user_info:
        st.session_state.user_info = user_info
        st.rerun()
    else:
        st.stop()

# -------------------- AUTH0 LOGIN END --------------------
user = st.session_state.user_info
st.sidebar.success(f"👤 {user['name']} | {user['email']}")
if st.sidebar.button("Logout"):
    del st.session_state.user_info
    st.rerun()

st.success(f"Welcome {user['name']} 👋")
st.markdown("---")

# Load the trained model
with open("UPI_Fraud_model.pkl", "rb") as file:
    model = pickle.load(file)

def predict_fraud(transaction_data):
    transaction_data['Date'] = pd.to_datetime(transaction_data['Date']).view("int64") / 10**9
    transaction_data = pd.get_dummies(transaction_data, columns=["Transaction_Type", "Payment_Gateway", "Transaction_State", "Merchant_Category"], drop_first=True)
    transaction_data = transaction_data.reindex(columns=model.get_booster().feature_names, fill_value=0)
    prediction = model.predict(transaction_data)
    return prediction

def visualize_results(df):
    pie_chart = df['fraud'].value_counts().reset_index()
    pie_chart.columns = ['Fraud Status', 'Count']
    fig_pie = px.pie(pie_chart, values='Count', names='Fraud Status', title='Fraud Detection Results', color='Fraud Status', 
                     color_discrete_sequence=['#636EFA', '#EF553B'])
    st.plotly_chart(fig_pie)

    line_chart = df.groupby('Date')['amount'].sum().reset_index()
    fig_line = px.line(line_chart, x='Date', y='amount', title='Total Transaction Amount Over Time')
    st.plotly_chart(fig_line)

st.title("PayGuardAI: UPI Transaction Fraud Detection")
st.markdown("""
    Inspect a single transaction or upload multiple. Our ML model detects fraudulent activity and shows analytics.
""")

st.sidebar.header("Individual Transaction")
transaction_date = st.sidebar.date_input("Select Transaction Date")
transaction_type = st.sidebar.selectbox("Select Transaction Type", ["Refund", "Bank Transfer", "Subscription", "Purchase", "Investment", "Other"])
payment_gateway = st.sidebar.selectbox("Select Payment Gateway", ["SamplePay", "UPI Pay", "Dummy Bank", "Alpha Bank", "Other"])
transaction_state = st.sidebar.selectbox("Select Transaction State", ["Maharashtra", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Other"])
merchant_category = st.sidebar.selectbox("Select Merchant Category", ["Brand Vouchers and OTT", "Home delivery", "Utilities","Investment","Travel bookings","Purchases", "Other"])
transaction_amount = st.sidebar.number_input("Enter Transaction Amount (₹)", min_value=0.0, max_value=500000.0)

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    with st.spinner("Processing your file with AI magic..."):
        df = pd.read_csv(uploaded_file)
        st.success("Done!")
        st.write("Uploaded Data:")
        st.dataframe(df)

        processed_data = pd.DataFrame({
            "Date": pd.to_datetime(df['Date']),
            "Transaction_Type": df['Transaction_Type'],
            "Payment_Gateway": df['Payment_Gateway'],
            "Transaction_State": df['Transaction_State'],
            "Merchant_Category": df['Merchant_Category'],
            "amount": df['amount']
        })

        processed_data['fraud'] = predict_fraud(processed_data)

        st.write("Processed Data with Predictions:")
        st.dataframe(processed_data)

        visualize_results(processed_data)

        for _, row in processed_data.iterrows():
            log_transaction_to_db(user['email'], row)

if st.button("Check Individual Transaction"):
    transaction_data = pd.DataFrame({
        "Date": [transaction_date],
        "Transaction_Type": [transaction_type],
        "Payment_Gateway": [payment_gateway],
        "Transaction_State": [transaction_state],
        "Merchant_Category": [merchant_category],
        "amount": [transaction_amount]
    })

    prediction = predict_fraud(transaction_data)
    if prediction[0] == 1:
        st.error("This transaction is likely to be fraudulent.")
    else:
        st.success("This transaction appears legitimate.")

    transaction_data["fraud"] = prediction[0]
    log_transaction_to_db(user['email'], transaction_data.iloc[0])

st.markdown(
    """
    <style>
    .reportview-container {
        background: url('https://cdn.sanity.io/images/9sed75bn/production/470934de877c88a13171081ae22e98994ce9cbd7-1792x1008.png') no-repeat center center fixed; 
        background-size: cover;
    }
    .sidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.8);
    }
    </style>
    """,
    unsafe_allow_html=True
)

print(xgboost.__version__)
