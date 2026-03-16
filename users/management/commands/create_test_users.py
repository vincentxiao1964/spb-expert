from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates test users (buyer and seller)'

    def handle(self, *args, **options):
        # Create Seller
        try:
            seller, created = User.objects.get_or_create(username='test_seller', defaults={'phone_number': '13800000001'})
            if created:
                seller.set_password('123456')
                seller.save()
                self.stdout.write(self.style.SUCCESS('Successfully created test_seller / 123456'))
            else:
                seller.set_password('123456')
                seller.save()
                self.stdout.write(self.style.SUCCESS('Updated test_seller password'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating seller: {e}'))

        # Create Buyer
        try:
            buyer, created = User.objects.get_or_create(username='test_buyer', defaults={'phone_number': '13800000002'})
            if created:
                buyer.set_password('123456')
                buyer.save()
                self.stdout.write(self.style.SUCCESS('Successfully created test_buyer / 123456'))
            else:
                buyer.set_password('123456')
                buyer.save()
                self.stdout.write(self.style.SUCCESS('Updated test_buyer password'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating buyer: {e}'))
