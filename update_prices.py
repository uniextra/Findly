import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the array
old_array = r"const priceSteps = \[0, 5, 15, 30, 50, 75, 105, 140, 180, 225, 275, 330, 390, 455, 525, 600, 680, 765, 855, 950, 1050, 1155, 1265, 1380, 1500, 1625, 1755, 1890, 2030\];"
new_array = "const priceSteps = [0, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500];"
html = re.sub(old_array, new_array, html)

# Replace the max index values
html = html.replace("const maxPriceIndex = ref(28);", "const maxPriceIndex = ref(36);")
html = html.replace("maxPriceIndex.value = 28;", "maxPriceIndex.value = 36;")
html = html.replace("max='28'", "max='36'")
html = html.replace("max=\"28\"", "max=\"36\"")
html = html.replace("28 * 100", "36 * 100")

# Replace max boundary checks
html = html.replace("actualMaxPrice >= 2000", "actualMaxPrice >= 1500")
html = html.replace("pMax >= 2000", "pMax >= 1500")
html = html.replace("p == null || p >= 2000", "p == null || p >= 1500")
html = html.replace("getIndexForPrice(search.max_price || 2000)", "getIndexForPrice(search.max_price || 1500)")
html = html.replace("getIndexForPrice(maxP ? parseFloat(maxP) : 2000)", "getIndexForPrice(maxP ? parseFloat(maxP) : 1500)")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
