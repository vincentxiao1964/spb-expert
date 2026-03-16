from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer, ReviewReplySerializer
from apps.core.permissions import IsOwnerOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product/Service Reviews.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by Target (Product/Service)
        # ?content_type=product&object_id=1
        content_type_str = self.request.query_params.get('content_type') # e.g. 'product', 'servicelisting'
        object_id = self.request.query_params.get('object_id')
        
        if content_type_str and object_id:
            from django.contrib.contenttypes.models import ContentType
            try:
                # Map 'product' -> 'store', 'product'
                # Map 'service' -> 'services', 'servicelisting'
                app_label = 'store' if content_type_str == 'product' else 'services'
                model_name = 'servicelisting' if content_type_str == 'service' else content_type_str
                
                ct = ContentType.objects.get(app_label=app_label, model=model_name)
                queryset = queryset.filter(content_type=ct, object_id=object_id)
            except ContentType.DoesNotExist:
                pass
                
        # Filter by Reviewer
        reviewer_id = self.request.query_params.get('reviewer')
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """
        Seller replies to a review.
        """
        review = self.get_object()
        user = request.user
        
        # Verify Seller Ownership
        # The seller of the product/service should be the one replying
        target = review.content_object
        seller = None
        if hasattr(target, 'seller'):
            seller = target.seller
        elif hasattr(target, 'provider'):
            seller = target.provider
            
        if user != seller:
            return Response({'error': 'Only the seller can reply to this review.'}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = ReviewReplySerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
