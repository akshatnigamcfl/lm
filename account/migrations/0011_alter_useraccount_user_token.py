# Generated by Django 5.1.3 on 2024-11-15 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_alter_useraccount_user_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='user_token',
            field=models.CharField(blank=True, default='QXmGqEoqkUHYgvyKQ7KJ4JbZE', max_length=300),
        ),
    ]
