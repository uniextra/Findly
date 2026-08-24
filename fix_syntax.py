import re

with open("scheduler.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace actual newlines inside the f-strings
code = code.replace('artículos nuevos.</b>\n"', 'artículos nuevos.</b>\\n"')
code = code.replace('artículos nuevos.</b>\r\n"', 'artículos nuevos.</b>\\n"')

code = code.replace('primeros {max_items_to_notify}.\n"', 'primeros {max_items_to_notify}.\\n"')
code = code.replace('primeros {max_items_to_notify}.\r\n"', 'primeros {max_items_to_notify}.\\n"')

with open("scheduler.py", "w", encoding="utf-8") as f:
    f.write(code)
