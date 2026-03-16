
import os
import json

base_dir = r"d:\spb-expert11\frontend\locale"
os.makedirs(base_dir, exist_ok=True)

zh = {
  "tabbar": {
    "home": "首页",
    "category": "分类",
    "cart": "购物车",
    "mine": "我的"
  },
  "common": {
    "loading": "加载中...",
    "login": "登录",
    "register": "注册",
    "confirm": "确认",
    "cancel": "取消"
  },
  "procurement": {
    "title": "买家店",
    "create": "发布求购",
    "list": "求购列表",
    "sample_required": "这就要求看样",
    "budget": "预算"
  }
}

en = {
  "tabbar": {
    "home": "Home",
    "category": "Categories",
    "cart": "Cart",
    "mine": "Me"
  },
  "common": {
    "loading": "Loading...",
    "login": "Login",
    "register": "Register",
    "confirm": "Confirm",
    "cancel": "Cancel"
  },
  "procurement": {
    "title": "Buyer Shop",
    "create": "Post RFQ",
    "list": "RFQ List",
    "sample_required": "Sample Required",
    "budget": "Budget"
  }
}

with open(os.path.join(base_dir, "zh-Hans.json"), "w", encoding='utf-8') as f:
    json.dump(zh, f, ensure_ascii=False, indent=2)

with open(os.path.join(base_dir, "en.json"), "w", encoding='utf-8') as f:
    json.dump(en, f, ensure_ascii=False, indent=2)

print("Created frontend locale files")
