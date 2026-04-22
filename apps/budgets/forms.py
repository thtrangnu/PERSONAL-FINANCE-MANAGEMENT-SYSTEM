from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import construct_instance
from django.db.models import Q
from django.utils import timezone

from apps.form_utils import enable_money_input
from apps.budgets.models import Budget
from apps.categories.models import ExpenseCategory


class BudgetForm(forms.ModelForm):
    period_month = forms.TypedChoiceField(
        coerce=int,
        choices=[(month, f'Tháng {month}') for month in range(1, 13)],
    )

    class Meta:
        model = Budget
        fields = (
            'budget_name',
            'budget_scope',
            'category',
            'period_month',
            'period_year',
            'spending_limit',
            'warning_percent',
            'status',
        )

    def __init__(self, *args, user_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date()
        self.user_profile = user_profile
        if user_profile is not None and not self.instance.pk:
            self.instance.user = user_profile
        enable_money_input(self, 'spending_limit', 'Ví dụ: 12.000.000')
        self.fields['budget_name'].label = 'Tên ngân sách'
        self.fields['budget_scope'].label = 'Kiểu ngân sách'
        self.fields['category'].label = 'Danh mục áp dụng'
        self.fields['period_month'].label = 'Tháng'
        self.fields['period_year'].label = 'Năm'
        self.fields['spending_limit'].label = 'Hạn mức'
        self.fields['warning_percent'].label = 'Cảnh báo khi đạt (%)'
        self.fields['status'].label = 'Trạng thái'
        self.fields['budget_scope'].choices = [
            (Budget.SCOPE_OVERALL, 'Ngân sách tổng'),
            (Budget.SCOPE_CATEGORY, 'Ngân sách theo danh mục'),
        ]
        self.fields['status'].choices = [
            (Budget.STATUS_ACTIVE, 'Đang dùng'),
            (Budget.STATUS_INACTIVE, 'Tạm tắt'),
            (Budget.STATUS_CLOSED, 'Đã đóng'),
        ]
        self.fields['period_year'].initial = self.fields['period_year'].initial or today.year
        self.fields['period_year'].widget.attrs.update({'min': today.year - 5, 'max': today.year + 5})
        self.fields['warning_percent'].initial = self.fields['warning_percent'].initial or 80
        self.fields['budget_name'].widget.attrs.update({'placeholder': 'Ví dụ: Ngân sách tháng này'})
        self.fields['status'].widget.attrs.update({
            'class': 'form-status-select',
            'data-status-select': '',
        })
        self.fields['category'].required = False
        if user_profile is not None:
            self.fields['category'].queryset = ExpenseCategory.objects.filter(
                Q(user=user_profile) | Q(user__isnull=True),
                category_type__in=[ExpenseCategory.TYPE_EXPENSE, ExpenseCategory.TYPE_BOTH],
                is_active=True,
            ).order_by('category_name')

    def clean_budget_name(self):
        return self.cleaned_data['budget_name'].strip()

    def clean_spending_limit(self):
        value = self.cleaned_data['spending_limit']
        if value is not None and value <= 0:
            raise forms.ValidationError('Hạn mức phải lớn hơn 0.')
        return value

    def clean_warning_percent(self):
        value = self.cleaned_data['warning_percent']
        if value is not None and (value <= 0 or value > 100):
            raise forms.ValidationError('Cảnh báo phải nằm trong khoảng từ 1 đến 100.')
        return value

    def clean(self):
        cleaned_data = super().clean()
        budget_scope = cleaned_data.get('budget_scope')
        category = cleaned_data.get('category')
        if budget_scope == Budget.SCOPE_CATEGORY and category is None:
            self.add_error('category', 'Vui lòng chọn danh mục cho ngân sách theo danh mục.')
        if budget_scope == Budget.SCOPE_OVERALL:
            cleaned_data['category'] = None
        return cleaned_data

    def _post_clean(self):
        opts = self._meta
        exclude = self._get_validation_exclusions()

        try:
            self.instance = construct_instance(self, self.instance, opts.fields, opts.exclude)
        except ValidationError as error:
            self._update_errors(error)

        try:
            self.instance.full_clean(
                exclude=exclude,
                validate_unique=False,
                validate_constraints=False,
            )
        except ValidationError as error:
            self._update_errors(error)

        if self._validate_unique:
            self.validate_unique()
