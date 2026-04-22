from django.urls import path

from apps.bank_accounts import views


urlpatterns = [
    path('bank-accounts/', views.bank_account_list, name='bank_account_list'),
    path('bank-accounts/new/', views.bank_account_create, name='bank_account_create'),
    path('bank-accounts/<int:bank_account_id>/', views.bank_account_detail, name='bank_account_detail'),
    path('bank-accounts/<int:bank_account_id>/edit/', views.bank_account_update, name='bank_account_update'),
    path(
        'bank-accounts/<int:bank_account_id>/toggle-status/',
        views.bank_account_toggle_status,
        name='bank_account_toggle_status',
    ),
    path('bank-accounts/<int:bank_account_id>/delete/', views.bank_account_delete, name='bank_account_delete'),
]
