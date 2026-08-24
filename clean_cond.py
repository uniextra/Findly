import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Strip ALL existing <!-- Condition --> blocks, no matter where they are
# The block starts with <!-- Condition --> and ends with the closing div of its button group.
# Wait, it's:
# <!-- Condition -->
# <div class="mt-4">
# ...
# </div>
# </div>
html = re.sub(r'\s*<!-- Condition -->.*?</div>\s*</div>', '', html, flags=re.DOTALL)

# 2. Insert it at the end of the form grid, BEFORE <div class="lg:col-span-2 flex flex-col justify-center">
good_condition = """

                          <!-- Condition -->
                          <div class="lg:col-span-5 mb-2 mt-2">
                              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('condition') }}</label>
                              <div class="flex flex-wrap gap-2">
                                  <button type="button" @click="formSearch.condition = ''" :class="formSearch.condition === '' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-4 py-1.5 rounded-full border text-sm font-semibold transition-colors">{{ t('cond_any') }}</button>
                                  <button type="button" @click="formSearch.condition = 'new'" :class="formSearch.condition === 'new' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-4 py-1.5 rounded-full border text-sm font-semibold transition-colors">{{ t('cond_new') }}</button>
                                  <button type="button" @click="formSearch.condition = 'mint'" :class="formSearch.condition === 'mint' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-4 py-1.5 rounded-full border text-sm font-semibold transition-colors">{{ t('cond_mint') }}</button>
                                  <button type="button" @click="formSearch.condition = 'good'" :class="formSearch.condition === 'good' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-4 py-1.5 rounded-full border text-sm font-semibold transition-colors">{{ t('cond_good') }}</button>
                                  <button type="button" @click="formSearch.condition = 'fair'" :class="formSearch.condition === 'fair' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-4 py-1.5 rounded-full border text-sm font-semibold transition-colors">{{ t('cond_fair') }}</button>
                                  <button type="button" @click="formSearch.condition = 'poor'" :class="formSearch.condition === 'poor' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-4 py-1.5 rounded-full border text-sm font-semibold transition-colors">{{ t('cond_poor') }}</button>
                              </div>
                          </div>"""

html = html.replace('<div class="lg:col-span-2 flex flex-col justify-center">', good_condition + '\n                          <div class="lg:col-span-2 flex flex-col justify-center">')

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
