from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from usuarios.models import Usuario
from produtos.models import Categoria, Marca, Produto, ImagemProduto
from vendas.models import Cliente, Venda, ItemVenda, Faturamento

admin.site.site_header = "Isailtom Motos - Administração"
admin.site.site_title = "Isailtom Motos Admin"
admin.site.index_title = "Bem-vindo ao painel administrativo"

@admin.register(Usuario)
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_active', 'date_joined']
    list_filter = ['tipo_usuario', 'is_active', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'cpf']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('tipo_usuario', 'telefone', 'endereco', 'data_nascimento', 'cpf')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('tipo_usuario', 'telefone', 'endereco', 'data_nascimento', 'cpf')
        }),
    )

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'ativo', 'produtos_count']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']
    
    def produtos_count(self, obj):
        return obj.produto_set.count()
    produtos_count.short_description = 'Produtos'

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'pais_origem', 'produtos_count']
    list_filter = ['pais_origem']
    search_fields = ['nome']
    ordering = ['nome']
    
    def produtos_count(self, obj):
        return obj.produto_set.count()
    produtos_count.short_description = 'Produtos'

class ImagemProdutoInline(admin.TabularInline):
    model = ImagemProduto
    extra = 1
    fields = ['imagem', 'legenda', 'ordem']

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'marca', 'categoria', 'tipo', 'preco', 'estoque', 'ativo', 'destaque']
    list_filter = ['tipo', 'categoria', 'marca', 'ativo', 'destaque', 'data_cadastro']
    search_fields = ['nome', 'descricao', 'modelo', 'codigo_barras']
    list_editable = ['ativo', 'destaque', 'estoque']
    ordering = ['-data_cadastro']
    date_hierarchy = 'data_cadastro'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'categoria', 'marca', 'tipo')
        }),
        ('Especificações Técnicas', {
            'fields': ('modelo', 'ano', 'cilindrada', 'cor'),
            'classes': ('collapse',)
        }),
        ('Preços e Estoque', {
            'fields': ('preco', 'preco_promocional', 'estoque', 'estoque_minimo')
        }),
        ('Identificação', {
            'fields': ('codigo_barras', 'imagem_principal'),
            'classes': ('collapse',)
        }),
        ('Configurações', {
            'fields': ('ativo', 'destaque')
        }),
    )
    
    inlines = [ImagemProdutoInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('categoria', 'marca')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'cpf_cnpj', 'telefone', 'cidade', 'estado', 'ativo', 'data_cadastro']
    list_filter = ['tipo', 'estado', 'ativo', 'data_cadastro']
    search_fields = ['nome', 'cpf_cnpj', 'email', 'telefone']
    ordering = ['nome']
    date_hierarchy = 'data_cadastro'
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'tipo', 'cpf_cnpj', 'email', 'telefone')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep')
        }),
        ('Configurações', {
            'fields': ('ativo',)
        }),
    )

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 1
    fields = ['produto', 'quantidade', 'preco_unitario', 'desconto_item']
    readonly_fields = ['subtotal']

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['numero_venda', 'cliente', 'vendedor', 'status', 'total', 'data_venda']
    list_filter = ['status', 'forma_pagamento', 'data_venda', 'vendedor']
    search_fields = ['numero_venda', 'cliente__nome', 'vendedor__username']
    ordering = ['-data_venda']
    date_hierarchy = 'data_venda'
    readonly_fields = ['numero_venda', 'subtotal', 'total', 'data_venda']
    
    fieldsets = (
        ('Informações da Venda', {
            'fields': ('numero_venda', 'cliente', 'vendedor', 'status', 'forma_pagamento')
        }),
        ('Valores', {
            'fields': ('subtotal', 'desconto', 'total')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Datas', {
            'fields': ('data_venda',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ItemVendaInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente', 'vendedor')

@admin.register(Faturamento)
class FaturamentoAdmin(admin.ModelAdmin):
    list_display = ['data', 'vendas_dia', 'faturamento_bruto', 'faturamento_liquido', 'lucro_estimado']
    list_filter = ['data']
    ordering = ['-data']
    date_hierarchy = 'data'
    readonly_fields = ['vendas_dia', 'faturamento_bruto', 'desconto_total', 'faturamento_liquido', 'lucro_estimado']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

admin.site.disable_action('delete_selected')

from django.contrib import messages
from django.utils.translation import ngettext

def make_active(modeladmin, request, queryset):
    updated = queryset.update(ativo=True)
    modeladmin.message_user(request, ngettext(
        '%d produto foi marcado como ativo.',
        '%d produtos foram marcados como ativos.',
        updated,
    ) % updated, messages.SUCCESS)
make_active.short_description = "Marcar produtos como ativos"

def make_inactive(modeladmin, request, queryset):
    updated = queryset.update(ativo=False)
    modeladmin.message_user(request, ngettext(
        '%d produto foi marcado como inativo.',
        '%d produtos foram marcados como inativos.',
        updated,
    ) % updated, messages.SUCCESS)
make_inactive.short_description = "Marcar produtos como inativos"

ProdutoAdmin.actions = [make_active, make_inactive]
