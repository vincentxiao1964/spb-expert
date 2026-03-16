from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from users.models import CustomUser
from market.models import ShipListing
from hymart_shipdata.models import ShipExtendedInfo, VoyageHistory
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populates the database with test data for Hymart matching'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data population...')
        
        # 1. Ensure a test user exists
        user, created = CustomUser.objects.get_or_create(
            username='hymart_owner',
            defaults={
                'email': 'owner@hymart.com',
                'phone_number': '13800000000',
                'company_name': 'Hymart Logistics Co., Ltd.',
                'business_content': 'Ship Owner'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(f'Created user: {user.username}')
        else:
            self.stdout.write(f'Using existing user: {user.username}')

        # 2. Define Ship Profiles
        ships_data = [
            {
                'title': 'Hymart Coastal Pioneer',
                'description': 'Reliable Coastal General Cargo Ship',
                'dwt': 5000,
                'delivery_area': 'China, Japan, Korea',
                'listing_type': ShipListing.ListingType.CHARTER_OFFER,
                'status': ShipListing.Status.APPROVED,
                'extended': {
                    'draft_laden': 6.5,
                    'draft_ballast': 4.2,
                    'grain_capacity': 6200,
                    'bale_capacity': 5900,
                    'hatch_size': '20x12m',
                    'hatch_count': 2,
                    'speed_laden': 11.5,
                    'fuel_consumption_sea': 9.0,
                    'imo_number': '9123456'
                }
            },
            {
                'title': 'Hymart River King',
                'description': 'Shallow Draft River Barge',
                'dwt': 2500,
                'delivery_area': 'Yangtze River',
                'listing_type': ShipListing.ListingType.CHARTER_OFFER,
                'status': ShipListing.Status.APPROVED,
                'extended': {
                    'draft_laden': 3.8,
                    'draft_ballast': 2.1,
                    'grain_capacity': 3000,
                    'bale_capacity': 2900,
                    'hatch_size': '15x10m',
                    'hatch_count': 1,
                    'speed_laden': 8.0,
                    'fuel_consumption_sea': 4.5,
                    'imo_number': '8888888'
                }
            },
            {
                'title': 'Hymart Ocean Giant',
                'description': 'Handymax Bulk Carrier',
                'dwt': 45000,
                'delivery_area': 'Global',
                'listing_type': ShipListing.ListingType.CHARTER_OFFER,
                'status': ShipListing.Status.APPROVED,
                'extended': {
                    'draft_laden': 11.2,
                    'draft_ballast': 6.5,
                    'grain_capacity': 58000,
                    'bale_capacity': 56000,
                    'hatch_size': '25x15m',
                    'hatch_count': 5,
                    'speed_laden': 13.5,
                    'fuel_consumption_sea': 24.0,
                    'imo_number': '9876543'
                }
            },
            {
                'title': 'Hymart Express',
                'description': 'Fast General Cargo',
                'dwt': 8000,
                'delivery_area': 'SE Asia',
                'listing_type': ShipListing.ListingType.CHARTER_OFFER,
                'status': ShipListing.Status.APPROVED,
                'extended': {
                    'draft_laden': 7.8,
                    'draft_ballast': 5.0,
                    'grain_capacity': 9500,
                    'bale_capacity': 9200,
                    'hatch_size': '22x14m',
                    'hatch_count': 2,
                    'speed_laden': 14.0,
                    'fuel_consumption_sea': 12.5,
                    'imo_number': '9555555'
                }
            }
        ]

        count = 0
        
        # Cleanup existing test data first to avoid conflicts
        # 1. Delete by Description
        descriptions = [d['description'] for d in ships_data]
        deleted_count_desc, _ = ShipListing.objects.filter(description__in=descriptions).delete()
        
        # 2. Delete by IMO (find ExtendedInfo -> ShipListing)
        imos = [d['extended']['imo_number'] for d in ships_data if 'imo_number' in d['extended']]
        existing_extended = ShipExtendedInfo.objects.filter(imo_number__in=imos)
        listing_ids = existing_extended.values_list('ship_listing_id', flat=True)
        deleted_count_imo, _ = ShipListing.objects.filter(id__in=listing_ids).delete()
        
        self.stdout.write(f"Cleaned up {deleted_count_desc + deleted_count_imo} existing test ships.")

        for data in ships_data:
            with transaction.atomic():
                # Create ShipListing
                ship = ShipListing.objects.create(
                    user=user,
                    description=data['description'],
                    dwt=data['dwt'],
                    delivery_area=data['delivery_area'],
                    listing_type=data['listing_type'],
                    status=data['status'],
                    start_time=timezone.now().date() + timedelta(days=random.randint(0, 10))
                )
                
                # Create Extended Info
                ext_data = data['extended']
                ShipExtendedInfo.objects.create(
                    ship_listing=ship,
                    **ext_data
                )
                
                # Create Fake Voyage History
                ports = ['Shanghai', 'Busan', 'Singapore', 'Tokyo', 'Ningbo', 'Kaohsiung']
                for _ in range(3):
                    VoyageHistory.objects.create(
                        ship_listing=ship,
                        departure_port=random.choice(ports),
                        arrival_port=random.choice(ports),
                        departure_date=timezone.now().date() - timedelta(days=random.randint(30, 365)),
                        cargo_description='General Cargo',
                        quantity=data['dwt'] * 0.9
                    )

                count += 1
                self.stdout.write(f"Created {data['title']} (DWT {data['dwt']})")

        self.stdout.write(self.style.SUCCESS(f'Successfully processed {count} ships.'))
