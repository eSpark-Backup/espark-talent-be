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
        onboarding_count = onboarding.objects.filter(user_id=user).count()

        data = {
            'username': user.username,
            'hiring_request_count': hiring_request_count,
            'interview_schedule_count': interview_schedule_count,
            'onboarding_count': onboarding_count,
            'active_employee': 0,
        }

        return Response(data, status=status.HTTP_200_OK)
    

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Start_Hiring(APIView):
    def post(self, request, *args, **kwargs):
        serializer=hiring_requestSerializer(data=request.data)
        if serializer.is_valid():
            hiring_request.objects.create(
                user_id = request.user,
                job_title = serializer.validated_data['job_title'],
                role_type = serializer.validated_data['role_type'],
                gender = serializer.validated_data['gender'],
                employment_term = serializer.validated_data['employment_term'],
                salary_range= serializer.validated_data['salary_range'],
                hiring_start_date = serializer.validated_data['hiring_start_date'],
                hiring_end_date = serializer.validated_data['hiring_end_date'],
            )
            print(request.data, request.user)
            return Response({"message": "Resquest created"},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


