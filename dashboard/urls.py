from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gestao/', views.gestao, name='gestao'),
    path('api/metrics/', views.api_metrics, name='api_metrics'),
    path('api/duplas/', views.api_duplas, name='api_duplas'),
    path('api/duplas/<int:dupla_id>/', views.api_get_dupla, name='api_get_dupla'),
    path('api/duplas/update/', views.api_update_dupla, name='api_update_dupla'),
    path('api/duplas/delete/', views.api_delete_duplas, name='api_delete_duplas'),
    path('api/duplas/sync_csv/', views.api_sync_csv, name='api_sync_csv'),
    path('api/metas/', views.api_metas, name='api_metas'),
    path('torneio/', views.torneio_view, name='torneio'),
    path('api/torneio/state/', views.api_torneio_state, name='api_torneio_state'),
]
