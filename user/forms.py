from django.contrib.auth.forms import UserChangeForm, UserCreationForm

class UserChangeForm(UserChangeForm):
    class Meta:
        fields = ["email",]

class UserCreationForm(UserCreationForm):
    class Meta:
        fields = ["email",]