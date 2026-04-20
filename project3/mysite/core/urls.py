from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('',                          views.home,          name='home'),
    path('records/',                  views.record_list,   name='record_list'),
    path('records/add/',              views.record_create, name='record_create'),
    path('records/<int:pk>/',         views.record_detail, name='record_detail'),
    path('records/<int:pk>/edit/',    views.record_update, name='record_update'),
    path('records/<int:pk>/delete/',  views.record_delete, name='record_delete'),
    
    # Section 2.4 — analytics URL's go below
]
