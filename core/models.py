from django.db import models

class Cliente(models.Model):
    # Nome completo do cliente
    nome = models.CharField(max_length=150)

    # Email do cliente (único no sistema)
    email = models.EmailField(unique=True)

    # Telefone de contato (opcional)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    # Data de criação do registro (automática)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Exibição do cliente no admin
        return self.nome

class Categoria(models.Model):
    # Nome da categoria (ex: Cervejas, Vinhos, Destilados)
    nome = models.CharField(max_length=100, unique=True)

    # Data de criação automática
    criado_em = models.DateTimeField(auto_now_add=True)

        # Imagem da categoria (upload no admin)
    imagem = models.ImageField(
        upload_to="categorias/",   # Pasta dentro de /media/
        blank=True,                # Permite categoria sem imagem
        null=True                  # Permite salvar no banco como vazio
    )
    def __str__(self):
        # Exibição da categoria no admin
        return self.nome    

class Produto(models.Model):
    # Nome do produto (ex: Heineken 350ml)
    nome = models.CharField(max_length=150)

    # Categoria do produto (relacionamento)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,  # Impede apagar categoria se existir produto vinculado
        related_name="produtos"
    )

    # Custo do produto (quanto você paga para ter ele em estoque)
    # Usamos DecimalField para valores monetários
    custo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Preço de venda (quanto o cliente paga)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    # Quantidade disponível em estoque (simples por enquanto)
    estoque_atual = models.PositiveIntegerField(default=0)

    # Indica se o produto aparece no catálogo da loja
    ativo = models.BooleanField(default=True)

    # Data de criação automática
    criado_em = models.DateTimeField(auto_now_add=True)

    # ✅ Imagem do produto 
    imagem = models . ImageField (upload_to = "produtos/", blank = True, null = True)   
    # salva em media/produtos/ blank = True , null = True     ) 
    # Dados de criação 
    criado_em = models . DateTimeField( auto_now_add = True ) 

    def __str__(self):
        # Exibição do produto no admin
        return self.nome
    
    @property
    def lucro_unitario(self):
        # Calcula lucro por unidade vendida (preço - custo)
        return self.preco - self.custo

class Pedido(models.Model):
    # Status do pedido (controle do processo interno)
    STATUS_CHOICES = [
        ("RECEBIDO", "Recebido"),
        ("PAGO", "Pago"),
        ("SEPARANDO", "Separando"),
        ("ENVIADO", "Enviado"),
        ("ENTREGUE", "Entregue"),
        ("CANCELADO", "Cancelado"),
    ]

    # Dados básicos do cliente (sem login por enquanto)
    nome_cliente = models.CharField(max_length=150)
    telefone_cliente = models.CharField(max_length=20)
    endereco_entrega = models.TextField()

    # Status inicial do pedido
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="RECEBIDO")

    # Totais “congelados” no momento do pedido (boas práticas)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lucro_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Datas de controle
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Exibição do pedido no admin
        return f"Pedido #{self.id} - {self.nome_cliente}"


class ItemPedido(models.Model):
    # Pedido pai
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="itens"
    )

    # Produto comprado
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT
    )

    # Quantidade comprada
    quantidade = models.PositiveIntegerField(default=1)

    # Preço e custo “congelados” no momento do pedido
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def subtotal(self):
        # Retorna subtotal (preço * quantidade)
        return self.preco_unitario * self.quantidade

    def lucro_item(self):
        # Retorna lucro do item ((preço - custo) * quantidade)
        return (self.preco_unitario - self.custo_unitario) * self.quantidade

    def __str__(self):
        # Exibição no admin
        return f"{self.quantidade}x {self.produto.nome}"    


