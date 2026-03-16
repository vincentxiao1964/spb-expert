from rest_framework import viewsets, permissions, filters
from .models import ServiceCategory, ServiceListing
from .serializers import ServiceCategorySerializer, ServiceListingSerializer
from apps.core.permissions import IsOwnerOrReadOnly

class ServiceCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Service Categories.
    List action returns only root categories (with recursive children).
    """
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer

    def get_queryset(self):
        if self.action == 'list':
            return ServiceCategory.objects.filter(parent__isnull=True).order_by('order')
        return ServiceCategory.objects.all()

class ServiceListingViewSet(viewsets.ModelViewSet):
    queryset = ServiceListing.objects.all().order_by('-created_at')
    serializer_class = ServiceListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'service_area']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category', None)
        provider_id = self.request.query_params.get('provider', None)
        
        if category_id:
            try:
                category = ServiceCategory.objects.get(id=category_id)
                
                # Recursive function to get all descendant IDs
                def get_descendant_ids(cat):
                    ids = [cat.id]
                    for child in cat.children.all():
                        ids.extend(get_descendant_ids(child))
                    return ids
                
                cat_ids = get_descendant_ids(category)
                queryset = queryset.filter(category_id__in=cat_ids)
            except ServiceCategory.DoesNotExist:
                pass
        
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)
