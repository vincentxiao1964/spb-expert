from rest_framework import viewsets, exceptions, views, status, mixins, filters
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.contenttypes.models import ContentType
from market.models import ShipListing, MarketNews, ListingImage, ListingMatch, Favorite
from ads.models import Advertisement
from core.models import MemberMessage, PrivateMessage, MessageReply, Notification
from users.models import UserFollow, VisitorLog, ChannelEvent
from crew.models import CrewListing
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    ShipListingSerializer, MarketNewsSerializer, AdvertisementSerializer, 
    ListingImageSerializer, MemberMessageSerializer, ListingMatchSerializer,
    PrivateMessageSerializer, FavoriteSerializer, CustomTokenObtainPairSerializer,
    MessageReplySerializer, MemberMessageDetailSerializer, UserFollowSerializer,
    CrewListingSerializer, NotificationSerializer
)
from .permissions import IsOwnerOrAdmin, IsActiveForWrite
from .wechat_utils import check_msg_sec, check_img_sec, submit_media_check_async
from .models import MediaCheckTask
from django.db.models import Q, F, Sum, Count, Max
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta
from .pagination import DefaultPagination
from django.db.models.functions import TruncHour
import requests
import random
import uuid
import hashlib
import xml.etree.ElementTree as ET
import json
from django.core.cache import cache
from django.core.mail import send_mail, get_connection
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import logging
import re
import time
from urllib.parse import urlparse, parse_qs, unquote_plus
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models as sms_models

User = get_user_model()
logger = logging.getLogger(__name__)

def _normalize_cn_phone_number(phone_number):
    if phone_number is None:
        return None
    s = str(phone_number).strip().replace(" ", "").replace("-", "")
    if s.startswith("+86"):
        s = s[3:]
    if s.startswith("86") and len(s) == 13:
        s = s[2:]
    if not re.fullmatch(r"1\d{10}", s):
        return None
    return s

def _e164_cn(phone_number):
    return f"+86{phone_number}"

def _normalize_email(email):
    if email is None:
        return None
    value = str(email).strip().lower()
    if not value:
        return None
    try:
        validate_email(value)
    except ValidationError:
        return None
    return value

def _get_wechat_oa_access_token(appid, secret):
    cache_key = f"wechat_oa_access_token:{appid}"
    token = cache.get(cache_key)
    if token:
        return token

    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        'grant_type': 'client_credential',
        'appid': appid,
        'secret': secret,
    }
    res = requests.get(url, params=params, timeout=10)
    data = res.json()
    if data.get('errcode') or not data.get('access_token'):
        raise ValueError(f"WeChat token error: {data.get('errmsg') or data}")

    token = data['access_token']
    expires_in = int(data.get('expires_in') or 7200)
    cache.set(cache_key, token, timeout=max(60, expires_in - 120))
    return token

def _sanitize_source_channel(value):
    if not value:
        return None
    value = str(value).strip()
    if not value:
        return None
    value = ''.join(c for c in value if c.isalnum() or c in ('-', '_'))[:32]
    return value or None

def _get_source_channel(request, *, fallback_state=None):
    ch = None
    try:
        ch = request.COOKIES.get('src_ch')
    except Exception:
        ch = None
    if not ch:
        try:
            ch = request.query_params.get('ch')
        except Exception:
            ch = None
    if not ch:
        try:
            ch = request.data.get('source_channel')
        except Exception:
            ch = None
    if not ch and fallback_state:
        try:
            state = unquote_plus(str(fallback_state))
            parsed = urlparse(state)
            q = parse_qs(parsed.query)
            if q.get('ch'):
                ch = q.get('ch')[0]
        except Exception:
            ch = None
    return _sanitize_source_channel(ch)

def _apply_source_channel(user, channel):
    if not channel or not user:
        return
    if getattr(user, 'source_channel', None):
        return
    user.source_channel = channel
    user.save(update_fields=['source_channel'])

def _track_channel_event(request, user, event_type):
    if not user:
        return
    channel = getattr(user, 'source_channel', None) or _get_source_channel(request)
    channel = _sanitize_source_channel(channel)
    ChannelEvent.objects.create(
        user=user,
        source_channel=channel,
        event_type=event_type,
    )

def _build_public_media_url(request, file_url):
    if not file_url:
        return ''
    url = file_url
    if not url.startswith('http'):
        try:
            url = request.build_absolute_uri(url)
        except Exception:
            url = ''
    if url.startswith('http://'):
        try:
            forwarded = request.META.get('HTTP_X_FORWARDED_PROTO')
        except Exception:
            forwarded = None
        if forwarded == 'https' or getattr(settings, 'SECURE_PROXY_SSL_HEADER', None):
            url = 'https://' + url[len('http://'):]
    return url


def _enqueue_media_check(request, object_type, object_id, file_url, object_field='image', scene=4):
    media_url = _build_public_media_url(request, file_url)
    if not media_url:
        return None
    openid = getattr(request.user, 'openid', '') if getattr(request, 'user', None) else ''
    trace_id, _ = submit_media_check_async(media_url=media_url, media_type=2, openid=openid, scene=scene)
    if not trace_id:
        return None
    try:
        MediaCheckTask.objects.update_or_create(
            trace_id=trace_id,
            defaults={
                'object_type': object_type,
                'object_id': int(object_id),
                'object_field': object_field,
                'media_type': 2,
                'media_url': media_url,
                'scene': int(scene),
                'openid': openid or None,
            },
        )
    except Exception:
        return None
    return trace_id


def _verify_wechat_signature(token, signature, timestamp, nonce):
    token = (token or '').strip()
    signature = (signature or '').strip()
    timestamp = (timestamp or '').strip()
    nonce = (nonce or '').strip()
    if not token or not signature or not timestamp or not nonce:
        return False
    raw = ''.join(sorted([token, timestamp, nonce]))
    return hashlib.sha1(raw.encode('utf-8')).hexdigest() == signature


def _parse_wechat_xml(body_bytes):
    root = ET.fromstring(body_bytes)
    data = {}
    for child in list(root):
        data[child.tag] = child.text
    return data


def _safe_json_loads(value):
    if not value:
        return None
    if isinstance(value, (dict, list)):
        return value
    s = str(value).strip()
    if not s:
        return None
    if not (s.startswith('{') or s.startswith('[')):
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


def _apply_media_check_enforcement(task):
    if task.object_type == 'listing_image':
        ListingImage.objects.filter(id=task.object_id).delete()
        return
    if task.object_type == 'market_news':
        obj = MarketNews.objects.filter(id=task.object_id).first()
        if not obj:
            return
        if obj.image:
            try:
                obj.image.delete(save=False)
            except Exception:
                pass
        obj.image = None
        obj.save(update_fields=['image'])
        return
    if task.object_type == 'advertisement':
        obj = Advertisement.objects.filter(id=task.object_id).first()
        if not obj:
            return
        if obj.image:
            try:
                obj.image.delete(save=False)
            except Exception:
                pass
        obj.image = None
        obj.save(update_fields=['image'])
        return
    if task.object_type == 'private_message':
        obj = PrivateMessage.objects.filter(id=task.object_id).first()
        if not obj:
            return
        if obj.image:
            try:
                obj.image.delete(save=False)
            except Exception:
                pass
        obj.image = None
        obj.content = ''
        obj.save(update_fields=['image', 'content'])


class WeChatMediaCheckCallbackView(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        token = getattr(settings, 'WECHAT_MSG_PUSH_TOKEN', None) or getattr(settings, 'WECHAT_MESSAGE_TOKEN', None) or ''
        signature = request.query_params.get('signature', '') or request.query_params.get('msg_signature', '')
        timestamp = request.query_params.get('timestamp', '')
        nonce = request.query_params.get('nonce', '')
        echostr = request.query_params.get('echostr', '')
        if token and not _verify_wechat_signature(token, signature, timestamp, nonce):
            return Response({'error': 'invalid signature'}, status=status.HTTP_403_FORBIDDEN)
        return HttpResponse(echostr)

    def post(self, request):
        token = getattr(settings, 'WECHAT_MSG_PUSH_TOKEN', None) or getattr(settings, 'WECHAT_MESSAGE_TOKEN', None) or ''
        signature = request.query_params.get('signature', '') or request.query_params.get('msg_signature', '')
        timestamp = request.query_params.get('timestamp', '')
        nonce = request.query_params.get('nonce', '')
        if token and not _verify_wechat_signature(token, signature, timestamp, nonce):
            return Response({'error': 'invalid signature'}, status=status.HTTP_403_FORBIDDEN)

        body = request.body or b''
        data = {}
        try:
            if body.strip().startswith(b'<'):
                data = _parse_wechat_xml(body)
            else:
                data = json.loads(body.decode('utf-8'))
        except Exception:
            data = {}

        trace_id = data.get('trace_id') or data.get('TraceId') or ''
        if not trace_id:
            return Response({'status': 'ok'})

        try:
            task = MediaCheckTask.objects.filter(trace_id=trace_id).first()
        except Exception:
            return Response({'status': 'ok'})
        if not task:
            return Response({'status': 'ok'})

        appid = data.get('appid') or data.get('AppId')
        errcode = data.get('errcode')
        if errcode is None:
            errcode = data.get('ErrCode')

        status_code = data.get('status_code')
        isrisky = data.get('isrisky')

        result = data.get('result')
        result_obj = _safe_json_loads(result) or (result if isinstance(result, dict) else None)
        suggest = None
        label = None
        if isinstance(result_obj, dict):
            suggest = result_obj.get('suggest')
            label = result_obj.get('label')

        final_status = MediaCheckTask.Status.PENDING
        if str(errcode or '0') != '0':
            final_status = MediaCheckTask.Status.ERROR
        elif str(status_code or '0') in ('-1008', '4294966288'):
            final_status = MediaCheckTask.Status.ERROR
        elif str(isrisky or '0') == '1':
            final_status = MediaCheckTask.Status.RISKY
        elif suggest in ('risky', 'review'):
            final_status = MediaCheckTask.Status.RISKY if suggest == 'risky' else MediaCheckTask.Status.REVIEW
        elif label is not None and int(label) != 100:
            final_status = MediaCheckTask.Status.RISKY
        else:
            final_status = MediaCheckTask.Status.PASS

        try:
            task.status = final_status
            task.appid = appid or task.appid
            task.suggest = suggest or task.suggest
            task.label = label if label is not None else task.label
            task.raw_result = data
            task.save(update_fields=['status', 'appid', 'suggest', 'label', 'raw_result', 'updated_at'])
        except Exception:
            return Response({'status': 'ok'})

        if task.status in (MediaCheckTask.Status.RISKY, MediaCheckTask.Status.REVIEW):
            _apply_media_check_enforcement(task)

        return Response({'status': 'ok'})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class SMSLoginView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        phone_number = _normalize_cn_phone_number(request.data.get('phone_number'))
        code = request.data.get('code')
        if not phone_number or not code:
            return Response({'error': 'Phone number and code are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify SMS code
        cache_key = f"sms_code_{phone_number}"
        cached_code = cache.get(cache_key)
        
        if not cached_code or str(cached_code) != str(code):
             return Response({'error': 'Invalid or expired verification code'}, status=status.HTTP_400_BAD_REQUEST)
             
        # Find or create user
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            # Auto-register
            # Use phone number as username by default
            username = phone_number
            if User.objects.filter(username=username).exists():
                # If username taken (unlikely but possible), append suffix
                import uuid
                username = f"{phone_number}_{uuid.uuid4().hex[:4]}"
            
            user = User.objects.create_user(username=username, phone_number=phone_number)
            # Set a random password or unusable password since they logged in via SMS
            user.set_unusable_password()
            user.save()

        _apply_source_channel(user, _get_source_channel(request))
            
        # Generate Token
        refresh = RefreshToken.for_user(user)
        
        # Clear cache
        cache.delete(cache_key)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
            'is_staff': user.is_staff
        })

class SendSMSView(views.APIView):
    """
    Send SMS verification code via Tencent Cloud.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = _normalize_cn_phone_number(request.data.get('phone_number'))
        if not phone_number:
            return Response({'error': 'Invalid phone number'}, status=status.HTTP_400_BAD_REQUEST)

        send_interval = int(getattr(settings, 'SMS_SEND_INTERVAL_SECONDS', 60) or 60)
        cooldown_key = f"sms_send_cooldown_{phone_number}"
        cooldown_until = cache.get(cooldown_key)
        if cooldown_until:
            retry_after = int(max(1, float(cooldown_until) - time.time()))
            return Response({'error': 'Too many requests', 'retry_after': retry_after}, status=429)

        code_ttl = int(getattr(settings, 'SMS_CODE_TTL_SECONDS', 300) or 300)
        code = str(random.randint(100000, 999999))

        secret_id = getattr(settings, 'TENCENT_CLOUD_SECRET_ID', None)
        secret_key = getattr(settings, 'TENCENT_CLOUD_SECRET_KEY', None)
        sms_sdk_app_id = getattr(settings, 'SMS_SDK_APP_ID', None)
        sms_sign_name = getattr(settings, 'SMS_SIGN_NAME', None)
        sms_template_id = getattr(settings, 'SMS_TEMPLATE_ID', None)
        sms_template_param_set = getattr(settings, 'SMS_TEMPLATE_PARAM_SET', '') or ''
        sms_region = getattr(settings, 'SMS_REGION', 'ap-guangzhou')

        has_sms_config = all([secret_id, secret_key, sms_sdk_app_id, sms_sign_name, sms_template_id])

        cache_key = f"sms_code_{phone_number}"

        if not has_sms_config:
            if getattr(settings, 'DEBUG', False):
                cache.set(cache_key, code, timeout=code_ttl)
                cache.set(cooldown_key, time.time() + send_interval, timeout=send_interval)
                return Response({'message': 'SMS sent successfully', 'code': code})
            return Response({'error': 'SMS not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            cred = credential.Credential(secret_id, secret_key)
            http_profile = HttpProfile()
            http_profile.endpoint = "sms.tencentcloudapi.com"
            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile
            client = sms_client.SmsClient(cred, sms_region, client_profile)

            req = sms_models.SendSmsRequest()
            req.SmsSdkAppId = str(sms_sdk_app_id)
            req.SignName = str(sms_sign_name)
            req.TemplateId = str(sms_template_id)
            req.PhoneNumberSet = [_e164_cn(phone_number)]
            ttl_minutes = str(max(1, code_ttl // 60))
            if sms_template_param_set.strip():
                parts = [p.strip() for p in sms_template_param_set.split(',') if p.strip()]
                req.TemplateParamSet = [p.replace('{code}', code).replace('{ttl}', ttl_minutes) for p in parts]
            else:
                req.TemplateParamSet = [code, ttl_minutes]

            resp = client.SendSms(req)
            status_set = getattr(resp, 'SendStatusSet', None) or []
            first = status_set[0] if status_set else None

            if not first:
                logger.error("Tencent SMS empty SendStatusSet, request_id=%s", getattr(resp, 'RequestId', None))
                return Response({'error': 'SMS provider error'}, status=status.HTTP_502_BAD_GATEWAY)

            if getattr(first, 'Code', None) != 'Ok':
                payload = {
                    'error': 'SMS send failed',
                    'sms_errcode': getattr(first, 'Code', None),
                    'sms_errmsg': getattr(first, 'Message', None),
                    'request_id': getattr(resp, 'RequestId', None),
                }
                logger.warning("Tencent SMS send failed: %s", payload)
                return Response(payload, status=status.HTTP_400_BAD_REQUEST)

            cache.set(cache_key, code, timeout=code_ttl)
            cache.set(cooldown_key, time.time() + send_interval, timeout=send_interval)
            return Response({'message': 'SMS sent successfully'})
        except TencentCloudSDKException as e:
            logger.exception("Tencent SMS SDK error")
            return Response({'error': 'SMS provider error', 'detail': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            logger.exception("SMS send error")
            return Response({'error': 'SMS send error', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SendEmailView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = _normalize_email(request.data.get('email'))
        if not email:
            return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

        send_interval = int(getattr(settings, 'EMAIL_SEND_INTERVAL_SECONDS', 60) or 60)
        cooldown_key = f"email_send_cooldown_{email}"
        cooldown_until = cache.get(cooldown_key)
        if cooldown_until:
            retry_after = int(max(1, float(cooldown_until) - time.time()))
            return Response({'error': 'Too many requests', 'retry_after': retry_after}, status=429)

        code_ttl = int(getattr(settings, 'EMAIL_CODE_TTL_SECONDS', 600) or 600)
        code = str(random.randint(100000, 999999))

        cache_key = f"email_code_{email}"

        has_email_config = all([
            getattr(settings, 'EMAIL_HOST', ''),
            getattr(settings, 'EMAIL_HOST_USER', ''),
            getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
        ])

        subject = getattr(settings, 'EMAIL_VERIFICATION_SUBJECT', 'SPB EXPERT verification code')
        ttl_minutes = str(max(1, code_ttl // 60))
        body = f"Your verification code is: {code}\n\nIt will expire in {ttl_minutes} minutes."

        if not has_email_config:
            if getattr(settings, 'DEBUG', False):
                cache.set(cache_key, code, timeout=code_ttl)
                cache.set(cooldown_key, time.time() + send_interval, timeout=send_interval)
                return Response({'message': 'Email sent successfully', 'code': code})
            return Response({'error': 'Email not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            timeout = int(getattr(settings, 'EMAIL_TIMEOUT', 15) or 15)
            connection = get_connection(timeout=timeout)
            send_mail(
                subject=subject,
                message=body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=[email],
                fail_silently=False,
                connection=connection,
            )
            cache.set(cache_key, code, timeout=code_ttl)
            cache.set(cooldown_key, time.time() + send_interval, timeout=send_interval)
            return Response({'message': 'Email sent successfully'})
        except Exception as e:
            logger.exception("Email send error")
            return Response({'error': 'Email send failed', 'detail': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

class EmailLoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = _normalize_email(request.data.get('email'))
        code = request.data.get('code')
        if not email or not code:
            return Response({'error': 'Email and code are required'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"email_code_{email}"
        cached_code = cache.get(cache_key)
        if not cached_code or str(cached_code) != str(code):
            return Response({'error': 'Invalid or expired verification code'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(login_email__iexact=email).first() or User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({'error': 'Email not registered', 'code': 'email_not_registered'}, status=status.HTTP_400_BAD_REQUEST)

        _apply_source_channel(user, _get_source_channel(request))

        refresh = RefreshToken.for_user(user)
        cache.delete(cache_key)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
            'is_staff': user.is_staff,
            'membership_level': getattr(user, 'membership_level', None),
            'phone_number': getattr(user, 'phone_number', None),
            'login_email': getattr(user, 'login_email', None),
        })

class EmailRegisterView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = _normalize_email(request.data.get('email'))
        code = request.data.get('code')
        if not email or not code:
            return Response({'error': 'Email and code are required'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"email_code_{email}"
        cached_code = cache.get(cache_key)
        if not cached_code or str(cached_code) != str(code):
            return Response({'error': 'Invalid or expired verification code'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(login_email__iexact=email).exists() or User.objects.filter(email__iexact=email).exists():
            return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

        base = email.split('@')[0]
        username = re.sub(r'[^a-zA-Z0-9_\\-]', '_', base)[:20] or 'user'
        if User.objects.filter(username=username).exists():
            username = f"em_{uuid.uuid4().hex[:8]}"

        user = User.objects.create_user(username=username, email=email)
        user.set_unusable_password()
        user.login_email = email
        user.save()

        _apply_source_channel(user, _get_source_channel(request))

        refresh = RefreshToken.for_user(user)
        cache.delete(cache_key)

        return Response({
            'status': 'registered',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
            'login_email': user.login_email,
        }, status=status.HTTP_201_CREATED)

class BindPhoneView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        code = request.data.get('code')
        company_name = request.data.get('company_name', '')
        job_title = request.data.get('job_title', '')
        business_content = request.data.get('business_content', '')

        if not phone_number or not code:
            return Response({'error': 'Phone number and code are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify SMS code
        cache_key = f"sms_code_{phone_number}"
        cached_code = cache.get(cache_key)
        
        if not cached_code or str(cached_code) != str(code):
             return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
             
        # Check if phone number is already registered
        User = get_user_model()
        existing_user = User.objects.filter(phone_number=phone_number).first()
        
        current_user = request.user
        
        if existing_user and existing_user.id != current_user.id:
            # Phone number belongs to another user
            if existing_user.openid:
                # The existing user is already bound to a WeChat account
                return Response({'error': 'This phone number is already bound to another WeChat account. Please log in with phone number directly.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # The existing user has no WeChat binding, so we can merge
            # Transfer WeChat info from current temporary user to existing user
            openid = current_user.openid
            unionid = current_user.unionid
            
            # Delete current temporary user to avoid unique constraint violation on openid
            current_user.delete()
            
            # Update existing user
            existing_user.openid = openid
            existing_user.unionid = unionid
            
            if company_name: existing_user.company_name = company_name
            if job_title: existing_user.job_title = job_title
            if business_content: existing_user.business_content = business_content
            
            existing_user.save()
            
            # Generate new tokens for the existing user
            refresh = RefreshToken.for_user(existing_user)
            
            return Response({
                'message': 'Phone bound successfully (merged)',
                'status': 'merged',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': existing_user.id,
                'username': existing_user.username,
                'phone_number': existing_user.phone_number
            })
            
        else:
            # Phone number is available or belongs to current user
            current_user.phone_number = phone_number
            if company_name: current_user.company_name = company_name
            if job_title: current_user.job_title = job_title
            if business_content: current_user.business_content = business_content
            
            try:
                current_user.save()
            except Exception as e:
                return Response({'error': f'Binding failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
            return Response({
                'message': 'Phone bound successfully',
                'status': 'updated',
                'user_id': current_user.id,
                'username': current_user.username,
                'phone_number': current_user.phone_number
            })

class BindWeChatView(views.APIView):
    """
    Bind WeChat account (OpenID/UnionID) to the current authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        if not code:
             return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve WeChat credentials
        appid = getattr(settings, 'WECHAT_MINI_PROGRAM_APP_ID', None)
        secret = getattr(settings, 'WECHAT_MINI_PROGRAM_APP_SECRET', None)
        
        if not appid or not secret:
             return Response({'error': 'WeChat credentials not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            'appid': appid,
            'secret': secret,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        
        try:
            res = requests.get(url, params=params)
            data = res.json()
            
            if 'errcode' in data and data['errcode'] != 0:
                logger.warning("WeChat jscode2session error (bind): %s", data)
                return Response(
                    {
                        'error': f"WeChat Error: {data.get('errmsg')}",
                        'wechat_errcode': data.get('errcode'),
                        'wechat_errmsg': data.get('errmsg'),
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            openid = data.get('openid')
            unionid = data.get('unionid')
            
            if not openid:
                return Response({'error': 'Failed to get OpenID'}, status=status.HTTP_400_BAD_REQUEST)

            current_user = request.user
            
            # Check if this WeChat account is already bound to ANOTHER user
            # Check by UnionID first (stronger link)
            existing_user = None
            if unionid:
                existing_user = User.objects.filter(unionid=unionid).exclude(id=current_user.id).first()
            
            if not existing_user:
                existing_user = User.objects.filter(openid=openid).exclude(id=current_user.id).first()
            
            if existing_user:
                # Merge Logic:
                # If existing user is a temporary WeChat account (no phone number OR phone number is a placeholder), merge it into current user.
                existing_user_phone = getattr(existing_user, 'phone_number', '')
                
                # Check if phone is empty OR starts with 'wx_' (placeholder)
                is_temp_account = not existing_user_phone or existing_user_phone.startswith('wx_')
                
                if is_temp_account:
                    # It's a temporary account, safe to steal the binding
                    existing_user.openid = None
                    existing_user.unionid = None
                    existing_user.save()
                    
                    # Delete if it's purely a placeholder
                    if existing_user.username.startswith('wx_'):
                         existing_user.delete()
                    
                else:
                    # It's a real account with a phone number
                    return Response({'error': f'This WeChat account is already bound to another phone user (User ID: {existing_user.id}). Please log in with that account.'}, status=status.HTTP_400_BAD_REQUEST)

            # Bind to current user
            current_user.openid = openid
            if unionid:
                current_user.unionid = unionid
            current_user.save()
            
            return Response({
                'status': 'success',
                'message': 'WeChat account bound successfully',
                'openid': openid,
                'unionid': unionid
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegisterView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        phone_number = request.data.get('phone_number')
        
        if not username or not password:
             return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
             
        if User.objects.filter(username=username).exists():
             return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
             
        user = User.objects.create_user(username=username, password=password, phone_number=phone_number)
        _apply_source_channel(user, _get_source_channel(request))
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username
        })

class UnbindWeChatView(views.APIView):
    """
    Unbind WeChat account from the current authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # Security check: Ensure user has an alternative login method (phone number)
        # If phone_number is empty or starts with 'wx_', they might be locked out
        phone_number = getattr(user, 'phone_number', '')
        if not phone_number or phone_number.startswith('wx_'):
             return Response({'error': 'Please bind a phone number before unbinding WeChat to ensure account access.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.openid = None
            user.unionid = None
            user.save()
            
            return Response({
                'status': 'success',
                'message': 'WeChat account unbound successfully'
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteUserView(views.APIView):
    """
    Allow user to delete (deactivate) their account.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        
        # Anonymize sensitive data
        import uuid
        random_suffix = uuid.uuid4().hex[:8]
        
        # We keep the ID for referential integrity of logs, but remove PII
        user.is_active = False
        user.username = f"deleted_{user.id}_{random_suffix}"
        user.phone_number = None  # Release the phone number
        user.email = f"deleted_{user.id}_{random_suffix}@deleted.com" # Placeholder to satisfy email format if needed
        
        # Unbind WeChat
        user.openid = None
        user.unionid = None
        
        # Clear profile info
        user.company_name = ""
        user.job_title = ""
        user.business_content = ""
        
        user.save()
        
        return Response({
            'status': 'success', 
            'message': 'Account deleted and data anonymized successfully'
        })

class UserInfoView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        
        avatar_url = user.avatar.url if user.avatar else None
        if avatar_url and not avatar_url.startswith('http'):
             avatar_url = request.build_absolute_uri(avatar_url)
             
        data = {
            'id': user.id,
            'username': user.username,
            'phone_number': getattr(user, 'phone_number', ''),
            'email': user.email,
            'is_staff': user.is_staff,
            'company_name': getattr(user, 'company_name', ''),
            'job_title': getattr(user, 'job_title', ''),
            'is_wechat_bound': bool(getattr(user, 'openid', None)),
            'avatar': avatar_url,
        }
        return Response(data)

class UserProfileUpdateView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        return self.put(request)

    def put(self, request):
        user = request.user
        user.company_name = request.data.get('company_name', user.company_name)
        user.job_title = request.data.get('job_title', user.job_title)
        
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            
        user.save()
        
        avatar_url = user.avatar.url if user.avatar else None
        if avatar_url and not avatar_url.startswith('http'):
             # Assuming standard media setup, but for API full URL is better
             request = self.request
             avatar_url = request.build_absolute_uri(avatar_url)
             
        return Response({
            'message': 'Profile updated',
            'company_name': user.company_name,
            'job_title': user.job_title,
            'phone_number': user.phone_number,
            'email': user.email,
            'avatar': avatar_url
        })

class UserSearchView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response([])
        users = User.objects.filter(username__icontains=query)[:10]
        data = [{'id': u.id, 'username': u.username} for u in users]
        return Response(data)

class AdminStatsView(views.APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        now = timezone.now()
        since = now - timedelta(days=7)

        total_users = User.objects.count()
        users_by_channel = User.objects.values('source_channel').annotate(count=Count('id')).order_by('-count')
        new_users_by_channel_7d = (
            User.objects.filter(date_joined__gte=since)
            .values('source_channel')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        def _normalize(items):
            result = []
            for row in items:
                result.append({
                    'source_channel': row.get('source_channel') or 'UNKNOWN',
                    'count': row.get('count', 0),
                })
            return result

        return Response({
            'total_users': total_users,
            'users_by_source_channel': _normalize(users_by_channel),
            'new_users_by_source_channel_last_7_days': _normalize(new_users_by_channel_7d),
        })

class AdminChannelStatsView(views.APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        days = int(request.query_params.get('days') or 7)
        days = max(1, min(days, 365))

        since = timezone.now() - timedelta(days=days)
        qs = ChannelEvent.objects.filter(created_at__gte=since)

        rows = (
            qs.values('source_channel', 'event_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        result = {}
        for row in rows:
            ch = row.get('source_channel') or 'UNKNOWN'
            et = row.get('event_type')
            if ch not in result:
                result[ch] = {}
            result[ch][et] = row.get('count', 0)

        return Response({
            'days': days,
            'since': since,
            'events_by_source_channel': result,
        })

class MineStatsView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({'message': 'Mine stats'})

class WeChatLoginView(views.APIView):
    """
    API endpoint for WeChat Mini Program login.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('code')
        user_info = request.data.get('userInfo', {})
        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve WeChat credentials
        appid = getattr(settings, 'WECHAT_MINI_PROGRAM_APP_ID', None)
        secret = getattr(settings, 'WECHAT_MINI_PROGRAM_APP_SECRET', None)
        
        if not appid or not secret:
             return Response({'error': 'WeChat credentials not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            'appid': appid,
            'secret': secret,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        
        try:
            res = requests.get(url, params=params)
            data = res.json()
            
            if 'errcode' in data and data['errcode'] != 0:
                logger.warning("WeChat jscode2session error (login): %s", data)
                return Response(
                    {
                        'error': f"WeChat Error: {data.get('errmsg')}",
                        'wechat_errcode': data.get('errcode'),
                        'wechat_errmsg': data.get('errmsg'),
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            openid = data.get('openid')
            unionid = data.get('unionid')
            
            if not openid:
                return Response({'error': 'Failed to get OpenID'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Find or create user
            # Try to find by unionid first if available (for cross-app account linking)
            user = None
            if unionid:
                user = User.objects.filter(unionid=unionid).first()
            
            if not user:
                user = User.objects.filter(openid=openid).first()
                
            if user:
                # User exists
                # Update unionid/openid if missing
                if not user.openid:
                    user.openid = openid
                    user.save()
                if unionid and not user.unionid:
                    user.unionid = unionid
                    user.save()

                _apply_source_channel(user, _get_source_channel(request))
                    
                refresh = RefreshToken.for_user(user)
                
                # Check if phone number is bound
                phone_number = getattr(user, 'phone_number', None)
                # Consider it bound if phone_number is present and doesn't start with 'wx_'
                is_bound = phone_number and not phone_number.startswith('wx_')
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_id': user.id,
                    'username': user.username,
                    'phone_number': phone_number if is_bound else None,
                    'is_staff': user.is_staff,
                    'status': 'active' if is_bound else 'bind_phone'
                })
            else:
                # Create new user
                # Use openid as temporary username
                username = f"wx_{openid[-8:]}"
                # Ensure uniqueness
                if User.objects.filter(username=username).exists():
                     username = f"wx_{uuid.uuid4().hex[:8]}"
                     
                user = User.objects.create_user(
                    username=username,
                    password=None, # Unusable password
                    openid=openid,
                    unionid=unionid,
                    phone_number=f"wx_{openid[:8]}" # Placeholder phone
                )
                user.set_unusable_password()
                user.save()

                _apply_source_channel(user, _get_source_channel(request))
                
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_id': user.id,
                    'username': user.username,
                    'status': 'bind_phone'
                })
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WeChatOAAuthorizeView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        appid = getattr(settings, 'WECHAT_OA_APP_ID', None)
        secret = getattr(settings, 'WECHAT_OA_APP_SECRET', None)
        if not appid or not secret:
            return Response({'error': 'WeChat OA credentials not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        next_url = (request.query_params.get('next') or '/').strip()
        if not next_url.startswith('/'):
            next_url = '/'

        callback = request.build_absolute_uri('/api/v1/auth/oa/callback/')
        scope = getattr(settings, 'WECHAT_OA_OAUTH_SCOPE', 'snsapi_base') or 'snsapi_base'

        auth_url = (
            "https://open.weixin.qq.com/connect/oauth2/authorize"
            f"?appid={appid}"
            f"&redirect_uri={requests.utils.quote(callback, safe='')}"
            "&response_type=code"
            f"&scope={scope}"
            f"&state={requests.utils.quote(next_url[:256], safe='')}"
            "#wechat_redirect"
        )
        return HttpResponseRedirect(auth_url)


class WeChatOACallbackView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get('code')
        state = (request.query_params.get('state') or '/').strip()
        if not state.startswith('/'):
            state = '/'

        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)

        appid = getattr(settings, 'WECHAT_OA_APP_ID', None)
        secret = getattr(settings, 'WECHAT_OA_APP_SECRET', None)
        if not appid or not secret:
            return Response({'error': 'WeChat OA credentials not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        params = {
            'appid': appid,
            'secret': secret,
            'code': code,
            'grant_type': 'authorization_code',
        }

        try:
            res = requests.get(token_url, params=params, timeout=10)
            data = res.json()

            if data.get('errcode'):
                return Response(
                    {
                        'error': f"WeChat Error: {data.get('errmsg')}",
                        'wechat_errcode': data.get('errcode'),
                        'wechat_errmsg': data.get('errmsg'),
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            oa_openid = data.get('openid')
            unionid = data.get('unionid')
            oauth_access_token = data.get('access_token')
            if not oa_openid:
                return Response({'error': 'Failed to get OpenID'}, status=status.HTTP_400_BAD_REQUEST)

            if not unionid:
                try:
                    if oauth_access_token:
                        sns_info_url = "https://api.weixin.qq.com/sns/userinfo"
                        sns_info_params = {
                            'access_token': oauth_access_token,
                            'openid': oa_openid,
                            'lang': 'zh_CN',
                        }
                        sns_info_res = requests.get(sns_info_url, params=sns_info_params, timeout=10)
                        sns_info_data = sns_info_res.json()
                        if sns_info_data.get('unionid'):
                            unionid = sns_info_data.get('unionid')
                except Exception:
                    logger.exception("WeChat OA sns/userinfo unionid fetch failed")

            if not unionid:
                try:
                    access_token = _get_wechat_oa_access_token(appid, secret)
                    info_url = "https://api.weixin.qq.com/cgi-bin/user/info"
                    info_params = {
                        'access_token': access_token,
                        'openid': oa_openid,
                        'lang': 'zh_CN',
                    }
                    info_res = requests.get(info_url, params=info_params, timeout=10)
                    info_data = info_res.json()
                    if info_data.get('unionid'):
                        unionid = info_data.get('unionid')
                except Exception:
                    logger.exception("WeChat OA cgi-bin/user/info unionid fetch failed")

            target_user = None
            if unionid:
                target_user = User.objects.filter(unionid=unionid).first()

            oa_user = User.objects.filter(oa_openid=oa_openid).first()

            if target_user and oa_user and oa_user.id != target_user.id:
                placeholder_phone = getattr(oa_user, 'phone_number', None) or ''
                if (
                    (getattr(oa_user, 'openid', None) in (None, '')) and
                    (getattr(oa_user, 'unionid', None) in (None, '')) and
                    placeholder_phone.startswith('wx_') and
                    (oa_user.username or '').startswith('oa_')
                ):
                    oa_user.delete()
                    oa_user = None
                else:
                    oa_user.oa_openid = None
                    oa_user.save(update_fields=['oa_openid'])
                    oa_user = None

            user = target_user or oa_user

            if user:
                updated = False
                if getattr(user, 'oa_openid', None) in (None, ''):
                    user.oa_openid = oa_openid
                    updated = True
                if unionid and getattr(user, 'unionid', None) in (None, ''):
                    user.unionid = unionid
                    updated = True
                if updated:
                    user.save()
            else:
                username = f"oa_{oa_openid[-8:]}"
                if User.objects.filter(username=username).exists():
                    username = f"oa_{uuid.uuid4().hex[:8]}"

                user = User.objects.create_user(
                    username=username,
                    password=None,
                    oa_openid=oa_openid,
                    unionid=unionid,
                    phone_number=f"wx_{oa_openid[:8]}",
                )
                user.set_unusable_password()
                user.save()

            _apply_source_channel(user, _get_source_channel(request, fallback_state=state))
            return HttpResponseRedirect(state)
        except Exception as e:
            logger.exception("WeChat OA callback error")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- ViewSets ---

class ShipListingViewSet(viewsets.ModelViewSet):
    queryset = ShipListing.objects.all().order_by('-created_at')
    serializer_class = ShipListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsActiveForWrite]
    pagination_class = DefaultPagination
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('user').select_related('extended_info').prefetch_related('images')

        manage = self.request.query_params.get('manage')
        if not self.request.user.is_authenticated or manage != 'true':
            queryset = queryset.filter(status=ShipListing.Status.APPROVED)
        
        # Filter by listing_type
        listing_type = self.request.query_params.get('listing_type')
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)
            
        # Filter by user (for management)
        if manage == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
            
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        return queryset
    
    def perform_create(self, serializer):
        data = serializer.validated_data
        check_content = " ".join([
            str(data.get('delivery_area', '') or ''),
            str(data.get('class_society', '') or ''),
            str(data.get('flag_state', '') or ''),
            str(data.get('description', '') or ''),
            str(data.get('description_en', '') or ''),
            str(data.get('contact_info', '') or ''),
        ]).strip()
        is_safe, _ = check_msg_sec(check_content, getattr(self.request.user, 'openid', ''), scene=4, scope='LISTING')
        if not is_safe:
            raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})
             
        serializer.save(user=self.request.user)
        _track_channel_event(self.request, self.request.user, ChannelEvent.EventType.LISTING_CREATE)

    def perform_update(self, serializer):
        data = serializer.validated_data
        check_content = " ".join([
            str(data.get('delivery_area', '') or ''),
            str(data.get('class_society', '') or ''),
            str(data.get('flag_state', '') or ''),
            str(data.get('description', '') or ''),
            str(data.get('description_en', '') or ''),
            str(data.get('contact_info', '') or ''),
        ]).strip()
        is_safe, _ = check_msg_sec(check_content, getattr(self.request.user, 'openid', ''), scene=4, scope='LISTING')
        if not is_safe:
            raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})
             
        serializer.save()

    @action(detail=False, methods=['GET'])
    def trending(self, request):
        """
        Return top 5 viewed listings for exposure.
        """
        trending_listings = self.queryset.order_by('-view_count')[:5]
        serializer = self.get_serializer(trending_listings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], parser_classes=[MultiPartParser])
    def upload_image(self, request, pk=None):
        listing = self.get_object()
        if 'image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded = request.FILES['image']
        image_bytes = uploaded.read()
        uploaded.seek(0)
        is_safe, _ = check_img_sec(image_bytes, filename=uploaded.name)
        if not is_safe:
            return Response({'error': '图片可能含违规信息，请更换后重试'}, status=status.HTTP_400_BAD_REQUEST)
        
        image = ListingImage.objects.create(
            listing=listing,
            image=request.FILES['image']
        )

        _enqueue_media_check(request, 'listing_image', image.id, getattr(image.image, 'url', ''), object_field='image', scene=4)
        
        serializer = ListingImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ListingImageViewSet(viewsets.ModelViewSet):
    queryset = ListingImage.objects.all()
    serializer_class = ListingImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class MarketNewsViewSet(viewsets.ModelViewSet):
    queryset = MarketNews.objects.all().select_related('user').order_by('-created_at')
    serializer_class = MarketNewsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsActiveForWrite]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'title_en', 'content_en']
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        manage = self.request.query_params.get('manage')
        if manage == 'true' and self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser):
            return queryset
        return queryset.filter(status=MarketNews.Status.APPROVED)

    def perform_create(self, serializer):
        data = serializer.validated_data
        check_content = " ".join([
            str(data.get('title', '') or ''),
            str(data.get('title_en', '') or ''),
            str(data.get('content', '') or ''),
            str(data.get('content_en', '') or ''),
            str(data.get('source_url', '') or ''),
            str(data.get('original_source', '') or ''),
        ]).strip()
        is_safe, _ = check_msg_sec(check_content, getattr(self.request.user, 'openid', ''), scene=4, scope='NEWS')
        if not is_safe:
            raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        data = serializer.validated_data
        check_content = " ".join([
            str(data.get('title', '') or ''),
            str(data.get('title_en', '') or ''),
            str(data.get('content', '') or ''),
            str(data.get('content_en', '') or ''),
            str(data.get('source_url', '') or ''),
            str(data.get('original_source', '') or ''),
        ]).strip()
        is_safe, _ = check_msg_sec(check_content, getattr(self.request.user, 'openid', ''), scene=4, scope='NEWS')
        if not is_safe:
            raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})
        serializer.save()

    @action(detail=True, methods=['POST'], parser_classes=[MultiPartParser])
    def upload_image(self, request, pk=None):
        print(f"upload_image called for pk={pk}")
        print(f"FILES keys: {request.FILES.keys()}")
        news = self.get_object()
        if 'image' not in request.FILES:
            print("No image in request.FILES")
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded = request.FILES['image']
        image_bytes = uploaded.read()
        uploaded.seek(0)
        is_safe, _ = check_img_sec(image_bytes, filename=uploaded.name)
        if not is_safe:
            return Response({'error': '图片可能含违规信息，请更换后重试'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Saving image: {request.FILES['image']}")
        news.image = request.FILES['image']
        news.save()
        print(f"Image saved. Path: {news.image.path}")

        _enqueue_media_check(request, 'market_news', news.id, getattr(news.image, 'url', ''), object_field='image', scene=4)
        
        serializer = self.get_serializer(news)
        return Response(serializer.data)

class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsActiveForWrite]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        data = serializer.validated_data
        check_content = " ".join([
            str(data.get('title', '') or ''),
            str(data.get('description', '') or ''),
            str(data.get('link', '') or ''),
        ]).strip()
        is_safe, _ = check_msg_sec(check_content, getattr(self.request.user, 'openid', ''), scene=4, scope='AD')
        if not is_safe:
            raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})

        image = self.request.FILES.get('image')
        if image:
            image_bytes = image.read()
            image.seek(0)
            ok, _ = check_img_sec(image_bytes, filename=image.name)
            if not ok:
                raise exceptions.ValidationError({'detail': '图片可能含违规信息，请更换后重试'})
        obj = serializer.save(user=self.request.user)
        if getattr(obj, 'image', None):
            _enqueue_media_check(self.request, 'advertisement', obj.id, getattr(obj.image, 'url', ''), object_field='image', scene=4)

    def perform_update(self, serializer):
        data = serializer.validated_data
        check_content = " ".join([
            str(data.get('title', '') or ''),
            str(data.get('description', '') or ''),
            str(data.get('link', '') or ''),
        ]).strip()
        is_safe, _ = check_msg_sec(check_content, getattr(self.request.user, 'openid', ''), scene=4, scope='AD')
        if not is_safe:
            raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})

        image = self.request.FILES.get('image')
        if image:
            image_bytes = image.read()
            image.seek(0)
            ok, _ = check_img_sec(image_bytes, filename=image.name)
            if not ok:
                raise exceptions.ValidationError({'detail': '图片可能含违规信息，请更换后重试'})
        obj = serializer.save()
        if getattr(obj, 'image', None):
            _enqueue_media_check(self.request, 'advertisement', obj.id, getattr(obj.image, 'url', ''), object_field='image', scene=4)

class MemberMessageViewSet(viewsets.ModelViewSet):
    queryset = MemberMessage.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticatedOrReadOnly, IsActiveForWrite, IsOwnerOrAdmin]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MemberMessageDetailSerializer
        return MemberMessageSerializer
    
    def perform_create(self, serializer):
        content = serializer.validated_data.get('content', '')
        is_safe, reason = check_msg_sec(content, getattr(self.request.user, 'openid', ''), scene=3, scope='FORUM')
        if not is_safe:
             raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        content = serializer.validated_data.get('content', '')
        is_safe, _ = check_msg_sec(content, getattr(self.request.user, 'openid', ''), scene=3, scope='FORUM')
        if not is_safe:
            raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})
        serializer.save()

class MessageReplyViewSet(viewsets.ModelViewSet):
    queryset = MessageReply.objects.all().order_by('created_at')
    serializer_class = MessageReplySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsActiveForWrite, IsOwnerOrAdmin]
    
    def perform_create(self, serializer):
        content = serializer.validated_data.get('content', '')
        is_safe, reason = check_msg_sec(content, getattr(self.request.user, 'openid', ''), scene=3, scope='FORUM')
        if not is_safe:
             raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        content = serializer.validated_data.get('content', '')
        is_safe, _ = check_msg_sec(content, getattr(self.request.user, 'openid', ''), scene=3, scope='FORUM')
        if not is_safe:
            raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})
        serializer.save()

class ListingMatchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ListingMatchSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return ListingMatch.objects.filter(user=self.request.user)

class PrivateMessageViewSet(mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    serializer_class = PrivateMessageSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    
    def get_queryset(self):
        user = self.request.user
        return PrivateMessage.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('created_at')

    def perform_create(self, serializer):
        content = serializer.validated_data.get('content', '')
        is_safe, reason = check_msg_sec(content, getattr(self.request.user, 'openid', ''), scene=4, scope='PRIVATE_MESSAGE')
        if not is_safe:
             raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})

        image = self.request.FILES.get('image')
        if image:
            image_bytes = image.read()
            image.seek(0)
            ok, _ = check_img_sec(image_bytes, filename=image.name)
            if not ok:
                raise exceptions.ValidationError({'detail': '图片可能含违规信息，请更换后重试'})
        msg = serializer.save(sender=self.request.user)
        if getattr(msg, 'image', None):
            _enqueue_media_check(self.request, 'private_message', msg.id, getattr(msg.image, 'url', ''), object_field='image', scene=4)
        _track_channel_event(self.request, self.request.user, ChannelEvent.EventType.PRIVATE_MESSAGE_SENT)

    @action(detail=False, methods=['GET'])
    def conversations(self, request):
        user = request.user
        
        # Get unique conversation partners from sent and received messages
        sent_receivers = PrivateMessage.objects.filter(sender=user).values_list('receiver', flat=True).distinct()
        received_senders = PrivateMessage.objects.filter(receiver=user).values_list('sender', flat=True).distinct()
        
        all_partner_ids = set(sent_receivers) | set(received_senders)
        
        conversations = []
        for partner_id in all_partner_ids:
            try:
                partner = User.objects.get(pk=partner_id)
            except User.DoesNotExist:
                continue
                
            last_msg = PrivateMessage.objects.filter(
                Q(sender=user, receiver=partner) | Q(sender=partner, receiver=user)
            ).order_by('-created_at').first()
            
            unread_count = PrivateMessage.objects.filter(
                sender=partner, receiver=user, is_read=False
            ).count()
            
            conversations.append({
                'user_id': partner.id,
                'username': partner.username,
                'last_message': last_msg.content if last_msg else '',
                'last_message_time': last_msg.created_at if last_msg else None,
                'unread_count': unread_count
            })
            
        conversations.sort(key=lambda x: x['last_message_time'] or timezone.now(), reverse=True)
        return Response(conversations)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def check(self, request):
        object_id = request.query_params.get('object_id')
        content_type_str = request.query_params.get('content_type')
        
        if not object_id or not content_type_str:
            return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            content_type = ContentType.objects.get(model=content_type_str.lower())
        except ContentType.DoesNotExist:
             return Response({'error': 'Invalid content type'}, status=status.HTTP_400_BAD_REQUEST)
             
        is_favorite = Favorite.objects.filter(
            user=request.user, 
            content_type=content_type, 
            object_id=object_id
        ).exists()
        
        return Response({'is_favorite': is_favorite})

    @action(detail=False, methods=['POST'])
    def toggle(self, request):
        object_id = request.data.get('object_id')
        content_type_str = request.data.get('content_type')
        
        if not object_id or not content_type_str:
            return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content_type = ContentType.objects.get(model=content_type_str.lower())
        except ContentType.DoesNotExist:
             return Response({'error': 'Invalid content type'}, status=status.HTTP_400_BAD_REQUEST)

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        )

        if not created:
            favorite.delete()
            is_favorite = False
        else:
            _track_channel_event(request, request.user, ChannelEvent.EventType.FAVORITE_ADD)
            is_favorite = True
            
        return Response({'is_favorite': is_favorite})

class UserFollowViewSet(viewsets.ModelViewSet):
    serializer_class = UserFollowSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return UserFollow.objects.filter(follower=self.request.user)
    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

    @action(detail=False, methods=['GET'])
    def check(self, request):
        followed_id = request.query_params.get('followed_id')
        if not followed_id:
             return Response({'error': 'Missing followed_id'}, status=status.HTTP_400_BAD_REQUEST)
             
        is_following = UserFollow.objects.filter(
            follower=request.user,
            followed_id=followed_id
        ).exists()
        
        return Response({'is_following': is_following})

    @action(detail=False, methods=['POST'])
    def toggle(self, request):
        followed_id = request.data.get('followed_id')
        if not followed_id:
             return Response({'error': 'Missing followed_id'}, status=status.HTTP_400_BAD_REQUEST)
             
        if str(request.user.id) == str(followed_id):
            return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = UserFollow.objects.get_or_create(
            follower=request.user,
            followed_id=followed_id
        )
        
        if not created:
            follow.delete()
            is_following = False
        else:
            is_following = True
            
        return Response({'is_following': is_following})

class CrewListingViewSet(viewsets.ModelViewSet):
    queryset = CrewListing.objects.all().order_by('-created_at')
    serializer_class = CrewListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsActiveForWrite]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'position', 'nationality', 'residence', 'resume', 'cert_number']

    def perform_create(self, serializer):
        data = serializer.validated_data
        check_content = " ".join([
            str(data.get('name', '') or ''),
            str(data.get('nationality', '') or ''),
            str(data.get('residence', '') or ''),
            str(data.get('position', '') or ''),
            str(data.get('cert_number', '') or ''),
            str(data.get('expected_salary', '') or ''),
            str(data.get('resume', '') or ''),
            str(data.get('phone', '') or ''),
            str(data.get('email', '') or ''),
        ]).strip()
        is_safe, _ = check_msg_sec(check_content, getattr(self.request.user, 'openid', ''), scene=1, scope='CREW')
        if not is_safe:
            raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        data = serializer.validated_data
        check_content = " ".join([
            str(data.get('name', '') or ''),
            str(data.get('nationality', '') or ''),
            str(data.get('residence', '') or ''),
            str(data.get('position', '') or ''),
            str(data.get('cert_number', '') or ''),
            str(data.get('expected_salary', '') or ''),
            str(data.get('resume', '') or ''),
            str(data.get('phone', '') or ''),
            str(data.get('email', '') or ''),
        ]).strip()
        is_safe, _ = check_msg_sec(check_content, getattr(self.request.user, 'openid', ''), scene=1, scope='CREW')
        if not is_safe:
            raise exceptions.ValidationError({'detail': '内容可能含违规信息，请修改后重试'})
        serializer.save()

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
        
    @action(detail=False, methods=['POST'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'ok'})
        
    @action(detail=True, methods=['POST'])
    def read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'status': 'ok'})

class UserProfileDetailView(views.APIView):
    """
    Get public profile of a user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check follow status
        follow_obj = UserFollow.objects.filter(follower=request.user, followed=target_user).first()
        is_following = follow_obj is not None
        follow_id = follow_obj.id if follow_obj else None
        
        # Get stats
        followers_count = UserFollow.objects.filter(followed=target_user).count()
        following_count = UserFollow.objects.filter(follower=target_user).count()
        
        avatar_url = target_user.avatar.url if target_user.avatar else None
        if avatar_url and not avatar_url.startswith('http'):
             avatar_url = request.build_absolute_uri(avatar_url)
        
        data = {
            'id': target_user.id,
            'username': target_user.username,
            'avatar': avatar_url,
            'company_name': getattr(target_user, 'company_name', ''),
            'job_title': getattr(target_user, 'job_title', ''),
            'is_following': is_following,
            'follow_id': follow_id,
            'followers_count': followers_count,
            'following_count': following_count,
        }
        return Response(data)
