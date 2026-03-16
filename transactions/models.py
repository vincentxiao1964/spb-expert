from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from market.models import ShipListing

class Transaction(models.Model):
    class Status(models.TextChoices):
        INITIATED = 'INITIATED', _('Initiated - Waiting for Docs')
        DOCS_REVIEW = 'DOCS_REVIEW', _('Docs Submitted - Under Review')
        CONTRACT_SIGNING = 'CONTRACT_SIGNING', _('Contract Signing')
        PAYMENT_PENDING = 'PAYMENT_PENDING', _('Payment Pending')
        PAYMENT_VERIFIED = 'PAYMENT_VERIFIED', _('Payment Verified - Start Transfer')
        COMPLETED = 'COMPLETED', _('Completed - Funds Released')
        CANCELLED = 'CANCELLED', _('Cancelled')

    listing = models.ForeignKey(ShipListing, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    title = models.CharField(_("Transaction Title"), max_length=255, blank=True, help_text="e.g. Bulk Carrier 5000DWT Sale")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buying_transactions')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='selling_transactions')
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.INITIATED)
    
    price_agreed = models.DecimalField(_("Agreed Price"), max_digits=15, decimal_places=2, null=True, blank=True)
    deposit_amount = models.DecimalField(_("Deposit Amount"), max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Signature tracking
    buyer_signed = models.BooleanField(default=False)
    seller_signed = models.BooleanField(default=False)
    buyer_signed_at = models.DateTimeField(null=True, blank=True)
    seller_signed_at = models.DateTimeField(null=True, blank=True)

    # Document Review
    buyer_docs_verified = models.BooleanField(_("Buyer Verified Docs"), default=False)
    buyer_docs_feedback = models.TextField(_("Buyer Feedback"), blank=True)

    needs_financing = models.BooleanField(_("Needs Financing Assistance"), default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        title = self.title if self.title else (self.listing.title if self.listing else "Untitled Transaction")
        return f"Txn #{self.id} - {title} ({self.get_status_display()})"

class TransactionDocument(models.Model):
    class DocType(models.TextChoices):
        SPECIFICATION = 'SPECIFICATION', _('Ship Specification')
        OWNERSHIP_CERT = 'OWNERSHIP_CERT', _('Ownership Certificate')
        CLASS_CERT = 'CLASS_CERT', _('Classification Society Certificate')
        ID_CARD = 'ID_CARD', _('Identity Document')
        CONTRACT_DRAFT = 'CONTRACT_DRAFT', _('Contract Draft')
        SIGNED_CONTRACT = 'SIGNED_CONTRACT', _('Signed Contract')
        PAYMENT_PROOF = 'PAYMENT_PROOF', _('Payment Proof')
        TRANSFER_PROOF = 'TRANSFER_PROOF', _('Transfer Proof')
        OTHER = 'OTHER', _('Other')

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='documents')
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='transaction_docs/%Y/%m/')
    doc_type = models.CharField(max_length=30, choices=DocType.choices)
    description = models.CharField(max_length=255, blank=True)
    
    is_verified = models.BooleanField(_("Verified by Platform"), default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_doc_type_display()} for Txn #{self.transaction.id}"

class TransactionLog(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='logs')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} at {self.timestamp}"
