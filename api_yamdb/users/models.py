from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb.settings import ADMIN, MODERATOR


CHOICES = (
    ('admin', 'администратор'),
    ('moderator', 'модератор'),
    ('user', 'пользователь'),
)


class User(AbstractUser):
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.TextField(
        choices=CHOICES,
        default='user',
    )
    email = models.EmailField(unique=True, max_length=254)
    password = models.CharField(blank=True, max_length=50)

    @property
    def is_admin(self):
        return (
            self.role == ADMIN or self.is_staff
        )

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username
