from django import forms

from apps.form_utils import enable_money_input
from apps.bank_accounts.models import BankAccount


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = (
            'account_name',
            'account_type',
            'provider_name',
            'opening_balance',
            'current_balance',
            'note',
            'is_active',
        )

    def __init__(self, *args, show_balance_split=True, **kwargs):
        self.show_balance_split = show_balance_split
        super().__init__(*args, **kwargs)
        enable_money_input(self, 'opening_balance', 'Ví dụ: 8.000.000')
        self.fields['account_name'].label = 'Tên tài khoản'
        self.fields['account_type'].label = 'Loại tài khoản'
        self.fields['provider_name'].label = 'Ngân hàng / ví'
        self.fields['opening_balance'].label = 'Số dư ban đầu' if show_balance_split else 'Số dư'
        self.fields['note'].label = 'Ghi chú'
        self.fields['is_active'].label = 'Trạng thái sử dụng'
        if show_balance_split:
            enable_money_input(self, 'current_balance', 'Ví dụ: 10.500.000')
            self.fields['current_balance'].label = 'Số dư hiện tại'
            self.fields['current_balance'].required = False
        else:
            self.fields.pop('current_balance')
        self.fields['account_type'].choices = [
            (BankAccount.TYPE_BANK, 'Tài khoản ngân hàng'),
            (BankAccount.TYPE_CASH, 'Tiền mặt'),
            (BankAccount.TYPE_E_WALLET, 'Ví điện tử'),
            (BankAccount.TYPE_OTHER, 'Khác'),
        ]
        self.fields['account_name'].widget.attrs.update({
            'placeholder': 'Ví dụ: Vietcombank chính, Ví MoMo, Tiền mặt',
        })
        self.fields['provider_name'].widget.attrs.update({
            'placeholder': 'Ví dụ: Vietcombank, MoMo, ZaloPay',
        })
        self.fields['is_active'].widget.attrs.update({
            'class': 'form-switch-input',
            'data-form-switch-input': '',
        })

    def clean_account_name(self):
        return self.cleaned_data['account_name'].strip()

    def clean(self):
        cleaned_data = super().clean()
        if 'current_balance' in self.fields and cleaned_data.get('current_balance') is None:
            cleaned_data['current_balance'] = cleaned_data.get('opening_balance') or 0
        return cleaned_data

    def save(self, commit=True):
        account = super().save(commit=False)
        if not self.show_balance_split:
            account.current_balance = account.opening_balance or 0
        if commit:
            account.save()
            self.save_m2m()
        return account
