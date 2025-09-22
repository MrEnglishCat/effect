import os

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from hashlib import pbkdf2_hmac
class CustomUserManager(BaseUserManager):


    # def set_password(self, raw_password):
    #     self._password = raw_password
    #
    #     salt = os.urandom(32)
    #     hasher = pbkdf2_hmac('sha256', raw_password.encode('utf-8'), salt, 100000)



    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('У пользователя должен быть email!')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUserModel(AbstractBaseUser):
    email = models.EmailField('e-mail пользователя', max_length=255, unique=True, help_text='email пользователя для идентификации.')
    first_name = models.CharField("Имя", max_length=150, blank=True, null=True, help_text='Имя пользователя.')
    middle_name = models.CharField('Отчество', max_length=150, blank=True, null=True, help_text='Отчество(если есть).')
    last_name = models.CharField('Фамилия', max_length=150, blank=True, null=True, help_text='Фамилия(если есть).')
    is_staff = models.BooleanField('Сотрудник', default=True, help_text='Указывает является ли пользователь персоналом.')
    is_superuser = models.BooleanField('Супервайзер', default=False, help_text='Указывает является ли пользователь супервазером(админом).')
    is_active = models.BooleanField('Активен', default=True, help_text='Указывает была ли учетная запись мягко удалена.')
    date_joined = models.DateTimeField('Дата регистрации', auto_now_add=True, help_text='Дара регистрации пользователя.')
    updated_at = models.DateTimeField('Дата обновления профиля', auto_now=True, help_text='Дата обновления данных пользователяЫ.')
    roles = models.ManyToManyField('auth_app.RolesModel', related_name='users', help_text='Поле для связи роли с пользователями и конкретным пользователем.', blank=True, null=True)



    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'middle_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    def get_full_name(self):
        parts = (self.last_name, self.middle_name, self.first_name)
        return " ".join(filter(None, parts))




