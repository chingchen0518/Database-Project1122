# Generated by Django 5.0.3 on 2024-04-29 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0027_usersssssssss'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersssssssss',
            name='name',
            field=models.CharField(default='0', max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='usersssssssss',
            name='name2',
            field=models.CharField(default='0', max_length=100, unique=True),
        ),
    ]
