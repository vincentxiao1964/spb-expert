from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from apps.users.models import LoginLog
from apps.forum.models import Thread, Post
from apps.news.models import Article, Comment
from apps.store.models import Product

User = get_user_model()

class RegulatoryViewSet(viewsets.ViewSet):
    """
    Special Interface for Regulatory/Public Security Bureau
    Allows querying users, logs, and content for investigation.
    """
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def user_query(self, request):
        """
        Query user registration info by mobile, username, or real name.
        """
        keyword = request.query_params.get('keyword')
        if not keyword:
            return Response({'error': 'Keyword required'}, status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.filter(
            mobile__icontains=keyword
        ) | User.objects.filter(
            username__icontains=keyword
        ) | User.objects.filter(
            crew_profile__real_name__icontains=keyword
        ) | User.objects.filter(
            company_profile__company_name__icontains=keyword
        )
        
        data = []
        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'mobile': user.mobile,
                'role': user.role,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'is_active': user.is_active,
                'real_name': user.crew_profile.real_name if hasattr(user, 'crew_profile') else '',
                'company_name': user.company_profile.user.company_name if hasattr(user, 'company_profile') else ''
            })
            
        return Response(data)

    @action(detail=False, methods=['get'])
    def login_logs(self, request):
        """
        Query login logs for a specific user (by ID or mobile)
        """
        user_id = request.query_params.get('user_id')
        mobile = request.query_params.get('mobile')
        
        queryset = LoginLog.objects.all()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        elif mobile:
            queryset = queryset.filter(user__mobile=mobile)
        else:
             return Response({'error': 'User ID or Mobile required'}, status=status.HTTP_400_BAD_REQUEST)
             
        data = []
        for log in queryset[:100]: # Limit to 100 recent
            data.append({
                'user': log.user.username,
                'ip_address': log.ip_address,
                'login_time': log.login_time,
                'user_agent': log.user_agent
            })
            
        return Response(data)

    @action(detail=False, methods=['get'])
    def content_query(self, request):
        """
        Query content (Forum, News, Products) by keyword
        """
        keyword = request.query_params.get('keyword')
        if not keyword:
             return Response({'error': 'Keyword required'}, status=status.HTTP_400_BAD_REQUEST)
             
        results = {
            'threads': [],
            'posts': [],
            'articles': [],
            'products': []
        }
        
        # Threads
        for t in Thread.objects.filter(title__icontains=keyword)[:20]:
            results['threads'].append({
                'id': t.id, 'title': t.title, 'author': t.author.username, 'created_at': t.created_at
            })
            
        # Posts
        for p in Post.objects.filter(content__icontains=keyword)[:20]:
             results['posts'].append({
                'id': p.id, 'thread': p.thread.title, 'author': p.author.username, 'content_snippet': p.content[:50]
            })
            
        # Articles
        for a in Article.objects.filter(title__icontains=keyword)[:20]:
             results['articles'].append({
                'id': a.id, 'title': a.title, 'author': a.author.username
            })
            
        return Response(results)
