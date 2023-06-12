from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy
from uuid import uuid4

from .manager import CustomUserManager

# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    '''Custom user model'''

    # gender choices
    MALE = 'M'
    FEMALE = 'F'

    gender_choice = [
        (MALE, 'Male'),
        (FEMALE, 'Female')
    ]

    # user role choice
    AUTHOR = 1
    USER = 2

    role_choice = [
        (AUTHOR, 'Author'),
        (USER, 'User')
    ]

    # id = models.UUIDField(default=uuid4, primary_key=True)
    email = models.EmailField(gettext_lazy('email address'), unique=True, null=False)
    first_name = models.CharField(max_length=128, null=False)
    last_name = models.CharField(max_length=128, null=False)
    profile_pic = models.ImageField(default='profile_pics/default.png', upload_to='profile_pics', null=True)
    gender = models.CharField(choices=gender_choice, max_length=1, default=MALE, null=False)
    role = models.IntegerField(choices=role_choice, default=USER, null=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
