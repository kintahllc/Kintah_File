from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('Super Admin', 'Super Admin'),
        ('Root User', 'Root User'),
        ('Regular User', 'Regular User'),
        ('Technical User', 'Technical User'),
        ('Deactivate User', 'Deactivate User'),
    )
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default='Deactivate User')


