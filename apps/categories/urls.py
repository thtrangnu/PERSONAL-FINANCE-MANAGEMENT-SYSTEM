from django.urls import path

from apps.categories import views


urlpatterns = [
    path('categories/', views.category_list, name='category_list'),
    path('categories/new/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_update, name='category_update'),
    path('categories/<int:category_id>/toggle-status/', views.category_toggle_status, name='category_toggle_status'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
]
