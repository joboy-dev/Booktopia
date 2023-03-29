from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import obtain_auth_token

from .models import CustomUser

User = get_user_model()

class CreateAccountSerializer(serializers.ModelSerializer):

    '''
        Serializer to create new user
    '''

    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'gender', 'password', 'password2', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        # validate password
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'error': 'Your passwords do not match'})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'message': 'Email already exists'})
        
        # validate password
        validate_password(data['password'])
        # return validated data
        return data
    
    def create(self, validated_data):
        # get all validated data
        email = validated_data.get('email')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        password = validated_data.get('password')
        gender = validated_data.get('gender')
        role = validated_data.get('role')

        # assign validated data to the data in User model
        account = User(email=email, first_name=first_name, last_name=last_name, gender=gender, role=role)

        # set password
        account.set_password(raw_password=password)

        # save user instance
        account.save()

        # create token
        Token.objects.create(user=account)

        # return user instance
        return account
    

class LoginSerializer(serializers.Serializer):

    '''
        Serializer to log in a user
    '''

    # declare fields to use for the serializer
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    
    def validate(self, data):
        # authenticate user with email and password
        user = authenticate(email=data['email'], password=data['password'])

        # check for existence of user
        if user is None:
            raise serializers.ValidationError({'error': 'User does not exist'})
        
        # remove fields from dictionary that you don't want to see in JSON response
        data.pop('email')
        data.pop('password')

        # get or create a new token
        token, created = Token.objects.get_or_create(user=user)

        token = Token.objects.get_or_create(user=user)

        # if token already exists ie if user has logged in before
        if not created:
            token.delete()
            token = Token.objects.create(user=user)

        data['message'] = f'Welcome {user}'
        data['token'] = token.key

        return data
    
class UpdateDetailsSerializer(serializers.ModelSerializer):

    '''
        Serializer to update a user's details (email, first name and last name)
    '''

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile_pic']
    
    def update(self, instance, validated_data):
        # instance.first_name = validated_data.get('first_name', instance.first_name)
        # instance.last_name = validated_data.get('last_name', instance.last_name)
        # instance.email = validated_data.get('email', instance.email)
        # instance.profile_pic = validated_data.get('profile_pic', instance.profile_pic)

        # you can do this
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance
    
class AddProfilePictureSerializer(serializers.Serializer):

    '''
        Serializer to update a user's profile picture
    '''

    profile_pic = serializers.ImageField(required=True)

    def update(self, instance, validated_data):
        instance.profile_pic = validated_data.get('profile_pic', instance.profile_pic)

        instance.save()

        return instance
