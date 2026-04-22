from copy import deepcopy
from decimal import Decimal

from django import forms


def normalize_money_string(value):
    if value in forms.Field.empty_values:
        return ''

    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return str(int(value))
        value = format(value.normalize(), 'f')

    text = str(value).strip()
    if not text:
        return ''

    negative = text.startswith('-')
    if negative:
        text = text[1:]

    if text.count('.') == 1 and text.replace('.', '').isdigit():
        left, right = text.split('.')
        if right and set(right) <= {'0'}:
            digits = left
        elif len(right) == 3 and left.isdigit():
            digits = left + right
        else:
            digits = ''.join(char for char in text if char.isdigit())
    else:
        digits = ''.join(char for char in text if char.isdigit())

    if digits:
        digits = digits.lstrip('0') or '0'

    return f'-{digits}' if negative and digits else digits


def format_money_string(value):
    normalized = normalize_money_string(value)
    if not normalized:
        return ''

    negative = normalized.startswith('-')
    digits = normalized[1:] if negative else normalized
    groups = []
    while digits:
        groups.insert(0, digits[-3:])
        digits = digits[:-3]

    return f"-{'.'.join(groups)}" if negative else '.'.join(groups)


class MoneyTextInput(forms.TextInput):
    def format_value(self, value):
        return format_money_string(value)


class MoneyDecimalField(forms.DecimalField):
    def to_python(self, value):
        normalized = normalize_money_string(value)
        if normalized in self.empty_values:
            return None
        return super().to_python(normalized)


def enable_money_input(form, field_name, placeholder='Ví dụ: 1.500.000'):
    original_field = form.fields[field_name]
    widget_attrs = deepcopy(getattr(original_field.widget, 'attrs', {}))
    widget_attrs.update({
        'data-money-input': 'true',
        'inputmode': 'numeric',
        'autocomplete': 'off',
    })
    if placeholder and not widget_attrs.get('placeholder'):
        widget_attrs['placeholder'] = placeholder

    form.fields[field_name] = MoneyDecimalField(
        max_value=getattr(original_field, 'max_value', None),
        min_value=getattr(original_field, 'min_value', None),
        max_digits=getattr(original_field, 'max_digits', None),
        decimal_places=getattr(original_field, 'decimal_places', None),
        required=original_field.required,
        label=original_field.label,
        initial=original_field.initial,
        help_text=original_field.help_text,
        disabled=original_field.disabled,
        error_messages=deepcopy(getattr(original_field, 'error_messages', {})),
        validators=list(getattr(original_field, 'validators', [])),
        widget=MoneyTextInput(attrs=widget_attrs),
    )
    return form.fields[field_name]
