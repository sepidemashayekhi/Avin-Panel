# Generated by Django 5.1 on 2024-08-28 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0008_alter_user_nationalcode_alter_user_password_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='access',
            name='AccessId',
            field=models.CharField(default=None, editable=False, max_length=50, unique=True),
        ),
        migrations.AddField(
            model_name='menu',
            name='MenuId',
            field=models.CharField(default=None, editable=False, max_length=50, unique=True),
        ),
    ]
