import re

with open("web.py", "r", encoding="utf-8") as f:
    web = f.read()

# Add get_setting for location
web = web.replace('"region": get_setting("region", "es"),', '"region": get_setting("region", "es"),\n        "location": get_setting("location", ""),')

# Add geocoding logic
geocoding_logic = """
import requests

def geocode_location(location_name: str, country_code: str = "es"):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location_name,
            "countrycodes": country_code,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "FindlyBot/1.0"}
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass
    return None, None
"""

# Insert geocoding function before save_settings
web = web.replace('@app.post("/api/settings")', geocoding_logic + '\n@app.post("/api/settings")')

# Handle the logic inside save_settings
saving_logic = """
        for s in settings:
            existing = db.query(AppSetting).filter(AppSetting.key == s.key).first()
            if existing:
                existing.value = s.value
            else:
                db.add(AppSetting(key=s.key, value=s.value))
                
            if s.key == "location" and s.value.strip():
                # Geocode and save lat/lon
                region_setting = next((x.value for x in settings if x.key == "region"), "es")
                lat, lon = geocode_location(s.value, region_setting)
                if lat and lon:
                    db_lat = db.query(AppSetting).filter(AppSetting.key == "latitude").first()
                    if db_lat: db_lat.value = str(lat)
                    else: db.add(AppSetting(key="latitude", value=str(lat)))
                    
                    db_lon = db.query(AppSetting).filter(AppSetting.key == "longitude").first()
                    if db_lon: db_lon.value = str(lon)
                    else: db.add(AppSetting(key="longitude", value=str(lon)))
"""
web = re.sub(r'        for s in settings:.*?db\.add\(AppSetting\(key=s\.key, value=s\.value\)\)', saving_logic.strip(), web, flags=re.DOTALL)

with open("web.py", "w", encoding="utf-8") as f:
    f.write(web)
