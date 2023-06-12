from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.exceptions import NotFound

from .models import Book, Comment

# user model
User = get_user_model()

class AddBookSerializer(serializers.ModelSerializer):
    '''
        Serializer for authors to add their books
    '''

    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return obj.author.email

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        return representation
    
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


class CommentSerializer(serializers.ModelSerializer):
    '''
        Serializer class for adding a comment to a book
    '''

    commenter = serializers.SerializerMethodField(read_only=True)
    book = serializers.SerializerMethodField(read_only=True)

    def get_commenter(self, obj):
        return obj.commenter.email
    
    def get_book(self, obj):
        return f'{obj.book.title} by {obj.book.author.email}'

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['created', 'updated']

    def validate(self, data):
        if len(data['comment']) < 3:
            raise serializers.ValidationError({'message': 'Comment must have at least three characters'})
        
        return data
    
    def create(self, validated_data):
        # get primary key that will be used in book queryset
        pk = self.context['view'].kwargs.get('pk')

        comment_content = validated_data.get('comment')
        rating = validated_data.get('rating')
        comment_author = self.context['request'].user
        book_obj = Book.objects.get(pk=pk)

        # check if a user has already made a comment on a book
        comment_queryset = Comment.objects.filter(book=book_obj, commenter=comment_author)

        if comment_queryset.exists():
            raise serializers.ValidationError({'message': 'You are allowed to comment only once on a particulr book.'})
        
        # create new comment object
        comment = Comment(
            comment=comment_content,
            rating=rating,
            book=book_obj,
            commenter=comment_author
        )

        comment.save()

        # update number of comments
        book_obj.no_of_comments += 1

        if book_obj.no_of_ratings == 0:
            # update the number of ratings and average rating value in book model
            book_obj.no_of_ratings += 1
            book_obj.average_rating = rating
        elif book_obj.no_of_ratings > 0:
            # get sum of all existing ratings
            existing_ratings_sum = book_obj.average_rating * book_obj.no_of_ratings
            
            # update number of ratings -- increment by 1
            book_obj.no_of_ratings += 1

            # update average rating
            book_obj.average_rating = (existing_ratings_sum + rating) / book_obj.no_of_ratings

        book_obj.save()

        return comment
    

class CommentDetailsSerializer(serializers.ModelSerializer):
    '''
        Serializer to perform operation on specific comment
    '''

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['created', 'updated']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['commenter'] = instance.commenter.email
        representation['book'] = f'{instance.book.title} by {instance.book.author.email}'
        return representation

    def validate(self, data):
        if len(data['comment']) < 3:
            raise serializers.ValidationError({'message': 'Comment must have at least three characters'})
        
        return data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()


        return instance    
