from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date

from .models import CargoRequest, MatchResult
from .services import MatchingService
from market.models import ShipListing
from hymart_shipdata.models import ShipExtendedInfo


class MatchingToleranceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='cargo_owner', password='pwd')

    def create_ship(self, dwt, draft_laden=None):
        ship = ShipListing.objects.create(
            user=self.user,
            listing_type=ShipListing.ListingType.CHARTER_OFFER,
            ship_category=ShipListing.ShipCategory.SELF_PROPELLED,
            status=ShipListing.Status.APPROVED,
            dwt=str(dwt),
            delivery_area='ANY',
            contact_info='test'
        )
        if draft_laden is not None:
            extended = ShipExtendedInfo.objects.create(
                ship_listing=ship,
                draft_laden=draft_laden
            )
        return ship

    def test_default_dwt_tolerance_10_percent(self):
        cargo = CargoRequest.objects.create(
            user=self.user,
            cargo_type=CargoRequest.CargoType.BULK,
            weight=10000,
            origin='ANY',
            destination='ANY',
            loading_date=date.today()
        )
        too_small = self.create_ship(dwt=9000)
        within_10_percent = self.create_ship(dwt=10999)
        too_large = self.create_ship(dwt=12000)

        matches = MatchingService.match_cargo(cargo.id)
        matched_ids = {m.ship_listing.id for m in MatchResult.objects.filter(cargo_request=cargo)}

        self.assertNotIn(too_small.id, matched_ids)
        self.assertIn(within_10_percent.id, matched_ids)
        self.assertNotIn(too_large.id, matched_ids)

    def test_custom_dwt_tolerance_20_percent(self):
        cargo = CargoRequest.objects.create(
            user=self.user,
            cargo_type=CargoRequest.CargoType.BULK,
            weight=10000,
            dwt_tolerance_percent=20,
            origin='ANY',
            destination='ANY',
            loading_date=date.today()
        )
        within_20_percent = self.create_ship(dwt=12000)
        over_20_percent = self.create_ship(dwt=13001)

        MatchingService.match_cargo(cargo.id)
        matched_ids = {m.ship_listing.id for m in MatchResult.objects.filter(cargo_request=cargo)}

        self.assertIn(within_20_percent.id, matched_ids)
        self.assertNotIn(over_20_percent.id, matched_ids)

    def test_draft_tolerance_applied(self):
        cargo = CargoRequest.objects.create(
            user=self.user,
            cargo_type=CargoRequest.CargoType.BULK,
            weight=10000,
            max_draft=10.0,
            draft_tolerance_percent=20,
            origin='ANY',
            destination='ANY',
            loading_date=date.today()
        )

        ship_ok = self.create_ship(dwt=11000, draft_laden=8.5)
        ship_too_shallow = self.create_ship(dwt=11000, draft_laden=7.0)
        ship_too_deep = self.create_ship(dwt=11000, draft_laden=10.5)

        MatchingService.match_cargo(cargo.id)
        matched_ids = {m.ship_listing.id for m in MatchResult.objects.filter(cargo_request=cargo)}

        self.assertIn(ship_ok.id, matched_ids)
        self.assertNotIn(ship_too_shallow.id, matched_ids)
        self.assertNotIn(ship_too_deep.id, matched_ids)
