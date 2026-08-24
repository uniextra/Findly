import re

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

new_features = """- **Location Geocoding**: Set your exact city or postal code with smart autocomplete. The bot will precisely calculate coordinates globally for localized searches.
- **Item Condition Filter**: Filter results precisely by item condition (New, Mint, Good, Fair, Poor). Findly automatically maps these universal conditions to both Wallapop and Vinted's native category IDs behind the scenes."""

# Insert it after Quick Add via URL
readme = readme.replace("- **Quick Add via URL**: Paste a Wallapop or Vinted URL directly in the Web UI or Telegram to auto-fill the search criteria.", 
                        f"- **Quick Add via URL**: Paste a Wallapop or Vinted URL directly in the Web UI or Telegram to auto-fill the search criteria.\n{new_features}")

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
