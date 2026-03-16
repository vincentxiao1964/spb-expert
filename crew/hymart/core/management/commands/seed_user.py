from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = "Create demo user and token"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username='demo', defaults={'email': 'demo@example.com'})
        if created:
            user.set_password('demo1234')
            user.save()
        prof = user.profile
        prof.is_merchant = True
        prof.is_buyer = True
        prof.save()
        token, _ = Token.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS(f"Demo user token: {token.key}"))
