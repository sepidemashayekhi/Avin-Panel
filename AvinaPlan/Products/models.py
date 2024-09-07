from django.db import models


class Setting(models.Model):
    Title = models.CharField(max_length=50)
    Value = models.BooleanField(default=False)

