import re

with open("web.py", "r", encoding="utf-8") as f:
    web = f.read()

web_replace = """@app.get("/api/settings")
def get_settings():
    return {
        "telegram_token": get_setting("telegram_token", ""),
        "allowed_chat_ids": get_setting("allowed_chat_ids", ""),
        "region": get_setting("region", "es"),
        "wallapop_interval": get_setting("wallapop_interval", "5"),
        "vinted_interval": get_setting("vinted_interval", "5")
    }"""
web = re.sub(r'@app\.get\("/api/settings"\).*?"vinted_interval", "5"\)\n\s*\}', web_replace, web, flags=re.DOTALL)

with open("web.py", "w", encoding="utf-8") as f:
    f.write(web)
