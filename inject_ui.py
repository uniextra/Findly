import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

ui_html = """
                    <!-- Location -->
                    <div class="mt-4">
                        <label class="block text-sm font-medium text-slate-700 mb-1">{{ t('location_label') }}</label>
                        <input type="text" v-model="settings.location" class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-shadow outline-none" placeholder="Madrid, 28001...">
                        <p class="text-xs text-slate-500 mt-1">Usado para calcular las distancias en Wallapop (Ej: Madrid, 28001)</p>
                    </div>
"""

# Find the end of the region select block
html = re.sub(r'(<select v-model="settings\.region".*?</select>\s*</div>)', r'\1' + ui_html, html, flags=re.DOTALL)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
