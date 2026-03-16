
import os

file_path = r'd:\spb-expert11\frontend\src\main.js'

content = """import Vue from 'vue'
import VueI18n from 'vue-i18n'
import App from './App'
import en from './locale/en.json'
import zhHans from './locale/zh-Hans.json'

Vue.config.productionTip = false

Vue.use(VueI18n)

const i18n = new VueI18n({
  locale: uni.getStorageSync('locale') || 'zh-Hans', // default locale
  messages: {
    'en': en,
    'zh-Hans': zhHans
  }
})

// Expose i18n to uni object for non-component usage
uni.$i18n = i18n

App.mpType = 'app'

const app = new Vue({
    i18n,
    ...App
})
app.$mount()
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
    print("Successfully updated main.js")
