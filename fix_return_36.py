import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace("if (p == null || p >= 1500) return 28;", "if (p == null || p >= 1500) return 36;")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
