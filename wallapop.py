import requests
import logging
import random
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

BASE_URL = "https://api.wallapop.com/api/v3"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def search_items(keywords: str, min_price: Optional[float] = None, max_price: Optional[float] = None, distance_in_km: Optional[int] = None) -> List[Dict]:
    """
    Search for items on Wallapop.
    """
    url = f"{BASE_URL}/search?"
    
    params = {
        "keywords": keywords,
        "order_by": "newest",
        "latitude": 41.4231,
        "longitude": 2.188,
        "country_code": "ES",
        "time_filter": "today",
        "source": "search_box"
    }

    if distance_in_km is not None:
        params["distance_in_km"] = distance_in_km

    if min_price is not None:
        params["min_sale_price"] = min_price
    if max_price is not None:
        params["max_sale_price"] = max_price

    session = requests.Session()
    retries = 0
    max_retries = 3

    while retries < max_retries:
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd, identity",
                "Accept-Language": "en",
                "Connection": "keep-alive",
                "Host": "api.wallapop.com",
                "Origin": "https://es.wallapop.com",
                "Referer": "https://es.wallapop.com/",
                "X-DeviceOS": "0"
            }
            session.headers.update(headers)
            
            logger.info(f"Searching Wallapop (Attempt {retries+1}/{max_retries}): {keywords}")
            response = session.get(url, params=params, timeout=10)
            
            if response.status_code in (401, 403, 404):
                logger.warning(f"Wallapop API returned {response.status_code}. Resetting session.")
                session.cookies.clear()
                # Dummy request to regenerate basic cookies/fingerprint
                session.get("https://es.wallapop.com/", timeout=10)
                retries += 1
                continue
                
            response.raise_for_status()
            
            data = response.json()
            
            # Parse new response structure
            try:
                items = data.get("data", {}).get("section", {}).get("payload", {}).get("items", [])
            except AttributeError:
                items = []
            
            results = []
            for item in items:
                # Extract relevant fields
                try:
                    item_id = item.get("id")
                    title = item.get("title")
                    
                    # Price is now a dict: {'amount': 250.0, 'currency': 'EUR'}
                    price_data = item.get("price", {})
                    if isinstance(price_data, dict):
                        price = price_data.get("amount")
                        currency = price_data.get("currency", "EUR")
                    else:
                        price = price_data
                        currency = "EUR"

                    url_slug = item.get("web_slug")
                    
                    # Images is a list of dicts
                    images = item.get("images", [])
                    image = None
                    if images and isinstance(images, list):
                        image = images[0].get("urls", {}).get("small")
                    
                    if item_id and title:
                        results.append({
                            "id": str(item_id),
                            "title": title,
                            "price": price,
                            "currency": currency,
                            "url": f"https://es.wallapop.com/item/{url_slug}" if url_slug else None,
                            "image": image,
                            "platform": "Wallapop"
                        })
                except Exception as e:
                    logger.error(f"Error parsing Wallapop item: {e}")
                    
            return results

        except requests.RequestException as e:
            logger.error(f"Error searching Wallapop: {e}")
            session.cookies.clear()
            retries += 1
            
    logger.error("Max retries reached for Wallapop search.")
    return []
