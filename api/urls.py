from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from transactions.views import TransactionViewSet, TransactionDocumentViewSet
from news.views import ArticleViewSet
from forum.views import SectionViewSet, ThreadViewSet
from reports.views import ReportViewSet
from regulatory.views import RegulatoryViewSet

router = DefaultRouter()
router.register(r'listings', views.ShipListingViewSet)
router.register(r'listing_images', views.ListingImageViewSet)
router.register(r'news', views.MarketNewsViewSet)
router.register(r'ads', views.AdvertisementViewSet)
router.register(r'messages', views.MemberMessageViewSet)
router.register(r'message-replies', views.MessageReplyViewSet)
router.register(r'matches', views.ListingMatchViewSet, basename='matches')
router.register(r'private-messages', views.PrivateMessageViewSet, basename='private-messages')
router.register(r'favorites', views.FavoriteViewSet, basename='favorites')
router.register(r'following', views.UserFollowViewSet, basename='following')
router.register(r'transactions', TransactionViewSet, basename='transactions')
router.register(r'transaction-docs', TransactionDocumentViewSet, basename='transaction-docs')
router.register(r'crew', views.CrewListingViewSet, basename='crew')
router.register(r'notifications', views.NotificationViewSet, basename='notifications')

# New compliant apps
router.register(r'articles', ArticleViewSet, basename='articles')
router.register(r'forum/sections', SectionViewSet, basename='forum-section')
router.register(r'forum/threads', ThreadViewSet, basename='forum-thread')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'regulatory', RegulatoryViewSet, basename='regulatory')

urlpatterns = [
    path('user/info/', views.UserInfoView.as_view(), name='user_info'),
    path('user/search/', views.UserSearchView.as_view(), name='user_search'),
    path('admin/stats/', views.AdminStatsView.as_view(), name='admin_stats'),
    path('admin/channel-stats/', views.AdminChannelStatsView.as_view(), name='admin_channel_stats'),
    path('mine/stats/', views.MineStatsView.as_view(), name='mine_stats'),
    path('auth/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/wechat/', views.WeChatLoginView.as_view(), name='wechat_login'),
    path('auth/oa/authorize/', views.WeChatOAAuthorizeView.as_view(), name='oa_authorize'),
    path('auth/oa/callback/', views.WeChatOACallbackView.as_view(), name='oa_callback'),
    path('auth/sms/send/', views.SendSMSView.as_view(), name='send_sms'),
    path('auth/sms/login/', views.SMSLoginView.as_view(), name='sms_login'),
    path('auth/email/send/', views.SendEmailView.as_view(), name='send_email'),
    path('auth/email/login/', views.EmailLoginView.as_view(), name='email_login'),
    path('auth/bind-phone/', views.BindPhoneView.as_view(), name='bind_phone'),
    path('auth/bind-wechat/', views.BindWeChatView.as_view(), name='bind_wechat'),
    path('auth/unbind-wechat/', views.UnbindWeChatView.as_view(), name='unbind_wechat'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('user/profile/update/', views.UserProfileUpdateView.as_view(), name='user_profile_update'),
    path('user/delete/', views.DeleteUserView.as_view(), name='user_delete'),
    path('users/<int:pk>/profile/', views.UserProfileDetailView.as_view(), name='user_profile_detail'),
    path('matching/', include('hymart_matching.urls')),
    path('', include(router.urls)),
]
