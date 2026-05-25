from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.central_analise_status, name='central_analise_status'),
    path('chat/', views.chat_view, name='central_analise_chat'),
    path('dashboard/', views.dashboard_data, name='central_analise_dashboard'),
    path('operador/<str:operadora>/', views.operador_detail, name='central_analise_operador'),
    path('dashboard/filtros/', views.dashboard_filtros, name='dashboard_filtros'),
    path('dashboard/passageiros/', views.dashboard_passageiros, name='dashboard_passageiros'),
    path('dashboard/operacional/', views.dashboard_operacional, name='dashboard_operacional'),
    path('contatos-whatsapp/', views.contatos_whatsapp_list, name='contatos_whatsapp_list'),
    path('contatos-whatsapp/<int:pk>/', views.contatos_whatsapp_detail, name='contatos_whatsapp_detail'),
    path('relatorio-diario/', views.relatorio_diario, name='relatorio_diario'),
    path('relatorio-mensal/', views.relatorio_mensal_pdf, name='relatorio_mensal_pdf'),
    path('relatorio-mensal-resumo/', views.relatorio_mensal_resumo, name='relatorio_mensal_resumo'),
    path('configuracao/', views.configuracao_relatorio, name='configuracao_relatorio'),
]
