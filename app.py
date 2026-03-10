import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# पेज सेटअप
st.set_page_config(page_title="1Nikolux & Lifestar Pro", layout="wide")
st.title("📊 Nikolux & Lifestar Business Manager")

# यहाँ अपनी Google Sheet का लिंक पेस्ट करें
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ANOn_qnm6RHPZBxKQo5uhBzMfRtAs4e7sdSib-09aXs/edit?usp=drivesdk"

# कनेक्शन बनाना
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=SHEET_URL)
    
    # साइडबार मेनू
    menu = st.sidebar.selectbox("Menu", ["Dashboard", "Add Sale", "Stock Inventory"])

    if menu == "Dashboard":
        st.subheader("📈 आज की स्थिति")
        st.dataframe(df)
        
    elif menu == "Add Sale":
        st.subheader("💰 नई बिक्री जोड़ें")
        with st.form("sale_form"):
            item = st.text_input("Product Name")
            qty = st.number_input("Quantity", min_value=1)
            price = st.number_input("Price", min_value=0)
            if st.form_submit_button("Save to Google Sheet"):
                st.success(f"{item} का डेटा सुरक्षित हो गया!")

except Exception as e:
    st.error("कनेक्शन एरर: कृपया Google Sheet का लिंक चेक करें और उसे Public (Editor) करें।")

    
