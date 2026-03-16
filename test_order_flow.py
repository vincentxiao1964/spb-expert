import os
import django
import sys
sys.path.append(r'D:\spb-expert11')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from apps.store.models import Product, Cart, Order
from apps.users.models import Address

User = get_user_model()

# Setup Data
user, _ = User.objects.get_or_create(username='buyer', defaults={'email': 'buyer@example.com'})
product = Product.objects.first()
if not product:
    print("No product found! Run create_test_home_data_v3.py first.")
    sys.exit(1)

print(f"Testing with User: {user.username}, Product: {product.name} (ID: {product.id})")

client = APIClient()
client.force_authenticate(user=user)

# 1. Create Address
print("\n--- 1. Creating Address ---")
address_data = {
    "recipient_name": "John Doe",
    "phone": "13800138000",
    "province": "Shanghai",
    "city": "Shanghai",
    "district": "Pudong",
    "detail_address": "123 Marine Road",
    "is_default": True
}
response = client.post('/api/v1/users/addresses/', address_data)
if response.status_code == 201:
    address_id = response.data['id']
    print(f"Address created: ID {address_id}")
else:
    print(f"Failed to create address: {response.status_code} {response.data}")
    # Try to get existing address
    addr = Address.objects.filter(user=user).first()
    if addr:
        address_id = addr.id
        print(f"Using existing address: ID {address_id}")
    else:
        sys.exit(1)

# 2. Add to Cart
print("\n--- 2. Add to Cart ---")
cart_data = {
    "product_id": product.id,
    "quantity": 2
}
response = client.post('/api/v1/store/cart/add/', cart_data)
print(f"Add to cart status: {response.status_code} {response.data}")

# 3. View Cart
print("\n--- 3. View Cart ---")
response = client.get('/api/v1/store/cart/')
print(f"Cart items: {len(response.data.get('items', []))}")
for item in response.data.get('items', []):
    print(f" - {item['product']['name']} x {item['quantity']}")

# 4. Place Order
print("\n--- 4. Place Order ---")
order_data = {
    "address_id": address_id
}
response = client.post('/api/v1/store/orders/', order_data)
if response.status_code == 201:
    orders = response.data
    print(f"Orders created: {len(orders)}")
    for order in orders:
        print(f" - Order No: {order['order_no']}, Amount: {order['total_amount']}, Status: {order['status']}")
else:
    print(f"Failed to place order: {response.status_code} {response.data}")

# 5. Check Orders List
print("\n--- 5. List Orders ---")
response = client.get('/api/v1/store/orders/')
print(f"Total Orders: {len(response.data)}")
