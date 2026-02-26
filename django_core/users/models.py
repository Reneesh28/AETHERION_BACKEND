from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User Model for Aetherion Governance Layer.
    Extends Django AbstractUser.
    No additional fields added yet.
    """
    pass