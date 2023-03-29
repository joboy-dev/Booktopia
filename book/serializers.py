from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Book

# user model
User = get_user_model()

class AddBookSerializer(serializers.ModelSerializer):

    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Book
        fields = '__all__'

    def validate(self, data):
        if len(data['title']) < 4:
            raise serializers.ValidationError({'message': 'This field must have at least four characters'})