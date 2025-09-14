from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css):
    """Добавляет CSS-класс к полю формы Django"""
    return field.as_widget(attrs={"class": css})
