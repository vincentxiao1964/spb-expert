from django.core.management.base import BaseCommand
from market.models import ShipListing, MarketNews
from hymart_matching.models import CargoRequest

class Command(BaseCommand):
    help = 'Populate unique_id for existing records'

    def handle(self, *args, **options):
        # 1. ShipListing
        self.stdout.write("Processing ShipListing...")
        for item in ShipListing.objects.filter(unique_id__isnull=True):
            item.save() # save() method will generate ID
            self.stdout.write(f"Updated ShipListing {item.id} -> {item.unique_id}")
        
        # 2. MarketNews
        self.stdout.write("Processing MarketNews...")
        for item in MarketNews.objects.filter(unique_id__isnull=True):
            item.save()
            self.stdout.write(f"Updated MarketNews {item.id} -> {item.unique_id}")

        # 3. CargoRequest
        self.stdout.write("Processing CargoRequest...")
        for item in CargoRequest.objects.filter(unique_id__isnull=True):
            item.save()
            self.stdout.write(f"Updated CargoRequest {item.id} -> {item.unique_id}")
            
        self.stdout.write(self.style.SUCCESS("Successfully populated all unique IDs"))