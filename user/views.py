from django.shortcuts import render

from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from . import serializers

User = get_user_model()

# Create your views here.
class RegisterView(generics.CreateAPIView):

    '''
        View to register users
    '''
    
    serializer_class = serializers.CreateAccountSerializer
    
    def perform_create(self, serializer):
        # check if serializer is valid
        serializer.is_valid(raise_exception=True)
        # save serializer
        serializer.save()
        return Response({'message': 'Registration successful'})
    

class LoginView(APIView):

    '''
        View to log in users
    '''

    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data)
    

class LogoutView(APIView):

    '''
        View to logout users
    '''

    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # get current user
        current_user = request.user

        # get token based on current user
        current_user_token = Token.objects.get(user=current_user)
        # delete token
        current_user_token.delete()
        return Response({'message': 'Successfully logged out'})
    

class UpdateDetailsView(generics.RetrieveUpdateAPIView):

    '''
        View to update user details (first name, last name, email, profile picture)
    '''
    
    serializer_class = serializers.UpdateDetailsSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.filter(pk=current_user.pk)
    
    # get current user object
    def get_object(self):
        return self.request.user
    

class ChangePasswordView(generics.RetrieveUpdateAPIView):
    '''
        View to change user password
    '''

    serializer_class = serializers.ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.filter(pk=current_user.pk)

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'message': 'Password change successful'})
