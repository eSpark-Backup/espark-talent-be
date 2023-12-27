from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *

class create_user(APIView):
    def post(self, request, *args, **kwargs):
        serializer = userSerializer(data=request.data)
        if serializer.is_valid():
            # Use the custom manager to create a user
            end_user.objects.create_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                username=serializer.validated_data['username'],
                role=serializer.validated_data['role'],
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            return Response({'token': token, 'role': user.role}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Client_Home(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        hiring_request_count = hiring_request.objects.filter(user_id=user).count()
        interview_schedule_count = interview_schedule.objects.filter(user_id=user).count()
        onboarding_count = onboarding.objects.filter(user_id=user, status='onboard').count()
        active_employee = onboarding.objects.filter(user_id=user, status='active').count()

        data = {
            'username': user.username,
            'hiring_request_count': hiring_request_count,
            'interview_schedule_count': interview_schedule_count,
            'onboarding_count': onboarding_count,
            'active_employee': active_employee,
        }

        return Response(data, status=status.HTTP_200_OK)
    

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Start_Hiring(APIView):
    def post(self, request, *args, **kwargs):
        serializer=hiring_requestSerializer(data=request.data)
        if serializer.is_valid():
            print(request.data)
            hiring_request.objects.create(
                user_id = request.user,
                job_title = serializer.validated_data['job_title'],
                role_type = serializer.validated_data['role_type'],
                gender = serializer.validated_data['gender'],
                employment_term = serializer.validated_data['employment_term'],
                salary_range= serializer.validated_data['salary_range'],
                country=serializer.validated_data['country'],
                hiring_start_date = serializer.validated_data['hiring_start_date'],
                hiring_end_date = serializer.validated_data['hiring_end_date'],
            )
            return Response({"message": "Resquest created"},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hiring_Resquest(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        hiring_requests = hiring_request.objects.filter(user_id=user)
        records={}
        if hiring_requests:
            for num,data in enumerate(hiring_requests):
                records['record'+str(num+1)]={
                    'job_title':data.job_title,
                    'role_type':data.role_type,
                    'gender':data.gender,
                    'employment_term':data.employment_term,
                    'salary_range':data.salary_range,
                    'hiring_start_date':data.hiring_start_date,
                    'hiring_end_date':data.hiring_end_date,
                }
            return Response(records,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Interview_Schedule(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        interview_schedules = interview_schedule.objects.filter(user_id=user)
        records={}
        if interview_schedules:
            for num,data in enumerate(interview_schedules):
                records['record'+str(num+1)]={
                    'employee_name':data.employee_id.username,
                    'gender':data.employee_id.gender,
                    'job_title':data.employee_id.designation,
                    'role_type':data.role_type,
                    'employment_term':data.employment_term,
                    'interview_date_time':data.interview_date_time,
                    'country':data.country,
                    'status':data.status,
                }
            return Response(records,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Onboarding(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        onboardings = onboarding.objects.filter(user_id=user, status='onboard')
        records={}
        if onboardings:
            for num,data in enumerate(onboardings):
                records['record'+str(num+1)]={
                    'employee_name':data.employee_id.username,
                    'gender':data.employee_id.gender,
                    'country':data.country,
                    'job_title':data.employee_id.designation,
                    'role_type':data.role_type,
                    'employment_term':data.employment_term,
                    'joining_date':data.joining_date,
                    'notice_period':data.notice_period,
                    'salary':data.salary,
                }
            return Response(records,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Team_Memebers(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        get_status=request.data['status']
        if get_status=='active' or get_status=='onboard' or get_status=='terminated':
            onboardings = onboarding.objects.filter(user_id=user, status=get_status)
        elif get_status=='all':
            onboardings = onboarding.objects.filter(user_id=user)
        records={}
        if onboardings:
            for num,data in enumerate(onboardings):
                records['record'+str(num+1)]={
                    'employee_name':data.employee_id.username,
                    'country':data.country,
                    'job_title':data.employee_id.designation,
                    'employment_term':data.employment_term,
                    'joining_date':data.joining_date,
                }
            return Response(records,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)