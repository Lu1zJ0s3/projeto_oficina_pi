from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    # URLs para templates
    path('', views.lista_produtos, name='lista'),
    path('novo/', views.criar_produto, name='criar'),
    path('<int:pk>/', views.detalhe_produto, name='detalhe'),
    path('<int:pk>/editar/', views.editar_produto, name='editar'),
    path('estoque/', views.estoque_produtos, name='estoque'),
    
    # URLs para API
    path('api/', views.lista_produtos_api, name='lista_api'),
    path('api/<int:pk>/', views.detalhe_produto_api, name='detalhe_api'),
    path('api/criar/', views.criar_produto_api, name='criar_api'),
    path('api/<int:pk>/atualizar/', views.atualizar_produto_api, name='atualizar_api'),
    path('api/<int:pk>/deletar/', views.deletar_produto_api, name='deletar_api'),
    path('api/estoque/', views.estoque_produtos_api, name='estoque_api'),
]
