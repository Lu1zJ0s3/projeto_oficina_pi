from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from usuarios.api.views import UsuarioViewSet
from produtos.views import ProdutoViewSet, CategoriaViewSet, MarcaViewSet
from vendas.api.views import VendaViewSet, ClienteViewSet, FaturamentoViewSet

router = routers.DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'produtos', ProdutoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'vendas', VendaViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'faturamento', FaturamentoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', include('usuarios.api.urls')),
    path('api/', include(router.urls)),
    path('api/vendas/', include('vendas.api.urls')),
    path('api/auth/', include('rest_framework.urls')),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('', include('usuarios.urls')),
    path('produtos/', include('produtos.urls')),
    path('vendas/', include('vendas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
