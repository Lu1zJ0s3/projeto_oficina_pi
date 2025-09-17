from django.urls import path
from . import views

app_name = 'usuarios_api'

urlpatterns = [
    # URLs para API
    path('teste/', views.teste_publico, name='teste_publico'),
    path('teste-simples/', views.teste_simples, name='teste_simples'),
    path('registro/', views.registro_simples, name='registro_api'),
    path('login/', views.login_simples, name='login_api'),
    path('logout/', views.logout_usuario, name='logout_api'),
    path('perfil/', views.perfil_usuario, name='perfil_api'),
]
