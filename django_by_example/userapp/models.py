from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    image = models.ImageField(upload_to='users_image', blank=True)
    description = models.CharField(max_length=150)
    age = models.PositiveIntegerField(default=None, null=True)
    created = models.DateTimeField(verbose_name='дата создания', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='дата обновления', auto_now=True)
