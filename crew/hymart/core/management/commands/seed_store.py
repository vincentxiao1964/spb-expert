from django.core.management.base import BaseCommand
from store.models import Category, Product

class Command(BaseCommand):
    help = "Seed basic store data for development"

    def handle(self, *args, **options):
        root, _ = Category.objects.get_or_create(name='Root', defaults={'order': 1})
        child, _ = Category.objects.get_or_create(name='Equipment', parent=root, defaults={'order': 2})
        prod, _ = Product.objects.get_or_create(
            title='Sample Winch',
            defaults={'category': child, 'price': 9999.99, 'stock': 10, 'description': 'Demo product'}
        )
        self.stdout.write(self.style.SUCCESS(f"Seeded: Category({root.id}), Child({child.id}), Product({prod.id})"))
