from django.urls import path
from .views import index_view, graphics_view


# app_name = 'cultivai'


urlpatterns = [
    path('', index_view, name='index'),
    path('graficos/', graphics_view, name='graficos'),
]