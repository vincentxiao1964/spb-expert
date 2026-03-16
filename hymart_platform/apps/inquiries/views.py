from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Inquiry, InquiryMessage
from .serializers import InquirySerializer, InquiryDetailSerializer, InquiryMessageSerializer
from apps.orders.models import Order, OrderItem

class InquiryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        user = self.request.user
        # Return inquiries where user is buyer or seller
        return Inquiry.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related('buyer', 'seller')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InquiryDetailSerializer
        return InquirySerializer

    def perform_create(self, serializer):
        # Validation handled in serializer.create
        serializer.save()

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """
        Post a reply message to the inquiry.
        """
        inquiry = self.get_object()
        user = request.user
        
        # Ensure user is part of the inquiry
        if user != inquiry.buyer and user != inquiry.seller:
            return Response(
                {'error': 'You do not have permission to reply to this inquiry.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        message_content = request.data.get('message')
        if not message_content:
            return Response({'error': 'Message content is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        is_quote = request.data.get('is_quote', False)
        price = request.data.get('price')
        
        # Only seller can send quotes
        if is_quote and user != inquiry.seller:
            return Response({'error': 'Only the seller can send a quotation.'}, status=status.HTTP_403_FORBIDDEN)
            
        # Create Message
        message = InquiryMessage.objects.create(
            inquiry=inquiry,
            sender=user,
            message=message_content,
            is_quote=is_quote,
            price=price if is_quote else None,
            valid_until=request.data.get('valid_until')
        )
        
        # Update Inquiry Timestamp
        inquiry.save()  # Updates updated_at via TimeStampedModel
        
        return Response(InquiryMessageSerializer(message).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept_quote(self, request, pk=None):
        """
        Buyer accepts a quote.
        """
        inquiry = self.get_object()
        if request.user != inquiry.buyer:
            return Response({'error': 'Only the buyer can accept a quote.'}, status=status.HTTP_403_FORBIDDEN)
            
        if inquiry.status != Inquiry.Status.QUOTED:
             return Response({'error': 'Inquiry is not in quoted status.'}, status=status.HTTP_400_BAD_REQUEST)
             
        # Find the latest quote message
        last_quote = inquiry.messages.filter(is_quote=True).last()
        if not last_quote:
            return Response({'error': 'No quote found to accept.'}, status=status.HTTP_400_BAD_REQUEST)
        
        inquiry.status = Inquiry.Status.ACCEPTED
        inquiry.save()
        
        # Auto-create Order
        try:
            # Calculate Total Amount based on quantity
            quantity = inquiry.quantity
            total_amount = last_quote.price * quantity
            
            order = Order.objects.create(
                buyer=inquiry.buyer,
                seller=inquiry.seller,
                total_amount=total_amount,
                status=Order.Status.PENDING,
                contact_name=inquiry.buyer.username, # Default, user should update in checkout
                contact_phone=inquiry.buyer.mobile if hasattr(inquiry.buyer, 'mobile') and inquiry.buyer.mobile else ""
            )
            
            OrderItem.objects.create(
                order=order,
                content_object=inquiry.content_object,
                quantity=quantity,
                price=last_quote.price
            )
            
            return Response({
                'status': 'Quote accepted',
                'order_id': order.id,
                'message': 'Order created successfully. Please proceed to payment.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Revert status if order creation fails
            inquiry.status = Inquiry.Status.QUOTED
            inquiry.save()
            return Response({'error': f'Failed to create order: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def reject_quote(self, request, pk=None):
        """
        Buyer rejects a quote.
        """
        inquiry = self.get_object()
        if request.user != inquiry.buyer:
            return Response({'error': 'Only the buyer can reject a quote.'}, status=status.HTTP_403_FORBIDDEN)
            
        inquiry.status = Inquiry.Status.REJECTED
        inquiry.save()
        
        return Response({'status': 'Quote rejected'}, status=status.HTTP_200_OK)
