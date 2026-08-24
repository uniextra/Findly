import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add condition to formSearch
html = html.replace("distance_index: 3, wallapop: true, vinted: true }", "distance_index: 3, condition: '', wallapop: true, vinted: true }")

# Add condition to reset form
html = html.replace("distance_index: 3,\n                wallapop: true,\n                vinted: true\n            }", "distance_index: 3,\n                condition: '',\n                wallapop: true,\n                vinted: true\n            }")

# Add condition translation strings
html = html.replace('distance: "Distancia", any: "Cualquiera",', 'distance: "Distancia", any: "Cualquiera", condition: "Estado", cond_any: "Cualquiera", cond_new: "Nuevo (etiquetas/sin etiquetas)", cond_mint: "Como nuevo / Muy bueno", cond_good: "En buen estado / Bueno", cond_fair: "Bastante usado / Satisfactorio", cond_poor: "Lo ha dado todo",')
html = html.replace('distance: "Distance", any: "Tous",', 'distance: "Distance", any: "Tous", condition: "État", cond_any: "Tous", cond_new: "Neuf (avec/sans étiquettes)", cond_mint: "Très bon état", cond_good: "Bon état", cond_fair: "Satisfaisant", cond_poor: "Très usé",')
html = html.replace('distance: "Distanza", any: "Qualsiasi",', 'distance: "Distanza", any: "Qualsiasi", condition: "Condizione", cond_any: "Qualsiasi", cond_new: "Nuovo (con/senza cartellino)", cond_mint: "Ottimo / Molto buono", cond_good: "Buono", cond_fair: "Discreto / Soddisfacente", cond_poor: "Molto usato",')
html = html.replace('distance: "Distǽncia", any: "Qualquer",', 'distance: "Distância", any: "Qualquer", condition: "Estado", cond_any: "Qualquer", cond_new: "Novo (com/sem etiquetas)", cond_mint: "Como novo / Muito bom", cond_good: "Bom estado / Bom", cond_fair: "Usado / Satisfatório", cond_poor: "Muito usado",')
html = html.replace('distance: "Distance", any: "Any",', 'distance: "Distance", any: "Any", condition: "Condition", cond_any: "Any", cond_new: "New (with/without tags)", cond_mint: "Like new / Very good", cond_good: "Good", cond_fair: "Fair / Satisfactory", cond_poor: "Poor",')

# Add to payload
payload_old = """const payload = {
                keywords: formSearch.value.keywords,
                min_price: minPrice,
                max_price: maxPrice === 1500 ? null : maxPrice,
                distance_in_km: distance,
                platform: platformStr
            }"""
payload_new = """const payload = {
                keywords: formSearch.value.keywords,
                min_price: minPrice,
                max_price: maxPrice === 1500 ? null : maxPrice,
                distance_in_km: distance,
                condition: formSearch.value.condition || null,
                platform: platformStr
            }"""
html = html.replace(payload_old, payload_new)

# Add to editSearch
edit_old = """
            if (search.distance_in_km === 5) dIndex = 0;
            else if (search.distance_in_km === 10) dIndex = 1;
            else if (search.distance_in_km === 30) dIndex = 2;

            minPriceIndex.value = getIndexForPrice(search.min_price || 0);
            maxPriceIndex.value = getIndexForPrice(search.max_price || 1500);

            formSearch.value = {
                keywords: search.keywords,
                min_price: search.min_price || 0,
                max_price: search.max_price || 1500,
                distance_index: dIndex,
                wallapop: search.platform === 'both' || search.platform === 'wallapop',
                vinted: search.platform === 'both' || search.platform === 'vinted'
            }
"""
edit_new = """
            if (search.distance_in_km === 5) dIndex = 0;
            else if (search.distance_in_km === 10) dIndex = 1;
            else if (search.distance_in_km === 30) dIndex = 2;

            minPriceIndex.value = getIndexForPrice(search.min_price || 0);
            maxPriceIndex.value = getIndexForPrice(search.max_price || 1500);

            formSearch.value = {
                keywords: search.keywords,
                min_price: search.min_price || 0,
                max_price: search.max_price || 1500,
                distance_index: dIndex,
                condition: search.condition || '',
                wallapop: search.platform === 'both' || search.platform === 'wallapop',
                vinted: search.platform === 'both' || search.platform === 'vinted'
            }
"""
html = html.replace(edit_old, edit_new)

# Inject the condition UI inside the grid cols, right after distance
ui_condition = """
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">{{ t('condition') }}</label>
                                    <select v-model="formSearch.condition" class="w-full rounded-md border-gray-300 shadow-sm py-2 px-3 focus:border-emerald-500 focus:ring-emerald-500">
                                        <option value="">{{ t('cond_any') }}</option>
                                        <option value="new">{{ t('cond_new') }}</option>
                                        <option value="mint">{{ t('cond_mint') }}</option>
                                        <option value="good">{{ t('cond_good') }}</option>
                                        <option value="fair">{{ t('cond_fair') }}</option>
                                        <option value="poor">{{ t('cond_poor') }}</option>
                                    </select>
                                </div>
"""
# Find distance element to replace
distance_el = """<div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">{{ t('distance') }} (Wallapop)</label>
                                    <input type="range" v-model="formSearch.distance_index" min="0" max="3" step="1" class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer">
                                    <div class="text-sm font-medium text-emerald-600 mt-2 text-center">{{ [5, 10, 30, t('any')][formSearch.distance_index] }} <span v-if="formSearch.distance_index < 3">km</span></div>
                                </div>"""

html = html.replace(distance_el, distance_el + ui_condition)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
