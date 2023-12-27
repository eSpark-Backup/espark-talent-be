from django.urls import path
from . views import *

urlpatterns=[
    path('user_create/',create_user.as_view()),
    path('login/',LoginView.as_view()),
    path('c_home/',Client_Home.as_view()),
    path('c_sh/',Start_Hiring.as_view()),
    path('c_hr/',Hiring_Resquest.as_view()),
    path('c_is/',Interview_Schedule.as_view()),
    path('c_onboard/',Onboarding.as_view()),
    path('c_team/',Team_Memebers.as_view())
]