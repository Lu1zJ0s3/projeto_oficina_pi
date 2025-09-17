from django import forms
from .models import Venda, Cliente, ItemVenda
from produtos.models import Produto

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nome', 'tipo', 'cpf_cnpj', 'email', 'telefone',
            'endereco', 'cidade', 'estado', 'cep'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome completo'
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'cpf_cnpj': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'CPF ou CNPJ'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'exemplo@email.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '(11) 99999-9999'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Endereço completo'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Cidade'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '00000-000'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Estados brasileiros
        ESTADOS_CHOICES = [
            ('', 'Selecione um estado'),
            ('AC', 'Acre'),
            ('AL', 'Alagoas'),
            ('AP', 'Amapá'),
            ('AM', 'Amazonas'),
            ('BA', 'Bahia'),
            ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'),
            ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'),
            ('PA', 'Pará'),
            ('PB', 'Paraíba'),
            ('PR', 'Paraná'),
            ('PE', 'Pernambuco'),
            ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'),
            ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'),
            ('SE', 'Sergipe'),
            ('TO', 'Tocantins'),
        ]
        self.fields['estado'].choices = ESTADOS_CHOICES
        
        # Adicionar classes CSS para labels
        for field_name, field in self.fields.items():
            field.label = field.label.title()
            field.label_suffix = ':'
    
    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data.get('cpf_cnpj')
        if cpf_cnpj:
            # Remover caracteres especiais
            cpf_cnpj = ''.join(filter(str.isdigit, cpf_cnpj))
            
            if len(cpf_cnpj) == 11:  # CPF
                # Validação básica de CPF
                if cpf_cnpj == cpf_cnpj[0] * 11:
                    raise forms.ValidationError('CPF inválido.')
            elif len(cpf_cnpj) == 14:  # CNPJ
                # Validação básica de CNPJ
                if cpf_cnpj == cpf_cnpj[0] * 14:
                    raise forms.ValidationError('CNPJ inválido.')
            else:
                raise forms.ValidationError('CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos.')
        
        return cpf_cnpj

class ItemVendaForm(forms.ModelForm):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True),
        empty_label="Selecione um produto",
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    class Meta:
        model = ItemVenda
        fields = ['produto', 'quantidade', 'preco_unitario', 'desconto_item']
        widgets = {
            'quantidade': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '1',
                'placeholder': '1',
                'required': 'required'
            }),
            'preco_unitario': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'placeholder': '0.00',
                'required': 'required'
            }),
            'desconto_item': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'placeholder': '0.00'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS para labels
        for field_name, field in self.fields.items():
            if field.label:
                field.label = field.label.title()
            field.label_suffix = ':'
    
    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade and quantidade <= 0:
            raise forms.ValidationError('A quantidade deve ser maior que zero.')
        return quantidade
    
    def clean_preco_unitario(self):
        preco = self.cleaned_data.get('preco_unitario')
        if preco and preco <= 0:
            raise forms.ValidationError('O preço deve ser maior que zero.')
        return preco
    
    def clean_desconto_item(self):
        desconto = self.cleaned_data.get('desconto_item')
        if desconto and desconto < 0:
            raise forms.ValidationError('O desconto não pode ser negativo.')
        return desconto

class VendaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(ativo=True),
        empty_label="Selecione um cliente",
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    class Meta:
        model = Venda
        fields = [
            'cliente', 'status', 'forma_pagamento', 'desconto', 'observacoes'
        ]
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'required': 'required'
            }),
            'forma_pagamento': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'required': 'required'
            }),
            'desconto': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Observações sobre a venda'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS para labels
        for field_name, field in self.fields.items():
            if field.label:
                field.label = field.label.title()
            field.label_suffix = ':'
    
    def clean_desconto(self):
        desconto = self.cleaned_data.get('desconto')
        if desconto and desconto < 0:
            raise forms.ValidationError('O desconto não pode ser negativo.')
        return desconto
    
    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get('cliente')
        forma_pagamento = cleaned_data.get('forma_pagamento')
        
        if not cliente:
            raise forms.ValidationError('Cliente é obrigatório.')
        
        if not forma_pagamento:
            raise forms.ValidationError('Forma de pagamento é obrigatória.')
        
        return cleaned_data

class VendaItemFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = ItemVenda.objects.none()
    
    def clean(self):
        super().clean()
        
        # Verificar se pelo menos um item válido foi preenchido
        itens_validos = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                produto = form.cleaned_data.get('produto')
                quantidade = form.cleaned_data.get('quantidade')
                preco_unitario = form.cleaned_data.get('preco_unitario')
                
                # Verificar se todos os campos obrigatórios estão preenchidos
                if produto and quantidade and preco_unitario:
                    # Verificar estoque apenas se o produto tem esse atributo
                    if hasattr(produto, 'estoque') and quantidade > produto.estoque:
                        raise forms.ValidationError(
                            f'Quantidade insuficiente em estoque para {produto.nome}. '
                            f'Disponível: {produto.estoque}'
                        )
                    itens_validos.append(form)
        
        # Não é obrigatório ter itens para salvar o formulário principal
        # A validação será feita na view
        return

VendaItemFormSet = forms.modelformset_factory(
    ItemVenda,
    form=ItemVendaForm,
    formset=VendaItemFormSet,
    extra=1,
    can_delete=True
)
