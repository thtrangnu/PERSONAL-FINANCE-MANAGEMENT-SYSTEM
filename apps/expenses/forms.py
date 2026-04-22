from django import forms
from django.db.models import Q

from apps.form_utils import enable_money_input
from apps.bank_accounts.models import BankAccount
from apps.categories.models import ExpenseCategory
from apps.expenses.models import Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = (
            'category',
            'bank_account',
            'amount',
            'expense_date',
            'payment_method',
            'description',
            'note',
        )
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_profile = user_profile
        enable_money_input(self, 'amount')
        self.fields['category'].label = 'Danh mục chi'
        self.fields['bank_account'].label = 'Tài khoản thanh toán'
        self.fields['amount'].label = 'Số tiền'
        self.fields['expense_date'].label = 'Ngày chi'
        self.fields['payment_method'].label = 'Cách thanh toán'
        self.fields['description'].label = 'Mô tả'
        self.fields['note'].label = 'Ghi chú'
        self.fields['payment_method'].choices = [
            ('', 'Chọn cách thanh toán'),
            (Expense.METHOD_CASH, 'Tiền mặt'),
            (Expense.METHOD_BANK, 'Chuyển khoản'),
            (Expense.METHOD_E_WALLET, 'Ví điện tử'),
            (Expense.METHOD_CREDIT_CARD, 'Thẻ tín dụng'),
            (Expense.METHOD_OTHER, 'Khác'),
        ]
        self.fields['description'].widget.attrs.update({'placeholder': 'Ví dụ: ăn trưa, mua sách, đổ xăng'})
        if user_profile is not None:
            self.fields['category'].queryset = ExpenseCategory.objects.filter(
                Q(user=user_profile) | Q(user__isnull=True),
                category_type__in=[ExpenseCategory.TYPE_EXPENSE, ExpenseCategory.TYPE_BOTH],
                is_active=True,
            ).order_by('category_name')
            self.fields['bank_account'].queryset = BankAccount.objects.filter(
                user=user_profile,
                is_active=True,
            ).order_by('account_name')
        self.fields['bank_account'].required = False
        self.fields['payment_method'].required = False
