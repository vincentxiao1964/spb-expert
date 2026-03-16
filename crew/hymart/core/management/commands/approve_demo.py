from django.core.management.base import BaseCommand
from store.models import Product
from services.models import ServiceListing

class Command(BaseCommand):
    help = "Approve all demo products and service listings"

    def handle(self, *args, **options):
        p = Product.objects.update(is_approved=True)
        s = ServiceListing.objects.update(is_approved=True)
        self.stdout.write(self.style.SUCCESS(f"Approved products:{p}, services:{s}"))
