from django.urls import path
from . import views

app_name = 'vendas'

urlpatterns = [
    #URLs para templates
    path('', views.dashboard_vendas, name='dashboard'),
    path('lista/', views.lista_vendas, name='lista'),
    path('nova/', views.criar_venda, name='criar'),
    path('<int:pk>/', views.detalhe_venda, name='detalhe'),
    path('<int:pk>/editar/', views.editar_venda, name='editar'),
    path('<int:pk>/deletar/', views.deletar_venda, name='deletar'),
    path('faturamento/', views.faturamento_view, name='faturamento'),
    path('atualizar-status/', views.atualizar_status_vendas, name='atualizar_status'),
    path('atualizar-faturamento/', views.atualizar_faturamento, name='atualizar_faturamento'),
    
    #URLs para clientes
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/novo/', views.criar_cliente, name='criar_cliente'),
    path('clientes/<int:pk>/', views.detalhe_cliente, name='detalhe_cliente'),
    path('clientes/<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),
]
