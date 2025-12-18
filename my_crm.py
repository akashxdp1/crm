import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide", page_title="HMA Live CRM", page_icon="🚀")

# --- TITLES ---
st.title("🚀 HMA Website CRM")
st.markdown("---")

# --- CONNECTION ENGINE ---
try:
    # Use the connection defined in Secrets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Force read from Sheet1
    df = conn.read(worksheet="Sheet1", ttl="0")
    
    # Clean up any empty rows from the Sheet
    df = df.dropna(how="all")
    
except Exception as e:
    st.error("❌ Connection Error: Streamlit cannot reach your Google Sheet.")
    st.info("Check your 'Secrets' in Streamlit Cloud. It must contain the correct link.")
    st.stop()

# --- API WEBHOOK LISTENER ---
params = st.query_params
if "email" in params:
    new_data = {
        'First Name': params.get("fname", ""),
        'Last Name': params.get("lname", ""),
        'Email': params.get("email", ""),
        'Phone': params.get("phone", ""),
        'Company': params.get("company", ""),
        'Address': params.get("address", "")
    }
    
    # Check if lead exists
    if new_data['Email'] not in df['Email'].values:
        new_row = pd.DataFrame([new_data])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_df)
        st.query_params.clear()
        st.balloons()
        st.rerun()

# --- INTERFACE ---
tab1, tab2 = st.tabs(["📋 Lead Pipeline", "➕ Manual Entry"])

with tab1:
    search = st.text_input("🔍 Search CRM...")
    if search:
        # Filter across all columns
        display_df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
    else:
        display_df = df

    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    if st.button("🔄 Refresh from Google Sheets"):
        st.rerun()

with tab2:
    with st.form("manual_entry", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fn = st.text_input("First Name")
            ln = st.text_input("Last Name")
            em = st.text_input("Email")
        with col2:
            ph = st.text_input("Phone")
            cp = st.text_input("Company")
            ad = st.text_input("Address")
        
        if st.form_submit_button("Save Lead"):
            if em:
                # Map the manual data to a new row
                new_entry = pd.DataFrame([[fn, ln, em, ph, cp, ad]], columns=df.columns)
                updated_df = pd.concat([df, new_entry], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success("Lead successfully saved to Google Sheets!")
                st.rerun()
            else:
                st.error("Email is required.")