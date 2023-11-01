from django.urls import path
from django.views.generic import TemplateView

from . import views


INDEX_TEMPLATE = 'local.html' if __package__ == 'web' else 'index_main.html'


urlpatterns = [
    path('transportation/', TemplateView.as_view(template_name=INDEX_TEMPLATE), name="transportation-app"),
    path('get_geojsons/', views.get_geojsons, name="get-geojsons"),
    path('get_geojson/', views.get_geojson, name="get-geojson"),
    path('get_geojson/<geojson_name>/', views.get_geojson, name="get-geojson"),
]
