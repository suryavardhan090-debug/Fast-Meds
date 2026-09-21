import streamlit as st
import pandas as pd
from pathlib import Path

DATA_FILE = Path(__file__).parents[1] / "inventory_editable.csv"

if not DATA_FILE.exists():
    template_df = pd.DataFrame(columns=[
        "store_id", "store_name", "lat", "lon",
        "open_time", "close_time", "medicine_name", "stock_qty"
    ])
    template_df.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE, dtype={"store_id": int, "stock_qty": int})

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Seller – Update Inventory", page_icon="🏪", layout="wide")
st.title("🏪 Seller Inventory Update")
st.caption(
    "Edit the pharmacy inventory below. Changes save to inventory_editable.csv "
    "and will show up in the public search."
)

df = load_data()

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key="inventory_editor",
)

if st.button("💾 Save changes"):
    if edited_df.isnull().any().any():
        st.error("Please fill in all fields before saving.")
    elif edited_df["store_id"].duplicated().any():
        st.error("Store ID must be unique for each row.")
    else:
        edited_df["stock_qty"] = edited_df["stock_qty"].astype(int)
        save_data(edited_df)
        st.success("Inventory saved successfully!")
        st.rerun()

st.markdown("---")
st.subheader("🔎 Preview (first 5 rows)")
st.dataframe(edited_df.head(), use_container_width=True)