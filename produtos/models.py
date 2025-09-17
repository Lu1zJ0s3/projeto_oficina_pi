from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name=_('Nome'))
    descricao = models.TextField(blank=True, verbose_name=_('Descrição'))
    ativo = models.BooleanField(default=True, verbose_name=_('Ativo'))
    
    class Meta:
        verbose_name = _('Categoria')
        verbose_name_plural = _('Categorias')
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Marca(models.Model):
    nome = models.CharField(max_length=100, verbose_name=_('Nome'))
    pais_origem = models.CharField(max_length=100, blank=True, verbose_name=_('País de Origem'))
    logo = models.ImageField(upload_to='marcas/', blank=True, null=True, verbose_name=_('Logo'))
    
    class Meta:
        verbose_name = _('Marca')
        verbose_name_plural = _('Marcas')
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Produto(models.Model):
    TIPO_CHOICES = [
        ('moto', 'Moto'),
        ('acessorio', 'Acessório'),
        ('peca', 'Peça'),
        ('servico', 'Serviço'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name=_('Nome'))
    descricao = models.TextField(verbose_name=_('Descrição'))
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        verbose_name=_('Categoria')
    )
    marca = models.ForeignKey(
        Marca, 
        on_delete=models.CASCADE, 
        verbose_name=_('Marca')
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='moto',
        verbose_name=_('Tipo')
    )
    modelo = models.CharField(max_length=100, blank=True, verbose_name=_('Modelo'))
    ano = models.IntegerField(blank=True, null=True, verbose_name=_('Ano'))
    cilindrada = models.CharField(max_length=50, blank=True, verbose_name=_('Cilindrada'))
    cor = models.CharField(max_length=50, blank=True, verbose_name=_('Cor'))
    preco = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name=_('Preço')
    )
    preco_promocional = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name=_('Preço Promocional')
    )
    estoque = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Estoque')
    )
    estoque_minimo = models.PositiveIntegerField(
        default=5,
        verbose_name=_('Estoque Mínimo')
    )
    codigo_barras = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name=_('Código de Barras')
    )
    imagem_principal = models.ImageField(
        upload_to='produtos/', 
        blank=True, 
        null=True,
        verbose_name=_('Imagem Principal')
    )
    ativo = models.BooleanField(default=True, verbose_name=_('Ativo'))
    destaque = models.BooleanField(default=False, verbose_name=_('Destaque'))
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name=_('Data de Cadastro'))
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name=_('Data de Atualização'))
    
    class Meta:
        verbose_name = _('Produto')
        verbose_name_plural = _('Produtos')
        ordering = ['-data_cadastro']
    
    def __str__(self):
        return f"{self.marca.nome} {self.nome} - {self.modelo}"
    
    @property
    def preco_atual(self):
        return self.preco_promocional if self.preco_promocional else self.preco
    
    @property
    def estoque_status(self):
        if self.estoque == 0:
            return 'sem_estoque'
        elif self.estoque <= self.estoque_minimo:
            return 'estoque_baixo'
        else:
            return 'estoque_ok'
    
    def atualizar_estoque(self, quantidade, tipo_operacao='venda'):
        """
        Atualiza o estoque do produto
        tipo_operacao: 'venda' (diminui) ou 'compra' (aumenta)
        """
        if tipo_operacao == 'venda':
            if self.estoque >= quantidade:
                self.estoque -= quantidade
                self.save()
                return True
            return False
        elif tipo_operacao == 'compra':
            self.estoque += quantidade
            self.save()
            return True
        return False

class ImagemProduto(models.Model):
    produto = models.ForeignKey(
        Produto, 
        on_delete=models.CASCADE, 
        related_name='imagens',
        verbose_name=_('Produto')
    )
    imagem = models.ImageField(upload_to='produtos/', verbose_name=_('Imagem'))
    legenda = models.CharField(max_length=200, blank=True, verbose_name=_('Legenda'))
    ordem = models.PositiveIntegerField(default=0, verbose_name=_('Ordem'))
    
    class Meta:
        verbose_name = _('Imagem do Produto')
        verbose_name_plural = _('Imagens dos Produtos')
        ordering = ['ordem']
    
    def __str__(self):
        return f"Imagem {self.ordem} - {self.produto.nome}"
