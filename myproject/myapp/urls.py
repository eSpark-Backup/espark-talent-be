from django.urls import path
from . views import *

urlpatterns=[
    # path('signup/',UserSignupAPI.as_view()),
    path('login/',LoginView.as_view()),
    path('home/',HomePageView.as_view()),
]