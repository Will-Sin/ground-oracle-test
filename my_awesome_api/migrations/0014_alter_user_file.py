# Generated by Django 4.1.3 on 2023-03-01 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_awesome_api', '0013_user_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='file',
            field=models.FileField(blank=True, upload_to=''),
        ),
    ]
