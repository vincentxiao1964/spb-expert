from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from market.models import ShipListing, ListingImage, MarketNews, ListingMatch, Favorite
from ads.models import Advertisement
from core.models import MemberMessage, PrivateMessage, MessageReply, Notification
from users.models import UserFollow
from crew.models import CrewListing
import base64
from django.core.files.base import ContentFile
import uuid

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            if not User.objects.filter(username=username).exists():
                try:
                    user = User.objects.get(phone_number=username)
                    attrs['username'] = user.username
                except User.DoesNotExist:
                    pass
                    
        data = super().validate(attrs)
        user = getattr(self, 'user', None)
        if user:
            data['user_id'] = user.id
            data['username'] = user.username
            data['is_staff'] = user.is_staff
            data['membership_level'] = getattr(user, 'membership_level', None)
            data['phone_number'] = getattr(user, 'phone_number', None)
        return data

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                header, data = data.split(';base64,')
                decoded_file = base64.b64decode(data)
                file_name = str(uuid.uuid4())[:12]
                file_extension = header.split('/')[-1]
                complete_file_name = "%s.%s" % (file_name, file_extension)
                data = ContentFile(decoded_file, name=complete_file_name)
            except Exception as e:
                raise serializers.ValidationError(f"Invalid image format: {e}")
        return super().to_internal_value(data)

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'listing', 'image', 'is_schematic']

from hymart_shipdata.serializers import ShipExtendedInfoSerializer

class ShipListingSerializer(serializers.ModelSerializer):
    unique_id = serializers.CharField(read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)
    extended_info = ShipExtendedInfoSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    listing_type_display = serializers.CharField(source='get_listing_type_display', read_only=True)
    ship_category_display = serializers.CharField(source='get_ship_category_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    is_owner = serializers.SerializerMethodField()
    share_image = serializers.SerializerMethodField()

    class Meta:
        model = ShipListing
        fields = [
            'unique_id',
            'id', 'user', 'user_name', 'listing_type', 'listing_type_display',
            'ship_category', 'ship_category_display',
            'length', 'width', 'depth', 'dwt', 'build_year',
            'class_society', 'flag_state', 'delivery_area',
            'start_time', 'description', 'description_en',
            'contact_info', 'status', 'status_display',
            'created_at', 'updated_at', 'images', 'extended_info', 'is_owner',
            'view_count', 'contact_count', 'share_image'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'view_count', 'contact_count']

    def get_share_image(self, obj):
        # Try to find a real image first
        first_image = obj.images.filter(is_schematic=False).first()
        if not first_image:
            first_image = obj.images.first()
            
        if first_image:
            image_url = first_image.image.url
            request = self.context.get('request')
            if request and not image_url.startswith('http'):
                return request.build_absolute_uri(image_url)
            return image_url
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            ret['contact_info'] = None
        return ret

    def validate_status(self, value):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return value
        if request.user.is_staff or request.user.is_superuser:
            return value
        if self.instance:
            if self.instance.status != value:
                 raise serializers.ValidationError("Only admins can change status.")
        else:
            if value != ShipListing.Status.PENDING:
                 raise serializers.ValidationError("Cannot set status on creation.")
        return value

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user or request.user.is_staff or request.user.is_superuser
        return False

class ListingMatchSerializer(serializers.ModelSerializer):
    target_listing = ShipListingSerializer(source='listing_target', read_only=True)
    source_listing = ShipListingSerializer(source='listing_source', read_only=True)
    
    class Meta:
        model = ListingMatch
        fields = ['id', 'listing_source', 'listing_target', 'score', 'is_notified', 'created_at', 'target_listing', 'source_listing']

class MarketNewsSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    is_owner = serializers.SerializerMethodField()
    
    class Meta:
        model = MarketNews
        fields = ['unique_id', 'id', 'user', 'user_name', 'title', 'title_en', 'content', 'content_en', 'image', 'source_url', 'original_source', 'status', 'status_display', 'created_at', 'updated_at', 'is_owner']
        read_only_fields = ['unique_id', 'user', 'created_at', 'updated_at']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user or request.user.is_staff or request.user.is_superuser
        return False

class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ['id', 'user', 'title', 'image', 'link', 'description', 'is_active', 'created_at', 'activated_at']
        read_only_fields = ['user', 'created_at', 'activated_at']

class MessageReplySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = MessageReply
        fields = ['id', 'message', 'user', 'user_name', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']

class MemberMessageSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    replies_count = serializers.IntegerField(source='replies.count', read_only=True)
    
    class Meta:
        model = MemberMessage
        fields = ['id', 'user', 'user_name', 'content', 'created_at', 'replies_count']
        read_only_fields = ['user', 'created_at']

class MemberMessageDetailSerializer(MemberMessageSerializer):
    replies = MessageReplySerializer(many=True, read_only=True)
    
    class Meta(MemberMessageSerializer.Meta):
        fields = MemberMessageSerializer.Meta.fields + ['replies']

class PrivateMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)
    sender_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = PrivateMessage
        fields = ['id', 'sender', 'sender_name', 'sender_avatar', 'receiver', 'receiver_name', 'content', 'image', 'is_read', 'created_at']
        read_only_fields = ['sender', 'created_at', 'is_read']

    def get_sender_avatar(self, obj):
        # Return default avatar or actual avatar if user profile has one
        # Assuming User has no avatar field yet, return default
        return '/static/images/default-avatar.png'

class NotificationSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'actor', 'actor_name', 'notification_type', 'type_display', 'title', 'content', 'target_url', 'is_read', 'created_at']
        read_only_fields = ['recipient', 'created_at']

class UserFollowSerializer(serializers.ModelSerializer):
    follower_name = serializers.CharField(source='follower.username', read_only=True)
    followed_name = serializers.CharField(source='followed.username', read_only=True)
    
    class Meta:
        model = UserFollow
        fields = ['id', 'follower', 'follower_name', 'followed', 'followed_name', 'created_at']
        read_only_fields = ['follower', 'created_at']

class FavoriteSerializer(serializers.ModelSerializer):
    content_type_model = serializers.CharField(source='content_type.model', read_only=True)
    content_object = serializers.SerializerMethodField()
    
    class Meta:
        model = Favorite
        fields = ['id', 'content_type', 'object_id', 'content_type_model', 'content_object', 'created_at']
        read_only_fields = ['user']

    def get_content_object(self, obj):
        if obj.content_type.model == 'shiplisting':
            serializer = ShipListingSerializer(obj.content_object, context=self.context)
            return serializer.data
        elif obj.content_type.model == 'marketnews':
            serializer = MarketNewsSerializer(obj.content_object, context=self.context)
            return serializer.data
        elif obj.content_type.model == 'advertisement':
            serializer = AdvertisementSerializer(obj.content_object, context=self.context)
            return serializer.data
        elif obj.content_type.model == 'membermessage':
            serializer = MemberMessageSerializer(obj.content_object, context=self.context)
            return serializer.data
        elif obj.content_type.model == 'crewlisting':
            serializer = CrewListingSerializer(obj.content_object, context=self.context)
            return serializer.data
        return None

class CrewListingSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    nationality_type_display = serializers.CharField(source='get_nationality_type_display', read_only=True)
    is_owner = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)
    is_following = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = CrewListing
        fields = [
            'id', 'user', 'user_name', 'name', 'gender', 'gender_display',
            'nationality_type', 'nationality_type_display', 'nationality',
            'residence', 'position', 'total_sea_experience',
            'current_rank_experience', 'cert_number', 'phone', 'email',
            'expected_salary', 'resume', 'status', 'status_display',
            'created_at', 'updated_at', 'is_owner', 'is_following', 'is_favorited'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            ret['phone'] = None
            ret['email'] = None
            ret['residence'] = None 
            ret['cert_number'] = None 
        return ret

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user or request.user.is_staff or request.user.is_superuser
        return False
        
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFollow.objects.filter(follower=request.user, followed=obj.user).exists()
        return False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from django.contrib.contenttypes.models import ContentType
            ct = ContentType.objects.get_for_model(CrewListing)
            return Favorite.objects.filter(user=request.user, content_type=ct, object_id=obj.id).exists()
        return False

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method == 'POST':
            if hasattr(request.user, 'crew_profile'):
                 raise serializers.ValidationError("You already have a crew profile.")
        return attrs
