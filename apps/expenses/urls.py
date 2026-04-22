from django.urls import path

from apps.expenses import views


urlpatterns = [
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/new/', views.expense_create, name='expense_create'),
    path('expenses/<int:expense_id>/edit/', views.expense_update, name='expense_update'),
    path('expenses/<int:expense_id>/delete/', views.expense_delete, name='expense_delete'),
]
