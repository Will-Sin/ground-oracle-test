# Generated by Django 4.1.3 on 2022-11-11 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_number', models.IntegerField()),
                ('chat_history', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Prompts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt_1', models.TextField()),
                ('prompt_2', models.TextField()),
            ],
        ),
    ]
