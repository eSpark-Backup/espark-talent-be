from django.urls import path
from . views import *

urlpatterns=[
    path('user_create/',create_user.as_view()),
    path('login/',LoginView.as_view()),
    path('chome/',Client_Home.as_view()),
    path('csh/',Start_Hiring.as_view()),
    path('chr/',Hiring_Resquest.as_view()),
    path('cis/',Interview_Schedule.as_view()),
    path('conboard/',Onboarding.as_view()),
    path('team/',Team_Memebers.as_view())
]