from django.urls import path
from . views import *

urlpatterns=[
    path('signup/',UserSignupAPI.as_view()),
    path('login/',UserSigninAPI.as_view()),
    # path('new_user/',views.new_user),
    # path('edit_user/',views.edit_user),
    # path('hiring_requests/',views.hiring_request),
]