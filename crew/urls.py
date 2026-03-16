from django.urls import path
from . import views

app_name = 'crew'

urlpatterns = [
    path('', views.CrewListView.as_view(), name='crew_list'),
    path('create/', views.CrewCreateView.as_view(), name='crew_create'),
    path('update/<int:pk>/', views.CrewUpdateView.as_view(), name='crew_update'),
    path('<int:pk>/', views.CrewDetailView.as_view(), name='crew_detail'),
]
