from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Permite buscar um valor em um dicionário usando uma chave variável no template.
    Uso: {{ dicionario|get_item:chave_variavel }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)