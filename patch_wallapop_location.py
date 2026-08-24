import re

with open("wallapop.py", "r", encoding="utf-8") as f:
    wallapop = f.read()

# Replace hardcoded coords with settings
old_coords = """
        "latitude": 41.4231,
        "longitude": 2.188,
"""
new_coords = """
        "latitude": float(get_setting("latitude", "40.4165")),
        "longitude": float(get_setting("longitude", "-3.70256")),
"""
wallapop = wallapop.replace(old_coords, new_coords)

with open("wallapop.py", "w", encoding="utf-8") as f:
    f.write(wallapop)
