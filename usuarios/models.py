from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import re

class Usuario(AbstractUser):
    TIPO_CHOICES = [
        ('proprietario', 'Proprietário'),
        ('vendedor', 'Vendedor'),
        ('gerente', 'Gerente'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='vendedor',
        verbose_name=_('Tipo de Usuário')
    )
    telefone = models.CharField(max_length=15, blank=True, verbose_name=_('Telefone'))
    endereco = models.TextField(blank=True, verbose_name=_('Endereço'))
    data_nascimento = models.DateField(null=True, blank=True, verbose_name=_('Data de Nascimento'))
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True, verbose_name=_('CPF'))
    
    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    @property
    def is_proprietario(self):
        return self.tipo_usuario == 'proprietario'
    
    def clean(self):
        """Validação personalizada do modelo"""
        super().clean()
        
        # Validação básica do CPF (comentada temporariamente para debug)
        # if self.cpf:
        #     # Remover caracteres não numéricos
        #     cpf_numeros = re.sub(r'[^0-9]', '', self.cpf)
        #     
        #     # Verificar se tem 11 dígitos
        #     if len(cpf_numeros) != 11:
        #         raise models.ValidationError({'cpf': 'CPF deve ter 11 dígitos'})
        #     
        #     # Verificar se todos os dígitos não são iguais
        #     if len(set(cpf_numeros)) == 1:
        #         raise models.ValidationError({'cpf': 'CPF inválido'})
        pass
    
    def _validar_cpf(self, cpf):
        """Validação dos dígitos verificadores do CPF"""
        if len(cpf) != 11:
            return False
        
        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Calcular primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Calcular segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verificar se os dígitos calculados são iguais aos do CPF
        return cpf[-2:] == f"{digito1}{digito2}"
