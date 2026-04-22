from django import forms

from apps.categories.models import ExpenseCategory


class CategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = (
            'category_name',
            'category_type',
            'description',
            'is_active',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category_name'].label = 'Tên danh mục'
        self.fields['category_type'].label = 'Loại danh mục'
        self.fields['description'].label = 'Mô tả'
        self.fields['is_active'].label = 'Trạng thái sử dụng'
        self.fields['category_type'].choices = [
            (ExpenseCategory.TYPE_EXPENSE, 'Chi tiêu'),
            (ExpenseCategory.TYPE_INCOME, 'Thu nhập'),
            (ExpenseCategory.TYPE_BOTH, 'Cả thu và chi'),
        ]
        self.fields['category_name'].widget.attrs.update({
            'placeholder': 'Ví dụ: Ăn uống, Lương, Mua sắm',
        })
        self.fields['description'].widget.attrs.update({
            'placeholder': 'Ghi chú ngắn về danh mục này',
        })
        self.fields['is_active'].widget.attrs.update({
            'class': 'form-switch-input',
            'data-form-switch-input': '',
        })

    def clean_category_name(self):
        return self.cleaned_data['category_name'].strip()
