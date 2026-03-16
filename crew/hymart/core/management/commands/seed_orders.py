from django.core.management.base import BaseCommand
from orders.models import Order, OrderItem
from store.models import Product, Category

class Command(BaseCommand):
    help = "Seed basic orders data for development"

    def handle(self, *args, **options):
        cat, _ = Category.objects.get_or_create(name='Root', defaults={'order': 1})
        prod, _ = Product.objects.get_or_create(title='Sample Winch', defaults={'category': cat, 'price': 9999.99, 'stock': 10})
        order = Order.objects.create(buyer_name='Demo Buyer', contact_phone='123456789')
        OrderItem.objects.create(order=order, product=prod, title=prod.title, price=prod.price, quantity=1)
        order.total_amount = prod.price
        order.save()
        self.stdout.write(self.style.SUCCESS(f"Seeded Order({order.id})"))
