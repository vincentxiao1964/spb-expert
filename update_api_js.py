
import os

api_js_path = r"d:\spb-expert11\frontend\src\common\api.js"

new_code = """
export const uploadFile = (options) => {
    return new Promise((resolve, reject) => {
        const token = uni.getStorageSync('token');
        const header = options.header || {};
        if (token) {
            header['Authorization'] = 'Bearer ' + token;
        }

        uni.uploadFile({
            url: BASE_URL + options.url,
            filePath: options.filePath,
            name: options.name || 'file',
            formData: options.formData || {},
            header: header,
            success: (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    // uni.uploadFile returns data as string
                    let data = res.data;
                    try {
                        data = JSON.parse(res.data);
                    } catch (e) {}
                    resolve(data);
                } else {
                    reject(res);
                }
            },
            fail: (err) => {
                reject(err);
            }
        });
    });
}
"""

try:
    with open(api_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "export const uploadFile" not in content:
        with open(api_js_path, 'a', encoding='utf-8') as f:
            f.write(new_code)
        print(f"Added uploadFile to {api_js_path}")
    else:
        print("uploadFile already exists")
        
except Exception as e:
    print(f"Error updating api.js: {e}")
