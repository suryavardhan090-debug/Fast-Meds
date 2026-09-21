import streamlit as st
from datetime import datetime
from utils import (
    load_csv, search_medicine, add_distance,
    sort_by_distance, emergency_filter, make_message,
    load_recent, save_recent
)

# ---- Page setup ----
st.set_page_config(page_title="Emergency Medicine Finder", page_icon="💊", layout="centered")
try:
    st.image("logo.png", width=180)
except Exception:
    pass
st.title("💊 Emergency Medicine Finder")
st.caption("Find nearby pharmacies that have the medicine you need, right now.")

# ---- Default location (Rewa, MP — change to your city if needed) ----
DEFAULT_LAT, DEFAULT_LON = 24.5854, 81.2999

# ---- Sidebar: location & mode ----
st.sidebar.header("Your location")
user_lat = st.sidebar.number_input("Latitude", value=DEFAULT_LAT, format="%.4f")
user_lon = st.sidebar.number_input("Longitude", value=DEFAULT_LON, format="%.4f")

st.sidebar.markdown("---")
emergency_mode = st.sidebar.toggle("🚨 Emergency mode (open now + in stock only)")
st.sidebar.markdown("---")
if st.sidebar.button("🗑 Clear search"):
    st.session_state["medicine_query"] = ""
    st.rerun()

# ---- Main search box ----
recent_queries = load_recent()
if recent_queries:
    st.caption("🕒 Recent searches:")
    cols = st.columns(len(recent_queries))
    for i, q in enumerate(recent_queries):
        if cols[i].button(q, key=f"recent_{i}"):
            st.session_state["medicine_query"] = q
            st.rerun()
            COMMON_MEDS = ["Paracetamol", "Ibuprofen", "Salbutamol", "Amoxicillin", "Cetirizine"]
if not recent_queries:
    st.caption("💊 Commonly searched:")
    cols = st.columns(len(COMMON_MEDS))
    for i, med in enumerate(COMMON_MEDS):
        if cols[i].button(med, key=f"common_{i}"):
            st.session_state["medicine_query"] = med
            st.rerun()
medicine_query = st.text_input(
    "🔎 Medicine name (e.g., paracetamol)",
    placeholder="Type part of the medicine name…",
    key="medicine_query"
)

if st.button("🔍 Find"):
    if not medicine_query.strip():
        st.warning("Please type a medicine name first.")
    else:
        save_recent(medicine_query.strip())
        with st.spinner("Searching…"):
            data = load_csv("inventory_editable.csv")
            results = search_medicine(data, medicine_query.strip())
            results = add_distance(results, user_lat, user_lon)

            if emergency_mode:
                results = emergency_filter(results, datetime.now().time())

            results = sort_by_distance(results)

        if not results:
            st.error("No matching pharmacies found. Try a different medicine or turn off Emergency mode.")
        else:
            st.success(f"Found {len(results)} result(s):")
            for row in results:
                st.write(make_message(row, medicine_query))