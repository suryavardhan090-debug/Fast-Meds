import csv
import math
from datetime import time


def load_csv(filename="pharmacy_data.csv"):
    """Read the pharmacy CSV file and return it as a list of dictionaries."""
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    # Convert numeric columns from text to actual numbers
    for row in rows:
        row["lat"] = float(row["lat"])
        row["lon"] = float(row["lon"])
        row["stock_qty"] = int(row["stock_qty"])
    return rows


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points on Earth."""
    R = 6371  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (math.sin(d_phi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def search_medicine(data, query):
    """Return only the rows whose medicine_name contains the search text (case-insensitive)."""
    if not query:
        return []
    query = query.lower()
    return [row for row in data if query in row["medicine_name"].lower()]


def add_distance(data, user_lat, user_lon):
    """Add a 'distance_km' field to each row, based on the user's location."""
    for row in data:
        row["distance_km"] = haversine(user_lat, user_lon, row["lat"], row["lon"])
    return data


def sort_by_distance(data):
    """Sort rows so the nearest shop comes first."""
    return sorted(data, key=lambda row: row["distance_km"])


def is_open_now(row, current_time):
    """Check if a shop is open right now, handling overnight hours (e.g. 22:00-06:00)."""
    open_t = time.fromisoformat(row["open_time"])
    close_t = time.fromisoformat(row["close_time"])
    if open_t <= close_t:
        return open_t <= current_time <= close_t
    else:
        # Overnight case: open time is later than close time (crosses midnight)
        return current_time >= open_t or current_time <= close_t


def emergency_filter(data, current_time):
    """Keep only shops that are open right now AND have stock available."""
    return [row for row in data if is_open_now(row, current_time) and row["stock_qty"] > 0]


def make_message(row, medicine_name):
    """Build a friendly one-line result message for a shop."""
    return (
        f"{row['store_name']} has {medicine_name} — "
        f"{row['distance_km']:.2f} km away, {row['stock_qty']} in stock."
    )

import json
import os

RECENT_FILE = "recent.json"
MAX_RECENT = 5

def load_recent():
    """Load the list of recent medicine queries from disk."""
    if not os.path.exists(RECENT_FILE):
        return []
    try:
        with open(RECENT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [str(item) for item in data]
    except Exception:
        pass
    return []

def save_recent(query):
    """Add a query to the recent list, avoiding duplicates, and save it."""
    if not query:
        return
    recent = load_recent()
    recent = [q for q in recent if q.lower() != query.lower()]
    recent.insert(0, query)
    recent = recent[:MAX_RECENT]
    try:
        with open(RECENT_FILE, "w", encoding="utf-8") as f:
            json.dump(recent, f, ensure_ascii=False, indent=2)
    except Exception:
        pass