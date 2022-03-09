from django.core.exceptions import ValidationError


def spaces_check(value):
    if value.split():
        raise ValidationError(
            'А кто поле будет заполнять, Пушкин?',
            params={'value': value},
        )
