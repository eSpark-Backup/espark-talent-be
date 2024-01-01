from .models import *
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class create_user(APIView):
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'role': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['email', 'password', 'username', 'role'],
    ),
    responses={
        201: openapi.Response(description='Successful created'),
        400: openapi.Response(description='Bad request'),
    },
    operation_description="Endpoint for user create.",
)
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
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
            'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
        },
        required=['email', 'password'],
    ),
    responses={
        200: openapi.Response(
            description='Successful login',
            schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING),
            'role': openapi.Schema(type=openapi.TYPE_STRING),
        })
        ),
        401: openapi.Response(description='Invalid credentials'),
    },
    operation_description="Endpoint for user login.",
)
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
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                    description='Successful request',
                    schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'hiring_request_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'interview_schedule_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'onboarding_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'active_employee': openapi.Schema(type=openapi.TYPE_INTEGER),
                     })
             ),
            401: openapi.Response('Unauthorized'),
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer Token',
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_description="Endpoint to retrieve client home data.",
    )
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
    @swagger_auto_schema(
        request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'job_title': openapi.Schema(type=openapi.TYPE_STRING),
            'role_type': openapi.Schema(type=openapi.TYPE_STRING),
            'gender': openapi.Schema(type=openapi.TYPE_STRING),
            'employment_term': openapi.Schema(type=openapi.TYPE_STRING),
            'salary_range': openapi.Schema(type=openapi.TYPE_OBJECT, properties={'minimum':openapi.Schema(type=openapi.TYPE_INTEGER),'maximum':openapi.Schema(type=openapi.TYPE_INTEGER)}),
            'country': openapi.Schema(type=openapi.TYPE_STRING),
            'hiring_start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            'hiring_end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        },
        required=['email', 'password'],
    ),
        responses={
            201: openapi.Response('Successful created'),
            400: openapi.Response('Bad request'),
            401: openapi.Response('UnAuthorize')
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer Token',
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_description="Endpoint to create hiring request.",
    )
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
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
            description='Successful response',
            schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_OBJECT,
             properties={
                 'job_title': openapi.Schema(type=openapi.TYPE_STRING),
                 'role_type': openapi.Schema(type=openapi.TYPE_STRING),
                 'gender': openapi.Schema(type=openapi.TYPE_STRING),
                 'employment_term': openapi.Schema(type=openapi.TYPE_STRING),
                 'salary_range': openapi.Schema(type=openapi.TYPE_OBJECT, properties={'minimum':openapi.Schema(type=openapi.TYPE_INTEGER),'maximum':openapi.Schema(type=openapi.TYPE_INTEGER)}),
                 'hiring_start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                 'hiring_end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        }))
        ),
            204: openapi.Response('No content'),
            401: openapi.Response('UnAuthorize')
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer Token',
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_description="Endpoint to retrieve hiring request data.",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        hiring_requests = hiring_request.objects.filter(user_id=user)

        if hiring_requests:
            records = []
            for data in hiring_requests:
                record = {
                    'job_title': data.job_title,
                    'role_type': data.role_type,
                    'gender': data.gender,
                    'employment_term': data.employment_term,
                    'salary_range': data.salary_range,
                    'hiring_start_date': data.hiring_start_date,
                    'hiring_end_date': data.hiring_end_date,
                }
                records.append(record)

            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
        

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Interview_Schedule(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
            description='Successful response',
            schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_OBJECT,
             properties={
                 'employee_name': openapi.Schema(type=openapi.TYPE_STRING),
                 'gender': openapi.Schema(type=openapi.TYPE_STRING),
                 'job_title': openapi.Schema(type=openapi.TYPE_STRING),
                 'role_type': openapi.Schema(type=openapi.TYPE_STRING),
                 'employment_term': openapi.Schema(type=openapi.TYPE_OBJECT, properties={'minimum':openapi.Schema(type=openapi.TYPE_INTEGER),'maximum':openapi.Schema(type=openapi.TYPE_INTEGER)}),
                 'interview_date_time': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                 'country': openapi.Schema(type=openapi.TYPE_STRING),
                 'status': openapi.Schema(type=openapi.TYPE_STRING),
        }))
        ),
            204: openapi.Response('No content'),
            401: openapi.Response('UnAuthorize')
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer Token',
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_description="Endpoint to retrieve interview schedule data.",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        interview_schedules = interview_schedule.objects.filter(user_id=user)
        records=[]
        if interview_schedules:
            for data in interview_schedules:
                record={
                    'employee_name':data.employee_id.username,
                    'gender':data.employee_id.gender,
                    'job_title':data.employee_id.designation,
                    'role_type':data.role_type,
                    'employment_term':data.employment_term,
                    'interview_date_time':data.interview_date_time,
                    'country':data.country,
                    'status':data.status,
                }
                records.append(record)
            return Response(records,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Onboarding(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
            description='Successful response',
            schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_OBJECT,
             properties={
                 'employee_name': openapi.Schema(type=openapi.TYPE_STRING),
                 'gender': openapi.Schema(type=openapi.TYPE_STRING),
                 'job_title': openapi.Schema(type=openapi.TYPE_STRING),
                 'role_type': openapi.Schema(type=openapi.TYPE_STRING),
                 'employment_term': openapi.Schema(type=openapi.TYPE_OBJECT, properties={'minimum':openapi.Schema(type=openapi.TYPE_INTEGER),'maximum':openapi.Schema(type=openapi.TYPE_INTEGER)}),
                 'joining_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                 'notice_period': openapi.Schema(type=openapi.TYPE_STRING),
                 'salary': openapi.Schema(type=openapi.TYPE_INTEGER),
        }))
        ),
            204: openapi.Response('No content'),
            401: openapi.Response('UnAuthorize')
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer Token',
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_description="Endpoint to retrieve on-boarding data.",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        onboardings = onboarding.objects.filter(user_id=user, status='onboard')
        records=[]
        if onboardings:
            for data in onboardings:
                record={
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
                records.append(record)
            return Response(records,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
        

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Team_Memeber(APIView):
    @swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description='Status filter (all, active, onboard, terminated)',
            type=openapi.TYPE_STRING,
            enum=['all', 'active', 'onboard', 'terminated'],
            required=True,
        ),
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description='Bearer Token',
            type=openapi.TYPE_STRING,
        ),
    ],
    responses={
        200: openapi.Response(
            description='Successful response',
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'employee_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'country': openapi.Schema(type=openapi.TYPE_STRING),
                        'job_title': openapi.Schema(type=openapi.TYPE_STRING),
                        'employment_term': openapi.Schema(type=openapi.TYPE_OBJECT, properties={'minimum':openapi.Schema(type=openapi.TYPE_INTEGER),'maximum':openapi.Schema(type=openapi.TYPE_INTEGER)}),
                        'joining_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                        'benefits': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            )
        ),
        204: openapi.Response('No content'),
        401: openapi.Response('UnAuthorize')
    },
    operation_description="Endpoint to retrieve team members data.",
)
    def get(self, request, *args, **kwargs):
        user = request.user
        get_status=request.query_params.get('status')
        if get_status=='active' or get_status=='onboard' or get_status=='terminated':
            onboardings = onboarding.objects.filter(user_id=user, status=get_status)
        elif get_status=='all':
            onboardings = onboarding.objects.filter(user_id=user)
        records=[]
        if onboardings:
            for data in onboardings:
                record={
                    'employee_name':data.employee_id.username,
                    'country':data.country,
                    'job_title':data.employee_id.designation,
                    'employment_term':data.employment_term,
                    'joining_date':data.joining_date,
                    'benefits': data.employee_id.benefits
                }
                records.append(record)
            return Response(records,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Leave_Request(APIView):
        @swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description='Status filter (all, pending, completed, rejected)',
            type=openapi.TYPE_STRING,
            enum=['all', 'pending', 'completed', 'rejected'],
            required=True,
        ),
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description='Bearer Token',
            type=openapi.TYPE_STRING,
        ),
    ],
    responses={
        200: openapi.Response(
            description='Successful response',
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        'employee_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'employee_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'country': openapi.Schema(type=openapi.TYPE_STRING),
                        'department': openapi.Schema(type=openapi.TYPE_STRING),
                        'leave_type': openapi.Schema(type=openapi.TYPE_STRING),
                        'start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE) ,
                        'end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'sandwich_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total':  openapi.Schema(type=openapi.TYPE_INTEGER),
                        'reason': openapi.Schema(type=openapi.TYPE_STRING) ,
                        'requested_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        ),
        204: openapi.Response('No content'),
        401: openapi.Response('UnAuthorize')
    },
    operation_description="Endpoint to retrieve Leave request data.",
)
        def get(self, request, *args, **kwargs):
            user = request.user
            get_status=request.query_params.get('status')
            if get_status=='pending' or get_status=='completed' or get_status=='rejected':
                leave_requests = leave_request.objects.filter(onboarding_id__user_id=user, status=get_status)
            elif get_status=='all':
                leave_requests = leave_request.objects.filter(onboarding_id__user_id=user)
            records = []

            if leave_requests:
                for data in leave_requests:
                    employee_serializer = EmployeeSerializer(data.onboarding_id.employee_id)
                    employee_data = employee_serializer.data

                    record = {
                        "id":data.id,
                        'employee_id': employee_data.get('employee_id', ''),
                        'employee_name': employee_data.get('username', ''),
                        'country': data.onboarding_id.country,
                        'department': employee_data.get('department', ''),
                        'leave_type': data.leave_type,
                        'start_date': data.start_date,
                        'end_date': data.end_date,
                        'count': data.count,
                        'sandwich_count': data.sandwich_count,
                        'total': data.total,
                        'reason': data.reason,
                        'requested_at': data.requested_at,
                        'status': data.status
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        
        @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'status': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description='Successful update'),
            204: openapi.Response(description='No content'),
            400: openapi.Response(description='Bad request'),
        },
        operation_description="Endpoint to update the status of a leave request.",
    )
            
        def patch(self, request, *args, **kwargs):
            user=request.user
            request_id=request.query_params.get('id')
            to_update_status=request.data['status']
            try:
                to_update_leave_request=leave_request.objects.get(id=request_id)
                if to_update_leave_request:
                    to_update_leave_request.status=to_update_status
                    to_update_leave_request.save()

                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Leave_Balance(APIView):
        @swagger_auto_schema(
        responses={
            200: openapi.Response(
            description='Successful response',
            schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_OBJECT,
             properties={
                        'employee_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'casual_leaves': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'sick_leaves': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'annual_leaves': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'taken': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'balance': openapi.Schema(type=openapi.TYPE_INTEGER),
        }))
        ),
            204: openapi.Response('No content'),
            401: openapi.Response('UnAuthorize')
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description='Bearer Token',
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_description="Endpoint to retrieve leave balance data.",
    )
        def get(self, balance, *args, **kwargs):
            user = balance.user
            leave_balances = leave_balance.objects.filter(onboarding_id__user_id=user)
            records = []

            if leave_balances:
                for data in leave_balances:
                    employee_serializer = EmployeeSerializer(data.onboarding_id.employee_id)
                    employee_data = employee_serializer.data

                    record = {
                        'employee_name': employee_data.get('username', ''),
                        'casual_leaves': data.casual_leaves,
                        'sick_leaves': data.sick_leaves,
                        'annual_leaves': data.annual_leaves,
                        'taken': data.taken,
                        'balance': data.balance,
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
            

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ClockInOut_Request(APIView):
        @swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description='Status filter (all, pending, completed, rejected)',
            type=openapi.TYPE_STRING,
            enum=['all', 'pending', 'completed', 'rejected'],
            required=True,
        ),
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description='Bearer Token',
            type=openapi.TYPE_STRING,
        ),
    ],
    responses={
        200: openapi.Response(
            description='Successful response',
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        'employee_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'employee_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'country': openapi.Schema(type=openapi.TYPE_STRING),
                        'date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE) ,
                        'punch_time': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                        'punch_type':  openapi.Schema(type=openapi.TYPE_STRING),
                        'description':  openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        ),
        204: openapi.Response('No content'),
        401: openapi.Response('UnAuthorize')
    },
    operation_description="Endpoint to retrieve clock IN and OUT request data.",
)
        def get(self, balance, *args, **kwargs):
            user = balance.user
            clockinout_requests = clockinout_request.objects.filter(onboarding_id__user_id=user)
            records = []

            if clockinout_requests:
                for data in clockinout_requests:
                    employee_serializer = EmployeeSerializer(data.onboarding_id.employee_id)
                    employee_data = employee_serializer.data

                    record = {
                        "id":data.id,
                        'employee_id': employee_data.get('employee_id', ''),
                        'employee_name': employee_data.get('username', ''),
                        'date': data.date,
                        'punch_time': data.punch_time,
                        'punch_type': data.punch_type,
                        'description': data.description,
                        'status': data.status
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        
        @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'status': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description='Successful update'),
            204: openapi.Response(description='No content'),
            400: openapi.Response(description='Bad request'),
        },
        operation_description="Endpoint to update the status of a clock in/out record.",
    )    
        def patch(self, request, *args, **kwargs):
            user=request.user
            request_id=request.query_params.get('id')
            to_update_status=request.data['status']
            try:
                to_update_clockinout_request=clockinout_request.objects.get(id=request_id)
                if to_update_clockinout_request:
                    to_update_clockinout_request.status=to_update_status
                    to_update_clockinout_request.save()

                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)