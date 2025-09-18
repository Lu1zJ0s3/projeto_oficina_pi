from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.db.models import F
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Produto, Categoria, Marca, ImagemProduto
from .api.serializers import (
    ProdutoSerializer, 
    ProdutoListSerializer, 
    ProdutoDetailSerializer,
    ProdutoEstoqueSerializer,
    CategoriaSerializer,
    MarcaSerializer
)
from .forms import ProdutoForm, CategoriaForm, MarcaForm

# Function Based Views (FBV)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_produtos_api(request):
    """API para listar produtos"""
    produtos = Produto.objects.filter(ativo=True)
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    marca_id = request.GET.get('marca')
    tipo = request.GET.get('tipo')
    search = request.GET.get('search')
    
    if categoria_id:
        produtos = produtos.filter(categoria_id=categoria_id)
    if marca_id:
        produtos = produtos.filter(marca_id=marca_id)
    if tipo:
        produtos = produtos.filter(tipo=tipo)
    if search:
        produtos = produtos.filter(nome__icontains=search)
    
    serializer = ProdutoListSerializer(produtos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalhe_produto_api(request, pk):
    """API para detalhes do produto"""
    try:
        produto = Produto.objects.get(pk=pk)
        serializer = ProdutoDetailSerializer(produto)
        return Response(serializer.data)
    except Produto.DoesNotExist:
        return Response(
            {'error': 'Produto não encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_produto_api(request):
    """API para criar produto"""
    serializer = ProdutoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def atualizar_produto_api(request, pk):
    """API para atualizar produto"""
    try:
        produto = Produto.objects.get(pk=pk)
        serializer = ProdutoSerializer(produto, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Produto.DoesNotExist:
        return Response(
            {'error': 'Produto não encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletar_produto_api(request, pk):
    """API para deletar produto"""
    try:
        produto = Produto.objects.get(pk=pk)
        produto.delete()
        return Response({'message': 'Produto deletado com sucesso!'})
    except Produto.DoesNotExist:
        return Response(
            {'error': 'Produto não encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estoque_produtos_api(request):
    """API para listar estoque dos produtos"""
    produtos = Produto.objects.all()
    serializer = ProdutoEstoqueSerializer(produtos, many=True)
    return Response(serializer.data)

# Class Based Views (CBV)
class ProdutoViewSet(ModelViewSet):
    """ViewSet para gerenciar produtos"""
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_fields = ['categoria', 'marca', 'tipo', 'ativo']
    search_fields = ['nome', 'descricao', 'modelo']
    ordering_fields = ['nome', 'preco', 'data_cadastro']
    ordering = ['-data_cadastro']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProdutoListSerializer
        elif self.action == 'retrieve':
            return ProdutoDetailSerializer
        return ProdutoSerializer

class CategoriaViewSet(ModelViewSet):
    """ViewSet para gerenciar categorias"""
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

class MarcaViewSet(ModelViewSet):
    """ViewSet para gerenciar marcas"""
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAuthenticated]

class ProdutoAPIView(APIView):
    """APIView para operações específicas de produto"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        """Obter produto específico ou listar produtos"""
        if pk:
            try:
                produto = Produto.objects.get(pk=pk)
                serializer = ProdutoDetailSerializer(produto)
                return Response(serializer.data)
            except Produto.DoesNotExist:
                return Response(
                    {'error': 'Produto não encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            produtos = Produto.objects.filter(ativo=True)
            serializer = ProdutoListSerializer(produtos, many=True)
            return Response(serializer.data)
    
    def post(self, request):
        """Criar novo produto"""
        serializer = ProdutoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        """Atualizar produto"""
        try:
            produto = Produto.objects.get(pk=pk)
            serializer = ProdutoSerializer(produto, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Produto.DoesNotExist:
            return Response(
                {'error': 'Produto não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, pk):
        """Deletar produto"""
        try:
            produto = Produto.objects.get(pk=pk)
            produto.delete()
            return Response({'message': 'Produto deletado com sucesso!'})
        except Produto.DoesNotExist:
            return Response(
                {'error': 'Produto não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

# Views para templates (Function Based Views)
@login_required
def lista_produtos(request):
    """Lista de produtos para template"""
    produtos = Produto.objects.filter(ativo=True)
    categorias = Categoria.objects.filter(ativo=True)
    marcas = Marca.objects.all()
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    marca_id = request.GET.get('marca')
    tipo = request.GET.get('tipo')
    search = request.GET.get('search')
    
    if categoria_id:
        produtos = produtos.filter(categoria_id=categoria_id)
    if marca_id:
        produtos = produtos.filter(marca_id=marca_id)
    if tipo:
        produtos = produtos.filter(tipo=tipo)
    if search:
        produtos = produtos.filter(nome__icontains=search)
    
    context = {
        'produtos': produtos,
        'categorias': categorias,
        'marcas': marcas,
        'titulo': 'Produtos - RPM Motos'
    }
    return render(request, 'produtos/lista.html', context)

@login_required
def detalhe_produto(request, pk):
    """Detalhes do produto para template"""
    produto = get_object_or_404(Produto, pk=pk)
    context = {
        'produto': produto,
        'titulo': f'{produto.nome} - RPM Motos'
    }
    return render(request, 'produtos/detalhe.html', context)

@login_required
def criar_produto(request):
    """Criar novo produto"""
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save()
            messages.success(request, 'Produto criado com sucesso!')
            return redirect('produtos:detalhe', pk=produto.pk)
    else:
        form = ProdutoForm()
    
    context = {
        'form': form,
        'titulo': 'Novo Produto - RPM Motos'
    }
    return render(request, 'produtos/form.html', context)

@login_required
def editar_produto(request, pk):
    """Editar produto existente"""
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('produtos:detalhe', pk=produto.pk)
    else:
        form = ProdutoForm(instance=produto)
    
    context = {
        'form': form,
        'produto': produto,
        'titulo': f'Editar {produto.nome} - RPM Motos'
    }
    return render(request, 'produtos/form.html', context)

@login_required
def estoque_produtos(request):
    """Página de controle de estoque"""
    produtos = Produto.objects.all().order_by('nome')
    categorias = Categoria.objects.filter(ativo=True)
    
    # Calcular estatísticas do estoque
    produtos_em_estoque = produtos.filter(estoque__gt=0).count()
    produtos_estoque_baixo = produtos.filter(estoque__lte=F('estoque_minimo'), estoque__gt=0).count()
    produtos_sem_estoque = produtos.filter(estoque=0).count()
    
    context = {
        'produtos': produtos,
        'categorias': categorias,
        'produtos_em_estoque': produtos_em_estoque,
        'produtos_estoque_baixo': produtos_estoque_baixo,
        'produtos_sem_estoque': produtos_sem_estoque,
        'titulo': 'Controle de Estoque - RPM Motos'
    }
    return render(request, 'produtos/estoque.html', context)
