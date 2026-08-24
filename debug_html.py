import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Delete ALL occurrences of <!-- Condition --> ... </div> blocks
html = re.sub(r'\s*<!-- Condition -->\s*<div.*?</div>\s*</div>\s*</div>', '\n                          </div>', html, flags=re.DOTALL)
html = re.sub(r'\s*<!-- Condition -->.*?</div>\s*</div>\s*', '\n', html, flags=re.DOTALL)

# Let's be surgical.
# Get a fresh copy from git and redo the condition patch correctly? No, git doesn't have it.
