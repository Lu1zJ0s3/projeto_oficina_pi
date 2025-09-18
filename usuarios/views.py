from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.db import models
from django.utils import timezone

# Function Based Views (FBV)
@csrf_exempt
def registro_simples(request):
    from django.http import JsonResponse
    import json
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Remover uso de UsuarioSerializer e Token
            # Implemente aqui lógica simples de criação de usuário, se necessário
            return JsonResponse({'message': 'Usuário criado (simples, sem DRF)'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def login_simples(request):
    from django.http import JsonResponse
    import json
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Remover uso de UsuarioLoginSerializer, UsuarioDetailSerializer, Token
            # Implemente aqui lógica simples de login, se necessário
            return JsonResponse({'message': 'Login realizado (simples, sem DRF)'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método não permitido'}, status=405)

def home_page(request):
    """Página inicial do sistema"""
    return render(request, 'home.html')

# Views para autenticação personalizada
def custom_login_view(request):
    """View personalizada de login"""
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            from django.contrib.auth import authenticate, login
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'usuarios:dashboard')
                return redirect(next_url)
            else:
                context = {'error': 'Usuário ou senha inválidos'}
                return render(request, 'registration/login.html', context)
    
    return render(request, 'registration/login.html')

def custom_register_view(request):
    """View personalizada de registro"""
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')
    
    if request.method == 'POST':
        # Obter dados do formulário
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        cpf = request.POST.get('cpf')
        
        errors = {}
        
        # Validações básicas
        if not username:
            errors['username'] = 'Nome de usuário é obrigatório'
        if not email:
            errors['email'] = 'Email é obrigatório'
        if not password1:
            errors['password1'] = 'Senha é obrigatória'
        if password1 != password2:
            errors['password2'] = 'Senhas não coincidem'
        if not cpf:
            errors['cpf'] = 'CPF é obrigatório'
        
        if not errors:
            try:
                from django.contrib.auth import get_user_model
                Usuario = get_user_model()
                
                # Verificar se usuário já existe
                if Usuario.objects.filter(username=username).exists():
                    errors['username'] = 'Nome de usuário já existe'
                elif Usuario.objects.filter(email=email).exists():
                    errors['email'] = 'Email já está em uso'
                elif Usuario.objects.filter(cpf=cpf).exists():
                    errors['cpf'] = 'CPF já está cadastrado'
                else:
                    # Criar usuário diretamente
                    user = Usuario.objects.create_user(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        cpf=cpf,
                        tipo_usuario='vendedor'
                    )
                    
                    # Definir senha
                    user.set_password(password1)
                    user.save()
                    
                    # Login automático após registro
                    from django.contrib.auth import login
                    login(request, user)
                    return redirect('usuarios:dashboard')
                    
            except Exception as e:
                errors['general'] = f'Erro ao criar usuário: {str(e)}'
                print(f"Erro detalhado: {e}")
        
        context = {
            'errors': errors,
            'form_data': request.POST
        }
        return render(request, 'registration/register.html', context)
    
    return render(request, 'registration/register.html')

def custom_logout_view(request):
    """View personalizada de logout"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('usuarios:home')

# Views para templates (Function Based Views)
@login_required
def dashboard_usuario(request):
    """Dashboard do usuário"""
    from produtos.models import Produto
    from vendas.models import Venda
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Estatísticas básicas
    total_produtos = Produto.objects.filter(ativo=True).count()
    total_vendas = Venda.objects.count()
    
    # Faturamento do mês atual
    hoje = timezone.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    faturamento_mes = Venda.objects.filter(
        data_venda__gte=inicio_mes,
        status='concluida'
    ).aggregate(
        total=models.Sum('total')
    )['total'] or 0
    
    # Produtos com estoque baixo (estoque menor que o estoque mínimo)
    estoque_baixo = 0
    for produto in Produto.objects.filter(ativo=True):
        if produto.estoque < produto.estoque_minimo:
            estoque_baixo += 1
    
    # Últimas vendas (apenas para proprietários)
    ultimas_vendas = None
    produtos_destaque = None
    
    if request.user.is_proprietario:
        ultimas_vendas = Venda.objects.select_related('cliente').order_by('-data_venda')[:5]
        produtos_destaque = Produto.objects.filter(ativo=True).order_by('-data_cadastro')[:5]
    
    context = {
        'usuario': request.user,
        'titulo': 'Dashboard - RPM Motos',
        'total_produtos': total_produtos,
        'total_vendas': total_vendas,
        'faturamento_mes': f"{faturamento_mes:.2f}",
        'estoque_baixo': estoque_baixo,
        'ultimas_vendas': ultimas_vendas,
        'produtos_destaque': produtos_destaque,
    }
    return render(request, 'usuarios/dashboard.html', context)

@login_required
def perfil_view(request):
    """Página de perfil do usuário"""
    context = {
        'usuario': request.user,
        'titulo': 'Meu Perfil - RPM Motos'
    }
    return render(request, 'usuarios/perfil.html', context)

@login_required
def editar_perfil_view(request):
    """Editar perfil do usuário"""
    if request.method == 'POST':
        # Obter dados do formulário
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        endereco = request.POST.get('endereco')
        data_nascimento = request.POST.get('data_nascimento')
        
        # Atualizar usuário
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.telefone = telefone
        user.endereco = endereco
        
        if data_nascimento:
            from datetime import datetime
            try:
                user.data_nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        user.save()
        
        from django.contrib import messages
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('usuarios:perfil')
    
    context = {
        'usuario': request.user,
        'titulo': 'Editar Perfil - RPM Motos'
    }
    return render(request, 'usuarios/editar_perfil.html', context)

def teste_simples(request):
    """View de teste simples sem DRF"""
    from django.http import JsonResponse
    from django.utils import timezone
    return JsonResponse({
        'message': 'View simples funcionando!',
        'timestamp': timezone.now().isoformat()
    })
