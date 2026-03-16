from rest_framework import serializers
from .models import CargoRequest, MatchResult
from api.serializers import ShipListingSerializer

class MatchResultSerializer(serializers.ModelSerializer):
    ship_listing = ShipListingSerializer(read_only=True)
    dwt_diff_percent = serializers.SerializerMethodField()
    draft_utilization_percent = serializers.SerializerMethodField()

    class Meta:
        model = MatchResult
        fields = ['id', 'ship_listing', 'score', 'dwt_diff_percent', 'draft_utilization_percent', 'created_at', 'is_viewed']

    def get_dwt_diff_percent(self, obj):
        weight = obj.cargo_request.weight
        ship_dwt_str = obj.ship_listing.dwt
        try:
            ship_dwt = float(ship_dwt_str) if ship_dwt_str else None
        except ValueError:
            return None
        if not weight or weight <= 0 or not ship_dwt:
            return None
        diff = ship_dwt - weight
        return round(diff / weight * 100, 2)

    def get_draft_utilization_percent(self, obj):
        max_draft = obj.cargo_request.max_draft
        extended_info = getattr(obj.ship_listing, 'extended_info', None)
        if not extended_info or not max_draft or max_draft <= 0:
            return None
        ship_draft = extended_info.draft_laden
        if not ship_draft:
            return None
        return round(ship_draft / max_draft * 100, 2)

class CargoRequestSerializer(serializers.ModelSerializer):
    matches = MatchResultSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    cargo_type_display = serializers.CharField(source='get_cargo_type_display', read_only=True)

    class Meta:
        model = CargoRequest
        fields = [
            'unique_id', 'id', 'user', 'cargo_type', 'cargo_type_display', 'weight',
            'volume', 'max_draft', 'dwt_tolerance_percent', 'draft_tolerance_percent',
            'origin', 'destination', 'loading_date', 'description',
            'created_at', 'status', 'status_display', 'matches'
        ]
        read_only_fields = ['unique_id', 'user', 'created_at', 'matches']

    def validate_weight(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError('weight must be greater than 0')
        return value

    def validate_volume(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError('volume must be greater than 0 when provided')
        return value

    def validate_max_draft(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError('max_draft must be greater than 0 when provided')
        return value

    def validate_dwt_tolerance_percent(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('dwt_tolerance_percent must be non-negative')
        return value

    def validate_draft_tolerance_percent(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('draft_tolerance_percent must be non-negative')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
