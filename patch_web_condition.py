import re

with open("web.py", "r", encoding="utf-8") as f:
    web = f.read()

# Add condition to SearchCreate
web = web.replace('distance_in_km: Optional[int] = None\n    platform: str = "both"', 'distance_in_km: Optional[int] = None\n    condition: Optional[str] = None\n    platform: str = "both"')

# Update Search creation
creation_old = """    new_search = Search(
        keywords=search.keywords,
        min_price=search.min_price,
        max_price=search.max_price,
        distance_in_km=search.distance_in_km,
        platform=search.platform,
        chat_id=chat_id
    )"""
creation_new = """    new_search = Search(
        keywords=search.keywords,
        min_price=search.min_price,
        max_price=search.max_price,
        distance_in_km=search.distance_in_km,
        condition=search.condition,
        platform=search.platform,
        chat_id=chat_id
    )"""
web = web.replace(creation_old, creation_new)

# Update Search update endpoint
update_old = """
        db_search.min_price = search.min_price
        db_search.max_price = search.max_price
        db_search.distance_in_km = search.distance_in_km
        db_search.platform = search.platform
"""
update_new = """
        db_search.min_price = search.min_price
        db_search.max_price = search.max_price
        db_search.distance_in_km = search.distance_in_km
        db_search.condition = getattr(search, 'condition', None)
        db_search.platform = search.platform
"""
web = web.replace(update_old, update_new)

with open("web.py", "w", encoding="utf-8") as f:
    f.write(web)
