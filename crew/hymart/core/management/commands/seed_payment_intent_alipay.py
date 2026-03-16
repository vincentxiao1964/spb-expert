from django.core.management.base import BaseCommand
from payments.models import PaymentIntent
from orders.models import Order

class Command(BaseCommand):
    help = "Create an Alipay payment intent for first order"

    def handle(self, *args, **options):
        order = Order.objects.order_by('id').first()
        if not order:
            self.stdout.write(self.style.ERROR("No orders found"))
            return
        intent = PaymentIntent.objects.create(order=order, amount=order.total_amount, provider='alipay')
        self.stdout.write(self.style.SUCCESS(f"Alipay PaymentIntent({intent.id}) for Order({order.id})"))
