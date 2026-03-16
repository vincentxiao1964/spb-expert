from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from apps.orders.models import Order
from apps.inquiries.models import Inquiry, InquiryMessage
from apps.reviews.models import Review
from .models import Notification

@receiver(post_save, sender=Order)
def notify_order_status_change(sender, instance, created, **kwargs):
    if created:
        # Notify Seller
        if instance.seller:
            Notification.objects.create(
                recipient=instance.seller,
                type=Notification.NotificationType.ORDER_UPDATE,
                title=f"New Order #{instance.order_number}",
                message=f"You have received a new order from {instance.buyer.username}.",
                content_object=instance
            )
    else:
        # Notify Buyer on status update
        # Note: Ideally check if status actually changed
        Notification.objects.create(
            recipient=instance.buyer,
            type=Notification.NotificationType.ORDER_UPDATE,
            title=f"Order #{instance.order_number} Update",
            message=f"Your order status is now: {instance.get_status_display()}",
            content_object=instance
        )

@receiver(post_save, sender=Inquiry)
def notify_inquiry_status_change(sender, instance, created, **kwargs):
    if created:
        # Notify Seller
        if instance.seller:
            Notification.objects.create(
                recipient=instance.seller,
                type=Notification.NotificationType.INQUIRY_UPDATE,
                title=f"New Inquiry #{instance.id}",
                message=f"You have received a new inquiry from {instance.buyer.username}.",
                content_object=instance
            )
    else:
        # Notify Buyer if status is QUOTED
        if instance.status == Inquiry.Status.QUOTED:
             Notification.objects.create(
                recipient=instance.buyer,
                type=Notification.NotificationType.INQUIRY_UPDATE,
                title=f"Inquiry #{instance.id} Quoted",
                message=f"You have received a quote for your inquiry.",
                content_object=instance
            )

@receiver(post_save, sender=InquiryMessage)
def notify_new_message(sender, instance, created, **kwargs):
    if created:
        inquiry = instance.inquiry
        sender_user = instance.sender
        
        # Determine recipient (the other party)
        if sender_user == inquiry.buyer:
            recipient = inquiry.seller if inquiry.seller else inquiry.provider
        else:
            recipient = inquiry.buyer
            
        if recipient:
            Notification.objects.create(
                recipient=recipient,
                type=Notification.NotificationType.MESSAGE,
                title=f"New Message on Inquiry #{inquiry.id}",
                message=f"You have a new message from {sender_user.username}: {instance.message[:50]}...",
                content_object=inquiry
            )

@receiver(post_save, sender=Review)
def notify_review(sender, instance, created, **kwargs):
    if created:
        # Notify Seller of new review
        target = instance.content_object
        seller = None
        if hasattr(target, 'seller'):
            seller = target.seller
        elif hasattr(target, 'provider'):
            seller = target.provider
            
        if seller:
            Notification.objects.create(
                recipient=seller,
                type=Notification.NotificationType.MESSAGE, # Reuse MESSAGE type or add new one
                title=f"New Review for {target}",
                message=f"{instance.reviewer.username} gave {instance.rating} stars.",
                content_object=instance
            )
    else:
        # Notify Buyer if replied
        if instance.reply and instance.replied_at:
             # Check if we should notify (avoid duplicates logic could be here)
             Notification.objects.create(
                recipient=instance.reviewer,
                type=Notification.NotificationType.MESSAGE,
                title=f"Seller Replied to your Review",
                message=f"Seller replied: {instance.reply[:50]}...",
                content_object=instance
            )
