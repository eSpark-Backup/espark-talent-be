from django.urls import path
from . views import *

urlpatterns=[
    path('user_create/',create_user.as_view()),
    path('login/',LoginView.as_view()),
    path('chome/',Client_Home.as_view()),
]