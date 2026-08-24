import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Remove the duplicate getVintedUrl
duplicate = """
        const getVintedUrl = (s) => {
            let u = new URL('https://www.vinted.es/catalog');
            u.searchParams.set('search_text', s.keywords);
            u.searchParams.set('order', 'newest_first');
            if (s.min_price) u.searchParams.set('price_from', s.min_price);
            if (s.max_price) u.searchParams.set('price_to', s.max_price);
            return u.toString();
        }"""

html = html.replace(duplicate, "")

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
