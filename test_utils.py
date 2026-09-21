from datetime import datetime
from utils import (
    haversine, search_medicine, add_distance,
    sort_by_distance, is_open_now, emergency_filter, make_message
)

def test_haversine_known():
    d = haversine(0, 0, 0, 1)
    assert 111 < d < 112

def test_search_medicine():
    data = [
        {"medicine_name": "Paracetamol"},
        {"medicine_name": "paracetamol forte"},
        {"medicine_name": "Ibuprofen"},
    ]
    assert len(search_medicine(data, "paracetamol")) == 2
    assert len(search_medicine(data, "IBU")) == 1
    assert search_medicine(data, "") == []

def test_add_distance():
    data = [{"lat": 28.6139, "lon": 77.2090}]
    result = add_distance(data, 28.6139, 77.2090)
    assert abs(result[0]["distance_km"] - 0.0) < 0.001

def test_sort_by_distance():
    data = [{"distance_km": 5.0}, {"distance_km": 1.0}, {"distance_km": 3.0}]
    sorted_data = sort_by_distance(data)
    assert [r["distance_km"] for r in sorted_data] == [1.0, 3.0, 5.0]

def test_is_open_now_midnight():
    row = {"open_time": "22:00", "close_time": "02:00"}
    now = datetime.strptime("00:30", "%H:%M").time()
    assert is_open_now(row, now) is True
    now = datetime.strptime("12:00", "%H:%M").time()
    assert is_open_now(row, now) is False

def test_emergency_filter():
    now = datetime.strptime("01:00", "%H:%M").time()
    data = [
        {"open_time": "22:00", "close_time": "06:00", "stock_qty": 0},
        {"open_time": "22:00", "close_time": "06:00", "stock_qty": 5},
        {"open_time": "08:00", "close_time": "20:00", "stock_qty": 10},
    ]
    filtered = emergency_filter(data, now)
    assert len(filtered) == 1
    assert filtered[0]["stock_qty"] == 5

def test_make_message():
    row = {"store_name": "Test Pharmacy", "distance_km": 2.5, "stock_qty": 12}
    msg = make_message(row, "Paracetamol")
    assert "Test Pharmacy" in msg
    assert "2.50" in msg
    assert "12" in msg