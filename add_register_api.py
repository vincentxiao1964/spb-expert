
import os

# 1. Append RegisterView to views.py
views_path = r"d:\spb-expert11\apps\users\views.py"
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "class RegisterView" not in content:
    register_view_code = """

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        is_merchant = request.data.get('is_merchant', False)
        
        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.create_user(username=username, email=email, password=password)
        
        if is_merchant:
            user.is_merchant = True
            user.save()
            # Create empty merchant profile
            MerchantProfile.objects.create(user=user, company_name=f"{username}'s Shop")
            
        # Generate tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
"""
    with open(views_path, 'a', encoding='utf-8') as f:
        f.write(register_view_code)
    print("Appended RegisterView to views.py")

# 2. Update urls.py
urls_path = r"d:\spb-expert11\apps\users\urls.py"
with open(urls_path, 'r', encoding='utf-8') as f:
    urls_content = f.read()

if "RegisterView" not in urls_content:
    # Add import
    if "from .views import" in urls_content:
        urls_content = urls_content.replace("from .views import", "from .views import RegisterView,")
    
    # Add path
    if "path('me/'," in urls_content:
        urls_content = urls_content.replace("path('me/',", "path('register/', RegisterView.as_view(), name='register'),\n    path('me/',")
    
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content)
    print("Updated urls.py with register path")

