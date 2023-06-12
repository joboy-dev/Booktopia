from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse

from rest_framework import filters
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import NotFound

from . import serializers
from .models import Book, Comment
from .permissions import IsBookAuthorOrReadOnly, IsAuthorRole, IsCommentAuthor
from .pagination import DefaultPagination

User = get_user_model()

# Create your views here.
class AddNewBookView(generics.CreateAPIView):
    '''
        View to add a new book
    '''

    serializer_class = serializers.AddBookSerializer
    permission_classes = [IsAuthenticated, IsAuthorRole]
    parser_classes = [MultiPartParser]
    queryset = Book.objects.all()

    def perform_create(self, serializer):
        # check permission before saving serializer
        self.check_object_permissions(self.request, self.queryset)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
        

class AuthorBooksView(generics.ListAPIView):
    '''
        View that displays a list of a specific user books
    '''

    serializer_class = serializers.BookDetailsSerializer
    permission_classes = [IsAuthenticated, IsAuthorRole]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created']

    def get_queryset(self):
        current_user = self.request.user
        return Book.objects.filter(author=current_user)
    
    def list(self, request, *args, **kwargs):
        current_user = self.request.user
        books = Book.objects.filter(author=current_user)

        self.check_object_permissions(self.request, books)

        # check for any book object
        if books.exists():
            serializer = self.serializer_class(books, many=True)
            return Response(serializer.data)
        else:
            response_data = {
                'message': 'You have no books yet. Click link below to add a new book',
                'link': reverse_lazy('book:addBook')
            }
            return Response(response_data)


class AllBooksView(generics.ListAPIView):
    '''
        View that displays a list of all available books
    '''

    serializer_class = serializers.BookDetailsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', '=author__first_name', '=author__last_name']
    ordering_fields = ['created']
    queryset = Book.objects.all()


class BookDetailsView(generics.RetrieveUpdateDestroyAPIView):
    '''
        View to view, update and delete books depending on level pf permission
    '''

    serializer_class = serializers.BookDetailsSerializer
    permission_classes = [IsAuthenticated, IsBookAuthorOrReadOnly]

    def get_queryset(self):
        current_user = self.request.user
        return Book.objects.filter(author=current_user.pk)
    
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']

        try:
            book = Book.objects.get(pk=pk)
            serializer = self.serializer_class(book)
            return Response(serializer.data)
        except Book.DoesNotExist:
            raise NotFound("This book does not exist")

    def get_object(self):
        pk = self.kwargs['pk']
        book = Book.objects.get(pk=pk)
        self.check_object_permissions(self.request, book)
        return book
    
    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            book = Book.objects.get(pk=pk)
            super().delete(request, *args, **kwargs)
            return Response({'message': f'Book {book.title} deleted.'})
        except Book.DoesNotExist:
            raise NotFound('Book does not exist')


class AddCommentView(generics.CreateAPIView):
    '''
        View to add a new comment
    '''

    serializer_class = serializers.CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    

class CommentDetailsView(generics.RetrieveUpdateDestroyAPIView):
    '''
        View to get, update and delete a comment
    '''

    serializer_class = serializers.CommentDetailsSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Comment.objects.filter(pk=pk)
    
    def get_object(self):
        pk = self.kwargs['pk']
        comment = Comment.objects.get(pk=pk)
        self.check_object_permissions(self.request, comment)
        return comment
    
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']

        try:
            comment = Comment.objects.get(pk=pk)
            serializer = self.serializer_class(comment)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            raise NotFound('This commment does not exist.')
        
    def perform_update(self, serializer):
        try:
            pk = self.kwargs['pk']

            comment = Comment.objects.get(pk=pk)
            book_obj = comment.book

            # get existing sum of all ratings
            existing_ratings_sum = book_obj.average_rating * book_obj.no_of_ratings

            # get current rating
            current_rating = comment.rating

            # subtract current rating from existing sum of ratings
            new_ratings_sum = existing_ratings_sum - current_rating

            # get updated rating from validated data
            updated_rating = serializer.validated_data['rating']

            # calculate the difference between updated rating and current rating
            rating_difference = updated_rating - current_rating

            # add the rating difference to the sum of ratings
            new_ratings_sum += rating_difference

            book_obj.average_rating = new_ratings_sum / book_obj.no_of_ratings
            book_obj.save()

            super().perform_update(serializer)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            raise NotFound('This comment does not exist.')
        
    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            comment = Comment.objects.get(pk=pk)

            # get book object
            book_obj = comment.book

            self.check_object_permissions(request, comment)
            
            # reduce number of comments by 1
            book_obj.no_of_comments -= 1

            if book_obj.no_of_ratings == 1:
                book_obj.average_rating = 0.00
        
                # reduce number of ratings by 1
                book_obj.no_of_ratings -= 1
            else:
                # get existing ratings sum
                existing_ratings_sum = book_obj.average_rating * book_obj.no_of_ratings
                
                # get the rating for the specific comment
                current_comment_rating = comment.rating

                # subtract current comment rating from the existing rating sum
                new_ratings_sum = existing_ratings_sum -current_comment_rating

                # reduce number of ratings by 1
                book_obj.no_of_ratings -= 1

                # get new average rating
                book_obj.average_rating = new_ratings_sum / book_obj.no_of_ratings

            # save book instance gotten from comment model
            book_obj.save()

            super().delete(request, *args, **kwargs)
            return Response({'message': 'Comment deleted'})
        except Comment.DoesNotExist:
            raise NotFound('This comment does not exist.')
        

class AllBookCommentsView(generics.ListAPIView):
    '''
        View to get all comments for a book
    '''

    serializer_class = serializers.CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated']

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Comment.objects.filter(book=pk)
    
    def list(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        book_comments =  Comment.objects.filter(book=pk)

        if book_comments.exists():
            serializer = self.serializer_class(book_comments, many=True)
            return Response(serializer.data)
        else:
            response_data = {
                'message': 'This book has no comments. Click link below to add a comment',
                # 'link': reverse('book:bookComments')
            }
            return Response(response_data)
        

class AllUserCommentsView(generics.ListAPIView):
    '''
        View tp get all user comments
    '''

    serializer_class = serializers.CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination


    def get_queryset(self):
        current_user = self.request.user
        return Comment.objects.filter(commenter=current_user)

    def list(self, request, *args, **kwargs):
        current_user = self.request.user
        user_comments = Comment.objects.filter(commenter=current_user)

        if user_comments.exists():
            serializer = self.serializer_class(user_comments, many=True)
            return Response(serializer.data)
        else:
            response_data = {
                'message': 'This book has no comments. Click link below to add a comment',
                # 'link': reverse_lazy('book:userComments')
            }
            return Response(response_data)