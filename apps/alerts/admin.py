from django.contrib import admin

from apps.alerts.models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('alert_id', 'user', 'alert_type', 'severity', 'title', 'is_read', 'created_at')
    list_filter = ('alert_type', 'severity', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    ordering = ('-created_at', '-alert_id')
