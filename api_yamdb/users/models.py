from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLES = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin')
    )

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=ROLES, default='user')
