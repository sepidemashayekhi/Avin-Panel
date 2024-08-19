from django.db import models
from django.contrib.auth.hashers import make_password

from config.tools import to_roman_numeral


class User(models.Model):

    class UserManager(models.Manager):

        def create_user(self, NationalCode, Password):
            if self.filter(NationalCode=NationalCode).first():
               return False
            hashed_pwd = make_password(password=Password)
            user = self.model(NationalCode=NationalCode, Password=hashed_pwd, Active=False)
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


