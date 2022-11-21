from django.db import models

from django.db import models


class Book(models.Model):
    book_number = models.IntegerField()
    scenario_number = models.IntegerField()
    username = models.TextField()
    chat_history = models.TextField()
    current_inquiry = models.TextField()
    empty_placeholder = models.TextField()


class Prompts(models.Model):
    prompt_1 = models.TextField()
    prompt_2 = models.TextField()