import os

content = """const path = require('path')
module.exports = {
  parser: require('postcss-comment'),
  plugins: {
    'postcss-import': {
      resolve(id, basedir, importOptions) {
        if (id.startsWith('~@/')) {
          return path.resolve(process.env.UNI_INPUT_DIR, id.substr(3))
        }
        if (id.startsWith('@/')) {
          return path.resolve(process.env.UNI_INPUT_DIR, id.substr(2))
        }
        if (id.startsWith('/') && !id.startsWith('//')) {
          return path.resolve(process.env.UNI_INPUT_DIR, id.substr(1))
        }
        return id
      }
    },
    'autoprefixer': {
      overrideBrowserslist: [
        "Android >= 4",
        "ios >= 8"
      ],
      remove: false
    },
    '@dcloudio/vue-cli-plugin-uni/packages/postcss': {}
  }
}
"""

file_path = r"d:\spb-expert11\frontend\postcss.config.js"

try:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {file_path}")
except Exception as e:
    print(f"Error creating file: {e}")
