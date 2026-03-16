from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('', views.ListingListView.as_view(), name='list'),
    path('create/', views.ListingCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ListingDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.ListingUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ListingDeleteView.as_view(), name='delete'),
    
    # News URLs
    path('news/', views.MarketNewsListView.as_view(), name='news_list'),
    path('news/create/', views.MarketNewsCreateView.as_view(), name='news_create'),
    path('news/<int:pk>/', views.MarketNewsDetailView.as_view(), name='news_detail'),
    path('news/<int:pk>/update/', views.MarketNewsUpdateView.as_view(), name='news_update'),
    path('news/<int:pk>/delete/', views.MarketNewsDeleteView.as_view(), name='news_delete'),
    
    # Internal Data
    path('intelligence/crawled-ships/', views.CrawledShipListView.as_view(), name='crawled_ships'),
]
