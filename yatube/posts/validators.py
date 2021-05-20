from django import forms


def validate_not_empty(value):
    if value == '':
        raise forms.ValidationError(
            'Поле обязательно для заполнения',
            params={'value': value},
        )
