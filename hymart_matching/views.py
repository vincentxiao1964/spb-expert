from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CargoRequest, MatchResult
from .serializers import CargoRequestSerializer
from .services import MatchingService

class CargoRequestViewSet(viewsets.ModelViewSet):
    serializer_class = CargoRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['cargo_type', 'origin', 'destination', 'description']

    def get_queryset(self):
        return CargoRequest.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Security Check
        data = serializer.validated_data
        check_content = f"{data.get('description', '')}"
        is_safe, reason = check_msg_sec(check_content, getattr(self.request.user, 'openid', ''))
        if not is_safe:
             raise exceptions.ValidationError({'detail': reason})
             
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Security Check
        data = serializer.validated_data
        check_content = f"{data.get('description', '')}"
        is_safe, reason = check_msg_sec(check_content, getattr(self.request.user, 'openid', ''))
        if not is_safe:
             raise exceptions.ValidationError({'detail': reason})
             
        serializer.save()

    @action(detail=True, methods=['post'])
    def find_matches(self, request, pk=None):
        cargo = self.get_object()
        matches = MatchingService.match_cargo(cargo.id)
        
        # Manually serialize the matches to ensure they are returned immediately
        # using the MatchResultSerializer (which needs to be imported if not already, or use CargoRequestSerializer's nested field)
        
        # Since CargoRequestSerializer has `matches = MatchResultSerializer(many=True)`, 
        # we need to make sure `cargo` object has the related `matches` populated.
        # `match_cargo` creates MatchResult objects in DB.
        
        # We can fetch them via the reverse relation.
        # Using prefetch_related might be cleaner if we reload.
        
        # Simple approach: return the match results directly in a custom envelope
        from .serializers import MatchResultSerializer
        match_serializer = MatchResultSerializer(matches, many=True)
        
        return Response({
            'cargo': self.get_serializer(cargo).data,
            'matches': match_serializer.data
        })

    @action(detail=True, methods=['post'])
    def delete_match(self, request, pk=None):
        cargo = self.get_object()
        match_id = request.data.get('match_id')
        if not match_id:
            return Response({'error': 'match_id required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            match = MatchResult.objects.get(id=match_id, cargo_request=cargo)
        except MatchResult.DoesNotExist:
            return Response({'error': 'match_not_found'}, status=status.HTTP_404_NOT_FOUND)
        
        match.is_deleted = True
        match.save()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_match_viewed(self, request, pk=None):
        cargo = self.get_object()
        match_id = request.data.get('match_id')
        if not match_id:
            return Response({'error': 'match_id required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            match = MatchResult.objects.get(id=match_id, cargo_request=cargo)
        except MatchResult.DoesNotExist:
            return Response({'error': 'match_not_found'}, status=status.HTTP_404_NOT_FOUND)
        match.is_viewed = True
        match.save()
        from .serializers import MatchResultSerializer
        serializer = MatchResultSerializer(match)
        return Response({'match': serializer.data})
