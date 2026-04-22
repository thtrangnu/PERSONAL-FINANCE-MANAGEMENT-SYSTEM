from django import forms
from django.db.models import Q

from apps.accounts.models import UserProfile
from apps.expenses.models import Expense
from apps.income.models import Income
from apps.sharing.models import SharingGroup, SharedTransaction


class SharingGroupForm(forms.ModelForm):
    class Meta:
        model = SharingGroup
        fields = ('group_name', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group_name'].label = 'Tên nhóm'
        self.fields['description'].label = 'Mô tả'
        self.fields['group_name'].widget.attrs.update({'placeholder': 'Ví dụ: Gia đình, chuyến đi Đà Lạt'})


class AddMemberForm(forms.Form):
    member = forms.CharField(label='Username hoặc email thành viên')

    def clean_member(self):
        value = self.cleaned_data['member'].strip()
        user = UserProfile.objects.filter(Q(username__iexact=value) | Q(email__iexact=value)).first()
        if user is None:
            raise forms.ValidationError('Không tìm thấy người dùng này.')
        self.cleaned_data['member_profile'] = user
        return value


class SharedTransactionForm(forms.ModelForm):
    class Meta:
        model = SharedTransaction
        fields = ('expense', 'income', 'note')

    def __init__(self, *args, user_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expense'].label = 'Khoản chi muốn chia sẻ'
        self.fields['income'].label = 'Khoản thu muốn chia sẻ'
        self.fields['note'].label = 'Ghi chú'
        self.fields['expense'].required = False
        self.fields['income'].required = False
        if user_profile is not None:
            self.fields['expense'].queryset = Expense.objects.filter(user=user_profile, status=Expense.STATUS_ACTIVE).order_by('-expense_date')
            self.fields['income'].queryset = Income.objects.filter(user=user_profile, status=Income.STATUS_ACTIVE).order_by('-income_date')

    def clean(self):
        cleaned_data = super().clean()
        expense = cleaned_data.get('expense')
        income = cleaned_data.get('income')
        if bool(expense) == bool(income):
            raise forms.ValidationError('Chọn đúng một giao dịch: hoặc khoản chi, hoặc khoản thu.')
        return cleaned_data
