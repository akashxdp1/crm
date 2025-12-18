import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide", page_title="HMA CRM Live")

# --- DATABASE CONNECTION ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # TTL=0 ensures we don't look at old, cached data
    df = conn.read(ttl="0") 
    df = df.dropna(how="all")
except Exception as e:
    st.error("❌ Connection Failed. Check your Secrets.")
    st.stop()

# --- WEBHOOK LISTENER ---
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
    
    if new_lead['Email'] not in df['Email'].astype(str).values:
        new_row = pd.DataFrame([new_lead])
        df = pd.concat([df, new_row], ignore_index=True)
        # Explicitly update Sheet1
        conn.update(worksheet="Sheet1", data=df)
        st.query_params.clear()
        st.balloons()
        st.rerun()

# --- MAIN APP UI ---
st.title("🚀 HMA Website CRM")

tab1, tab2 = st.tabs(["📋 Lead Pipeline", "➕ Add Manual"])

with tab1:
    search = st.text_input("🔍 Search Leads...")
    display_df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)] if search else df
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab2:
    # clear_on_submit helps prevent double-clicking errors
    with st.form("manual_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fn = st.text_input("First Name")
            ln = st.text_input("Last Name")
            em = st.text_input("Email")
        with col2:
            ph = st.text_input("Phone")
            cp = st.text_input("Company")
            ad = st.text_input("Address")
        
        submitted = st.form_submit_button("Save to CRM")
        
        if submitted:
            if em:
                # 1. Create the new row
                new_entry = pd.DataFrame([[fn, ln, em, ph, cp, ad]], columns=df.columns)
                # 2. Combine with existing data
                updated_df = pd.concat([df, new_entry], ignore_index=True)
                # 3. Push to Google Sheets
                try:
                    conn.update(worksheet="Sheet1", data=updated_df)
                    st.success("Lead Saved Successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving to Google Sheets: {e}")
            else:
                st.warning("Email is a required field.")