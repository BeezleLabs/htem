from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('event_manager/', include('event_manager.urls')),
    path('admin/', admin.site.urls),
]
