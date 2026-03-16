
import json

file_path = r'd:\spb-expert11\frontend\src\pages.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check if page exists
exists = any(p['path'] == 'pages/order/detail' for p in data['pages'])

if not exists:
    new_page = {
        "path": "pages/order/detail",
        "style": {
            "navigationBarTitleText": "Order Detail"
        }
    }
    # Add after order list
    insert_index = -1
    for i, p in enumerate(data['pages']):
        if p['path'] == 'pages/order/order':
            insert_index = i + 1
            break
            
    if insert_index != -1:
        data['pages'].insert(insert_index, new_page)
    else:
        data['pages'].append(new_page)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Successfully added pages/order/detail to pages.json")
else:
    print("Page already exists in pages.json")
