from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime
import pytz

utc=pytz.UTC


class UserManager(BaseUserManager):
    def create_user(self, wallet, password, **extra_fields):
        if not wallet:
            raise ValueError('user must have wallet')
        
        user = self.model(wallet=wallet, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, wallet, password, **other_fields):
        if not wallet:
            raise ValueError('user must have wallet')
        
        user = self.create_user(
            wallet=wallet,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    wallet = models.CharField(max_length=80, unique=True)
    true_wallet = models.CharField(max_length=80)
    private_key = models.CharField(max_length=80)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "wallet"
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    class Meta:
        ordering = ['-wallet']
    
    def __str__(self):
        return self.wallet


class UserOperation(models.Model):
    class OperationType(models.TextChoices):
        REPLENISHMENT = 'RE', _('Replenishment'),
        PURCHASE = 'PU', _('Purchase'),
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    op_type = models.CharField(
        max_length=2,
        choices=OperationType.choices,
        default='RE', # TODO Remove default value
    )
    desc = models.CharField(max_length=30)
    performed = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-performed']


class Token(models.Model):
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=30, default="33333333333333333")
    last_id = models.IntegerField(default=1)


# TokenSeries
class TokenSeries(models.Model):
    left_id = models.IntegerField()
    right_id = models.IntegerField()
    last_id = models.IntegerField()
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    number_of_tokens = models.IntegerField()
    created = models.DateTimeField(auto_now=True)
    cost = models.IntegerField()
    metainfo = models.TextField(default="")
    expiration_datetime = models.DateTimeField(default=None)
    dividends = models.IntegerField(default=0) # number of percents

    class Meta:
        ordering = ['-name']
    

class PackOfTokens(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token_series = models.ForeignKey(TokenSeries, on_delete=models.CASCADE)
    number_of_tokens = models.IntegerField()
    left_id = models.IntegerField()
    right_id = models.IntegerField()
