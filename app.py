import streamlit as st
from datetime import datetime
from utils import (
    load_csv, search_medicine, add_distance,
    sort_by_distance, emergency_filter, make_message,
    load_recent, save_recent
)

# ---- Page setup ----
st.set_page_config(page_title="Emergency Medicine Finder", page_icon="💊", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"]  {
    font-family: 'IBM Plex Sans', sans-serif;
}

.app-title {
    font-family: 'Spectral', serif;
    font-weight: 700;
    font-size: 2.3rem;
    color: #16221E;
    margin-bottom: 0.1rem;
}
.app-subtitle {
    color: #4B5A55;
    font-size: 1rem;
    margin-bottom: 0.4rem;
}
.app-divider {
    border: none;
    border-top: 2px solid #1F6F5C;
    height: 1px;
    margin: 0.6rem 0 1.6rem 0;
}

.stButton>button {
    background-color: #1F6F5C;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    font-weight: 500;
}
.stButton>button:hover {
    background-color: #16523F;
    color: #FFFFFF;
}

.result-card {
    border: 1px solid #D8DED9;
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
    background-color: #FFFFFF;
}
.result-store {
    font-family: 'Spectral', serif;
    font-weight: 600;
    font-size: 1.15rem;
    color: #16221E;
}
.result-meta {
    color: #4B5A55;
    font-size: 0.92rem;
    margin-top: 0.2rem;
}
.badge {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 3px;
    font-size: 0.8rem;
    font-weight: 500;
    margin-left: 0.4rem;
}
.badge-instock { background-color: #E4F0EA; color: #1F6F5C; }
.badge-low { background-color: #FCEEE3; color: #B5651D; }
.badge-out { background-color: #FBE9E7; color: #B3261E; }

.emergency-banner {
    background-color: #FBE9E7;
    border-left: 4px solid #C1441E;
    padding: 0.6rem 0.9rem;
    border-radius: 4px;
    color: #7A2E1B;
    font-size: 0.92rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)
try:
    st.image("logo.png", width=180)
except Exception:
    pass
st.markdown('<div class="app-title">💊 Emergency Medicine Finder</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Find nearby pharmacies that have what you need, right now.</div>', unsafe_allow_html=True)
st.markdown('<hr class="app-divider">', unsafe_allow_html=True)


# ---- Default location (Rewa, MP — change to your city if needed) ----
DEFAULT_LAT, DEFAULT_LON = 24.5854, 81.2999

# ---- Sidebar: location & mode ----
st.sidebar.header("Your location")
user_lat = st.sidebar.number_input("Latitude", value=DEFAULT_LAT, format="%.4f")
user_lon = st.sidebar.number_input("Longitude", value=DEFAULT_LON, format="%.4f")

st.sidebar.markdown("---")
emergency_mode = st.sidebar.toggle("🚨 Emergency mode (open now + in stock only)")
if emergency_mode:
    st.markdown('<div class="emergency-banner">🚨 Emergency mode — showing only pharmacies open now with stock available.</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")
if st.sidebar.button("🗑 Clear search"):
    st.session_state["medicine_query"] = ""
    if st.button("🔍 Find"):
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

def render_result_card(row, medicine_name):
    stock = row["stock_qty"]
    if stock == 0:
        badge = '<span class="badge badge-out">Out of stock</span>'
    elif stock <= 5:
        badge = f'<span class="badge badge-low">Low stock · {stock}</span>'
    else:
        badge = f'<span class="badge badge-instock">In stock · {stock}</span>'

    st.markdown(f"""
    <div class="result-card">
        <div class="result-store">{row['store_name']}</div>
        <div class="result-meta">{medicine_name.title()} — {row['distance_km']:.2f} km away{badge}</div>
    </div>
    """, unsafe_allow_html=True)

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
                render_result_card(row, medicine_query)