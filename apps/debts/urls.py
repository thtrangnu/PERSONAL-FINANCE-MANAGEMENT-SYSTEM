from django.urls import path

from apps.debts import views


urlpatterns = [
    path('debts/', views.debt_list, name='debt_list'),
    path('debts/new/', views.debt_create, name='debt_create'),
    path('debts/<int:debt_id>/', views.debt_detail, name='debt_detail'),
    path('debts/<int:debt_id>/payment/', views.debt_payment_create, name='debt_payment_create'),
]
