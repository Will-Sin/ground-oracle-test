from django.db import models


class Book(models.Model):
    book_number = models.TextField()
    chat_history = models.TextField(blank=True, default="")
    full_chat_history = models.TextField(blank=True, default="")


class User(models.Model):
    CAVE_OPTIONS = [
            ('GREEN', 'GREEN'),
            ('BEAUTY', 'BEAUTY'),
            ('RAGE', 'RAGE'),
            ('BODY', 'BODY'),
            ('FAITH', 'FAITH'),
            ('KNOWLEDGE', 'KNOWLEDGE'),
            ('DISORDER', 'DISORDER')
        ]
    cave = models.TextField(choices=CAVE_OPTIONS, default="GREEN")
    book_number = models.TextField(blank=True, default="")
    interactions_available = models.IntegerField(default='0')
    next_scenario = models.IntegerField(default='0')
    file = models.FileField(blank=True, null=False)


class PackageForm(models.Model):
    hope = models.TextField(blank=True, default="")
    fear = models.TextField(blank=True, default="")


class Prompts(models.Model):
    prompt_1 = models.TextField()
    prompt_2 = models.TextField()


"""
USER: Inquiry, Chat_History
RECEIVES: Response, Chat_History

BOOK:
    Book ID
    USER:
        User ID
        Chat History
     
"""