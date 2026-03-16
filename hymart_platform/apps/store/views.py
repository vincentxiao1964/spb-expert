from rest_framework import viewsets, permissions, filters
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from apps.core.permissions import IsOwnerOrReadOnly
from django.utils.text import slugify
import uuid

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product Categories.
    List action returns only root categories (with recursive children).
    Retrieve action allows accessing any category by ID.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        if self.action == 'list':
            return Category.objects.filter(parent__isnull=True).order_by('order')
        return Category.objects.all()

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'view_count', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category', None)
        seller_id = self.request.query_params.get('seller', None)
        
        if category_id:
            # Get category and all its descendants
            try:
                category = Category.objects.get(id=category_id)
                
                # Recursive function to get all descendant IDs
                def get_descendant_ids(cat):
                    ids = [cat.id]
                    for child in cat.children.all():
                        ids.extend(get_descendant_ids(child))
                    return ids
                
                cat_ids = get_descendant_ids(category)
                queryset = queryset.filter(category_id__in=cat_ids)
            except Category.DoesNotExist:
                pass
        
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
            
        return queryset

    def perform_create(self, serializer):
        title = serializer.validated_data.get('title')
        slug = f"{slugify(title)}-{str(uuid.uuid4())[:8]}"
        serializer.save(seller=self.request.user, slug=slug)
