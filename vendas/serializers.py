from rest_framework import serializers
from .models import Cliente, Venda, ItemVenda, Faturamento
from produtos.serializers import ProdutoSerializer

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id', 'nome', 'tipo', 'cpf_cnpj', 'email', 'telefone',
            'endereco', 'cidade', 'estado', 'cep', 'data_cadastro', 'ativo'
        ]
        read_only_fields = ['id', 'data_cadastro']

class ClienteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome', 'tipo', 'cpf_cnpj', 'telefone', 'cidade', 'estado', 'ativo']

class ItemVendaSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    produto_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ItemVenda
        fields = [
            'id', 'produto', 'quantidade', 'preco_unitario',
            'desconto_item', 'subtotal', 'produto_id'
        ]
        read_only_fields = ['id', 'subtotal']
    
    def create(self, validated_data):
        produto_id = validated_data.pop('produto_id')
        validated_data['produto_id'] = produto_id
        return super().create(validated_data)

class VendaSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    vendedor = serializers.StringRelatedField(read_only=True)
    itens = ItemVendaSerializer(many=True, read_only=True)
    cliente_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Venda
        fields = [
            'id', 'numero_venda', 'cliente', 'vendedor', 'data_venda',
            'status', 'forma_pagamento', 'subtotal', 'desconto', 'total',
            'observacoes', 'cliente_id', 'itens'
        ]
        read_only_fields = ['id', 'numero_venda', 'vendedor', 'data_venda', 'subtotal', 'total']
    
    def create(self, validated_data):
        cliente_id = validated_data.pop('cliente_id')
        validated_data['cliente_id'] = cliente_id
        validated_data['vendedor'] = self.context['request'].user
        
        # Gerar número da venda
        from datetime import datetime
        validated_data['numero_venda'] = f"V{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return super().create(validated_data)

class VendaListSerializer(serializers.ModelSerializer):
    cliente = ClienteListSerializer(read_only=True)
    vendedor = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Venda
        fields = [
            'id', 'numero_venda', 'cliente', 'vendedor', 'data_venda',
            'status', 'total'
        ]

class VendaDetailSerializer(VendaSerializer):
    class Meta(VendaSerializer.Meta):
        fields = VendaSerializer.Meta.fields + ['lucro_estimado']

class FaturamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faturamento
        fields = [
            'id', 'data', 'vendas_dia', 'faturamento_bruto',
            'desconto_total', 'faturamento_liquido', 'lucro_estimado'
        ]
        read_only_fields = ['id']

class FaturamentoResumoSerializer(serializers.Serializer):
    total_vendas = serializers.IntegerField()
    faturamento_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    lucro_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    periodo = serializers.CharField()
