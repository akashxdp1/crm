import streamlit as st
import pandas as pd
import requests

st.set_page_config(layout="wide", page_title="HMA CRM Live")

# IMPORTANT: Paste your Google Web App URL here
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwIbGiWKkJr56WAqqX_w7q00pxIzHQKauC3nm14K7J4vpQVHDKVcIOunYH4Ayymuro/exec"

# IMPORTANT: Paste your Public Google Sheet CSV Link here for reading
# To get this: File > Share > Publish to web > Whole Document > CSV
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQg96A-7q5MIe0TBgEjrigzIqFU1lMc7eakk7ZBawqpw4fC29tIhE9gRm7A0co3LMzYTutDTX4_mw2F/pubhtml"

st.title("🚀 HMA Website CRM")

# --- DATA READING ---
try:
    df = pd.read_csv(SHEET_READ_URL)
except:
    # Default columns if sheet is empty
    df = pd.DataFrame(columns=["First Name", "Last Name", "Email", "Phone", "Company", "Address"])

# --- API LISTENER & MANUAL ADD ---
params = st.query_params

def save_lead(data):
    # Sends data to the Google Apps Script
    payload = {
        "fname": data.get("First Name"),
        "lname": data.get("Last Name"),
        "email": data.get("Email"),
        "phone": data.get("Phone"),
        "company": data.get("Company"),
        "address": data.get("Address")
    }
    response = requests.get(SCRIPT_URL, params=payload)
    return response.status_code == 200

# Handle incoming website lead
if "email" in params:
    new_lead = {
        "First Name": params.get("fname", ""),
        "Last Name": params.get("lname", ""),
        "Email": params.get("email", ""),
        "Phone": params.get("phone", ""),
        "Company": params.get("company", ""),
        "Address": params.get("address", "")
    }
    if save_lead(new_lead):
        st.query_params.clear()
        st.balloons()
        st.rerun()

# --- UI TABS ---
tab1, tab2 = st.tabs(["📋 Lead Pipeline", "➕ Add Manual"])

with tab1:
    st.dataframe(df, use_container_width=True, hide_index=True)
    if st.button("🔄 Refresh Data"):
        st.rerun()

with tab2:
    with st.form("manual_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fn, ln, em = st.text_input("First Name"), st.text_input("Last Name"), st.text_input("Email")
        with c2:
            ph, cp, ad = st.text_input("Phone"), st.text_input("Company"), st.text_input("Address")
        
        if st.form_submit_button("Save to Google Sheet"):
            if em:
                manual_lead = {"First Name": fn, "Last Name": ln, "Email": em, "Phone": ph, "Company": cp, "Address": ad}
                if save_lead(manual_lead):
                    st.success("Lead Saved Successfully!")
                    st.rerun()
            else:
                st.error("Email is required.")