import re

with open("web.py", "r", encoding="utf-8") as f:
    web = f.read()

location_api_code = """
@app.get("/api/location/search")
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
    except Exception as e:
        print(f"Error in geocoding proxy: {e}")
    return []

"""

# Insert right before @app.get("/api/settings")
web = web.replace('@app.get("/api/settings")', location_api_code + '@app.get("/api/settings")')

with open("web.py", "w", encoding="utf-8") as f:
    f.write(web)
