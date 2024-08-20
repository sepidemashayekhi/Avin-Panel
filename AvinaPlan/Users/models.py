from django.db import models
from django.contrib.auth.hashers import make_password, check_password

from config.tools import to_roman_numeral

from django_otp.plugins.otp_totp.models import key_validator, default_key
from django_otp.oath import TOTP

from binascii import unhexlify
import time

class User(models.Model):

    class UserManager(models.Manager):

        def create_user(self, NationalCode, Password):
            if self.filter(NationalCode=NationalCode).first():
               return False
            hashed_pwd = make_password(password=Password)
            user = self.model(NationalCode=NationalCode, Password=hashed_pwd, Active=False)
            return user

        def check_user_pass(self, NationalCode, Password):
            user = self.filter(NationalCode=NationalCode,Active=True).first()
            if not user:
                return False
            if not check_password(password=Password,encoded=user.Password):
                return False
            return user


    UserId = models.CharField(max_length=50, unique=True, editable=False)
    FullName = models.CharField(max_length=150, null=True, blank=True)
    NationalCode = models.CharField(max_length=15, null=False, blank=False, unique=True)
    PhoneNumber = models.CharField(max_length=15, null=True)
    Password = models.CharField(max_length=50, null=False, blank=False, default=None)
    Active = models.BooleanField(default=False)
    CreatedAt = models.DateTimeField(null=True)
    UpdateAt = models.DateTimeField(null=True)
    IsAdmin = models.BooleanField(default=False)

    objects = UserManager()



    def save(self, *args, **kwargs):
        if not self.UserId:
            last_id = User.objects.all().aggregate(largest=models.Max('id'))['largest']
            next_id = 1 if last_id is None else last_id + 1
            self.UserId = to_roman_numeral(next_id)
        super(User, self).save(*args, **kwargs)

class Flag(models.Model):
    Title = models.CharField(max_length=50, null=False)
    Priority = models.IntegerField(null=False)

class Menu(models.Model):
    Title = models.CharField(max_length=80)
    FlagId = models.ForeignKey(Flag, on_delete=models.SET_NULL, null=True)

class Access(models.Model):
    Title = models.CharField(max_length=50)

class UserAccess(models.Model):
    MenuId = models.ForeignKey(Menu, on_delete=models.CASCADE)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    AccessId = models.ForeignKey(Access, on_delete=models.CASCADE)
    UrlPath = models.CharField(max_length=100, null=True)

    def save(self, *args, **kwargs):
        if not self.UrlPath:
            self.UrlPath = f'/{self.MenuId.Title}/{self.AccessId.Title}'
        super(UserAccess, self).save(*args, **kwargs)

class MyTOTPDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    key = models.CharField(
        max_length=80,
        validators=[key_validator],
        default=default_key,
        help_text="A hex-encoded secret key of up to 40 bytes.",
    )
    step = models.PositiveSmallIntegerField(
        default=30, help_text="The time step in seconds."
    )
    digits = models.PositiveSmallIntegerField(
        choices=[(6, 6), (8, 8)],
        default=6,
        help_text="The number of digits to expect in a token.",
    )
    tolerance = models.PositiveSmallIntegerField(
        default=1, help_text="The number of time steps in the past or future to allow."
    )
    drift = models.SmallIntegerField(
        default=0,
        help_text="The number of time steps the prover is known to deviate from our clock.",
    )
    last_t = models.BigIntegerField(
        default=-1,
        help_text="The t value of the latest verified token. The next token must be at a higher time step.",
    )
    t0 = models.BigIntegerField(
        default=0, help_text="The Unix time at which to begin counting steps."
    )

    @property
    def bin_key(self):
        return unhexlify(self.key.encode())

    def verify_token(self, token):
        try:
            token = int(token)
        except Exception:
            verified = False
        else:
            if self.tolerance > 1:
                return False
            key = self.bin_key

            totp = TOTP(key, self.step, self.t0, self.digits, self.drift)
            totp.time = time.time()

            verified = totp.verify(token, self.tolerance, self.last_t + 1)
            if not verified:
                verified = False
            self.tolerance = self.tolerance+1
            self.save()
        return verified

