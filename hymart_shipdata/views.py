from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ShipExtendedInfo, VoyageHistory
from .serializers import ShipExtendedInfoSerializer, VoyageHistorySerializer
from market.models import ShipListing

class ShipExtendedInfoViewSet(viewsets.ModelViewSet):
    """
    Manage extended technical details for a ship.
    Usually accessed via /hymart/api/ships/{ship_id}/extended_info/
    """
    serializer_class = ShipExtendedInfoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = ShipExtendedInfo.objects.all()

    def get_queryset(self):
        # Optional: Filter by ship_id if passed in query params
        ship_id = self.request.query_params.get('ship_id')
        if ship_id:
            return self.queryset.filter(ship_listing_id=ship_id)
        return self.queryset

    def perform_create(self, serializer):
        # We need to ensure we link it to a valid ship owned by the user
        ship_id = self.request.data.get('ship_listing')
        if not ship_id:
            # If not provided in body, maybe we can infer or it's an error
            # But usually frontend should send it.
            pass
        serializer.save()

class VoyageHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = VoyageHistorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = VoyageHistory.objects.all()

    def get_queryset(self):
        ship_id = self.request.query_params.get('ship_id')
        if ship_id:
            return self.queryset.filter(ship_listing_id=ship_id)
        return self.queryset
