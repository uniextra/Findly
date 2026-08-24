import re

with open("scheduler.py", "r", encoding="utf-8") as f:
    scheduler = f.read()

scheduler_replace = """
        if new_items_count > max_items_to_notify:
            region = get_setting("region", "es").lower()
            wallapop_region = region if region in ["es", "it", "pt"] else "es"
            vinted_domain = "co.uk" if region == "uk" else region
            
            base_web_url = f"https://{wallapop_region}.wallapop.com/search"
            params = {
                "keywords": search.keywords,
                "order_by": "newest",
                "time_filter": "today"
            }
            if search.min_price: params["min_sale_price"] = search.min_price
            if search.max_price: params["max_sale_price"] = search.max_price
                
            web_url = f"{base_web_url}?{urllib.parse.urlencode(params)}"
            vinted_url = f"https://www.vinted.{vinted_domain}/catalog?search_text={search.keywords}"
            
            summary_msg = (
                f"⚠️ <b>Se han encontrado {new_items_count} artículos nuevos.</b>\\n"
                f"Solo se han mostrado los primeros {max_items_to_notify}.\\n"
            )
            if target_platform == "wallapop":
                 summary_msg += f"<a href='{web_url}'>Ver todos los resultados en Wallapop</a>"
            elif target_platform == "vinted":
                 summary_msg += f"<a href='{vinted_url}'>Ver todos los resultados en Vinted</a>"
            else:
                 summary_msg += f"<a href='{web_url}'>Ver en Wallapop</a> | <a href='{vinted_url}'>Ver en Vinted</a>"
"""
scheduler = re.sub(r'        if new_items_count > max_items_to_notify:.*?Ver en Vinted</a>"', scheduler_replace, scheduler, flags=re.DOTALL)

with open("scheduler.py", "w", encoding="utf-8") as f:
    f.write(scheduler)
