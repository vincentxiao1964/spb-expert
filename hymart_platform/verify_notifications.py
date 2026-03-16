import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.store.models import Category, Product
from apps.orders.models import Order, OrderItem
from apps.inquiries.models import Inquiry, InquiryMessage
from apps.notifications.models import Notification

User = get_user_model()

def run_verification():
    print("--- Verifying Notification System ---")
    
    # 1. Setup Users
    buyer, _ = User.objects.get_or_create(username='notify_buyer', defaults={'email': 'nb@example.com', 'role': 'BUYER'})
    seller, _ = User.objects.get_or_create(username='notify_seller', defaults={'email': 'ns@example.com', 'role': 'SELLER'})
    
    # Clear previous notifications
    Notification.objects.all().delete()
    
    # 2. Test Order Notification
    print("\n[Test 1] Creating Order...")
    
    # Need a product
    cat, _ = Category.objects.get_or_create(slug='test-cat', defaults={'name': 'Test Cat'})
    product, _ = Product.objects.get_or_create(
        slug='notify-prod', 
        seller=seller, 
        defaults={'title': 'Notify Product', 'price': 100, 'stock': 10, 'category': cat}
    )
    
    order = Order.objects.create(buyer=buyer, seller=seller, total_amount=100)
    OrderItem.objects.create(order=order, content_object=product, quantity=1, price=100)
    
    # Check Seller Notification
    notifs = Notification.objects.filter(recipient=seller, type=Notification.NotificationType.ORDER_UPDATE)
    if notifs.exists():
        print(f"✅ Seller received Order notification: {notifs.first().title}")
    else:
        print("❌ Seller did NOT receive Order notification")
        
    # 3. Test Inquiry Notification
    print("\n[Test 2] Creating Inquiry...")
    inquiry = Inquiry.objects.create(
        buyer=buyer,
        seller=seller,
        content_object=product,
        subject="Price check"
    )
    InquiryMessage.objects.create(
        inquiry=inquiry,
        sender=buyer,
        message="Best price?"
    )
    
    # Check Seller Notification
    notifs = Notification.objects.filter(recipient=seller, type=Notification.NotificationType.INQUIRY_UPDATE)
    if notifs.exists():
        print(f"✅ Seller received Inquiry notification: {notifs.first().title}")
    else:
        print("❌ Seller did NOT receive Inquiry notification")

    # 4. Test Message Notification
    print("\n[Test 3] Sending Inquiry Message...")
    InquiryMessage.objects.create(
        inquiry=inquiry,
        sender=seller,
        message="Yes, 90 is ok."
    )
    
    # Check Buyer Notification
    notifs = Notification.objects.filter(recipient=buyer, type=Notification.NotificationType.MESSAGE)
    if notifs.exists():
        print(f"✅ Buyer received Message notification: {notifs.first().title}")
    else:
        print("❌ Buyer did NOT receive Message notification")

if __name__ == '__main__':
    run_verification()
