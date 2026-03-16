from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rules/', views.rules, name='rules'),
    path('contact/', views.contact_admin, name='contact_admin'),
    path('messages/', views.member_message_list, name='member_messages'),
    path('messages/<int:pk>/reply/', views.reply_message, name='member_message_reply'),
    path('messages/<int:pk>/update/', views.MemberMessageUpdateView.as_view(), name='member_message_update'),
    path('messages/<int:pk>/delete/', views.MemberMessageDeleteView.as_view(), name='member_message_delete'),
]
