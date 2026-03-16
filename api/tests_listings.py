from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from market.models import ShipListing

User = get_user_model()

class ShipListingFilterTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password', phone_number='1111111111')
        self.client.force_authenticate(user=self.user)
        
        # Create listings of different types
        self.sell_listing = ShipListing.objects.create(
            user=self.user,
            listing_type=ShipListing.ListingType.SELL,
            ship_category=ShipListing.ShipCategory.SELF_PROPELLED,
            description="Selling a ship",
            status=ShipListing.Status.APPROVED
        )
        self.buy_listing = ShipListing.objects.create(
            user=self.user,
            listing_type=ShipListing.ListingType.BUY,
            ship_category=ShipListing.ShipCategory.SELF_PROPELLED,
            description="Buying a ship",
            status=ShipListing.Status.APPROVED
        )
        self.charter_offer_listing = ShipListing.objects.create(
            user=self.user,
            listing_type=ShipListing.ListingType.CHARTER_OFFER,
            ship_category=ShipListing.ShipCategory.NON_SELF_PROPELLED,
            description="Charter offer",
            status=ShipListing.Status.APPROVED
        )
        
        # Determine the URL - assuming it's registered as 'listings'
        # Since router usage might vary, I'll try to find the correct name.
        # Usually 'shiplisting-list' if basename not set, or basename-list.
        # I didn't set basename explicitly in router.register(r'listings', ...), 
        # so it defaults to queryset model name lowercased: 'shiplisting-list' or 'listings-list'?
        # Let's try constructing manually or using reverse if possible.
        self.url = '/api/v1/listings/'

    def test_filter_by_sell_type(self):
        response = self.client.get(self.url, {'listing_type': 'SELL'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.sell_listing.id)
        self.assertEqual(results[0]['listing_type'], 'SELL')

    def test_filter_by_buy_type(self):
        response = self.client.get(self.url, {'listing_type': 'BUY'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.buy_listing.id)

    def test_filter_by_charter_offer(self):
        response = self.client.get(self.url, {'listing_type': 'CHARTER_OFFER'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.charter_offer_listing.id)

    def test_no_filter_returns_all(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 3)
