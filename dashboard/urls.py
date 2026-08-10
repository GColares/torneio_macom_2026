from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gestao/', views.gestao, name='gestao'),
    path('api/metrics/', views.api_metrics, name='api_metrics'),
    path('api/duplas/', views.api_duplas, name='api_duplas'),
    path('api/duplas/update/', views.api_update_dupla, name='api_update_dupla'),
    path('api/duplas/delete/', views.api_delete_duplas, name='api_delete_duplas'),
    path('api/metas/', views.api_metas, name='api_metas'),
]
