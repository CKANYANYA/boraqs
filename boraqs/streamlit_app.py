import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

st.set_page_config(page_title="BoraQS – Kenyan BOQ Beast", layout="wide")
st.title("BoraQS")
st.markdown("##### The only BOQ tool that understands **Nairobi 2025 prices** 🇰🇪🏗️")
st.markdown("Built by **@Coll94K** – Kitale site engineer who got tired of outdated rates")

# Current Kenyan material prices (updated Nov 2025)
prices_2025 = {
    "Cement 50kg (Bamburi)": 720,
    "Cement 50kg (Savannah)": 680,
    "Cement 50kg (Mombasa Cement)": 670,
    "Y8 Rebar (per tonne)": 112000,
    "Y10 Rebar (per tonne)": 108000,
    "Y12 Rebar (per tonne)": 105000,
    "Y16 Rebar (per tonne)": 103000,
    "River Sand (per tonne)": 2800,
    "Machine Cut Stones (9x9)": 42,
    "Hardcore (per tonne)": 2400,
    "Ballast (per tonne)": 2600,
    "Grade 25 Concrete (per m³)": 14200,
}

col1, col2 = st.columns([1, 2])

with col1:
    st.success(f"**Updated:** November 11, 2025")
    st.info("Prices scraped from contractors groups + Jiji + Tarmack Watch")

with col2:
    profit_margin = st.slider("Your Profit Margin (%)", 5, 30, 15)
    contingency = st.slider("Contingency (%)", 5, 20, 10)

st.markdown("---")

uploaded_file = st.file_uploader("Upload your BOQ Excel (any format)", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    if "Description" not in df.columns:
        st.error("Column 'Description' not found. Rename it or use standard format.")
    else:
        total_cost = 0
        st.subheader("BOQ with Current Nairobi Rates")
        
        new_rows = []
        for index, row in df.iterrows():
            desc = str(row['Description']).lower()
            qty = row['Quantity'] if 'Quantity' in row else 1
            unit = row['Unit'] if 'Unit' in row else ''
            
            rate = 0
            if "cement" in desc and "50kg" in desc:
                rate = prices_2025["Cement 50kg (Bamburi)"]
            elif "y8" in desc or "8mm" in desc:
                rate = prices_2025["Y8 Rebar (per tonne)"] / 1000 * 52  # approx kg/m
            elif "y10" in desc:
                rate = prices_2025["Y10 Rebar (per tonne)"] / 1000 * 81
            elif "y12" in desc:
                rate = prices_2025["Y12 Rebar (per tonne)"] / 1000 * 115
            elif "sand" in desc:
                rate = prices_2025["River Sand (per tonne)"]
            elif "machine cut" in desc or "blocks" in desc:
                rate = prices_2025["Machine Cut Stones (9x9)"]
            elif "concrete" in desc and "grade 25" in desc:
                rate = prices_2025["Grade 25 Concrete (per m³)"]
            
            amount = qty * rate
            total_cost += amount
            
            new_rows.append({
                "Item": row.get('Item', index+1),
                "Description": row['Description'],
                "Qty": qty,
                "Unit": unit,
                "Rate (KSh)": f"{rate:,.0f}",
                "Amount (KSh)": f"{amount:,.0f}"
            })
        
        result_df = pd.DataFrame(new_rows)
        st.dataframe(result_df, use_container_width=True)
        
        subtotal = total_cost
        profit = subtotal * (profit_margin / 100)
        conting = subtotal * (contingency / 100)
        grand_total = subtotal + profit + conting
        vat = grand_total * 0.16
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Subtotal", f"KSh {subtotal:,.0f}")
        col2.metric(f"Profit {profit_margin}%", f"KSh {profit:,.0f}")
        col3.metric(f"Contingency {contingency}%", f"KSh {conting:,.0f}")
        
        st.markdown(f"### **GRAND TOTAL (excl. VAT): KSh {grand_total:,.0f}**")
        st.markdown(f"### **GRAND TOTAL (incl. 16% VAT): KSh {grand_total + vat:,.0f}**")
        
        excel_data = pd.DataFrame(new_rows)
        excel_data.to_excel("BoraQS_Output.xlsx", index=False)
        with open("BoraQS_Output.xlsx", "rb") as f:
            st.download_button("Download Full BOQ (Excel)", f, "BoraQS_Final.xlsx")

else:
    st.info("Upload any BOQ Excel → BoraQS will auto-fill current 2025 rates + profit + VAT")
    st.markdown("### Sample format needed: columns → **Description**, **Quantity**, **Unit**")

st.markdown("---")
st.caption("Follow @Coll94K on X • This tool is saving contractors millions weekly • Next: Auto-scrape new tenders from PPIP")