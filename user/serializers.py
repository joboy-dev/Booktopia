from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()

class CreateAccountSerializer(serializers.ModelSerializer):

    '''
        Serializer to create new user
    '''

    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'gender', 'password', 'password2', 'role']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True}
        }

    def validate(self, data):
        '''Account creation validation function'''

        # validate password
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'message': 'Your passwords do not match'})
        
        # check if email exists
        elif User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'message': 'Email already exists'})
        
        # check if gender and role choices areb valid
        elif len(data['gender']) > 1:
            raise serializers.ValidationError({'message': 'Gender choice is not valid'})
        elif data['role'] > 2:
            raise serializers.ValidationError({'message': 'Role choice is not valid'})
        
        # validate password
        validate_password(data['password'])
        # return validated data
        return data
    
    def create(self, validated_data):
        '''Account creation function'''

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
        '''Authentication validation function'''

        # authenticate user with email and password
        user = authenticate(email=data['email'], password=data['password'])

        # check for existence of user
        if user is None:
            raise serializers.ValidationError({'message': 'User does not exist'})
        
        # remove fields from dictionary that you don't want to see in JSON response
        email = data.pop('email')
        data.pop('password')

        # get or create a new token
        token= Token.objects.get_or_create(user=user)

        data['message'] = f'Welcome {email}'
        data['token'] = token[0].key

        return data

    
class UpdateDetailsSerializer(serializers.ModelSerializer):

    '''
        Serializer to update a user's details (email, first name and last name)
    '''

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile_pic', 'role']
    
    def update(self, instance, validated_data):
        '''Update details function'''

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance
    

class ChangePasswordSerializer(serializers.Serializer):
    '''
        Serializer to change user password
    '''

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def update(self, instance, validated_data):
        email = validated_data.get('email')
        old_password = validated_data.get('password')
        new_password = validated_data.get('new_password')
        confirm_password = validated_data.get('confirm_password')

        user = authenticate(email=email, password=old_password)

        if user is None:
            raise serializers.ValidationError({'message': 'User credentials incorrect. Check your email and password and try again.'})
        elif old_password == new_password:
            raise serializers.ValidationError({'message': 'New password cannot be the same as old password.'})
        elif new_password != confirm_password:
            raise serializers.ValidationError({'message': 'New password and confirm password field has to be the same.'})
        
        validate_password(new_password)
        instance.set_password(new_password)

        instance.save()

        return instance
    