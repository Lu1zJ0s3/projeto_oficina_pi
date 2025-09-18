from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from vendas.models import Venda, Cliente, ItemVenda, Faturamento
from .serializers import (
    VendaSerializer, 
    VendaListSerializer, 
    VendaDetailSerializer,
    ClienteSerializer,
    ClienteListSerializer,
    FaturamentoSerializer,
    FaturamentoResumoSerializer
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_vendas_api(request):
    vendas = Venda.objects.all()
    status_venda = request.GET.get('status')
    cliente_id = request.GET.get('cliente')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    if status_venda:
        vendas = vendas.filter(status=status_venda)
    if cliente_id:
        vendas = vendas.filter(cliente_id=cliente_id)
    if data_inicio:
        vendas = vendas.filter(data_venda__date__gte=data_inicio)
    if data_fim:
        vendas = vendas.filter(data_venda__date__lte=data_fim)
    serializer = VendaListSerializer(vendas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalhe_venda_api(request, pk):
    try:
        venda = Venda.objects.get(pk=pk)
        serializer = VendaDetailSerializer(venda)
        return Response(serializer.data)
    except Venda.DoesNotExist:
        return Response({'error': 'Venda não encontrada'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_venda_api(request):
    serializer = VendaSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        venda = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def atualizar_venda_api(request, pk):
    try:
        venda = Venda.objects.get(pk=pk)
        serializer = VendaSerializer(venda, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Venda.DoesNotExist:
        return Response({'error': 'Venda não encontrada'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletar_venda_api(request, pk):
    try:
        venda = Venda.objects.get(pk=pk)
        venda.delete()
        return Response({'message': 'Venda deletada com sucesso!'})
    except Venda.DoesNotExist:
        return Response({'error': 'Venda não encontrada'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def faturamento_api(request):
    if not request.user.is_proprietario:
        return Response({'error': 'Acesso negado. Apenas proprietários podem ver o faturamento.'}, status=status.HTTP_403_FORBIDDEN)
    periodo = request.GET.get('periodo', 'mes')
    from datetime import datetime, timedelta
    if periodo == 'dia':
        data_inicio = datetime.now().date()
        data_fim = datetime.now().date()
    elif periodo == 'semana':
        data_inicio = datetime.now().date() - timedelta(days=7)
        data_fim = datetime.now().date()
    elif periodo == 'mes':
        data_inicio = datetime.now().date().replace(day=1)
        data_fim = datetime.now().date()
    else:
        data_inicio = datetime.now().date() - timedelta(days=30)
        data_fim = datetime.now().date()
    vendas = Venda.objects.filter(
        data_venda__date__range=[data_inicio, data_fim],
        status__in=['concluida', 'aprovada']
    )
    total_vendas = vendas.count()
    faturamento_total = sum(v.total for v in vendas)
    lucro_total = sum(v.lucro_estimado for v in vendas)
    data = {
        'total_vendas': total_vendas,
        'faturamento_total': faturamento_total,
        'lucro_total': lucro_total,
        'periodo': periodo,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    }
    return Response(data)

class VendaViewSet(viewsets.ModelViewSet):
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_fields = ['cliente', 'vendedor', 'status', 'data_venda']
    search_fields = ['numero_venda', 'cliente__nome', 'vendedor__username']
    ordering_fields = ['data_venda', 'total', 'numero_venda']
    ordering = ['-data_venda']
    def get_serializer_class(self):
        if self.action == 'list':
            return VendaListSerializer
        elif self.action == 'retrieve':
            return VendaDetailSerializer
        return VendaSerializer
    def perform_create(self, serializer):
        serializer.save(vendedor=self.request.user)

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_fields = ['tipo', 'ativo', 'estado']
    search_fields = ['nome', 'cpf_cnpj', 'email']
    ordering_fields = ['nome', 'data_cadastro']
    ordering = ['nome']

class FaturamentoViewSet(viewsets.ModelViewSet):
    queryset = Faturamento.objects.all()
    serializer_class = FaturamentoSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if not self.request.user.is_proprietario:
            return Faturamento.objects.none()
        return Faturamento.objects.all()

class VendaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None):
        if pk:
            try:
                venda = Venda.objects.get(pk=pk)
                serializer = VendaDetailSerializer(venda)
                return Response(serializer.data)
            except Venda.DoesNotExist:
                return Response({'error': 'Venda não encontrada'}, status=status.HTTP_404_NOT_FOUND)
        else:
            vendas = Venda.objects.all()
            serializer = VendaListSerializer(vendas, many=True)
            return Response(serializer.data)
    def post(self, request):
        serializer = VendaSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, pk):
        try:
            venda = Venda.objects.get(pk=pk)
            serializer = VendaSerializer(venda, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Venda.DoesNotExist:
            return Response({'error': 'Venda não encontrada'}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, pk):
        try:
            venda = Venda.objects.get(pk=pk)
            venda.delete()
            return Response({'message': 'Venda deletada com sucesso!'})
        except Venda.DoesNotExist:
            return Response({'error': 'Venda não encontrada'}, status=status.HTTP_404_NOT_FOUND)
