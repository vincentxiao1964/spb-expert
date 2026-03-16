
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
    "procurement": {
        "budget": "Budget",
        "negotiable": "Negotiable",
        "deadline": "Deadline",
        "requirements": "Requirements",
        "sample_required_badge": "Sample Required",
        "submit_quotation": "Submit Quotation",
        "price_placeholder": "Your Price",
        "message_placeholder": "Message to buyer (e.g. delivery time, specs)",
        "sample_provided_question": "Sample Provided?",
        "submit_btn": "Submit Quote",
        "your_quotation": "Your Quotation",
        "price": "Price",
        "status": "Status",
        "received_quotations": "Received Quotations",
        "accept": "Accept",
        "supplier": "Supplier"
    }
}

zh_additions = {
    "procurement": {
        "budget": "预算",
        "negotiable": "面议",
        "deadline": "截止日期",
        "requirements": "需求描述",
        "sample_required_badge": "需要样品",
        "submit_quotation": "提交报价",
        "price_placeholder": "请输入价格",
        "message_placeholder": "给买家的留言（如发货时间、规格等）",
        "sample_provided_question": "提供样品？",
        "submit_btn": "提交报价",
        "your_quotation": "您的报价",
        "price": "价格",
        "status": "状态",
        "received_quotations": "收到的报价",
        "accept": "接受",
        "supplier": "供应商"
    }
}

update_locale(en_path, en_additions)
update_locale(zh_path, zh_additions)
print("Updated locale files for procurement")
