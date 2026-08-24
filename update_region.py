import re

# 1. Update vinted.py
with open("vinted.py", "r", encoding="utf-8") as f:
    vinted = f.read()

vinted_replace = """from typing import List, Dict, Optional
from database import get_setting

logger = logging.getLogger(__name__)"""
vinted = vinted.replace("from typing import List, Dict, Optional\n\nlogger = logging.getLogger(__name__)", vinted_replace)

vinted_url = """def search_vinted(keywords: str, min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[Dict]:
    \"\"\"
    Search for items on Vinted.
    \"\"\"
    region = get_setting("region", "es").lower()
    domain = "co.uk" if region == "uk" else region
    
    url = f"https://www.vinted.{domain}/api/v2/catalog/items\""""
vinted = re.sub(r'def search_vinted.*?url = "https://www\.vinted\.es/api/v2/catalog/items"', vinted_url, vinted, flags=re.DOTALL)

vinted_headers = """            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": f"{region}-{region.upper()},en;q=0.9",
                "Host": f"www.vinted.{domain}"
            }
            session.headers.update(headers)
            
            # Fetch cookies if we don't have them
            if 'access_token_web' not in [c.name for c in session.cookies]:
                session.get(f"https://www.vinted.{domain}/", timeout=10)"""
vinted = re.sub(r'            headers = \{.*?session\.get\("https://www\.vinted\.es/", timeout=10\)', vinted_headers, vinted, flags=re.DOTALL)

with open("vinted.py", "w", encoding="utf-8") as f:
    f.write(vinted)

# 2. Update wallapop.py
with open("wallapop.py", "r", encoding="utf-8") as f:
    wallapop = f.read()

wallapop_replace = """from typing import List, Dict, Optional
from database import get_setting

logger = logging.getLogger(__name__)"""
wallapop = wallapop.replace("from typing import List, Dict, Optional\n\nlogger = logging.getLogger(__name__)", wallapop_replace)

wallapop_url = """def search_items(keywords: str, min_price: Optional[float] = None, max_price: Optional[float] = None, distance_in_km: Optional[int] = None) -> List[Dict]:
    \"\"\"
    Search for items on Wallapop.
    \"\"\"
    region = get_setting("region", "es").lower()
    if region not in ["es", "it", "pt"]:
        region = "es" # Wallapop only operates in these 3
        
    url = f"{BASE_URL}/search?"
    
    params = {
        "keywords": keywords,
        "order_by": "newest",
        "latitude": 41.4231,
        "longitude": 2.188,
        "country_code": region.upper(),
        "time_filter": "today",
        "source": "search_box"
    }"""
wallapop = re.sub(r'def search_items.*?source": "search_box"\n\s*\}', wallapop_url, wallapop, flags=re.DOTALL)

wallapop_headers = """            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd, identity",
                "Accept-Language": "en",
                "Connection": "keep-alive",
                "Host": "api.wallapop.com",
                "Origin": f"https://{region}.wallapop.com",
                "Referer": f"https://{region}.wallapop.com/",
                "X-DeviceOS": "0"
            }
            session.headers.update(headers)
            
            logger.info(f"Searching Wallapop (Attempt {retries+1}/{max_retries}): {keywords}")
            response = session.get(url, params=params, timeout=10)
            
            if response.status_code in (401, 403, 404):
                logger.warning(f"Wallapop API returned {response.status_code}. Resetting session.")
                session.cookies.clear()
                # Dummy request to regenerate basic cookies/fingerprint
                session.get(f"https://{region}.wallapop.com/", timeout=10)"""
wallapop = re.sub(r'            headers = \{.*?session\.get\("https://es\.wallapop\.com/", timeout=10\)', wallapop_headers, wallapop, flags=re.DOTALL)

wallapop_url_builder = """                        results.append({
                            "id": str(item_id),
                            "title": title,
                            "price": price,
                            "currency": currency,
                            "url": f"https://{region}.wallapop.com/item/{url_slug}" if url_slug else None,"""
wallapop = re.sub(r'                        results\.append\(\{.*?url": f"https://es\.wallapop\.com/item/\{url_slug\}" if url_slug else None,', wallapop_url_builder, wallapop, flags=re.DOTALL)

with open("wallapop.py", "w", encoding="utf-8") as f:
    f.write(wallapop)

# 3. Update index.html
with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("settings = ref({ telegram_token: '', allowed_chat_ids: '' })", "settings = ref({ telegram_token: '', allowed_chat_ids: '', region: 'es' })")

settings_html = """                <!-- Scraping Intervals Box -->
                <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <h3 class="text-lg font-semibold mb-6 flex items-center gap-2 text-gray-800"><span class="material-symbols-outlined text-primary">schedule</span> Scraping & Region</h3>
                    
                    <div class="mb-6">
                        <label class="block text-sm font-medium text-gray-700 mb-1">Base Region</label>
                        <select v-model="settings.region" class="w-full rounded-md border-gray-300 shadow-sm py-2 px-3 focus:border-primary focus:ring-primary">
                            <option value="es">Spain (es)</option>
                            <option value="fr">France (fr)</option>
                            <option value="it">Italy (it)</option>
                            <option value="pt">Portugal (pt)</option>
                            <option value="uk">United Kingdom (co.uk)</option>
                        </select>
                        <p class="text-xs text-gray-500 mt-1">Select the country to adapt platform search domains.</p>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">"""
html = re.sub(r'                <!-- Scraping Intervals Box -->.*?<div class="grid grid-cols-1 md:grid-cols-2 gap-4">', settings_html, html, flags=re.DOTALL)

save_settings = """            const payload = [
                { key: 'telegram_token', value: settings.value.telegram_token },
                { key: 'allowed_chat_ids', value: settings.value.allowed_chat_ids },
                { key: 'region', value: settings.value.region },
                { key: 'wallapop_interval', value: String(settings.value.wallapop_interval) },
                { key: 'vinted_interval', value: String(settings.value.vinted_interval) }
            ]"""
html = re.sub(r'            const payload = \[\s*\{ key: \'telegram_token\'.*?value: String\(settings\.value\.vinted_interval\) \}\s*\]', save_settings, html, flags=re.DOTALL)

# Dynamic URLs in web view based on settings.region
get_wallapop_url = """        const getWallapopUrl = (s) => {
            const r = settings.value.region === 'it' || settings.value.region === 'pt' ? settings.value.region : 'es';
            let u = new URL(`https://${r}.wallapop.com/search`);
            u.searchParams.set('keywords', s.keywords);
            u.searchParams.set('order_by', 'newest');
            u.searchParams.set('time_filter', 'today');
            if (s.min_price) u.searchParams.set('min_sale_price', s.min_price);
            if (s.max_price) u.searchParams.set('max_sale_price', s.max_price);
            if (s.distance_in_km) u.searchParams.set('distance_in_km', s.distance_in_km);
            return u.toString();
        }

        const getVintedUrl = (s) => {
            const r = settings.value.region || 'es';
            const domain = r === 'uk' ? 'co.uk' : r;
            let u = new URL(`https://www.vinted.${domain}/catalog`);
            u.searchParams.set('search_text', s.keywords);
            u.searchParams.set('order', 'newest_first');
            if (s.min_price) u.searchParams.set('price_from', s.min_price);
            if (s.max_price) u.searchParams.set('price_to', s.max_price);
            return u.toString();
        }"""
html = re.sub(r'        const getWallapopUrl = \(s\) => \{.*?return u\.toString\(\);\n\s*\}', get_wallapop_url, html, flags=re.DOTALL)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
