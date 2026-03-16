from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        # Users can see orders they bought OR sold
        user = self.request.user
        queryset = Order.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related('buyer', 'seller').prefetch_related('items')

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        return queryset

    def perform_create(self, serializer):
        # Buyer is set in serializer.create
        serializer.save()

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """
        Buyer pays for the order (Mock Payment).
        """
        order = self.get_object()
        if request.user != order.buyer:
            return Response({'error': 'Only buyer can pay.'}, status=status.HTTP_403_FORBIDDEN)
            
        if order.status != Order.Status.PENDING:
            return Response({'error': 'Order is not pending payment.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Mock Payment Logic
        order.status = Order.Status.PAID
        # In real system, this might trigger "PROCESSING" immediately or wait for confirmation
        order.save()
        
        return Response({'status': 'Order paid successfully'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """
        Seller marks order as shipped/in-service.
        """
        order = self.get_object()
        if request.user != order.seller:
             return Response({'error': 'Only seller can mark as shipped.'}, status=status.HTTP_403_FORBIDDEN)
             
        if order.status not in [Order.Status.PAID, Order.Status.PROCESSING]:
             return Response({'error': 'Order must be paid before shipping.'}, status=status.HTTP_400_BAD_REQUEST)
             
        # Determine status based on item type (Product vs Service)
        # Assuming single-type orders for simplicity
        first_item = order.items.first()
        from apps.services.models import ServiceListing
        
        if first_item and isinstance(first_item.content_object, ServiceListing):
             order.status = Order.Status.IN_SERVICE
        else:
             order.status = Order.Status.SHIPPED
             
        order.save()
        return Response({'status': 'Order marked as shipped/in-service'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Buyer confirms receipt/completion.
        """
        order = self.get_object()
        if request.user != order.buyer:
             return Response({'error': 'Only buyer can confirm completion.'}, status=status.HTTP_403_FORBIDDEN)
             
        if order.status not in [Order.Status.SHIPPED, Order.Status.IN_SERVICE]:
             return Response({'error': 'Order must be shipped/in-service before completion.'}, status=status.HTTP_400_BAD_REQUEST)
             
        order.status = Order.Status.COMPLETED
        order.save()
        return Response({'status': 'Order completed'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Allow user to cancel their own order if it's still pending.
        """
        order = self.get_object()
        
        # Allow Buyer or Seller to cancel if PENDING
        if request.user != order.buyer and request.user != order.seller:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        if order.status == Order.Status.PENDING:
            order.status = Order.Status.CANCELLED
            order.save()
            
            # Restore stock for products
            for item in order.items.all():
                if hasattr(item.content_object, 'stock'):
                    item.content_object.stock += item.quantity
                    item.content_object.save()
            
            return Response({'status': 'Order cancelled'}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Cannot cancel order that is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
