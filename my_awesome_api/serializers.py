from rest_framework import serializers
from rest_framework.serializers import Serializer, FileField

from .models import Book, User


class BookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = ('book_number', 'username', 'current_inquiry', 'chat_history', 'scenario_number', 'empty_placeholder')


# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
