from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from decimal import Decimal
from datetime import datetime, timedelta
import json

from produtos import models
from .models import Venda, Cliente, ItemVenda, Faturamento
from .forms import VendaForm, ClienteForm, VendaItemFormSet
from produtos.models import Produto

# Views para templates (Function Based Views)
@login_required
def lista_vendas(request):
    """Lista de vendas para template"""
    vendas = Venda.objects.all().order_by('-data_venda')
    clientes = Cliente.objects.filter(ativo=True)
    
    # Filtros
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
    
    context = {
        'vendas': vendas,
        'clientes': clientes,
        'titulo': 'Vendas - RPM Motos'
    }
    return render(request, 'vendas/lista.html', context)

@login_required
def detalhe_venda(request, pk):
    """Detalhes da venda para template"""
    venda = get_object_or_404(Venda, pk=pk)
    context = {
        'venda': venda,
        'titulo': f'Venda {venda.numero_venda} - RPM Motos'
    }
    return render(request, 'vendas/detalhe.html', context)

@login_required
def criar_venda(request):
    if request.method == 'POST':
        form = VendaForm(request.POST)
        formset = VendaItemFormSet(request.POST, prefix='itens')
        
        print(f"POST data: {request.POST}")
        print(f"Formset data: {request.POST.getlist('itens-0-produto')}")
        
        if form.is_valid() and formset.is_valid():
            venda = form.save(commit=False)
            venda.vendedor = request.user
            
            from datetime import datetime
            venda.numero_venda = f"V{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            if not venda.status:
                venda.status = 'aprovada'
            
            venda.save()
            
            instances = formset.save(commit=False)
            itens_salvos = 0
            
            print(f"Instâncias do formset: {len(instances)}")
            
            for i, instance in enumerate(instances):
                print(f"Item {i}: produto={instance.produto}, quantidade={instance.quantidade}, preco={instance.preco_unitario}")
                
                if instance.produto and instance.quantidade and instance.preco_unitario:
                    instance.venda = venda
                    instance.save()
                    itens_salvos += 1
                    print(f"Item {i} salvo com sucesso")
                else:
                    print(f"Item {i} não foi salvo - dados incompletos")
            
            if itens_salvos == 0:
                messages.error(request, 'Pelo menos um item deve ser adicionado à venda.')
                venda.delete()
                return render(request, 'vendas/form.html', context)
            
            venda.calcular_totais()
            
            messages.success(request, f'Venda criada com sucesso! {itens_salvos} itens salvos.')
            return redirect('vendas:detalhe', pk=venda.pk)
        else:
            if not form.is_valid():
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Erro no campo {field}: {error}')
            
            if not formset.is_valid():
                if formset.non_form_errors():
                    for error in formset.non_form_errors():
                        messages.error(request, f'Erro no formset: {error}')
                for form_item in formset:
                    if form_item.errors:
                        for field, errors in form_item.errors.items():
                            for error in errors:
                                messages.error(request, f'Erro no item: {error}')
    else:
        form = VendaForm()
        formset = VendaItemFormSet(prefix='itens')
    
    context = {
        'form': form,
        'formset': formset,
        'produtos': Produto.objects.filter(ativo=True),
        'titulo': 'Nova Venda - RPM Motos'
    }
    return render(request, 'vendas/form.html', context)

@login_required
def editar_venda(request, pk):
    venda = get_object_or_404(Venda, pk=pk)
    if request.method == 'POST':
        form = VendaForm(request.POST, instance=venda)
        formset = VendaItemFormSet(request.POST, prefix='itens')
        
        if form.is_valid() and formset.is_valid():
            form.save()
            
            venda.itens.all().delete()
            
            instances = formset.save(commit=False)
            itens_salvos = 0
            
            for instance in instances:
                if instance.produto and instance.quantidade and instance.preco_unitario:
                    instance.venda = venda
                    instance.save()
                    itens_salvos += 1
            
            venda.calcular_totais()
            
            messages.success(request, f'Venda atualizada com sucesso! {itens_salvos} itens salvos.')
            return redirect('vendas:detalhe', pk=venda.pk)
        else:
            if not form.is_valid():
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Erro no campo {field}: {error}')
            
            if not formset.is_valid():
                if formset.non_form_errors():
                    for error in formset.non_form_errors():
                        messages.error(request, f'Erro no formset: {error}')
                for form_item in formset:
                    if form_item.errors:
                        for field, errors in form_item.errors.items():
                            for error in errors:
                                messages.error(request, f'Erro no item: {error}')
    else:
        form = VendaForm(instance=venda)
        formset = VendaItemFormSet(prefix='itens', initial=[
            {
                'produto': item.produto,
                'quantidade': item.quantidade,
                'preco_unitario': item.preco_unitario,
                'desconto_item': item.desconto_item,
            }
            for item in venda.itens.all()
        ])
    
    context = {
        'form': form,
        'formset': formset,
        'venda': venda,
        'produtos': Produto.objects.filter(ativo=True),
        'titulo': f'Editar Venda {venda.numero_venda} - RPM Motos'
    }
    return render(request, 'vendas/form.html', context)

@login_required
def deletar_venda(request, pk):
    venda = get_object_or_404(Venda, pk=pk)
    
    if request.method == 'POST':
        numero_venda = venda.numero_venda
        cliente_nome = venda.cliente.nome
        
        venda.delete()
        
        messages.success(request, f'Venda {numero_venda} do cliente {cliente_nome} foi excluída com sucesso!')
        return redirect('vendas:lista')
    
    context = {
        'venda': venda,
        'titulo': f'Excluir Venda {venda.numero_venda} - RPM Motos'
    }
    return render(request, 'vendas/confirmar_exclusao.html', context)

@login_required
def dashboard_vendas(request):
    total_vendas = Venda.objects.count()
    vendas_hoje = Venda.objects.filter(data_venda__date=datetime.now().date()).count()
    vendas_mes = Venda.objects.filter(
        data_venda__month=datetime.now().month,
        status__in=['concluida', 'aprovada']
    )
    faturamento_mes = sum(v.total for v in vendas_mes)
    
    ticket_medio = faturamento_mes / total_vendas if total_vendas > 0 else 0
    
    ultimas_vendas = Venda.objects.all()[:5]
    
    context = {
        'total_vendas': total_vendas,
        'vendas_hoje': vendas_hoje,
        'faturamento_mes': faturamento_mes,
        'ticket_medio': ticket_medio,
        'ultimas_vendas': ultimas_vendas,
        'titulo': 'Dashboard de Vendas - RPM Motos'
    }
    return render(request, 'vendas/dashboard.html', context)

@login_required
def faturamento_view(request):
    if not request.user.is_proprietario:
        messages.error(request, 'Acesso negado. Apenas proprietários podem ver o faturamento.')
        return redirect('dashboard_vendas')
    
    data_inicio = datetime.now().date() - timedelta(days=30)
    data_fim = datetime.now().date()
    
    vendas = Venda.objects.filter(
        data_venda__date__range=[data_inicio, data_fim],
        status__in=['concluida', 'aprovada']
    )
    
    faturamento_diario = {}
    for i in range(30):
        data = data_fim - timedelta(days=i)
        vendas_dia = vendas.filter(data_venda__date=data)
        faturamento_diario[data] = {
            'vendas': vendas_dia.count(),
            'total': sum(v.total for v in vendas_dia),
            'lucro': sum(v.lucro_estimado for v in vendas_dia)
        }
    
    faturamento_total = sum(dados['total'] for dados in faturamento_diario.values())
    lucro_total = sum(dados['lucro'] for dados in faturamento_diario.values())
    faturamento_diario_json = json.dumps({str(data): dados for data, dados in faturamento_diario.items()}, default=str)
    context = {
        'faturamento_diario': faturamento_diario,
        'faturamento_diario_json': faturamento_diario_json,
        'faturamento_total': faturamento_total,
        'lucro_total': lucro_total,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'titulo': 'Faturamento - RPM Motos'
    }
    return render(request, 'vendas/faturamento.html', context)

@login_required
def atualizar_status_vendas(request):
    if request.method == 'POST':
        vendas_para_atualizar = Venda.objects.filter(status__in=['cancelada', 'pendente', 'aprovada'])
        count = vendas_para_atualizar.update(status='concluida')
        
        datas_para_atualizar = set()
        for venda in vendas_para_atualizar:
            datas_para_atualizar.add(venda.data_venda.date())
        
        for data in datas_para_atualizar:
            Faturamento.atualizar_faturamento_dia(data)
        
        messages.success(request, f'{count} vendas foram atualizadas para concluída (canceladas, pendentes e aprovadas).')
        return redirect('vendas:lista')
    
    return render(request, 'vendas/atualizar_status.html', {
        'titulo': 'Atualizar Status das Vendas - RPM Motos'
    })

@login_required
def atualizar_faturamento(request):
    if request.method == 'POST':
        data_inicio = datetime.now().date() - timedelta(days=30)
        data_fim = datetime.now().date()
        
        count = 0
        for i in range(30):
            data = data_fim - timedelta(days=i)
            try:
                Faturamento.atualizar_faturamento_dia(data)
                count += 1
            except Exception as e:
                print(f"Erro ao atualizar faturamento para {data}: {e}")
        
        messages.success(request, f'Faturamento atualizado para {count} dias.')
        return redirect('vendas:faturamento')
    
    return render(request, 'vendas/atualizar_faturamento.html', {
        'titulo': 'Atualizar Faturamento - RPM Motos'
    })

# Views para gerenciar clientes
@login_required
def lista_clientes(request):
    clientes = Cliente.objects.all().order_by('nome')
    
    tipo = request.GET.get('tipo')
    ativo = request.GET.get('ativo')
    search = request.GET.get('search')
    
    if tipo:
        clientes = clientes.filter(tipo=tipo)
    if ativo:
        clientes = clientes.filter(ativo=ativo == 'true')
    if search:
        clientes = clientes.filter(
            models.Q(nome__icontains=search) |
            models.Q(cpf_cnpj__icontains=search) |
            models.Q(email__icontains=search)
        )
    
    context = {
        'clientes': clientes,
        'titulo': 'Clientes - RPM Motos'
    }
    return render(request, 'vendas/clientes/lista.html', context)

@login_required
def criar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, 'Cliente criado com sucesso!')
            return redirect('vendas:detalhe_cliente', pk=cliente.pk)
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
        'titulo': 'Novo Cliente - RPM Motos'
    }
    return render(request, 'vendas/clientes/form.html', context)

@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('vendas:detalhe_cliente', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'cliente': cliente,
        'titulo': f'Editar Cliente - {cliente.nome}'
    }
    return render(request, 'vendas/clientes/form.html', context)

@login_required
def detalhe_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    vendas_cliente = Venda.objects.filter(cliente=cliente).order_by('-data_venda')[:10]
    
    context = {
        'cliente': cliente,
        'vendas_cliente': vendas_cliente,
        'titulo': f'Cliente {cliente.nome} - RPM Motos'
    }
    return render(request, 'vendas/clientes/detalhe.html', context)
