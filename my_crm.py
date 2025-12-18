import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide", page_title="HMA CRM Live")

# --- DATABASE CONNECTION ---
# This looks for the "spreadsheet" URL in your Streamlit Cloud Secrets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # We use a simple read to verify the connection
    df = conn.read(ttl="0") 
    df = df.dropna(how="all") # Ignore empty rows in the sheet
except Exception as e:
    st.error("❌ Connection Failed.")
    st.info("Check your Streamlit Secrets. It MUST be: spreadsheet = 'YOUR_URL'")
    st.stop()

# --- WEBHOOK LISTENER (For Website Integration) ---
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
    
    # Add if email is new
    if new_lead['Email'] not in df['Email'].astype(str).values:
        new_row = pd.DataFrame([new_lead])
        df = pd.concat([df, new_row], ignore_index=True)
        conn.update(data=df)
        st.query_params.clear()
        st.balloons()
        st.rerun()

# --- MAIN APP UI ---
st.title("🚀 HMA Website CRM")

tab1, tab2 = st.tabs(["📋 Lead Pipeline", "➕ Add Manual"])

with tab1:
    search = st.text_input("🔍 Search Leads...")
    if search:
        display_df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
    else:
        display_df = df
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    if st.button("🔄 Sync with Google Sheet"):
        st.rerun()

with tab2:
    with st.form("manual_entry", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fn, ln, em = st.text_input("First Name"), st.text_input("Last Name"), st.text_input("Email")
        with col2:
            ph, cp, ad = st.text_input("Phone"), st.text_input("Company"), st.text_input("Address")
        
        if st.form_submit_button("Save to CRM"):
            if em:
                new_entry = pd.DataFrame([[fn, ln, em, ph, cp, ad]], columns=df.columns)
                df = pd.concat([df, new_entry], ignore_index=True)
                conn.update(data=df)
                st.success("Lead Saved!")
                st.rerun()
            else:
                st.error("Email is required.")