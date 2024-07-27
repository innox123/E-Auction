from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    phone_number = models.CharField(_('phone number'),max_length=13, unique=True)
    is_verified = models.BooleanField(default=False)
    has_mfa = models.BooleanField(default=False)
    address = models.CharField(_('address'),max_length=100)
    avatar = models.ImageField(default='images.jpg', upload_to='uploads/avatars/')
    id_card = models.FileField(upload_to='uploads/id_cards/')

    def __str__(self):
        return self.username
    


