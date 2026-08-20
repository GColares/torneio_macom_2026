from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gestao/', views.gestao, name='gestao'),
    path('comprovantes/', views.gestao_comprovantes, name='gestao_comprovantes'),
    path('fichas/', views.gestao_fichas, name='gestao_fichas'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('api/metrics/', views.api_metrics, name='api_metrics'),
    path('api/duplas/', views.api_duplas, name='api_duplas'),
    path('api/comprovantes/criar/', views.api_criar_comprovante, name='api_criar_comprovante'),
    path('api/comprovantes/update/', views.api_update_comprovante, name='api_update_comprovante'),
    path('api/comprovantes/delete/', views.api_delete_comprovante, name='api_delete_comprovante'),
    path('api/fichas/update/', views.api_update_ficha, name='api_update_ficha'),
    path('api/duplas/<int:dupla_id>/', views.api_get_dupla, name='api_get_dupla'),
    path('api/duplas/update/', views.api_update_dupla, name='api_update_dupla'),
    path('api/duplas/<int:dupla_id>/excluir/', views.api_excluir_dupla, name='api_excluir_dupla'),
    path('api/duplas/delete/', views.api_delete_duplas, name='api_delete_duplas'),
    path('api/duplas/sync_csv/', views.api_sync_csv, name='api_sync_csv'),
    path('api/metas/', views.api_metas, name='api_metas'),
    path('api/revisao/confirmar/', views.api_confirmar_revisao, name='api_confirmar_revisao'),
    path('api/revisao/descartar/', views.api_descartar_revisao, name='api_descartar_revisao'),
    path('torneio/', views.torneio_view, name='torneio'),
    path('api/torneio/state/', views.api_torneio_state, name='api_torneio_state'),
]
