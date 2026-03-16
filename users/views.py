from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, Max
from django.db.models.functions import TruncHour
from django.contrib.auth import get_user_model
from market.models import ShipListing
from .models import VisitorLog
import os
from django.conf import settings
from django.http import HttpResponse, Http404

User = get_user_model()

@staff_member_required
def download_backup(request, filename):
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    filepath = os.path.join(backup_dir, filename)
    
    if os.path.exists(filepath) and os.path.isfile(filepath):
        with open(filepath, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    raise Http404("Backup file not found")

@staff_member_required
def admin_dashboard(request):
    now = timezone.now()
    today = now.date()
    
    # Backup Files
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    backup_files = []
    if os.path.exists(backup_dir):
        for f in sorted(os.listdir(backup_dir), reverse=True):
            if f.endswith('.zip'):
                filepath = os.path.join(backup_dir, f)
                stat = os.stat(filepath)
                backup_files.append({
                    'name': f,
                    'size': f"{stat.st_size / 1024 / 1024:.2f} MB",
                    'created': datetime.fromtimestamp(stat.st_mtime)
                })
    
    # Basic Stats
    user_count = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    listing_count = ShipListing.objects.count()
    listing_pending = ShipListing.objects.filter(status='PENDING').count()

    # Visitor Stats
    # 1. Current Visitors (Active in last 10 mins)
    ten_mins_ago = now - timedelta(minutes=10)
    active_logs = VisitorLog.objects.filter(created_at__gte=ten_mins_ago)
    current_visitor_count = active_logs.values('ip_address').distinct().count()

    # 2. Online Visitor Info
    online_visitors = []
    latest_logs = active_logs.values('ip_address', 'user__username', 'user__id').annotate(last_seen=Max('created_at')).order_by('-last_seen')
    for log in latest_logs:
        online_visitors.append({
            'ip': log['ip_address'],
            'username': log['user__username'] or 'Guest',
            'user_id': log['user__id'],
            'last_seen': log['last_seen']
        })

    # 3. Cumulative Visitors
    cumulative_visitors = VisitorLog.objects.values('ip_address').distinct().count()

    # 4. Recent Logs
    recent_visitors = VisitorLog.objects.select_related('user').order_by('-created_at')[:20]

    # 5. Hourly Curve
    hourly_stats = VisitorLog.objects.filter(created_at__date=today)\
        .annotate(hour=TruncHour('created_at'))\
        .values('hour')\
        .annotate(count=Count('id'))\
        .order_by('hour')
        
    # Prepare data for Chart.js
    # Labels: 0-23, Data: counts
    chart_labels = list(range(24))
    chart_data = [0] * 24
    for stat in hourly_stats:
        h = stat['hour'].hour
        chart_data[h] = stat['count']

    context = {
        'user_count': user_count,
        'new_users_today': new_users_today,
        'listing_count': listing_count,
        'listing_pending': listing_pending,
        'current_visitor_count': current_visitor_count,
        'online_visitors': online_visitors,
        'cumulative_visitors': cumulative_visitors,
        'recent_visitors': recent_visitors,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'backup_files': backup_files,
    }
    return render(request, 'users/admin_dashboard.html', context)

from django.contrib.auth import login
from .forms import CustomUserCreationForm, WebSMSLoginForm, AccountCreationForm
from django.contrib.auth.decorators import login_required
from ads.models import Advertisement
from market.models import ListingMatch
from .models import UserFollow
from core.models import PrivateMessage

def register(request):
    mode = request.GET.get('mode', 'phone')
    
    if request.method == 'POST':
        mode = request.POST.get('mode', mode)
        if mode == 'account':
            form = AccountCreationForm(request.POST)
        else:
            form = CustomUserCreationForm(request.POST)
            
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        if mode == 'account':
            form = AccountCreationForm()
        else:
            form = CustomUserCreationForm()
            
    return render(request, 'users/register.html', {'form': form, 'mode': mode})

def sms_login_view(request):
    if request.method == 'POST':
        form = WebSMSLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = WebSMSLoginForm()
    return render(request, 'users/login_sms.html', {'form': form})

@login_required
def profile(request):
    # My Matches: Listings that match my needs (where I am source)
    # Actually, ListingMatch logic: Source=Listing, Target=MatchCandidate.
    # If I posted a 'BUY' listing (Source), I want 'SELL' listings (Target).
    # So matches for my listings are where listing_source.user == me.
    my_matches = ListingMatch.objects.filter(listing_source__user=request.user).select_related('listing_target', 'listing_source')

    # My Following
    following = UserFollow.objects.filter(follower=request.user).select_related('followed')

    # Followers
    followers = UserFollow.objects.filter(followed=request.user).select_related('follower')

    # Contacted Me (Received Messages)
    # Group by sender to show list of people who contacted me
    # We can just show the list of messages for now, or distinct senders.
    # Distinct on SQLite might be tricky if not careful, but let's try to get unique senders.
    # Or just show recent messages. Let's show all received messages for now.
    received_messages = PrivateMessage.objects.filter(receiver=request.user).select_related('sender').order_by('-created_at')
    
    # If we want unique senders:
    # senders = set(msg.sender for msg in received_messages)

    context = {
        'my_matches': my_matches,
        'following': following,
        'followers': followers,
        'received_messages': received_messages,
    }
    return render(request, 'users/profile.html', context)
