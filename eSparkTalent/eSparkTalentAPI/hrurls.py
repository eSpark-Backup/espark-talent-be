from django.urls import path
from .clientviews import LoginView
from .hrviews import *

urlpatterns=[
    path('login/',LoginView.as_view()),
]