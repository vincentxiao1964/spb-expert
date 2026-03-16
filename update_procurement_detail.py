
import os

detail_path = r"d:\spb-expert11\frontend\src\pages\procurement\detail.vue"

old_code = """            async handleQuote(quoteId, status) {
                // Implement accept logic
                uni.showToast({ title: 'Feature coming soon', icon: 'none' });
            }"""

new_code = """            async handleQuote(quoteId, status) {
                try {
                    await request({
                        url: `/procurement/quotations/${quoteId}/`,
                        method: 'PATCH',
                        data: { status: status }
                    });
                    uni.showToast({ title: 'Updated' });
                    this.loadData();
                } catch (e) {
                    uni.showToast({ title: 'Failed', icon: 'none' });
                }
            }"""

try:
    with open(detail_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if old_code in content:
        new_content = content.replace(old_code, new_code)
        with open(detail_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {detail_path}")
    else:
        print("Could not find old code block to replace")

except Exception as e:
    print(f"Error updating detail.vue: {e}")
