
import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spb_expert.settings")
django.setup()

from users.models import CustomUser

def check_wechat_users():
    print("Checking for users with WeChat OpenID/UnionID...")
    users = CustomUser.objects.filter(openid__isnull=False).exclude(openid='')
    
    if not users.exists():
        print("No users found with WeChat OpenID.")
    else:
        for user in users:
            print(f"User: {user.username}")
            print(f"  Phone: {user.phone_number}")
            print(f"  OpenID: {user.openid}")
            print(f"  UnionID: {user.unionid}")
            print("-" * 30)

if __name__ == "__main__":
    check_wechat_users()
