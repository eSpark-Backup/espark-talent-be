from django.urls import path
from .clientviews import LoginView
from .hrviews import *

urlpatterns=[
    path('login/',LoginView.as_view()),
    path('hr_add_emp/', Add_Employee.as_view()),
    path('hr_add_client/', Add_Client.as_view()),
    path('hr_add_asset/', Add_Asset.as_view()),
    path('hr_empinv/', Employee_Invoice.as_view()),
    path('hr_otherinv/', Other_Payment.as_view()),
    path('hr_home/', Hr_Home.as_view()),
    path('hr_emps/', Hr_Employees.as_view()),
    path('hr_emp_prof/', Hr_Employee.as_view()),
    path('hr_update_empinfo/', Update_Emp_Person_Info.as_view()),
    path('hr_update_empcontact/', Update_Emp_Emerg_Info.as_view()),
    path('hr_update_empimg/', Update_Emp_Profile_Pic.as_view()),
    path('hr_update_empcred/', Edit_Cridentials.as_view()),
    path('hr_start_hire/', Start_Hiring.as_view()),
    path('hr_onboarding/', Onboarding.as_view()),
    path('hr_is/', Interview_Schedule.as_view()),
    path('hr_clients/', Hr_Clients.as_view()),
    path('hr_client_prof/', Hr_Client.as_view()),
]