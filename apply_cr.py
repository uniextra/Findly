import re

with open("web.py", "r", encoding="utf-8") as f:
    web = f.read()

# 1. Update search_location
old_search_location = """@app.get("/api/location/search")
def search_location(q: str):
    import requests
    if not q or len(q) < 3:
        return []
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": q,
            "format": "json",
            "limit": 5,
            "addressdetails": 1
        }
        headers = {"User-Agent": "FindlyBot/1.0"}
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except (requests.RequestException, ValueError) as e:
        print(f"Error in geocoding proxy: {e}")
    return []"""

new_search_location = """@app.get("/api/location/search")
async def search_location(q: str):
    import httpx
    from fastapi import HTTPException
    if not q or len(q) < 3:
        return []
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": q,
            "format": "json",
            "limit": 5,
            "addressdetails": 1
        }
        headers = {"User-Agent": "FindlyBot/1.0"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers=headers, timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
            else:
                raise HTTPException(status_code=resp.status_code, detail="Geocoding service returned an error")
    except httpx.TimeoutException:
        raise HTTPException(status_code=503, detail="Geocoding service timed out")
    except (httpx.RequestError, ValueError) as e:
        print(f"Error in geocoding proxy: {e}")
        raise HTTPException(status_code=503, detail="Geocoding service unavailable")"""

web = web.replace(old_search_location, new_search_location)

# 2. Update geocode_location
old_geocode_location = """def geocode_location(location_name: str, country_code: str = "es"):
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
    except (ValueError, KeyError, IndexError):
        pass
    return None, None"""

new_geocode_location = """async def geocode_location(location_name: str, country_code: str = "es"):
    import httpx
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location_name,
            "countrycodes": country_code,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "FindlyBot/1.0"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers=headers, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    return float(data[0]["lat"]), float(data[0]["lon"])
    except (httpx.RequestError, ValueError, KeyError, IndexError) as e:
        print(f"Geocode location failed: {e}")
    return None, None"""

web = web.replace(old_geocode_location, new_geocode_location)

# 3. Update save_settings to be async and handle the exception
old_save_settings = """@app.post("/api/settings")
def save_settings(settings: list[SettingUpdate], background_tasks: BackgroundTasks):
    db = SessionLocal()
    try:
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
                    else: db.add(AppSetting(key="longitude", value=str(lon)))"""

new_save_settings = """@app.post("/api/settings")
async def save_settings(settings: list[SettingUpdate], background_tasks: BackgroundTasks):
    from fastapi import HTTPException
    db = SessionLocal()
    try:
        for s in settings:
            existing = db.query(AppSetting).filter(AppSetting.key == s.key).first()
            if existing:
                existing.value = s.value
            else:
                db.add(AppSetting(key=s.key, value=s.value))
                
            if s.key == "location" and s.value.strip():
                # Geocode and save lat/lon
                region_setting = next((x.value for x in settings if x.key == "region"), "es")
                lat, lon = await geocode_location(s.value, region_setting)
                if lat is not None and lon is not None:
                    db_lat = db.query(AppSetting).filter(AppSetting.key == "latitude").first()
                    if db_lat: db_lat.value = str(lat)
                    else: db.add(AppSetting(key="latitude", value=str(lat)))
                    
                    db_lon = db.query(AppSetting).filter(AppSetting.key == "longitude").first()
                    if db_lon: db_lon.value = str(lon)
                    else: db.add(AppSetting(key="longitude", value=str(lon)))
                else:
                    raise HTTPException(status_code=400, detail=f"No se pudieron encontrar las coordenadas para la ciudad '{s.value}'.")"""

web = web.replace(old_save_settings, new_save_settings)

# 4. Replace getattr in update search
web = web.replace("db_search.condition = getattr(search, 'condition', None)", "db_search.condition = search.condition")

with open("web.py", "w", encoding="utf-8") as f:
    f.write(web)
