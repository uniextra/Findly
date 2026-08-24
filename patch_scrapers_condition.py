import re

with open("wallapop.py", "r", encoding="utf-8") as f:
    wallapop = f.read()

# Update signature
old_sig = 'def search_items(keywords: str, min_price: Optional[float] = None, max_price: Optional[float] = None, distance_in_km: Optional[int] = None) -> List[Dict]:'
new_sig = 'def search_items(keywords: str, min_price: Optional[float] = None, max_price: Optional[float] = None, distance_in_km: Optional[int] = None, condition: Optional[str] = None) -> List[Dict]:'
wallapop = wallapop.replace(old_sig, new_sig)

# Add mapping
condition_logic = """
    if min_price is not None:
        params["min_sale_price"] = min_price
    if max_price is not None:
        params["max_sale_price"] = max_price

    if condition:
        # Map generic condition to Wallapop condition
        w_map = {
            "new": "new",
            "mint": "as_good_as_new",
            "good": "good",
            "fair": "fair",
            "poor": "has_given_it_all"
        }
        mapped = w_map.get(condition)
        if mapped:
            params["condition"] = mapped
"""
wallapop = wallapop.replace("""
    if min_price is not None:
        params["min_sale_price"] = min_price
    if max_price is not None:
        params["max_sale_price"] = max_price
""", condition_logic)

with open("wallapop.py", "w", encoding="utf-8") as f:
    f.write(wallapop)


with open("vinted.py", "r", encoding="utf-8") as f:
    vinted = f.read()

# Update signature
old_sig_v = 'def search_vinted(keywords: str, min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[Dict]:'
new_sig_v = 'def search_vinted(keywords: str, min_price: Optional[float] = None, max_price: Optional[float] = None, condition: Optional[str] = None) -> List[Dict]:'
vinted = vinted.replace(old_sig_v, new_sig_v)

# Add mapping
cond_logic_v = """
    if min_price is not None:
        params["price_from"] = min_price
    if max_price is not None:
        params["price_to"] = max_price

    if condition:
        # Map generic condition to Vinted status_ids array
        v_map = {
            "new": "6,1", # Nuevo con y sin etiquetas
            "mint": "2", # Muy bueno
            "good": "3", # Bueno
            "fair": "4", # Satisfactorio
            "poor": "" # No equivalent in Vinted really, but we can omit or pass nothing
        }
        mapped = v_map.get(condition)
        if mapped:
            params["status_ids"] = mapped
"""
vinted = vinted.replace("""
    if min_price is not None:
        params["price_from"] = min_price
    if max_price is not None:
        params["price_to"] = max_price
""", cond_logic_v)

with open("vinted.py", "w", encoding="utf-8") as f:
    f.write(vinted)


# Also need to update scheduler.py!
with open("scheduler.py", "r", encoding="utf-8") as f:
    sched = f.read()

sched = sched.replace('items.extend(search_items(search.keywords, search.min_price, search.max_price, search.distance_in_km))', 'items.extend(search_items(search.keywords, search.min_price, search.max_price, search.distance_in_km, search.condition))')
sched = sched.replace('items.extend(search_vinted(search.keywords, search.min_price, search.max_price))', 'items.extend(search_vinted(search.keywords, search.min_price, search.max_price, search.condition))')

# Update web link params in scheduler.py
sched_link = """
            if search.min_price: params["min_sale_price"] = search.min_price
            if search.max_price: params["max_sale_price"] = search.max_price
            
            if search.condition:
                w_map = {"new": "new", "mint": "as_good_as_new", "good": "good", "fair": "fair", "poor": "has_given_it_all"}
                if search.condition in w_map: params["condition"] = w_map[search.condition]
                
            web_url = f"{base_web_url}?{urllib.parse.urlencode(params)}"
            
            v_params = {"search_text": search.keywords}
            if search.condition:
                v_map = {"new": "6,1", "mint": "2", "good": "3", "fair": "4"}
                if search.condition in v_map: v_params["status_ids"] = v_map[search.condition]
            vinted_url = f"https://www.vinted.{vinted_domain}/catalog?{urllib.parse.urlencode(v_params)}"
"""
sched = re.sub(r'            if search\.min_price: params\["min_sale_price"\].*?vinted_url = f"https://www\.vinted\.\{vinted_domain\}/catalog\?search_text=\{search\.keywords\}"', sched_link.strip(), sched, flags=re.DOTALL)

with open("scheduler.py", "w", encoding="utf-8") as f:
    f.write(sched)
