"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# backend/api/urls.py
## backend/backend/urls.py
# backend/urls.py
from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('', views.home),
    path('admin/', admin.site.urls),
    path('api/health/', views.health),
    path('api/destinations/', views.destinations_list),
    path('api/recommendations/', views.recommendations),
    path('api/chat/', views.intelligent_travel_chat),  # ← Bonne fonction
    path('api/collect-external-data/', views.collect_external_data),
]