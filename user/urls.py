from django.urls import path
from . import views

app_name = 'user'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('update/', views.UpdateDetailsView.as_view(), name='update'),
    path('changePassword/', views.ChangePasswordView.as_view(), name='change-password')
]