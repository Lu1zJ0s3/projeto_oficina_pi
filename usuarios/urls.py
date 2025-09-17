from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # URLs para templates
    path('', views.home_page, name='home'),  
    path('dashboard/', views.dashboard_usuario, name='dashboard'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
    
    # URLs de autenticação personalizada
    path('login/', views.custom_login_view, name='login'),
    path('register/', views.custom_register_view, name='register'),
    path('logout/', views.custom_logout_view, name='logout'),
    
    # URLs para API 
    path('teste/', views.teste_publico, name='teste_publico'),
    path('registro/', views.registro_simples, name='registro_api'),
    path('login-api/', views.login_simples, name='login_api'),
    path('logout-api/', views.logout_usuario, name='logout_api'),
    path('perfil-api/', views.perfil_usuario, name='perfil_api'),
]
