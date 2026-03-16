from rest_framework import serializers
from .models import Transaction, TransactionDocument, TransactionLog
from api.serializers import ShipListingSerializer
from users.serializers import UserSerializer

class TransactionDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionDocument
        fields = ['id', 'transaction', 'uploader', 'file', 'doc_type', 'description', 'is_verified', 'uploaded_at']
        read_only_fields = ['uploader', 'is_verified', 'uploaded_at']

class TransactionLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    
    class Meta:
        model = TransactionLog
        fields = ['id', 'actor', 'actor_name', 'action', 'timestamp']

class TransactionSerializer(serializers.ModelSerializer):
    listing_detail = ShipListingSerializer(source='listing', read_only=True)
    buyer_detail = UserSerializer(source='buyer', read_only=True)
    seller_detail = UserSerializer(source='seller', read_only=True)
    documents = TransactionDocumentSerializer(many=True, read_only=True)
    logs = TransactionLogSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'title', 'listing', 'listing_detail', 
            'buyer', 'buyer_detail', 
            'seller', 'seller_detail', 
            'status', 'status_display',
            'price_agreed', 'deposit_amount', 'needs_financing',
            'buyer_docs_verified', 'buyer_docs_feedback',
            'buyer_signed', 'seller_signed',
            'documents', 'logs',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['buyer', 'seller', 'status', 'created_at', 'updated_at', 'buyer_docs_verified', 'buyer_docs_feedback', 'buyer_signed', 'seller_signed']
        extra_kwargs = {
            'listing': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        # Handle buyer assignment
        request = self.context.get('request')
        User = None
        if request and request.user.is_staff:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # 1. Handle Buyer
            if 'buyer' in self.initial_data:
                try:
                    buyer_id = self.initial_data.get('buyer')
                    validated_data['buyer'] = User.objects.get(pk=buyer_id)
                except User.DoesNotExist:
                    raise serializers.ValidationError({"buyer": "Buyer user not found"})
            
            # 2. Handle Seller (Explicit assignment)
            if 'seller' in self.initial_data:
                try:
                    seller_id = self.initial_data.get('seller')
                    validated_data['seller'] = User.objects.get(pk=seller_id)
                except User.DoesNotExist:
                    raise serializers.ValidationError({"seller": "Seller user not found"})

        # Defaults if not set (or not admin)
        if 'buyer' not in validated_data:
            validated_data['buyer'] = request.user
            
        if 'seller' not in validated_data:
            # Default seller is the listing owner
            listing = validated_data.get('listing')
            if listing:
                validated_data['seller'] = listing.user
            else:
                raise serializers.ValidationError({"seller": "Seller must be specified if no listing is linked."})
        
        transaction = super(TransactionSerializer, self).create(validated_data) # Use super(TransactionSerializer, self) for compatibility if needed, or just super()
        
        # Log creation
        # Handle title construction safely since ShipListing has no 'title' field
        if transaction.title:
            log_title = transaction.title
        elif transaction.listing:
            log_title = f"{transaction.listing.get_ship_category_display()} - {transaction.listing.dwt}t"
        else:
            log_title = "Untitled Transaction"
            
        TransactionLog.objects.create(
            transaction=transaction,
            actor=request.user,
            action=f"Transaction initiated for {log_title}"
        )
        return transaction
