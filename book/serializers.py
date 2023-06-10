from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Book

# user model
User = get_user_model()

class AddBookSerializer(serializers.ModelSerializer):
    '''
        Serializer for authors to add their books
    '''

    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['created', 'updated']

    def validate(self, data):
        '''Function to validate user input'''
        if len(data['title']) < 4:
            raise serializers.ValidationError({'message': 'Book title must have at least four characters'})
        elif data['title'] == data['description']:
            raise serializers.ValidationError({'message': 'Book title and description cannot be the same'})
        else:
            return data
        
    def create(self, validated_data):
        '''Function to create a new book'''

        # get all needed data
        book_title = validated_data.get('title')
        book_description = validated_data.get('description')
        book_file = validated_data.get('book_file')
        book_cover_picture = validated_data.get('book_cover_picture')
        # get current user
        book_author = self.context['request'].user

        # create a new book object
        new_book = Book(title=book_title, 
                        description=book_description, 
                        book_file=book_file, 
                        book_cover_picture=book_cover_picture, 
                        author=book_author
                    )
        
        # save book object and return it
        new_book.save()
        return new_book


class BookDetailsSerializer(serializers.ModelSerializer):
    '''
        Serializer to update book details
    '''

    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['created', 'updated']

    def validate(self, data):
        '''Function to validate user input'''
        if len(data['title']) < 4:
            raise serializers.ValidationError({'message': 'Book title must have at least four characters'})
        elif data['title'] == data['description']:
            raise serializers.ValidationError({'message': 'Book title and description cannot be the same'})
        else:
            return data
        
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # save new instance and return it
        instance.save()
        return instance
    