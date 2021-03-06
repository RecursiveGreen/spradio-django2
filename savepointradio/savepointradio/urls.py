from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('accounts/', include('authtools.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
