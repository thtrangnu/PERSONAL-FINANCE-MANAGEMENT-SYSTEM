from django.db import models


class UserProfile(models.Model):
    ROLE_USER = 'user'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_USER, 'User'),
        (ROLE_ADMIN, 'Admin'),
    ]

    user_id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar_url = models.CharField(max_length=500, blank=True, null=True)
    default_currency = models.CharField(max_length=10, blank=True, null=True, default='VND')
    timezone = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    is_active = models.BooleanField(default=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['role'], name='idx_users_role'),
            models.Index(fields=['is_active'], name='idx_users_is_active'),
        ]
        verbose_name = 'user profile'
        verbose_name_plural = 'user profiles'

    def __str__(self):
        return self.username
