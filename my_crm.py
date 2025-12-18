import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide", page_title="HMA Live CRM")

st.title("🚀 HMA Website CRM")

# --- CONNECTION ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Sheet1", ttl="0")
except Exception as e:
    st.error("⚠️ Connection Error: Your Google Sheet link in 'Secrets' might be wrong or the Sheet is not shared correctly.")
    st.info("Make sure your Sheet is set to 'Anyone with the link can Edit'.")
    st.stop() # Stops the code here so you don't see the red crash

# --- API LISTENER ---
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
    
    # Add to existing data
    if new_lead['Email'] not in df['Email'].values:
        new_row = pd.DataFrame([new_lead])
        df = pd.concat([df, new_row], ignore_index=True)
        conn.update(worksheet="Sheet1", data=df)
        st.query_params.clear()
        st.balloons()
        st.rerun()

# --- DISPLAY ---
tab1, tab2 = st.tabs(["📋 Lead Pipeline", "➕ Add Single"])

with tab1:
    search = st.text_input("🔍 Search Leads...")
    if search:
        df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    with st.form("manual_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fn, ln, em = st.text_input("First Name"), st.text_input("Last Name"), st.text_input("Email")
        with c2:
            ph, cp, ad = st.text_input("Phone"), st.text_input("Company"), st.text_input("Address")
        
        if st.form_submit_button("Save Lead"):
            new_row = pd.DataFrame([[fn, ln, em, ph, cp, ad]], columns=df.columns)
            df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=df)
            st.success("Lead Saved!")
            st.rerun()