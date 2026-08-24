import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("<title>Findly - Dashboard</title>", "<title>Findly - Dashboard</title>\n    <link rel=\"icon\" type=\"image/png\" href=\"/static/favicon.png\">")

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
