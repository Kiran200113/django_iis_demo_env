from django.contrib import admin
from django.urls import path, include
from home import views

urlpatterns = [    
    path('', views.index, name='home'),
    path('generate/', views.generateExcel, name='generate'),
]
