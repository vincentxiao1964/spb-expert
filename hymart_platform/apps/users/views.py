from rest_framework import viewsets, permissions, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, UserUpdateSerializer, 
    CompanyProfileSerializer, CrewProfileSerializer
)
from .models import CompanyProfile, CrewProfile
from apps.orders.models import Order
from apps.inquiries.models import Inquiry
from apps.store.models import Product
from apps.services.models import ServiceListing

User = get_user_model()

class CompanyListingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing verified Company Profiles.
    """
    queryset = CompanyProfile.objects.filter(is_verified=True, verification_status=CompanyProfile.VerificationStatus.VERIFIED)
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__company_name', 'description', 'address']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post']

    def get_queryset(self):
        # Users can only see their own profile in list view if not admin
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'])
    def info(self, request):
        """
        Get current user info with profile details
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], url_path='profile/update')
    def update_profile(self, request):
        """
        Update user profile (Basic + Role specific)
        """
        user = request.user
        
        # 1. Update Basic Info
        user_serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # 2. Update Role Specific Profile
        if user.role == User.Role.COMPANY:
            profile, created = CompanyProfile.objects.get_or_create(user=user)
            profile_serializer = CompanyProfileSerializer(profile, data=request.data, partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        elif user.role == User.Role.CREW:
            profile, created = CrewProfile.objects.get_or_create(user=user)
            profile_serializer = CrewProfileSerializer(profile, data=request.data, partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Return updated full info
        return Response(self.get_serializer(user).data)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, JSONParser])
    def upload(self, request):
        """
        Upload user related files (avatar, business_license, resume)
        """
        user = request.user
        field = request.data.get('field')
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not field:
            return Response({'error': 'No field specified'}, status=status.HTTP_400_BAD_REQUEST)
            
        url = ''
        
        if field == 'avatar':
            user.avatar = file_obj
            user.save()
            url = user.avatar.url if user.avatar else ''
            
        elif field == 'business_license':
            # Auto-switch role if needed or check role? 
            # Ideally user should be COMPANY or upgrading to it.
            # We don't force role switch here, just check if profile exists or create it.
            profile, _ = CompanyProfile.objects.get_or_create(user=user)
            profile.business_license_img = file_obj
            profile.save()
            url = profile.business_license_img.url if profile.business_license_img else ''
            
        elif field == 'resume':
             profile, _ = CrewProfile.objects.get_or_create(user=user)
             profile.resume_file = file_obj
             profile.save()
             url = profile.resume_file.url if profile.resume_file else ''
             
        else:
             return Response({'error': 'Invalid field'}, status=status.HTTP_400_BAD_REQUEST)
             
        # Build absolute URL
        if url and not url.startswith('http'):
            url = request.build_absolute_uri(url)
            
        return Response({'url': url, 'field': field})

class UserStatsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        stats = {
            'orders_count': Order.objects.filter(buyer=user).count(),
            'inquiries_sent_count': Inquiry.objects.filter(buyer=user).count(),
            'inquiries_received_count': Inquiry.objects.filter(seller=user).count(),
            'unread_messages_count': 0, # TODO: Implement notification/message system
        }
        
        if user.role == User.Role.COMPANY:
            stats.update({
                'products_count': Product.objects.filter(seller=user).count(),
                'services_count': ServiceListing.objects.filter(provider=user).count(),
                'pending_orders_count': Order.objects.filter(seller=user, status=Order.Status.PENDING).count()
            })
            
        return Response(stats)
