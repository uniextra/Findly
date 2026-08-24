import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add Vue
if 'vue.global.js' not in html:
    html = html.replace('</head>', '<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>\n</head>')

# Remove Support button
html = re.sub(r'<button[^>]*>\s*<span class="material-symbols-outlined[^>]*>help_outline</span>\s*<span[^>]*>Support</span>\s*</button>', '', html)
# Remove Settings button
html = re.sub(r'<button[^>]*>\s*<span class="material-symbols-outlined[^>]*>settings</span>\s*<span[^>]*>Settings</span>\s*</button>', '', html)
# Remove Sign In / Avatar
html = re.sub(r'<div class="flex items-center gap-4">.*?</div>\s*</div>\s*</header>', '</div></header>', html, flags=re.DOTALL)
# Remove Nav Links (Home, Discover, Watchlist) because they don't do anything
html = re.sub(r'<nav class="hidden md:flex items-center gap-6">.*?</nav>', '', html, flags=re.DOTALL)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
