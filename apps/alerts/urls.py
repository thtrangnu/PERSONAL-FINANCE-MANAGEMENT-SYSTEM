from django.urls import path

from apps.alerts import views


urlpatterns = [
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/<int:alert_id>/read/', views.alert_mark_read, name='alert_mark_read'),
]
