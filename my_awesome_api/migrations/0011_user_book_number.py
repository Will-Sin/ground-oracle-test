# Generated by Django 4.1.3 on 2023-02-02 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_awesome_api', '0010_user_remove_book_next_scenario'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='book_number',
            field=models.TextField(blank=True, default=''),
        ),
    ]
