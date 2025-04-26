import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from streamlit_extras.let_it_rain import rain

st.set_page_config(page_title="🔍 UPI Reputation Tracker", layout="wide")

st.title("🔍 UPI Reputation Tracker")
st.markdown("""
Help the community by flagging suspicious UPI IDs or rating trustworthy ones. Check any UPI’s reputation below.
""")

# -------------------- DATABASE SETUP --------------------
def get_connection():
    return sqlite3.connect("users_data.db")

# -------------------- RATING / FLAGGING SECTION --------------------
st.markdown("### ✍️ Rate or Flag a UPI ID")
input_upi = st.text_input("Enter UPI ID (e.g. example@upi)")
rating = st.slider("Rate this UPI's trustworthiness", 1, 5, 3)
flag_reason = st.text_area("Reason for flagging (optional)")

if st.button("🚩 Submit Rating / Flag"):
    if not input_upi:
        st.error("Please enter a UPI ID.")
    else:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if user already rated this UPI
        cursor.execute("SELECT 1 FROM upi_reputation WHERE upi_id = ? AND user_email = ?", (input_upi, st.session_state.user_info['email']))
        already_rated = cursor.fetchone()

        if already_rated:
            st.warning("⚠️ You've already rated or flagged this UPI ID.")
        else:
            cursor.execute('''
                INSERT INTO upi_reputation (upi_id, user_email, rating, flag_reason, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (input_upi, st.session_state.user_info['email'], rating, flag_reason or None, datetime.now()))
            conn.commit()
            st.success("✅ Your contribution has been recorded!")
            # rain(emoji="💡", font_size=30, falling_speed=5, animation_length="infinite")
            # st.rerun()

        conn.close()

# -------------------- LOOKUP SECTION --------------------
st.markdown("---")
st.markdown("### 🔎 Check UPI Reputation")
lookup_upi = st.text_input("🔍 Enter UPI ID to lookup", key="lookup")

if st.button("Check Reputation") and lookup_upi:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM upi_reputation WHERE upi_id = ?", conn, params=(lookup_upi,))
    conn.close()

    if df.empty:
        st.info("No data available for this UPI ID yet. Be the first to contribute!")
    else:
        avg_rating = round(df['rating'].mean(), 2)
        num_flags = df['flag_reason'].notnull().sum()
        rating_count = len(df)

        st.metric("⭐ Average Rating", avg_rating)
        st.metric("🚩 Times Flagged", num_flags)

        # Determine Trust Level
        if rating_count <= 2:
            trust_level = "⚪️ Unknown"
        elif rating_count <= 5:
            trust_level = "🟡 Low Trust"
        elif rating_count <= 10:
            trust_level = "🟠 Medium Trust"
        else:
            trust_level = "🟢 High Trust"

        color_map = {
            "⚪️ Unknown": "#cccccc",
            "🟡 Low Trust": "#f1c40f",
            "🟠 Medium Trust": "#e67e22",
            "🟢 High Trust": "#2ecc71"
        }

        st.markdown(f"""
            <div style='background-color:{color_map[trust_level]};padding:0.8em;border-radius:10px;font-weight:bold;text-align:center;'>
                {trust_level} (based on {rating_count} ratings)
            </div>
        """, unsafe_allow_html=True)

        with st.expander("📋 See All Submissions"):
            st.dataframe(df[['user_email', 'rating', 'flag_reason', 'timestamp']])

# -------------------- FOOTER --------------------
st.markdown("""
---
💡 **How it works:** Ratings and flags submitted by users build a reputation score for each UPI. More data = more accuracy!
""")

st.sidebar.header("🔧 Account Settings")
if st.sidebar.button("Logout"):
    del st.session_state.user_info
    st.experimental_rerun()