from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from produtos.models import Produto
from decimal import Decimal

Usuario = get_user_model()

class Cliente(models.Model):
    TIPO_CHOICES = [
        ('pessoa_fisica', 'Pessoa Física'),
        ('pessoa_juridica', 'Pessoa Jurídica'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name=_('Nome'))
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='pessoa_fisica',
        verbose_name=_('Tipo')
    )
    cpf_cnpj = models.CharField(max_length=18, unique=True, verbose_name=_('CPF/CNPJ'))
    email = models.EmailField(blank=True, verbose_name=_('E-mail'))
    telefone = models.CharField(max_length=15, verbose_name=_('Telefone'))
    endereco = models.TextField(verbose_name=_('Endereço'))
    cidade = models.CharField(max_length=100, verbose_name=_('Cidade'))
    estado = models.CharField(max_length=2, verbose_name=_('Estado'))
    cep = models.CharField(max_length=9, verbose_name=_('CEP'))
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name=_('Data de Cadastro'))
    ativo = models.BooleanField(default=True, verbose_name=_('Ativo'))
    
    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.cpf_cnpj})"

class Venda(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('transferencia', 'Transferência'),
        ('boleto', 'Boleto'),
    ]
    
    numero_venda = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name=_('Número da Venda')
    )
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        verbose_name=_('Cliente')
    )
    vendedor = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        verbose_name=_('Vendedor')
    )
    data_venda = models.DateTimeField(auto_now_add=True, verbose_name=_('Data da Venda'))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name=_('Status')
    )
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        verbose_name=_('Forma de Pagamento')
    )
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Subtotal')
    )
    desconto = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Desconto')
    )
    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Total')
    )
    observacoes = models.TextField(blank=True, verbose_name=_('Observações'))
    
    class Meta:
        verbose_name = _('Venda')
        verbose_name_plural = _('Vendas')
        ordering = ['-data_venda']
    
    def __str__(self):
        return f"Venda {self.numero_venda} - {self.cliente.nome}"
    
    def calcular_totais(self):
        """Calcula subtotal e total da venda"""
        self.subtotal = sum(item.subtotal for item in self.itens.all())
        self.total = self.subtotal - self.desconto
        self.save()
    
    @property
    def lucro_estimado(self):
        """Calcula o lucro estimado da venda"""
        return sum(item.lucro_estimado for item in self.itens.all())

class ItemVenda(models.Model):
    venda = models.ForeignKey(
        Venda, 
        on_delete=models.CASCADE, 
        related_name='itens',
        verbose_name=_('Venda')
    )
    produto = models.ForeignKey(
        Produto, 
        on_delete=models.CASCADE, 
        verbose_name=_('Produto')
    )
    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Quantidade')
    )
    preco_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_('Preço Unitário')
    )
    desconto_item = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Desconto do Item')
    )
    
    class Meta:
        verbose_name = _('Item da Venda')
        verbose_name_plural = _('Itens da Venda')
    
    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade}x"
    
    @property
    def subtotal(self):
        """Calcula o subtotal do item"""
        return self.quantidade * self.preco_unitario - self.desconto_item
    
    @property
    def lucro_estimado(self):
        """Calcula o lucro estimado do item (assumindo margem de 30%)"""
        custo_estimado = self.preco_unitario * Decimal('0.7')  # Margem de 30%
        return (self.preco_unitario - custo_estimado) * self.quantidade
    
    def save(self, *args, **kwargs):
        """Atualiza o estoque quando o item é salvo"""
        is_new = self.pk is None
        
        # Salvar primeiro o item
        super().save(*args, **kwargs)
        
        # Depois atualizar estoque se necessário (apenas para novos itens)
        if is_new and hasattr(self.produto, 'atualizar_estoque'):
            self.produto.atualizar_estoque(self.quantidade, 'venda')
        
        # Calcular totais da venda
        if hasattr(self, 'venda') and self.venda:
            self.venda.calcular_totais()

class Faturamento(models.Model):
    """Modelo para controlar o faturamento total da empresa"""
    data = models.DateField(unique=True, verbose_name=_('Data'))
    vendas_dia = models.PositiveIntegerField(default=0, verbose_name=_('Vendas do Dia'))
    faturamento_bruto = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Faturamento Bruto')
    )
    desconto_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Desconto Total')
    )
    faturamento_liquido = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Faturamento Líquido')
    )
    lucro_estimado = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Lucro Estimado')
    )
    
    class Meta:
        verbose_name = _('Faturamento')
        verbose_name_plural = _('Faturamentos')
        ordering = ['-data']
    
    def __str__(self):
        return f"Faturamento {self.data} - R$ {self.faturamento_liquido}"
    
    @classmethod
    def atualizar_faturamento_dia(cls, data):
        """Atualiza o faturamento de uma data específica"""
        vendas = Venda.objects.filter(
            data_venda__date=data,
            status__in=['concluida', 'aprovada']
        )
        
        faturamento, created = cls.objects.get_or_create(data=data)
        faturamento.vendas_dia = vendas.count()
        faturamento.faturamento_bruto = sum(v.subtotal for v in vendas)
        faturamento.desconto_total = sum(v.desconto for v in vendas)
        faturamento.faturamento_liquido = sum(v.total for v in vendas)
        faturamento.lucro_estimado = sum(v.lucro_estimado for v in vendas)
        faturamento.save()
        
        return faturamento
