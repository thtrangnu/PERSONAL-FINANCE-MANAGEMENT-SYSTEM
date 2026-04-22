from django.contrib import admin

from apps.accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'email', 'full_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'default_currency')
    search_fields = ('username', 'email', 'full_name', 'phone_number')
    ordering = ('user_id',)
