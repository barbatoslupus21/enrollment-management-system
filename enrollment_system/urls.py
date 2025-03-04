from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('sysadmin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('overview/', include('overview.urls')),
    path('admin/', include('administrator.urls')),
    path('notification/', include('notification.urls')),
    path('users/', include('usersection.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    