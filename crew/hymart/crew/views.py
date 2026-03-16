from rest_framework import viewsets, permissions, decorators
from rest_framework.response import Response
from django.db.models import Q, F, Sum
from .models import JobPosition, JobListing
from .serializers import JobPositionSerializer, JobListingSerializer


class JobPositionViewSet(viewsets.ModelViewSet):
    queryset = JobPosition.objects.all().order_by('order', 'name')
    serializer_class = JobPositionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        parent = self.request.query_params.get('parent')
        if parent == 'root':
            qs = qs.filter(parent__isnull=True)
        elif parent:
            qs = qs.filter(parent_id=parent)
        return qs


class JobListingViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.select_related('employer', 'position').all().order_by('-created_at')
    serializer_class = JobListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        position_id = self.request.query_params.get('position')
        ship_type = self.request.query_params.get('ship_type')
        active = self.request.query_params.get('active')
        q = self.request.query_params.get('q')
        if position_id:
            qs = qs.filter(position_id=position_id)
        if ship_type:
            qs = qs.filter(ship_type=ship_type)
        if active == '1':
            qs = qs.filter(is_active=True)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(requirements__icontains=q))
        return qs

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)

    def _check_owner_permission(self, request, obj):
        u = request.user
        if not u.is_authenticated:
            return False
        if u.is_staff:
            return True
        return getattr(obj, 'employer_id', None) == u.id

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self._check_owner_permission(request, obj):
            return Response({'error': 'Permission denied'}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self._check_owner_permission(request, obj):
            return Response({'error': 'Permission denied'}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self._check_owner_permission(request, obj):
            return Response({'error': 'Permission denied'}, status=403)
        return super().destroy(request, *args, **kwargs)

    @decorators.action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        qs = self.get_queryset().filter(employer=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def viewed(self, request, pk=None):
        job = self.get_object()
        JobListing.objects.filter(pk=job.pk).update(view_count=F('view_count') + 1)
        job.refresh_from_db(fields=['view_count'])
        return Response({'id': job.id, 'view_count': job.view_count})

    @decorators.action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def stats(self, request):
        qs = JobListing.objects.all()
        position_id = request.query_params.get('position')
        ship_type = request.query_params.get('ship_type')
        active = request.query_params.get('active')
        if position_id:
            qs = qs.filter(position_id=position_id)
        if ship_type:
            qs = qs.filter(ship_type=ship_type)
        if active == '1':
            qs = qs.filter(is_active=True)
        total = qs.count()
        active_count = qs.filter(is_active=True).count()
        agg = qs.aggregate(total_views=Sum('view_count'))
        total_views = agg['total_views'] or 0
        return Response({
            'total': total,
            'active': active_count,
            'total_views': total_views,
        })
