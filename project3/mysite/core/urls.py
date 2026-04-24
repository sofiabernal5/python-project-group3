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
    path('city/fetch/', views.fetch_page, name='fetch_page'),
    path('fetch/', views.fetch_weather_data, name='fetch_weather'),
<<<<<<< HEAD
    path('city/add/', views.city_create, name='city_create'),
    path('city/<int:pk>/', views.city_detail, name='city_detail'),
    path('city/<int:pk>/edit/', views.city_update, name='city_update'),
    path('city/<int:pk>/delete/', views.city_delete, name='city_delete'),
=======
    path('cities/add/', views.city_create, name='city_create'),
    path('cities/<int:pk>/', views.city_detail, name='city_detail'),
    path('cities/<int:pk>/edit/', views.city_update, name='city_update'),
    path('cities/<int:pk>/delete/', views.city_delete, name='city_delete'),
>>>>>>> 2.5-updates
    path('analytics/', views.analytics, name='analytics'),
    
    # Section 2.4 - analytics URL's go below
]
