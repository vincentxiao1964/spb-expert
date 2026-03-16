import os

# Update pages.json to include new refund list pages
pages_path = r'D:\spb-expert11\frontend\pages.json'
with open(pages_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_pages = [
    '{"path": "pages/merchant/refund_list", "style": {"navigationBarTitleText": "Refund Management"}}',
    '{"path": "pages/user/refund_list", "style": {"navigationBarTitleText": "My Refunds"}}'
]

# Insert before "globalStyle"
if "pages/merchant/refund_list" not in content:
    idx = content.find('"globalStyle"')
    if idx != -1:
        pre_content = content[:idx]
        last_bracket = pre_content.rfind(']')
        if last_bracket != -1:
            content = content[:last_bracket] + "," + ",".join(new_pages) + content[last_bracket:]

with open(pages_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated pages.json with Refund List pages")
