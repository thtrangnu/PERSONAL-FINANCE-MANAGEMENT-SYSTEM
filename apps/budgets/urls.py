from django.urls import path

from apps.budgets import views


urlpatterns = [
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/new/', views.budget_create, name='budget_create'),
    path('budgets/<int:budget_id>/edit/', views.budget_update, name='budget_update'),
    path('budgets/<int:budget_id>/toggle-status/', views.budget_toggle_status, name='budget_toggle_status'),
    path('budgets/<int:budget_id>/delete/', views.budget_delete, name='budget_delete'),
]
