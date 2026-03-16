
import requests
import json
import random
import string
import os

BASE_URL = "http://127.0.0.1:8000/api/v1"

def get_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def register_user(username, password):
    url = f"{BASE_URL}/users/register/"
    data = {
        "username": username,
        "password": password,
        "confirm_password": password,
        "email": f"{username}@example.com"
    }
    try:
        res = requests.post(url, json=data)
        if res.status_code == 201:
            return res.json()
        return login_user(username, password)
    except:
        return None

def login_user(username, password):
    url = f"{BASE_URL}/users/login/"
    data = {"username": username, "password": password}
    res = requests.post(url, json=data)
    if res.status_code == 200:
        return res.json()
    return None

def run_test():
    print("--- 1. User Setup ---")
    user_name = "logistics_" + get_random_string()
    auth = register_user(user_name, "pass123")
    if not auth:
        print("Auth failed")
        return
    token = auth['access']
    headers = {"Authorization": f"Bearer {token}"}
    print(f"User {user_name} logged in.")

    print("--- 2. Setup Data (Manual) ---")
    setup_script = f"""
import os
import sys
import django
sys.path.append(r'd:\\spb-expert11')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.store.models import Order
from apps.logistics.models import Shipment, LogisticsProvider

User = get_user_model()
try:
    u = User.objects.get(username='{user_name}')
    
    # Create dummy order
    o = Order.objects.create(
        user=u, 
        order_no='ORD-{get_random_string()}',
        total_amount=100.00,
        status='shipped'
    )
    
    # Create provider
    p, _ = LogisticsProvider.objects.get_or_create(name='Maersk Line')
    
    # Create shipment
    s = Shipment.objects.create(
        order=o,
        provider=p,
        tracking_number='TRK-{get_random_string()}',
        status='in_transit',
        customs_status='Cleared'
    )
    print(f"Created Shipment ID {{s.id}} for Order {{o.order_no}}")
except Exception as e:
    print(f"Setup failed: {{e}}")
"""
    with open(r"d:\spb-expert11\setup_logistics_data.py", "w") as f:
        f.write(setup_script)
    
    import subprocess
    # Run in the correct directory
    subprocess.run(["python", r"d:\spb-expert11\setup_logistics_data.py"], shell=True)

    print("\n--- 3. List Shipments ---")
    res = requests.get(f"{BASE_URL}/logistics/shipments/", headers=headers)
    if res.status_code == 200:
        data = res.json()
        print(f"Shipments found: {len(data)}")
        if len(data) > 0:
            shipment_id = data[0]['id']
            print(f"First shipment: {data[0]['tracking_number']} - {data[0]['status']}")
            
            print("\n--- 4. Track Shipment ---")
            res = requests.get(f"{BASE_URL}/logistics/shipments/{shipment_id}/track/", headers=headers)
            if res.status_code == 200:
                track_data = res.json()
                print(f"Timeline events: {len(track_data['timeline'])}")
                print(f"Latest status: {track_data['timeline'][-1]['status']}")
            else:
                print(f"Track failed: {res.text}")
    else:
        print(f"List failed: {res.text}")

if __name__ == "__main__":
    run_test()
