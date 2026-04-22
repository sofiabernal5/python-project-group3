from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('air-quality/', views.air_quality_list,   name='air_quality_list'),
    path('air-quality/add/', views.air_quality_create, name='air_quality_create'),
    path('air-quality/<int:pk>/', views.air_quality_detail, name='air_quality_detail'),
    path('air-quality/<int:pk>/edit/', views.air_quality_update, name='air_quality_update'),
    path('air-quality/<int:pk>/delete/', views.air_quality_delete, name='air_quality_delete'),
    path('weather/', views.weather_list, name='weather_list'),
    path('weather/<int:pk>/', views.weather_detail, name='weather_detail'),
    path('weather/<int:pk>/edit/', views.weather_update, name='weather_update'),
    path('weather/<int:pk>/delete/', views.weather_delete, name='weather_delete'),
    path('analytics/', views.analytics, name='analytics'),
    
    # Section 2.4 - analytics URL's go below
]
