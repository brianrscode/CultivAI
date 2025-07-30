from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.cultivai.urls'), name='cultivai'),
    path('api/recommendations/', include('apps.recommendations.urls'), name='recommendations'),
]
