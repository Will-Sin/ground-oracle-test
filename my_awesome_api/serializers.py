from rest_framework import serializers

from .models import Book


class BookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = ('book_number', 'username', 'current_inquiry', 'chat_history', 'scenario_number', 'empty_placeholder')