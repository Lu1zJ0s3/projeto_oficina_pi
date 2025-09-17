from django.contrib import admin
from .models import Venda, Cliente, ItemVenda, Faturamento

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'cpf_cnpj', 'telefone', 'cidade', 'estado', 'ativo']
    list_filter = ['tipo', 'estado', 'ativo', 'data_cadastro']
    search_fields = ['nome', 'cpf_cnpj', 'email', 'telefone']
    list_editable = ['ativo']
    ordering = ['nome']

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['numero_venda', 'cliente', 'vendedor', 'data_venda', 'status', 'total', 'forma_pagamento']
    list_filter = ['status', 'forma_pagamento', 'data_venda', 'vendedor']
    search_fields = ['numero_venda', 'cliente__nome', 'vendedor__username']
    readonly_fields = ['numero_venda', 'data_venda', 'subtotal', 'total']
    ordering = ['-data_venda']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente', 'vendedor')

@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    list_display = ['venda', 'produto', 'quantidade', 'preco_unitario', 'subtotal']
    list_filter = ['produto__categoria', 'produto__marca']
    search_fields = ['venda__numero_venda', 'produto__nome']
    readonly_fields = ['subtotal']
    ordering = ['-venda__data_venda']

@admin.register(Faturamento)
class FaturamentoAdmin(admin.ModelAdmin):
    list_display = ['data', 'vendas_dia', 'faturamento_bruto', 'faturamento_liquido', 'lucro_estimado']
    list_filter = ['data']
    ordering = ['-data']
    readonly_fields = ['data', 'vendas_dia', 'faturamento_bruto', 'faturamento_liquido', 'lucro_estimado']
