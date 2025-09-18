from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from produtos.models import Produto, Categoria, Marca, ImagemProduto
from .serializers import (
    ProdutoSerializer, 
    ProdutoListSerializer, 
    ProdutoDetailSerializer,
    ProdutoEstoqueSerializer,
    CategoriaSerializer,
    MarcaSerializer
)

# Function Based Views (FBV)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_produtos_api(request):
    produtos = Produto.objects.filter(ativo=True)
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
    try:
        produto = Produto.objects.get(pk=pk)
        serializer = ProdutoDetailSerializer(produto)
        return Response(serializer.data)
    except Produto.DoesNotExist:
        return Response({'error': 'Produto não encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_produto_api(request):
    serializer = ProdutoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def atualizar_produto_api(request, pk):
    try:
        produto = Produto.objects.get(pk=pk)
        serializer = ProdutoSerializer(produto, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Produto.DoesNotExist:
        return Response({'error': 'Produto não encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletar_produto_api(request, pk):
    try:
        produto = Produto.objects.get(pk=pk)
        produto.delete()
        return Response({'message': 'Produto deletado com sucesso!'})
    except Produto.DoesNotExist:
        return Response({'error': 'Produto não encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estoque_produtos_api(request):
    produtos = Produto.objects.all()
    serializer = ProdutoEstoqueSerializer(produtos, many=True)
    return Response(serializer.data)

class ProdutoViewSet(viewsets.ModelViewSet):
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

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAuthenticated]
