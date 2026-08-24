import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

old_cond_ui = """                            <div class="mt-4">
                                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('condition') }}</label>
                                <select v-model="formSearch.condition" class="w-full rounded-md border-gray-300 shadow-sm py-2 px-3 focus:border-primary focus:ring-primary text-sm">
                                    <option value="">{{ t('cond_any') }}</option>
                                    <option value="new">{{ t('cond_new') }}</option>
                                    <option value="mint">{{ t('cond_mint') }}</option>
                                    <option value="good">{{ t('cond_good') }}</option>
                                    <option value="fair">{{ t('cond_fair') }}</option>
                                    <option value="poor">{{ t('cond_poor') }}</option>
                                </select>
                            </div>"""

new_cond_ui = """                            <div class="mt-4">
                                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('condition') }}</label>
                                <div class="flex flex-wrap gap-2">
                                    <button type="button" @click="formSearch.condition = ''" :class="formSearch.condition === '' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_any') }}</button>
                                    <button type="button" @click="formSearch.condition = 'new'" :class="formSearch.condition === 'new' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_new') }}</button>
                                    <button type="button" @click="formSearch.condition = 'mint'" :class="formSearch.condition === 'mint' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_mint') }}</button>
                                    <button type="button" @click="formSearch.condition = 'good'" :class="formSearch.condition === 'good' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_good') }}</button>
                                    <button type="button" @click="formSearch.condition = 'fair'" :class="formSearch.condition === 'fair' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_fair') }}</button>
                                    <button type="button" @click="formSearch.condition = 'poor'" :class="formSearch.condition === 'poor' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_poor') }}</button>
                                </div>
                            </div>"""

html = html.replace(old_cond_ui, new_cond_ui)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
