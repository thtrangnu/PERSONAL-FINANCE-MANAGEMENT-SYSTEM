from django import forms
from django.db.models import Q

from apps.form_utils import enable_money_input
from apps.bank_accounts.models import BankAccount
from apps.categories.models import ExpenseCategory
from apps.income.models import Income


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = (
            'title',
            'category',
            'bank_account',
            'amount',
            'income_date',
            'description',
            'note',
        )
        widgets = {
            'income_date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_profile = user_profile
        enable_money_input(self, 'amount')
        self.fields['title'].label = 'Tên khoản thu'
        self.fields['category'].label = 'Danh mục'
        self.fields['bank_account'].label = 'Tài khoản nhận tiền'
        self.fields['amount'].label = 'Số tiền'
        self.fields['income_date'].label = 'Ngày nhận'
        self.fields['description'].label = 'Mô tả'
        self.fields['note'].label = 'Ghi chú'
        self.fields['title'].widget.attrs.update({'placeholder': 'Ví dụ: Lương tháng, thưởng, freelance'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Mô tả ngắn nếu cần'})
        if user_profile is not None:
            self.fields['category'].queryset = ExpenseCategory.objects.filter(
                Q(user=user_profile) | Q(user__isnull=True),
                category_type__in=[ExpenseCategory.TYPE_INCOME, ExpenseCategory.TYPE_BOTH],
                is_active=True,
            ).order_by('category_name')
            self.fields['bank_account'].queryset = BankAccount.objects.filter(
                user=user_profile,
                is_active=True,
            ).order_by('account_name')
        self.fields['bank_account'].required = False

    def clean_title(self):
        return self.cleaned_data['title'].strip()
