import requests
import logging
import random
from typing import List, Dict, Optional
from database import get_setting

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def search_vinted(keywords: str, min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[Dict]:
    """
    Search for items on Vinted.
    """
    region = get_setting("region", "es").lower()
    domain = "co.uk" if region == "uk" else region
    
    url = f"https://www.vinted.{domain}/api/v2/catalog/items"
    
    params = {
        "search_text": keywords,
        "order": "newest_first",
        "per_page": 50,
    }
    if min_price is not None:
        params["price_from"] = min_price
    if max_price is not None:
        params["price_to"] = max_price

    session = requests.Session()
    retries = 0
    max_retries = 3

    while retries < max_retries:
        try:
            # Rotate user agent
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": f"{region}-{region.upper()},en;q=0.9",
                "Host": f"www.vinted.{domain}"
            }
            session.headers.update(headers)
            
            # Fetch cookies if we don't have them
            if 'access_token_web' not in [c.name for c in session.cookies]:
                session.get(f"https://www.vinted.{domain}/", timeout=10)
            
            logger.info(f"Searching Vinted (Attempt {retries+1}/{max_retries}): {keywords}")
            response = session.get(url, params=params, timeout=10)
            
            if response.status_code in (401, 403, 404):
                logger.warning(f"Vinted API returned {response.status_code}. Resetting session.")
                session.cookies.clear()
                retries += 1
                continue
                
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", [])[:50]  # Hard limit to first 50 results
            
            import time
            results = []
            now_ts = int(time.time())
            
            for item in items:
                try:
                    # Filter by timestamp (less than 20 minutes old)
                    photo = item.get("photo", {})
                    if photo:
                        high_res = photo.get("high_resolution", {})
                        timestamp = high_res.get("timestamp")
                        if timestamp:
                            if (now_ts - int(timestamp)) > 20 * 60:
                                continue # Too old, skip it
                    
                    item_id = item.get("id")
                    title = item.get("title")
                    
                    price_data = item.get("price")
                    if isinstance(price_data, dict):
                        price = float(price_data.get("amount", 0))
                        currency = price_data.get("currency_code", "EUR")
                    else:
                        # Fallback just in case Vinted changes back to string/float
                        price = float(price_data or 0)
                        currency = item.get("currency", "EUR")
                    
                    url_slug = item.get("url")
                    
                    images = item.get("photos", [])
                    image = images[0].get("url") if images else None
                    if not image and photo:
                        image = photo.get("url")
                    
                    if item_id and title:
                        results.append({
                            "id": f"vinted_{item_id}",
                            "title": title,
                            "price": price,
                            "currency": currency,
                            "url": url_slug,
                            "image": image,
                            "platform": "Vinted"
                        })
                except Exception as e:
                    logger.error(f"Error parsing Vinted item: {e}")
                    
            return results

        except requests.RequestException as e:
            logger.error(f"Error searching Vinted: {e}")
            session.cookies.clear()
            retries += 1
            
    logger.error("Max retries reached for Vinted search.")
    return []
