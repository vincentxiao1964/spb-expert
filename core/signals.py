from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import PrivateMessage, MessageReply, Notification
from users.models import UserFollow

@receiver(post_save, sender=PrivateMessage)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.receiver,
            actor=instance.sender,
            notification_type=Notification.Type.MESSAGE,
            title='New Private Message',
            content=f'You have a new message from {instance.sender.username}',
            target_url=f'/pages/messages/chat/chat?userId={instance.sender.id}&username={instance.sender.username}'
        )

@receiver(post_save, sender=MessageReply)
def create_reply_notification(sender, instance, created, **kwargs):
    if created:
        # Determine recipient: The owner of the original message
        # But wait, MessageReply is reply to MemberMessage?
        # Let's check MemberMessage model relation
        original_msg = instance.message
        if original_msg.user != instance.user:
            Notification.objects.create(
                recipient=original_msg.user,
                actor=instance.user,
                notification_type=Notification.Type.REPLY,
                title='New Reply',
                content=f'{instance.user.username} replied to your post',
                target_url=f'/pages/messages/detail/detail?id={original_msg.id}'
            )

@receiver(post_save, sender=UserFollow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.followed,
            actor=instance.follower,
            notification_type=Notification.Type.FOLLOW,
            title='New Follower',
            content=f'{instance.follower.username} started following you',
            target_url=f'/pages/mine/user-profile/user-profile?userId={instance.follower.id}'
        )
