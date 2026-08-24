import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

ui_condition = """
                          <!-- Condition -->
                          <div class="mt-4">
                              <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('condition') }}</label>
                              <select v-model="formSearch.condition" class="w-full rounded-md border-gray-300 shadow-sm py-2 px-3 focus:border-primary focus:ring-primary text-sm">
                                  <option value="">{{ t('cond_any') }}</option>
                                  <option value="new">{{ t('cond_new') }}</option>
                                  <option value="mint">{{ t('cond_mint') }}</option>
                                  <option value="good">{{ t('cond_good') }}</option>
                                  <option value="fair">{{ t('cond_fair') }}</option>
                                  <option value="poor">{{ t('cond_poor') }}</option>
                              </select>
                          </div>
"""

# We'll inject it right after the distance slider block
# The distance block ends with <span>{{ t('any') }}</span>\n                              </div>
html = re.sub(r'(<span>\{\{\s*t\(\'any\'\)\s*\}\}</span>\s*</div>)', r'\1' + ui_condition, html, flags=re.DOTALL)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
