from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST
from .models import Categoria, Produto, Pedido, ItemPedido
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Chave usada para salvar o carrinho dentro da sessão
CART_SESSION_KEY = "carrinho"

@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Login simples usando autenticação do Django.
    Se existir ?next=..., redireciona para lá após logar.
    """
    if request.user.is_authenticated:
        return redirect("catalogo")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Se o Django mandou o "next", voltamos pra página que o usuário queria
            next_url = request.GET.get("next")
            return redirect(next_url or "catalogo")

        # Se falhar, volta com erro
        return render(request, "core/login.html", {"erro": "Usuário ou senha inválidos."})

    return render(request, "core/login.html")


def logout_view(request):
    """
    Faz logout e volta para o catálogo.
    """
    logout(request)
    return redirect("catalogo")

def _get_cart(request):
    """
    Recupera o carrinho da sessão.
    Se não existir, cria um carrinho vazio na sessão.
    Estrutura do carrinho:
    {
        "1": 2,   # produto_id (str): quantidade (int)
        "5": 1
    }
    """
    cart = request.session.get(CART_SESSION_KEY)
    if cart is None:
        cart = {}
        request.session[CART_SESSION_KEY] = cart
    return cart


# =========================
# LOJA (CATÁLOGO / DETALHES)
# =========================
def lista_categorias(request):
    """
    Mostra todas as categorias disponíveis.
    """
    categorias = Categoria.objects.order_by("nome")
    return render(request, "core/categorias.html", {"categorias": categorias})


def produtos_por_categoria(request, categoria_id):
    """
    Mostra os produtos de uma categoria específica.
    """
    categoria = get_object_or_404(Categoria, id=categoria_id)

        # Salva na sessão a última categoria visitada (para "continuar comprando")
    request.session["ultima_categoria_id"] = categoria.id
    request.session.modified = True

    # Busca produtos ativos daquela categoria
    produtos = Produto.objects.filter(ativo=True, categoria=categoria).order_by("nome")

    return render(request, "core/produtos_por_categoria.html", {
        "categoria": categoria,
        "produtos": produtos,
    })

def continuar_comprando(request):
    """
    Redireciona o cliente para a última categoria visitada.
    Se não houver, volta para a lista de categorias.
    """
    ultima_categoria_id = request.session.get("ultima_categoria_id")

    # Se tiver categoria salva, vai para ela
    if ultima_categoria_id:
        return redirect("produtos_por_categoria", categoria_id=ultima_categoria_id)

    # Se não tiver, vai para a lista de categorias
    return redirect("lista_categorias")


def catalogo(request):
    """
    Página inicial do site: lista produtos ativos.
    """
    produtos = Produto.objects.filter(ativo=True).order_by("nome")
    return render(request, "core/catalogo.html", {"produtos": produtos})


def detalhes_produto(request, produto_id):
    """
    Página de detalhes do produto.
    """
    produto = get_object_or_404(Produto, id=produto_id, ativo=True)
    return render(request, "core/detalhes_produto.html", {"produto": produto})


# =========================
# CARRINHO (SESSÃO)
# =========================


def adicionar_ao_carrinho(request, produto_id):
    """
    Adiciona 1 unidade do produto ao carrinho na sessão.
    """
    # Garante que o produto existe e está ativo
    produto = get_object_or_404(Produto, id=produto_id, ativo=True)

    # Recupera o carrinho atual da sessão
    cart = _get_cart(request)

    # Usamos string como chave (sessão serializa melhor)
    pid = str(produto.id)

    # Se já existe, soma +1; se não, cria com quantidade 1
    cart[pid] = cart.get(pid, 0) + 1

    # Marca a sessão como modificada para garantir que será salva
    request.session.modified = True

    # Redireciona para a página do carrinho
    return redirect("ver_carrinho")


@require_POST
def atualizar_quantidade(request, produto_id):
    """
    Atualiza a quantidade do produto no carrinho para o valor digitado.
    Respeita o limite de estoque.
    """
    # Busca o produto para validar estoque
    produto = get_object_or_404(Produto, id=produto_id, ativo=True)

    cart = _get_cart(request)
    pid = str(produto.id)

    # Tenta ler a quantidade digitada
    try:
        quantidade = int(request.POST.get("quantidade", 1))
    except ValueError:
        quantidade = 1

    # Se quantidade <= 0, remove o item inteiro
    if quantidade <= 0:
        if pid in cart:
            del cart[pid]
            request.session.modified = True
        return redirect("ver_carrinho")

    # Limita ao estoque disponível
    if quantidade > produto.estoque_atual:
        quantidade = produto.estoque_atual

    # Se estoque for 0, remove do carrinho
    if produto.estoque_atual <= 0:
        if pid in cart:
            del cart[pid]
            request.session.modified = True
        return redirect("ver_carrinho")

    # Atualiza a quantidade no carrinho
    cart[pid] = quantidade
    request.session.modified = True

    return redirect("ver_carrinho")


def remover_do_carrinho(request, produto_id):
    """
    Remove 1 unidade do produto do carrinho.
    Se chegar em 0, remove o item do carrinho.
    """
    cart = _get_cart(request)
    pid = str(produto_id)

    if pid in cart:
        cart[pid] -= 1

        # Se quantidade ficar 0 ou menos, remove o item
        if cart[pid] <= 0:
            del cart[pid]

        request.session.modified = True

    return redirect("ver_carrinho")


def deletar_do_carrinho(request, produto_id):
    """
    Remove o item inteiro do carrinho (independente da quantidade).
    """
    cart = _get_cart(request)
    pid = str(produto_id)

    # Se existir no carrinho, remove a chave inteira
    if pid in cart:
        del cart[pid]
        request.session.modified = True

    return redirect("ver_carrinho")


def limpar_carrinho(request):
    """
    Remove todos os itens do carrinho.
    """
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True
    return redirect("ver_carrinho")

def ver_carrinho(request):
    """
    Mostra o carrinho com itens + totais calculados.
    """
    cart = _get_cart(request)

    # Se carrinho vazio, evita consulta desnecessária
    if not cart:
        return render(request, "core/carrinho.html", {"itens": [], "total": Decimal("0.00")})

    # Converte chaves em lista de IDs
    produto_ids = [int(pid) for pid in cart.keys()]

    # Busca os produtos do banco
    produtos = Produto.objects.filter(id__in=produto_ids, ativo=True)

    itens = []
    total = Decimal("0.00")

    # Monta itens com subtotal
    for produto in produtos:
        quantidade = int(cart.get(str(produto.id), 0))
        subtotal = produto.preco * quantidade
        total += subtotal

        itens.append({
            "produto": produto,
            "quantidade": quantidade,
            "subtotal": subtotal,
        })

    return render(request, "core/carrinho.html", {"itens": itens, "total": total})


# =========================
# CHECKOUT (CARRINHO -> PEDIDO)
# =========================

@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    """
    Converte o carrinho (sessão) em:
    - Pedido (no banco)
    - ItemPedido (um por produto)
    Depois limpa o carrinho e redireciona para a tela de sucesso.
    """
    cart = _get_cart(request)

    # Se carrinho vazio, volta pro catálogo
    if not cart:
        return redirect("catalogo")

    if request.method == "POST":
        # Captura dados do formulário
        nome = request.POST.get("nome_cliente", "").strip()
        telefone = request.POST.get("telefone_cliente", "").strip()
        endereco = request.POST.get("endereco_entrega", "").strip()

        # Validação simples
        if not nome or not telefone or not endereco:
            return render(request, "core/checkout.html", {
                "erro": "Preencha nome, telefone e endereço.",
            })

        # Busca produtos do carrinho
        produto_ids = [int(pid) for pid in cart.keys()]
        produtos = Produto.objects.filter(id__in=produto_ids, ativo=True)

        # Cria o pedido (status inicial)
        pedido = Pedido.objects.create(
            nome_cliente=nome,
            telefone_cliente=telefone,
            endereco_entrega=endereco,
            status="RECEBIDO",
            total=Decimal("0.00"),
            lucro_estimado=Decimal("0.00"),
        )

        total = Decimal("0.00")
        lucro = Decimal("0.00")

        # Cria itens do pedido e calcula totais
        for produto in produtos:
            qtd = int(cart.get(str(produto.id), 0))
            if qtd <= 0:
                continue

            # Congela preço e custo atuais (boa prática)
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=qtd,
                preco_unitario=produto.preco,
                custo_unitario=produto.custo,
            )

            total += produto.preco * qtd
            lucro += (produto.preco - produto.custo) * qtd

        # Salva totais no pedido
        pedido.total = total
        pedido.lucro_estimado = lucro
        pedido.save()

        # Limpa carrinho após finalizar
        request.session[CART_SESSION_KEY] = {}
        request.session.modified = True

        # Redireciona para tela de sucesso
        return redirect("pedido_sucesso", pedido_id=pedido.id)

    # GET: mostrar página de checkout
    return render(request, "core/checkout.html")


def pedido_sucesso(request, pedido_id):
    """
    Tela de sucesso após criar pedido.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, "core/pedido_sucesso.html", {"pedido": pedido})