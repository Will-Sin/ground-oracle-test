# Generated by Django 4.1.3 on 2023-01-10 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_awesome_api', '0005_book_empty_placeholder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='current_inquiry',
        ),
        migrations.RemoveField(
            model_name='book',
            name='empty_placeholder',
        ),
        migrations.RemoveField(
            model_name='book',
            name='scenario_number',
        ),
        migrations.RemoveField(
            model_name='book',
            name='username',
        ),
    ]
