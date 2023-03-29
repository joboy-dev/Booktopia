from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy

class CustomUserManager(BaseUserManager):

    def create(self, email, password, **extras):
        # check for a value in email
        if not email:
            raise ValueError(gettext_lazy('Email field cannot be empty'))

        # normalize email field
        email = self.normalize_email(email)

        # assign values to the model
        user = self.model(email=email, **extras)

        # set password
        user.set_password(password)

        # save user instance
        user.save()

        # return user instance
        return user

    def create_superuser(self, email, password, **extras):
        
        # set default values for is_active, is_staff, is_superuser
        extras.setdefault('is_active', True)
        extras.setdefault('is_staff', True)
        extras.setdefault('is_superuser', True)

        # check if is_staff and is_superuser is True
        if extras.get('is_staff') is not True:
            raise ValueError(gettext_lazy('Superuser must have is_admin=True'))

        if extras.get('is_superuser') is not True:
            raise ValueError(gettext_lazy('Superuser must have is_superuser=True'))
        
        # create user
        user = self.create(email, password, **extras)

        return user
        
