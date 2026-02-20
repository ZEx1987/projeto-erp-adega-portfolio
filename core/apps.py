from django.apps import AppConfig

class CoreConfig(AppConfig):
    # Define o tipo de chave primária padrão
    default_auto_field = 'django.db.models.BigAutoField'

    # Nome do app (tem que ser "core")
    name = 'core'