from rest_framework import serializers
from .models import Categoria, Marca, Produto, ImagemProduto

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descricao', 'ativo']

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ['id', 'nome', 'pais_origem', 'logo']

class ImagemProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemProduto
        fields = ['id', 'imagem', 'legenda', 'ordem']

class ProdutoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    marca = MarcaSerializer(read_only=True)
    imagens = ImagemProdutoSerializer(many=True, read_only=True)
    categoria_id = serializers.IntegerField(write_only=True)
    marca_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'descricao', 'categoria', 'marca', 'tipo',
            'modelo', 'ano', 'cilindrada', 'cor', 'preco', 'preco_promocional',
            'estoque', 'estoque_minimo', 'codigo_barras', 'imagem_principal',
            'ativo', 'destaque', 'data_cadastro', 'data_atualizacao',
            'categoria_id', 'marca_id', 'imagens'
        ]
        read_only_fields = ['id', 'data_cadastro', 'data_atualizacao']
    
    def create(self, validated_data):
        categoria_id = validated_data.pop('categoria_id')
        marca_id = validated_data.pop('marca_id')
        
        validated_data['categoria_id'] = categoria_id
        validated_data['marca_id'] = marca_id
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'categoria_id' in validated_data:
            categoria_id = validated_data.pop('categoria_id')
            validated_data['categoria_id'] = categoria_id
        
        if 'marca_id' in validated_data:
            marca_id = validated_data.pop('marca_id')
            validated_data['marca_id'] = marca_id
        
        return super().update(instance, validated_data)

class ProdutoListSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    marca = MarcaSerializer(read_only=True)
    
    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'categoria', 'marca', 'tipo', 'modelo',
            'preco', 'preco_promocional', 'estoque', 'imagem_principal',
            'ativo', 'destaque'
        ]

class ProdutoDetailSerializer(ProdutoSerializer):
    class Meta(ProdutoSerializer.Meta):
        fields = ProdutoSerializer.Meta.fields + ['estoque_status', 'preco_atual']

class ProdutoEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'estoque', 'estoque_minimo', 'estoque_status']
