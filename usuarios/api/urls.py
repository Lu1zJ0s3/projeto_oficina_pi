from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    UsuarioViewSet,
    registro_usuario,
    login_usuario,
    logout_usuario,
    perfil_usuario,
    teste_publico
)

router = DefaultRouter()
router.register(r'', UsuarioViewSet)

urlpatterns = [
    path('registro/', registro_usuario, name='registro_usuario'),
    path('login/', login_usuario, name='login_usuario'),
    path('logout/', logout_usuario, name='logout_usuario'),
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('teste/', teste_publico, name='teste_publico'),
] + router.urls
