from django.urls import path

from apps.sharing import views


urlpatterns = [
    path('sharing/', views.group_list, name='sharing_group_list'),
    path('sharing/new/', views.group_create, name='sharing_group_create'),
    path('sharing/<int:group_id>/', views.group_detail, name='sharing_group_detail'),
    path('sharing/<int:group_id>/members/add/', views.group_member_add, name='sharing_member_add'),
    path('sharing/invitations/<int:membership_id>/accept/', views.group_invitation_accept, name='sharing_invitation_accept'),
    path('sharing/invitations/<int:membership_id>/decline/', views.group_invitation_decline, name='sharing_invitation_decline'),
    path('sharing/<int:group_id>/transactions/add/', views.shared_transaction_create, name='shared_transaction_create'),
]
