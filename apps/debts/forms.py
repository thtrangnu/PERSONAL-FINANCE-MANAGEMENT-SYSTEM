from django import forms

from apps.form_utils import enable_money_input
from apps.bank_accounts.models import BankAccount
from apps.debts.models import Debt, DebtPayment


class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = (
            'debt_type',
            'counterparty_name',
            'original_amount',
            'due_date',
            'description',
            'note',
        )
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        enable_money_input(self, 'original_amount', 'Ví dụ: 5.000.000')
        self.fields['debt_type'].label = 'Loại khoản nợ'
        self.fields['counterparty_name'].label = 'Người / bên liên quan'
        self.fields['original_amount'].label = 'Số tiền ban đầu'
        self.fields['due_date'].label = 'Hạn trả'
        self.fields['description'].label = 'Mô tả'
        self.fields['note'].label = 'Ghi chú'
        self.fields['counterparty_name'].widget.attrs.update({'placeholder': 'Ví dụ: An, chị Linh, khoản vay xe'})

    def clean_counterparty_name(self):
        return self.cleaned_data['counterparty_name'].strip()


class DebtPaymentForm(forms.ModelForm):
    class Meta:
        model = DebtPayment
        fields = ('bank_account', 'payment_date', 'amount', 'note')
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user_profile=None, debt=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.debt = debt
        enable_money_input(self, 'amount')
        self.fields['bank_account'].label = 'Tài khoản thanh toán'
        self.fields['bank_account'].empty_label = 'Chọn tài khoản đã thêm'
        self.fields['bank_account'].error_messages['required'] = 'Vui lòng chọn tài khoản thanh toán.'
        self.fields['bank_account'].help_text = 'Bắt buộc chọn tài khoản đang dùng để hệ thống cập nhật số dư.'
        self.fields['payment_date'].label = 'Ngày thanh toán'
        self.fields['amount'].label = 'Số tiền'
        self.fields['note'].label = 'Ghi chú'
        self.fields['bank_account'].required = True
        self.fields['bank_account'].queryset = BankAccount.objects.none()
        self.fields['amount'].widget.attrs.update({
            'min': '0.01',
            'step': '0.01',
            'placeholder': 'Nhập số tiền muốn thanh toán',
            'data-payment-amount': 'true',
        })
        if debt is not None:
            self.fields['amount'].widget.attrs['max'] = f'{debt.remaining_amount:.2f}'
            self.fields['amount'].help_text = 'Số tiền không được lớn hơn khoản còn lại.'
        if user_profile is not None:
            self.fields['bank_account'].queryset = BankAccount.objects.filter(
                user=user_profile,
                is_active=True,
            ).order_by('account_name')

    def clean_bank_account(self):
        bank_account = self.cleaned_data['bank_account']
        if not bank_account.is_active:
            raise forms.ValidationError('Tài khoản thanh toán này hiện không còn được sử dụng.')
        return bank_account

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.debt is not None and amount > self.debt.remaining_amount:
            raise forms.ValidationError('Số tiền thanh toán không được lớn hơn khoản còn lại.')
        return amount
