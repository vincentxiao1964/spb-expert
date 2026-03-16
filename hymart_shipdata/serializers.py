from rest_framework import serializers
from .models import ShipExtendedInfo, VoyageHistory

class ShipExtendedInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipExtendedInfo
        fields = [
            'id', 'draft_laden', 'draft_ballast',
            'hatch_size', 'hatch_count',
            'main_engine_power', 'speed_laden', 'speed_ballast',
            'fuel_consumption_sea', 'fuel_consumption_port',
            'grain_capacity', 'bale_capacity', 'deck_strength',
            'imo_number', 'call_sign', 'mmsi'
        ]

class VoyageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VoyageHistory
        fields = [
            'id', 'departure_port', 'arrival_port',
            'departure_date', 'arrival_date',
            'cargo_description', 'quantity', 'created_at'
        ]
