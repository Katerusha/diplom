from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


class CustomUser(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        error_messages={'unique': 'Пользователь с таким именем уже существует.'},
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Номер телефона")
    is_email_verified = models.BooleanField('Email подтверждён', default=False)

    def __str__(self):
        return self.username