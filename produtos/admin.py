from django.contrib import admin
from .models import Produto, Categoria, Marca

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']
    list_editable = ['ativo']
    ordering = ['nome']

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'pais_origem']
    list_filter = ['pais_origem']
    search_fields = ['nome']
    ordering = ['nome']

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'marca', 'tipo', 'preco', 'estoque', 'ativo', 'destaque']
    list_filter = ['categoria', 'marca', 'tipo', 'ativo', 'destaque', 'ano']
    search_fields = ['nome', 'modelo', 'codigo_barras']
    list_editable = ['preco', 'estoque', 'ativo', 'destaque']
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    ordering = ['nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'categoria', 'marca', 'tipo')
        }),
        ('Especificações', {
            'fields': ('modelo', 'ano', 'cilindrada', 'cor')
        }),
        ('Preços e Estoque', {
            'fields': ('preco', 'preco_promocional', 'estoque', 'estoque_minimo')
        }),
        ('Outros', {
            'fields': ('codigo_barras', 'imagem_principal', 'ativo', 'destaque')
        }),
        ('Datas', {
            'fields': ('data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('categoria', 'marca')
