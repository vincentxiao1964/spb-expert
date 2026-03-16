from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('voyage-estimator/', views.voyage_estimator, name='voyage_estimator'),
    path('port-distance/', views.port_distance_calculator, name='port_distance'),
    path('bunker-prices/', views.bunker_index, name='bunker_index'),
    path('contracts/', views.contract_templates, name='contract_templates'),
    path('api/calculate-distance/', views.calculate_distance_api, name='calculate_distance_api'),
]
