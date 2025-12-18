import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Page config
st.set_page_config(layout="wide", page_title="HMA Live CRM", page_icon="🌐")

# --- GOOGLE SHEETS CONNECTION ---
# This connects to the sheet you will define in your Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(worksheet="Sheet1", ttl="0") # ttl=0 ensures we always see the freshest data

def save_data(df):
    conn.update(worksheet="Sheet1", data=df)

# --- LIVE API LISTENER ---
params = st.query_params
if "email" in params:
    new_lead = {
        'First Name': params.get("fname", ""),
        'Last Name': params.get("lname", ""),
        'Email': params.get("email", ""),
        'Phone': params.get("phone", ""),
        'Company': params.get("company", ""),
        'Address': params.get("address", "")
    }
    
    df = load_data()
    # Check for duplicates
    if new_lead['Email'] not in df['Email'].values:
        new_row = pd.DataFrame([new_lead])
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.query_params.clear()
        st.toast(f"New Lead: {new_lead['First Name']} added!")
        st.rerun()

# --- UI ---
st.title("🚀 HMA Website CRM")
df = load_data()

tab1, tab2, tab3 = st.tabs(["📋 Lead Pipeline", "➕ Manual Add", "🔗 Your API Link"])

with tab1:
    search = st.text_input("🔍 Search Leads...")
    if search:
        df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
    st.dataframe(df, use_container_width=True, hide_index=True)
    if st.button("🔄 Refresh Data"):
        st.rerun()

with tab2:
    with st.form("manual_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fn, ln = st.text_input("First Name"), st.text_input("Last Name")
            em = st.text_input("Email")
        with col2:
            ph, cp = st.text_input("Phone"), st.text_input("Company")
            ad = st.text_input("Address")
        
        if st.form_submit_button("Save Lead"):
            new_row = pd.DataFrame([[fn, ln, em, ph, cp, ad]], columns=df.columns)
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("Saved to Google Sheets!")

with tab3:
    st.subheader("Your Personal Webhook URL")
    st.write("Use this URL in your website form's redirect/webhook setting:")
    webhook_url = f"https://hma-crm.streamlit.app/?fname=VALUE&lname=VALUE&email=VALUE&phone=VALUE&company=VALUE&address=VALUE"
    st.code(webhook_url)