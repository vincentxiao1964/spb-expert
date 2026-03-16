from django.core.management.base import BaseCommand
from orders.models import OrderRefund, Order

class Command(BaseCommand):
    help = "Create a refund request for first order"

    def handle(self, *args, **options):
        order = Order.objects.order_by('id').first()
        if not order:
            self.stdout.write(self.style.ERROR("No orders found"))
            return
        refund, _ = OrderRefund.objects.get_or_create(order=order, amount=order.total_amount, reason='Demo reason')
        self.stdout.write(self.style.SUCCESS(f"Refund({refund.id}) for Order({order.id})"))
