import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add new variables to Vue setup
vars_to_add = """
        const showSuggestions = Vue.ref(false)
        const locationSuggestions = Vue.ref([])
        const isSearchingLocation = Vue.ref(false)
        let locationTimeout = null

        const handleLocationInput = () => {
            if (locationTimeout) clearTimeout(locationTimeout)
            if (!settings.value.location || settings.value.location.length < 3) {
                showSuggestions.value = false
                locationSuggestions.value = []
                return
            }
            locationTimeout = setTimeout(async () => {
                isSearchingLocation.value = true
                try {
                    const res = await fetch('/api/location/search?q=' + encodeURIComponent(settings.value.location))
                    if (res.ok) {
                        locationSuggestions.value = await res.json()
                        showSuggestions.value = locationSuggestions.value.length > 0
                    }
                } catch (e) {
                    console.error("Geocoding failed", e)
                } finally {
                    isSearchingLocation.value = false
                }
            }, 500)
        }

        const selectLocation = (loc) => {
            settings.value.location = loc.display_name
            showSuggestions.value = false
        }
"""
html = html.replace("const saveSearch = async () => {", vars_to_add + "\n        const saveSearch = async () => {")

# Add to return block
return_adds = """
            showSuggestions,
            locationSuggestions,
            isSearchingLocation,
            handleLocationInput,
            selectLocation,
"""
html = html.replace("return {", "return {\n" + return_adds)

# Update the UI
old_ui = """                    <!-- Location -->
                    <div class="mb-6">
                        <label class="block text-sm font-medium text-slate-700 mb-1">{{ t('location_label') }}</label>
                        <input type="text" v-model="settings.location" class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-shadow outline-none" placeholder="Madrid, 28001...">
                        <p class="text-xs text-slate-500 mt-1">Usado para calcular las distancias en Wallapop (Ej: Madrid, 28001)</p>
                    </div>"""

new_ui = """                    <!-- Location -->
                    <div class="mb-6">
                        <label class="block text-sm font-medium text-slate-700 mb-1">{{ t('location_label') }}</label>
                        <div class="relative">
                            <input type="text" v-model="settings.location" @input="handleLocationInput" @focus="settings.location && settings.location.length >= 3 && locationSuggestions.length > 0 ? showSuggestions = true : null" class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-shadow outline-none" placeholder="Madrid, 28001...">
                            
                            <!-- Autocomplete dropdown -->
                            <div v-if="showSuggestions" class="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto">
                                <div v-if="isSearchingLocation" class="px-4 py-2 text-sm text-gray-500">Buscando...</div>
                                <ul v-else>
                                    <li v-for="loc in locationSuggestions" :key="loc.place_id" @click="selectLocation(loc)" class="px-4 py-2 text-sm hover:bg-emerald-50 cursor-pointer border-b border-gray-100 last:border-0 truncate">
                                        {{ loc.display_name }}
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <p class="text-xs text-slate-500 mt-1">Usado para calcular las distancias en Wallapop (Ej: Madrid, 28001)</p>
                    </div>"""

html = html.replace(old_ui, new_ui)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
