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

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user1 = Client.objects.get(email=email)
        user1.set_password(password)
        user1.save()

        user = authenticate(request, email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            return Response({'token': token, 'role': user.role}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class HomePageView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        print(user)
        hiring_request_count = hiring_request.objects.filter(user_id=user).count()
        interview_schedule_count = interview_schedule.objects.filter(user_id=user).count()

        data = {
            'username': user.username,
            'hiring_request_count': hiring_request_count,
            'interview_schedule_count': interview_schedule_count,
        }

        return Response(data, status=status.HTTP_200_OK)