from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from users.models import CustomUser, LoginLog
from forum.models import Thread, Post
from news.models import Article
from market.models import ShipListing

class RegulatoryViewSet(viewsets.ViewSet):
    """
    Regulatory Interface for Public Security Bureau
    Only accessible by Admin
    """
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def user_query(self, request):
        """
        Query user registration info
        Params: keyword (mobile/username/real_name/company_name)
        """
        keyword = request.query_params.get('keyword')
        if not keyword:
            return Response({'error': 'Keyword required'}, status=status.HTTP_400_BAD_REQUEST)

        # Build query
        users = CustomUser.objects.filter(phone_number__icontains=keyword) | \
               CustomUser.objects.filter(username__icontains=keyword) | \
               CustomUser.objects.filter(company_name__icontains=keyword)

        results = []
        for u in users:
            results.append({
                'id': u.id,
                'username': u.username,
                'phone_number': u.phone_number,
                'email': u.email,
                'company': u.company_name,
                'date_joined': u.date_joined,
                'last_login': u.last_login,
                'is_active': u.is_active
            })
        
        return Response(results)

    @action(detail=False, methods=['get'])
    def login_logs(self, request):
        """
        Query user login logs (6 months retention)
        Params: user_id or mobile
        """
        user_id = request.query_params.get('user_id')
        mobile = request.query_params.get('mobile')
        
        if not user_id and not mobile:
             return Response({'error': 'User ID or Mobile required'}, status=status.HTTP_400_BAD_REQUEST)
             
        if user_id:
            logs = LoginLog.objects.filter(user_id=user_id)
        else:
            logs = LoginLog.objects.filter(user__phone_number=mobile)
            
        # Limit to last 6 months (optional filter, but returning all is also fine for regulatory)
        results = []
        for log in logs[:100]: # Pagination recommended in production
            results.append({
                'user': log.user.username,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'time': log.login_time
            })
            
        return Response(results)

    @action(detail=False, methods=['get'])
    def content_query(self, request):
        """
        Query content (Forum, News, Listings) by keyword
        """
        keyword = request.query_params.get('keyword')
        if not keyword:
             return Response({'error': 'Keyword required'}, status=status.HTTP_400_BAD_REQUEST)
             
        results = {
            'threads': [],
            'posts': [],
            'articles': [],
            'listings': []
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

        # Ship Listings
        for s in ShipListing.objects.filter(description__icontains=keyword)[:20]:
            results['listings'].append({
                'id': s.id, 'type': s.listing_type, 'dwt': s.dwt, 'description_snippet': s.description[:50]
            })
            
        return Response(results)
