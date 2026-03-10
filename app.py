import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
from streamlit_option_menu import option_menu

# --- 1. पेज और फाइल सेटअप ---
st.set_page_config(page_title="Nikolux & Lifestar Pro", layout="wide")

FILES = {"stock": "inventory.csv", "sales": "sales_log.csv", "exp": "expenses.csv"}

def init_files():
    if not os.path.exists(FILES["stock"]):
        pd.DataFrame({"Brand": ["Nikolux", "Lifestar"], "Stock": [100.0, 100.0], "Cost": [50.0, 60.0]}).to_csv(FILES["stock"], index=False)
    if not os.path.exists(FILES["sales"]):
        pd.DataFrame(columns=["Date", "Customer", "Phone", "Brand", "Qty", "Amount", "Profit"]).to_csv(FILES["sales"], index=False)
    if not os.path.exists(FILES["exp"]):
        pd.DataFrame(columns=["Date", "Type", "Amount", "Note"]).to_csv(FILES["exp"], index=False)

init_files()

# --- 2. भाषा और नेविगेशन ---
lang = st.sidebar.selectbox("Language / भाषा", ["हिन्दी", "English"])
T = {
    "हिन्दी": {"sale": "बिक्री और बिल", "search": "ग्राहक खोजें", "stock": "स्टॉक", "exp": "खर्चे", "target": "लक्ष्य (Target)"},
    "English": {"sale": "Billing", "search": "Search", "stock": "Stock", "exp": "Expenses", "target": "Target"}
}[lang]

with st.sidebar:
    selected = option_menu("Menu", [T["sale"], T["search"], T["stock"], T["exp"], T["target"]], 
    icons=['cart-check', 'search', 'box-seam', 'cash-coin', 'trophy'], menu_icon="cast", default_index=0)

# --- 3. डेटा लोड करना ---
stock_df = pd.read_csv(FILES["stock"])
sales_df = pd.read_csv(FILES["sales"])
exp_df = pd.read_csv(FILES["exp"])

# --- 4. मुख्य डैशबोर्ड (Top Stats) ---
st.title("🧼 Nikolux & Lifestar Pro Manager")
gross_p = sales_df["Profit"].sum() if not sales_df.empty else 0
total_e = exp_df["Amount"].sum() if not exp_df.empty else 0
net_p = gross_p - total_e

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"₹{sales_df['Amount'].sum() if not sales_df.empty else 0}")
col2.metric("Expenses", f"₹{total_e}")
col3.metric("Net Profit", f"₹{net_p}", delta=float(net_p))
st.divider()

# --- 5. फीचर्स (Feature Logic) ---

# A. बिक्री और बिलिंग
if selected == T["sale"]:
    st.subheader("🛒 नई बिक्री दर्ज करें")
    with st.form("bill_form"):
        c_name = st.text_input("ग्राहक का नाम")
        c_phone = st.text_input("मोबाइल")
        brand = st.selectbox("ब्रांड", stock_df["Brand"].tolist())
        qty = st.number_input("मात्रा (kg)", min_value=0.1)
        price = st.number_input("कुल कीमत (₹)", min_value=1)
        if st.form_submit_button("बिल जनरेट करें"):
            cost = stock_df.loc[stock_df["Brand"] == brand, "Cost"].values[0]
            profit = price - (cost * qty)
            # सेव और अपडेट
            stock_df.loc[stock_df["Brand"] == brand, "Stock"] -= qty
            stock_df.to_csv(FILES["stock"], index=False)
            new_s = {"Date": datetime.now().strftime("%Y-%m-%d"), "Customer": c_name, "Phone": c_phone, "Brand": brand, "Qty": qty, "Amount": price, "Profit": profit}
            sales_df = pd.concat([sales_df, pd.DataFrame([new_s])], ignore_index=True)
            sales_df.to_csv(FILES["sales"], index=False)
            st.success("बिक्री दर्ज! कृपया पेज रिफ्रेश करें।")

# B. सर्च और ग्राहक इतिहास
elif selected == T["search"]:
    st.subheader("🔍 ग्राहक का रिकॉर्ड खोजें")
    q = st.text_input("नाम या मोबाइल नंबर लिखें")
    if q:
        res = sales_df[sales_df['Customer'].str.contains(q, case=False, na=False) | sales_df['Phone'].astype(str).str.contains(q)]
        st.table(res)

# C. स्टॉक मैनेजमेंट
elif selected == T["stock"]:
    st.subheader("📦 स्टॉक की स्थिति")
    st.dataframe(stock_df, use_container_width=True)
    with st.expander("नया स्टॉक जोड़ें"):
        b = st.selectbox("ब्रांड", ["Nikolux", "Lifestar"])
        a = st.number_input("कितना kg आया?", min_value=1.0)
        if st.button("स्टॉक अपडेट करें"):
            stock_df.loc[stock_df["Brand"] == b, "Stock"] += a
            stock_df.to_csv(FILES["stock"], index=False)
            st.rerun()

# D. खर्चे
elif selected == T["exp"]:
    st.subheader("💸 बिजनेस के खर्चे")
    with st.form("exp"):
        etype = st.selectbox("प्रकार", ["Rent", "Electricity", "Fuel", "Labor", "Other"])
        eamt = st.number_input("राशि (₹)", min_value=1)
        if st.form_submit_button("खर्चा जोड़ें"):
            new_e = {"Date": datetime.now().strftime("%Y-%m-%d"), "Type": etype, "Amount": eamt}
            pd.concat([exp_df, pd.DataFrame([new_e])]).to_csv(FILES["exp"], index=False)
            st.rerun()
    st.table(exp_df)

# E. लक्ष्य और ग्राफ (Target & Analytics)
elif selected == T["target"]:
    st.subheader("🎯 मासिक लक्ष्य और प्रगति")
    target = st.number_input("इस महीने का लक्ष्य (₹)", value=50000)
    current_sales = sales_df["Amount"].sum() if not sales_df.empty else 0
    prog = min(current_sales / target, 1.0)
    st.progress(prog)
    st.write(f"प्रगति: {int(prog*100)}%")
    
    st.divider()
    st.subheader("📈 बिक्री का ग्राफ")
    if not sales_df.empty:
        sales_df['Date'] = pd.to_datetime(sales_df['Date'])
        chart_data = sales_df.groupby('Date')['Amount'].sum()
        st.line_chart(chart_data)
