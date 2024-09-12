from django.db import models

from config import to_roman_numeral

class Setting(models.Model):
    Title = models.CharField(max_length=50)
    Value = models.BooleanField(default=False)


class Category(models.Model):
    CategoryId = models.CharField(max_length=50, unique=True, editable=False, default=None)
    Title = models.CharField(max_length=50, null=False, default=None)
    ParentId = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        if not self.CategoryId:
            last_id = Category.objects.all().aggregate(largest=models.Max('id'))['largest']
            next_id = 1 if last_id is None else last_id + 1
            self.CategoryId = to_roman_numeral(next_id)
        super(Category, self).save(*args, **kwargs)


class Products(models.Model):
    ProductId = models.CharField(max_length=50, unique=True, editable=False, default=None)
    Title = models.CharField(max_length=50, null=False, blank=False, default=None)
    CategoryId = models.ForeignKey(Category, on_delete=models.CASCADE, default=None)
    Price = models.FloatField(null=False)
    Quantity = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        if not self.CategoryId:
            last_id = Products.objects.all().aggregate(largest=models.Max('id'))['largest']
            next_id = 1 if last_id is None else last_id + 1
            self.ProductId = to_roman_numeral(next_id)
        super(Products, self).save(*args, **kwargs)


class Units(models.Model):
    UnitId = models.CharField(max_length=50, unique=True, editable=False, default=None)
    Title = models.CharField(max_length=50, null=False)

    def save(self, *args, **kwargs):
        if not self.UnitId:
            last_id = Units.objects.all().aggregate(largest=models.Max('id'))['largest']
            next_id = 1 if last_id is None else last_id + 1
            self.UnitId = to_roman_numeral(next_id)
        super(Units, self).save(*args, **kwargs)

class ProductsUnit(models.Model):

    UnitId = models.ForeignKey(Units, on_delete=models.CASCADE, null=True)
    ProductId = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    Coefficient = models.IntegerField()
    IsDefault = models.BooleanField(default=False)
    IsPrimary = models.BooleanField(default=False)

