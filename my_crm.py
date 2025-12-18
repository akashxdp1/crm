import streamlit as st
import pandas as pd
import os

# File setup
FILE_NAME = 'leads_data.csv'
REQUIRED_COLS = ['First Name', 'Last Name', 'Email', 'Phone', 'Company', 'Address']

st.set_page_config(layout="wide", page_title="Live Website CRM")

# --- DATABASE ENGINE ---
def load_data():
    if not os.path.isfile(FILE_NAME):
        return pd.DataFrame(columns=REQUIRED_COLS)
    try:
        df = pd.read_csv(FILE_NAME)
        # Ensure correct columns
        for col in REQUIRED_COLS:
            if col not in df.columns:
                df[col] = ""
        return df[REQUIRED_COLS].fillna("")
    except:
        return pd.DataFrame(columns=REQUIRED_COLS)

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# --- WEBHOOK / API LOGIC ---
# This part checks the URL for incoming data from your website
query_params = st.query_params

if "fname" in query_params:
    # Get data from URL: ?fname=John&lname=Doe&email=test@test.com
    new_entry = {
        'First Name': query_params.get("fname", ""),
        'Last Name': query_params.get("lname", ""),
        'Email': query_params.get("email", ""),
        'Phone': query_params.get("phone", ""),
        'Company': query_params.get("company", ""),
        'Address': query_params.get("address", "")
    }
    
    current_df = load_data()
    # Check if email already exists to prevent duplicates
    if new_entry['Email'] not in current_df['Email'].values:
        new_row = pd.DataFrame([new_entry])
        updated_df = pd.concat([current_df, new_row], ignore_index=True)
        save_data(updated_df)
        # Clear params after saving
        st.query_params.clear()
        st.toast("New Lead Added from Website!")
        st.rerun()

# --- UI ---
st.title("🌐 Website Integrated CRM")
df = load_data()

tab1, tab2, tab3 = st.tabs(["📋 Lead Pipeline", "➕ Manual Add", "⚙️ API Integration Details"])

with tab1:
    search = st.text_input("🔍 Search Leads...")
    display_df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)] if search else df
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    if st.button("Refresh Data"):
        st.rerun()

with tab2:
    with st.form("manual_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fn = st.text_input("First Name")
            ln = st.text_input("Last Name")
            em = st.text_input("Email")
        with c2:
            ph = st.text_input("Phone")
            cp = st.text_input("Company")
            ad = st.text_input("Address")
        
        if st.form_submit_button("Add Lead"):
            new_row = pd.DataFrame([[fn, ln, em, ph, cp, ad]], columns=REQUIRED_COLS)
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("Saved!")
            st.rerun()

with tab3:
    st.header("Connect Your Website")
    st.write("To send leads from your website form to this CRM, set your form's 'Redirect' or 'Webhook' URL to:")
    
    # This automatically detects your app's URL
    base_url = "http://localhost:8501" # Change this to your public URL when hosted
    api_example = f"{base_url}/?fname=VALUE&lname=VALUE&email=VALUE&phone=VALUE"
    
    st.code(api_example)
    st.info("When a user submits a form, your website should send a GET request to this URL with the data filled in.")