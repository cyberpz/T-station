from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    email_confirmed = models.BooleanField(default=False)


    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="customuser",
    )
    
    # Override the user_permissions field and provide a custom related_name
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_user_permissions",
        related_query_name="customuser_permission",
    )

    objects = CustomUserManager()