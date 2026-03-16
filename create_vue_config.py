
template = """module.exports = {
  transpileDependencies: ['@dcloudio/uni-ui'],
  chainWebpack: config => {
    const rules = ['css', 'postcss', 'scss', 'sass', 'less', 'stylus'];
    rules.forEach(rule => {
      const ruleDef = config.module.rules.get(rule);
      if (ruleDef) {
        ruleDef.oneOfs.store.forEach(oneOf => {
            if (oneOf.uses.has('postcss-loader')) {
                oneOf.use('postcss-loader').tap(options => {
                    if (options && options.config) {
                        delete options.config;
                    }
                    return options;
                });
            }
        });
      }
    });
  }
}
"""

file_path = r"d:\spb-expert11\frontend\vue.config.js"

try:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"Created {file_path}")
except Exception as e:
    print(f"Error creating file: {e}")
