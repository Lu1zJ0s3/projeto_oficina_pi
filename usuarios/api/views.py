from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token
from usuarios.api.serializers import (
    UsuarioSerializer, 
    UsuarioFormSerializer,
    UsuarioLoginSerializer, 
    UsuarioDetailSerializer
)
from django.contrib.auth import login, logout
from django.utils import timezone
from django.shortcuts import get_object_or_404
from usuarios.models import Usuario


@api_view(['POST'])
@permission_classes([AllowAny])
def registro_usuario(request):
    """Endpoint para registro de usuário"""
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Usuário criado com sucesso!',
            'user_id': user.id,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_usuario(request):
    """Endpoint para login de usuário"""
    serializer = UsuarioLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Login realizado com sucesso!',
            'user': UsuarioDetailSerializer(user).data,
            'token': token.key
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_usuario(request):
    """Endpoint para logout de usuário"""
    try:
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({'message': 'Logout realizado com sucesso!'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_usuario(request):
    """Endpoint para obter perfil do usuário logado"""
    serializer = UsuarioDetailSerializer(request.user)
    return Response(serializer.data)

class UsuarioViewSet(ModelViewSet):
    """ViewSet para gerenciar usuários (apenas para proprietários)"""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioDetailSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.user.is_proprietario:
            return Usuario.objects.all()
        return Usuario.objects.filter(id=self.request.user.id)
    def perform_create(self, serializer):
        if not self.request.user.is_proprietario:
            raise PermissionError("Apenas proprietários podem criar usuários")
        serializer.save()
    def perform_update(self, serializer):
        if serializer.instance.id != self.request.user.id and not self.request.user.is_proprietario:
            raise PermissionError("Você só pode editar seu próprio perfil")
        serializer.save()
    def perform_destroy(self, instance):
        if not self.request.user.is_proprietario:
            raise PermissionError("Apenas proprietários podem deletar usuários")
        instance.delete()

class UsuarioAPIView(APIView):
    """APIView para operações específicas de usuário"""
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None):
        if pk:
            try:
                user = Usuario.objects.get(pk=pk)
                if user.id != request.user.id and not request.user.is_proprietario:
                    return Response({'error': 'Acesso negado'}, status=status.HTTP_403_FORBIDDEN)
                serializer = UsuarioDetailSerializer(user)
                return Response(serializer.data)
            except Usuario.DoesNotExist:
                return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if not request.user.is_proprietario:
                return Response({'error': 'Acesso negado'}, status=status.HTTP_403_FORBIDDEN)
            usuarios = Usuario.objects.all()
            serializer = UsuarioDetailSerializer(usuarios, many=True)
            return Response(serializer.data)
    def put(self, request, pk):
        try:
            user = Usuario.objects.get(pk=pk)
            if user.id != request.user.id and not request.user.is_proprietario:
                return Response({'error': 'Acesso negado'}, status=status.HTTP_403_FORBIDDEN)
            serializer = UsuarioDetailSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def teste_publico(request):
    """Endpoint de teste público"""
    return Response({
        'message': 'Endpoint público funcionando!',
        'timestamp': timezone.now().isoformat()
    })
