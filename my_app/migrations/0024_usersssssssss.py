# Generated by Django 5.0.3 on 2024-04-29 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0023_rename_in_level_rdetail_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usersssssssss',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False, unique=True)),
                ('password', models.CharField(default='0', max_length=100)),
            ],
            options={
                'db_table': 'Usersssssssss',
            },
        ),
    ]
