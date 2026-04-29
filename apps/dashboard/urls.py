from django.urls import path

from apps.dashboard import views


urlpatterns = [
    path('healthz/', views.healthz, name='healthz'),
    path('metrics', views.metrics, name='metrics'),
    path('metrics/', views.metrics, name='metrics_slash'),
    path('policies/legal/', views.legal_policy, name='legal_policy'),
    path('policies/user/', views.user_policy, name='user_policy'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
