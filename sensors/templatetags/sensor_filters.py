from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter สำหรับดึงค่าจาก dictionary"""
    return dictionary.get(key)
