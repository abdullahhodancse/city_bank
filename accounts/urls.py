
from django.urls import path
from .views import UserRegistrationView,UserLogInView,UserLogOutView,UserBankAccountUpdateView


urlpatterns = [
    
    path('register/', UserRegistrationView.as_view(),name='register'),
    path('login/', UserLogInView.as_view(),name='login'),
    path('logout/', UserLogOutView.as_view(),name='logout'),
     path('profile/', UserBankAccountUpdateView.as_view(), name='profile' )

]