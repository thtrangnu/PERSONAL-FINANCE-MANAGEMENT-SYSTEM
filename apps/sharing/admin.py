from django.contrib import admin

from apps.sharing.models import GroupMember, SharedTransaction, SharingGroup


@admin.register(SharingGroup)
class SharingGroupAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'group_name', 'owner_user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('group_name', 'description')


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('group_member_id', 'group', 'user', 'member_role', 'status')
    list_filter = ('member_role', 'status')


@admin.register(SharedTransaction)
class SharedTransactionAdmin(admin.ModelAdmin):
    list_display = ('shared_transaction_id', 'group', 'shared_by_user', 'visibility_status', 'created_at')
    list_filter = ('visibility_status',)
