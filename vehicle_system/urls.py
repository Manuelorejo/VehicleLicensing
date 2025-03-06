# vehicle_system/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]

# core/urls.py
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/auth/login/', obtain_auth_token, name='login'),
    # Add other viewset routes here using a router
]