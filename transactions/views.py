from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from .models import Transaction, TransactionDocument, TransactionLog
from .serializers import TransactionSerializer, TransactionDocumentSerializer

from django.utils import timezone

class IsTransactionPartyOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.buyer == request.user or obj.seller == request.user

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsTransactionPartyOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(Q(buyer=user) | Q(seller=user)).order_by('-created_at')

    def perform_create(self, serializer):
        # Validation logic can go here (e.g., check if user already has active txn for this ship)
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        return Response({'error': 'Deletion disabled. Use status updates (e.g., CANCELLED).'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @decorators.action(detail=True, methods=['post'])
    def review_docs(self, request, pk=None):
        transaction = self.get_object()
        user = request.user
        
        # Only Buyer can review docs (or Admin)
        if user != transaction.buyer and not user.is_staff:
             return Response({'error': 'Only buyer can review documents'}, status=status.HTTP_403_FORBIDDEN)
             
        approved = request.data.get('approved')
        feedback = request.data.get('feedback', '')
        
        if approved:
            transaction.buyer_docs_verified = True
            transaction.buyer_docs_feedback = ""
            action_msg = "Buyer approved documents"
        else:
            transaction.buyer_docs_verified = False
            transaction.buyer_docs_feedback = feedback
            # If rejected, status could be set back or remain same, but UI will show feedback
            # User requirement: "Buyer passes -> Admin next... Buyer rejects -> Re-upload"
            # We can keep status as is, but maybe reset to INITIATED to signal "Start Over"
            # However, INITIATED implies "Waiting for Docs". So it fits.
            if transaction.status == Transaction.Status.DOCS_REVIEW:
                 transaction.status = Transaction.Status.INITIATED
            action_msg = f"Buyer rejected documents: {feedback}"
            
        transaction.save()
        TransactionLog.objects.create(transaction=transaction, actor=user, action=action_msg)
        return Response({'status': 'reviewed', 'verified': transaction.buyer_docs_verified})

    @decorators.action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        transaction = self.get_object()
        new_status = request.data.get('status')
        note = request.data.get('note', '')
        
        if new_status:
            # Basic guardrail: non-admin can only cancel prior to payment/signing
            if not request.user.is_staff:
                blocked = [
                    Transaction.Status.CONTRACT_SIGNING,
                    Transaction.Status.PAYMENT_PENDING,
                    Transaction.Status.PAYMENT_VERIFIED,
                    Transaction.Status.COMPLETED,
                ]
                if new_status != Transaction.Status.CANCELLED or transaction.status in blocked:
                    return Response({'error': 'Only CANCELLED allowed before signing/payment'}, status=status.HTTP_403_FORBIDDEN)
            
            old_status = transaction.status
            transaction.status = new_status
            transaction.save()
            
            TransactionLog.objects.create(
                transaction=transaction,
                actor=request.user,
                action=f"Status changed from {old_status} to {new_status}. Note: {note}"
            )
            return Response({'status': 'updated'})
        return Response({'error': 'No status provided'}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        transaction = self.get_object()
        user = request.user
        
        if transaction.status != Transaction.Status.CONTRACT_SIGNING:
            return Response({'error': 'Not in signing status'}, status=status.HTTP_400_BAD_REQUEST)

        if user == transaction.buyer:
            if transaction.buyer_signed:
                return Response({'status': 'already signed'})
            transaction.buyer_signed = True
            transaction.buyer_signed_at = timezone.now()
            TransactionLog.objects.create(transaction=transaction, actor=user, action="Buyer signed contract")
        elif user == transaction.seller:
            if transaction.seller_signed:
                return Response({'status': 'already signed'})
            transaction.seller_signed = True
            transaction.seller_signed_at = timezone.now()
            TransactionLog.objects.create(transaction=transaction, actor=user, action="Seller signed contract")
        else:
             return Response({'error': 'Not a party to this transaction'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if both signed
        if transaction.buyer_signed and transaction.seller_signed:
            transaction.status = Transaction.Status.PAYMENT_PENDING
            TransactionLog.objects.create(transaction=transaction, actor=None, action="Both parties signed. Moving to Payment Pending.")
            
        transaction.save()
        return Response({'status': 'signed', 'new_status': transaction.status})

class TransactionDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionDocumentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return TransactionDocument.objects.all()
        return TransactionDocument.objects.filter(
            Q(transaction__buyer=user) | Q(transaction__seller=user)
        )

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)
        
        # Log upload
        TransactionLog.objects.create(
            transaction=serializer.instance.transaction,
            actor=self.request.user,
            action=f"Uploaded document: {serializer.instance.get_doc_type_display()}"
        )
