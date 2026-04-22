from django.urls import path

from apps.accounts import views


urlpatterns = [
    path('login/', views.AccountLoginView.as_view(), name='login'),
    path('login/google/', views.google_login_start, name='google_login_start'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/avatar/', views.profile_avatar_upload, name='profile_avatar_upload'),
    path('media/avatars/<path:avatar_path>', views.avatar_file, name='avatar_file'),
]
