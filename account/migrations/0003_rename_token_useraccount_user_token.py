# Generated by Django 5.1.3 on 2024-11-13 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_rename_user_pwd_token_useraccount_token'),
    ]

    operations = [
        migrations.RenameField(
            model_name='useraccount',
            old_name='token',
            new_name='user_token',
        ),
    ]
