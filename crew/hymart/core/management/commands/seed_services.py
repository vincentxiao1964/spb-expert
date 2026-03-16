from django.core.management.base import BaseCommand
from services.models import ServiceCategory, ServiceListing

class Command(BaseCommand):
    help = "Seed basic services data for development"

    def handle(self, *args, **options):
        root, _ = ServiceCategory.objects.get_or_create(name='Services', defaults={'order': 1})
        child, _ = ServiceCategory.objects.get_or_create(name='Inspection', parent=root, defaults={'order': 2})
        item, _ = ServiceListing.objects.get_or_create(
            title='Hull Inspection',
            defaults={'category': child, 'price': 4999.00, 'description': 'Demo service'}
        )
        self.stdout.write(self.style.SUCCESS(f"Seeded: ServiceCategory({root.id}), Child({child.id}), Listing({item.id})"))
