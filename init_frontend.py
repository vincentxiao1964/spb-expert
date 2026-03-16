import os

base_dir = r'D:\spb-expert11\frontend'
dirs = [
    r'pages\index',
    r'pages\category',
    r'pages\cart',
    r'pages\user',
    r'static',
    r'common'
]

for d in dirs:
    path = os.path.join(base_dir, d)
    os.makedirs(path, exist_ok=True)
    print(f"Created {path}")

# Create pages.json
pages_json = """{
	"pages": [
		{
			"path": "pages/index/index",
			"style": {
				"navigationBarTitleText": "Marine Mall"
			}
		},
		{
			"path": "pages/category/category",
			"style": {
				"navigationBarTitleText": "Categories"
			}
		},
		{
			"path": "pages/cart/cart",
			"style": {
				"navigationBarTitleText": "Shopping Cart"
			}
		},
		{
			"path": "pages/user/user",
			"style": {
				"navigationBarTitleText": "Me"
			}
		}
	],
	"globalStyle": {
		"navigationBarTextStyle": "black",
		"navigationBarTitleText": "SPB Expert",
		"navigationBarBackgroundColor": "#F8F8F8",
		"backgroundColor": "#F8F8F8"
	},
	"tabBar": {
		"color": "#7A7E83",
		"selectedColor": "#3cc51f",
		"borderStyle": "black",
		"backgroundColor": "#ffffff",
		"list": [{
				"pagePath": "pages/index/index",
				"text": "Home"
			}, {
				"pagePath": "pages/category/category",
				"text": "Category"
			},
            {
				"pagePath": "pages/cart/cart",
				"text": "Cart"
			},
            {
				"pagePath": "pages/user/user",
				"text": "Me"
			}
		]
	}
}"""

with open(os.path.join(base_dir, 'pages.json'), 'w', encoding='utf-8') as f:
    f.write(pages_json)

# Create manifest.json (Minimal)
manifest_json = """{
	"name": "spb-expert11",
	"appid": "",
	"description": "",
	"versionName": "1.0.0",
	"versionCode": "100",
	"transformPx": false,
	"app-plus": {
		"modules": {}
	},
	"quickapp": {},
	"mp-weixin": {
		"appid": "",
		"setting": {
			"urlCheck": false
		},
		"usingComponents": true
	}
}"""
with open(os.path.join(base_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
    f.write(manifest_json)

# Create main.js
main_js = """import Vue from 'vue'
import App from './App'

Vue.config.productionTip = false

App.mpType = 'app'

const app = new Vue({
    ...App
})
app.$mount()
"""
with open(os.path.join(base_dir, 'main.js'), 'w', encoding='utf-8') as f:
    f.write(main_js)

# Create App.vue
app_vue = """<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style>
	/* Global CSS */
    view {
        box-sizing: border-box;
    }
</style>
"""
with open(os.path.join(base_dir, 'App.vue'), 'w', encoding='utf-8') as f:
    f.write(app_vue)

print("Created Project Config Files")
