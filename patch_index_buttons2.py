import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

new_cond_ui = """<div class="flex flex-wrap gap-2">
                                    <button type="button" @click="formSearch.condition = ''" :class="formSearch.condition === '' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_any') }}</button>
                                    <button type="button" @click="formSearch.condition = 'new'" :class="formSearch.condition === 'new' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_new') }}</button>
                                    <button type="button" @click="formSearch.condition = 'mint'" :class="formSearch.condition === 'mint' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_mint') }}</button>
                                    <button type="button" @click="formSearch.condition = 'good'" :class="formSearch.condition === 'good' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_good') }}</button>
                                    <button type="button" @click="formSearch.condition = 'fair'" :class="formSearch.condition === 'fair' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_fair') }}</button>
                                    <button type="button" @click="formSearch.condition = 'poor'" :class="formSearch.condition === 'poor' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_poor') }}</button>
                                </div>"""

html = re.sub(r'<select v-model="formSearch\.condition".*?</select>', new_cond_ui, html, flags=re.DOTALL)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
