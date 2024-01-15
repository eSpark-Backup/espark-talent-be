from django.urls import path
from .clientviews import LoginView
from .hrviews import *

urlpatterns=[
    path('login/',LoginView.as_view()),
    path('hr_add_emp/', Add_Employee.as_view()),
    path('hr_add_client/', Add_Client.as_view()),
    path('hr_add_asset/', Add_Asset.as_view()),
    path('hr_empinv/', Employee_Invoice.as_view()),
    path('hr_otherpay/', Other_Payment.as_view()),
]