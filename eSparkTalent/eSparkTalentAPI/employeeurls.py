from django.urls import path
from .clientviews import LoginView
from .employeeviews import *

urlpatterns=[
    path('login/',LoginView.as_view()),
]