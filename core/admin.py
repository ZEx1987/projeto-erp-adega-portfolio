from django.contrib import admin
from .models import Cliente, Categoria, Produto
from .models import Pedido, ItemPedido

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # Colunas mostradas na listagem
    list_display = ("nome", "email", "telefone", "criado_em")

    # Busca por nome/email
    search_fields = ("nome", "email")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # Colunas mostradas na listagem
    list_display = ("nome", "criado_em")

    # Busca por nome
    search_fields = ("nome",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    # Colunas mostradas na listagem
    list_display = ("nome", "categoria", "custo", "preco", "estoque_atual", "ativo", "criado_em", "imagem")

    # Filtros laterais
    list_filter = ("categoria", "ativo")

    # Busca por nome
    search_fields = ("nome",)

    # Edição rápida na listagem
    list_editable = ("custo", "preco", "estoque_atual", "ativo")

class ItemPedidoInline(admin.TabularInline):
    # Mostra os itens dentro do pedido no admin
    model = ItemPedido
    extra = 0
    readonly_fields = ("preco_unitario", "custo_unitario")
    can_delete = False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    # Colunas principais na lista
    list_display = ("id", "nome_cliente", "telefone_cliente", "status", "total", "lucro_estimado", "criado_em")

    # Filtros úteis
    list_filter = ("status", "criado_em")

    # Busca rápida
    search_fields = ("nome_cliente", "telefone_cliente")

    # Mostra itens dentro do pedido
    inlines = [ItemPedidoInline]    