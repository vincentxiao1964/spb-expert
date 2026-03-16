
import json
import os

en_path = r'd:\spb-expert11\frontend\src\locale\en.json'
zh_path = r'd:\spb-expert11\frontend\src\locale\zh-Hans.json'

def update_locale(path, new_keys):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Merge
    for section, keys in new_keys.items():
        if section not in data:
            data[section] = {}
        for k, v in keys.items():
            data[section][k] = v
            
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

en_additions = {
    "order": {
        "detail_title": "Order Detail",
        "status": "Status",
        "no": "Order No",
        "logistics": "Logistics Info",
        "carrier": "Carrier",
        "tracking_no": "Tracking #",
        "customs": "Customs",
        "no_events": "No tracking events yet.",
        "original_total": "Original Total",
        "discount": "Discount",
        "final_total": "Final Total",
        "items": "Items"
    },
    "logistics": {
        "pending": "Pending",
        "picked_up": "Picked Up",
        "in_transit": "In Transit",
        "delivered": "Delivered"
    }
}

zh_additions = {
    "order": {
        "detail_title": "订单详情",
        "status": "状态",
        "no": "订单号",
        "logistics": "物流信息",
        "carrier": "承运商",
        "tracking_no": "运单号",
        "customs": "海关状态",
        "no_events": "暂无物流信息",
        "original_total": "原价",
        "discount": "优惠",
        "final_total": "实付",
        "items": "商品"
    },
    "logistics": {
        "pending": "待发货",
        "picked_up": "已揽收",
        "in_transit": "运输中",
        "delivered": "已送达"
    }
}

update_locale(en_path, en_additions)
update_locale(zh_path, zh_additions)
print("Updated locale files")
