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
    
    # Health - Alias pour faciliter les tests (sans slash final pour éviter 301)
    path('health', views.health),  # ✅ Alias simple (sans slash)
    path('health/', views.health),  # ✅ Alias avec slash
    path('api/health/', views.health),  # ✅ Endpoint complet
    
    # Chat - Les 2 URLs pointent vers la même fonction
    path('api/chat/', views.intelligent_travel_chat),
    path('api/intelligent_travel_chat/', views.intelligent_travel_chat),
    
    # Autres
    path('api/destinations/', views.destinations_list),
    path('api/recommendations/', views.recommendations),
    path('api/collect-external-data/', views.collect_external_data),
]