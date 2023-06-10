from django.shortcuts import render

from django.contrib.auth import get_user_model
from rest_framework import filters
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser

from . import serializers
from .models import Book
from .permissions import IsBookAuthorOrReadOnly, IsAuthorRole
from .pagination import BooksPagination

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
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        

class AuthorBooksView(generics.ListAPIView):
    '''
        View that displays a list of a specific user books
    '''

    serializer_class = serializers.BookDetailsSerializer
    permission_classes = [IsAuthenticated, IsAuthorRole]
    pagination_class = BooksPagination
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
            return Response({'message': 'You have no books yet.'})


class AllBooksView(generics.ListAPIView):
    '''
        View that displays a list of all available books
    '''

    serializer_class = serializers.BookDetailsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = BooksPagination
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
            return Response({'message': "This book does not exist"})
        
    def get_object(self):
        pk = self.kwargs['pk']
        book = Book.objects.get(pk=pk)
        self.check_object_permissions(self.request, book)
        return book
    