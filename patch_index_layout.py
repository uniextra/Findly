import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# The condition block inside distance
bad_condition = """                            <!-- Condition -->
                            <div class="mt-4">
                                <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('condition') }}</label>
                                <div class="flex flex-wrap gap-2">
                                      <button type="button" @click="formSearch.condition = ''" :class="formSearch.condition === '' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_any') }}</button>
                                      <button type="button" @click="formSearch.condition = 'new'" :class="formSearch.condition === 'new' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_new') }}</button>
                                      <button type="button" @click="formSearch.condition = 'mint'" :class="formSearch.condition === 'mint' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_mint') }}</button>
                                      <button type="button" @click="formSearch.condition = 'good'" :class="formSearch.condition === 'good' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_good') }}</button>
                                      <button type="button" @click="formSearch.condition = 'fair'" :class="formSearch.condition === 'fair' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_fair') }}</button>
                                      <button type="button" @click="formSearch.condition = 'poor'" :class="formSearch.condition === 'poor' ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'" class="px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors">{{ t('cond_poor') }}</button>
                                  </div>
                            </div>"""

# Remove it from where it is
html = html.replace(bad_condition, "")

good_condition = """                          <!-- Condition -->
                          <div class="lg:col-span-5 mb-2">
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

# Insert it AFTER the distance div closes.
# Let's find:
#                          </div>
#                          <div class="lg:col-span-2 flex flex-col justify-center">
#                              <label class="block text-sm font-medium text-gray-700 mb-3">{{ t('platforms') }}</label>

html = html.replace('                          </div>\n                          <div class="lg:col-span-2 flex flex-col justify-center">', '                          </div>\n' + good_condition + '\n                          <div class="lg:col-span-2 flex flex-col justify-center">')

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
