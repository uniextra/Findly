import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add translation string `location_label`
html = html.replace('wallapop_interval: "Intervalo Wallapop (min)"', 'location_label: "Ciudad o Código Postal", wallapop_interval: "Intervalo Wallapop (min)"')
html = html.replace('wallapop_interval: "Intervalle Wallapop (min)"', 'location_label: "Ville ou Code Postal", wallapop_interval: "Intervalle Wallapop (min)"')
html = html.replace('wallapop_interval: "Intervallo Wallapop (min)"', 'location_label: "Città o CAP", wallapop_interval: "Intervallo Wallapop (min)"')
html = html.replace('wallapop_interval: "Intervalo Wallapop (min)"', 'location_label: "Cidade ou Código Postal", wallapop_interval: "Intervalo Wallapop (min)"')
html = html.replace('wallapop_interval: "Wallapop Interval (mins)"', 'location_label: "City or Postal Code", wallapop_interval: "Wallapop Interval (mins)"')

# Add to state and payload
html = html.replace("region: 'es',", "region: 'es',\n                    location: '',")
html = html.replace("s.region !== o.region ||", "s.region !== o.region ||\n                    s.location !== o.location ||")
html = html.replace("{ key: 'region', value: settings.value.region },", "{ key: 'region', value: settings.value.region },\n                { key: 'location', value: settings.value.location },")

# Add to UI under region
ui_html = """
                    <!-- Location -->
                    <div class="mt-4">
                        <label class="block text-sm font-medium text-slate-700 mb-1">{{ t('location_label') }}</label>
                        <input type="text" v-model="settings.location" class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-shadow outline-none" placeholder="Madrid, 28001...">
                        <p class="text-xs text-slate-500 mt-1">Usado para calcular las distancias en Wallapop (Ej: Madrid, 28001)</p>
                    </div>"""
html = html.replace('</select>\n                    </div>', '</select>\n                    </div>' + ui_html)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
