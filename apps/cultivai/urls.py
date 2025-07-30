from django.urls import path
from .views import index_view, graphics_view, receive_arduino_data, obtener_ultimos_datos
from . import views


urlpatterns = [
    path('', index_view, name='index'),
    path('receive_arduino_data/', receive_arduino_data, name='receive_arduino_data'),
    path('graficos/', graphics_view, name='graficos'),
    path('api/obtener_ultimos_datos/', obtener_ultimos_datos, name='obtener_ultimos_datos'),
]