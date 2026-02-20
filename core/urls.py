from django.urls import path
from . import views

urlpatterns = [
    #tela de login/logout
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Loja
    path("", views.catalogo, name="catalogo"),
    path("produto/<int:produto_id>/", views.detalhes_produto, name="detalhes_produto"),

    # Categorias para separar produtos
    path("categorias/", views.lista_categorias, name="lista_categorias"),
    path("categoria/<int:categoria_id>/", views.produtos_por_categoria, name="produtos_por_categoria"),

    # Carrinho
    path("carrinho/", views.ver_carrinho, name="ver_carrinho"),
    path("carrinho/adicionar/<int:produto_id>/", views.adicionar_ao_carrinho, name="adicionar_ao_carrinho"),
    path("carrinho/remover/<int:produto_id>/", views.remover_do_carrinho, name="remover_do_carrinho"),
    path("carrinho/limpar/", views.limpar_carrinho, name="limpar_carrinho"),
    path("continuar-comprando/", views.continuar_comprando, name="continuar_comprando"),
    path("carrinho/deletar/<int:produto_id>/", views.deletar_do_carrinho, name="deletar_do_carrinho"),
    path("carrinho/atualizar/<int:produto_id>/", views.atualizar_quantidade, name="atualizar_quantidade"),
    
    # Checkout / Pedido
    path("checkout/", views.checkout, name="checkout"),
    path("pedido/<int:pedido_id>/sucesso/", views.pedido_sucesso, name="pedido_sucesso"),

]
  