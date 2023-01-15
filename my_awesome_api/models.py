from django.db import models


class Book(models.Model):
    book_number = models.TextField()
    chat_history = models.TextField(blank=True, default="")
    next_scenario = models.IntegerField(default='0')


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