from django.urls import path
from .views import (
    dashboard_usuario,
    perfil_view,
    editar_perfil_view,
    home_page,
    custom_login_view,
    custom_register_view,
    custom_logout_view
)

app_name = 'usuarios'

urlpatterns = [
    # URLs para templates
    path('', home_page, name='home'),  
    path('dashboard/', dashboard_usuario, name='dashboard'),
    path('perfil/', perfil_view, name='perfil'),
    path('perfil/editar/', editar_perfil_view, name='editar_perfil'),
    
    # URLs de autenticação personalizada
    path('login/', custom_login_view, name='login'),
    path('register/', custom_register_view, name='register'),
    path('logout/', custom_logout_view, name='logout'),
]
