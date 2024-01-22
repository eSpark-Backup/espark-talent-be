from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import datetime
from rest_framework.parsers import MultiPartParser


class LoginView(APIView):
    @swagger_auto_schema(
        tags=["Authentication Login"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
                ),
            },
            required=["email", "password"],
        ),
        responses={
            200: openapi.Response(
                description="Successful login",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "token": openapi.Schema(type=openapi.TYPE_STRING),
                        "role": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            401: openapi.Response(description="Invalid credentials"),
        },
        operation_summary="Endpoint for user login.",
        operation_id=".",
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            return Response(
                {"token": token, "role": user.role}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Client_Home(APIView):
    @swagger_auto_schema(
        tags=["Dashboard"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "username": openapi.Schema(type=openapi.TYPE_STRING),
                        "hiring_request_count": openapi.Schema(
                            type=openapi.TYPE_INTEGER
                        ),
                        "interview_schedule_count": openapi.Schema(
                            type=openapi.TYPE_INTEGER
                        ),
                        "onboarding_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "active_employee": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "Client_image": openapi.Schema(type=openapi.TYPE_FILE),
                    },
                ),
            ),
            401: openapi.Response("Unauthorized"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to retrieve client home data.",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        hiring_request_count = hiring_request.objects.filter(client__email=user).count()
        interview_schedule_count = interview_schedule.objects.filter(
            client__email=user
        ).count()
        onboarding_count = onboarding.objects.filter(
            client__email=user, status="onboard"
        ).count()
        active_employee = onboarding.objects.filter(
            client__email=user, status="active"
        ).count()

        try:
            client_instance = client.objects.get(email=user)
            image_path = client_instance.image.path
        except client.DoesNotExist:
            image_path = None

        data = {
            "username": user.username,
            "hiring_request_count": hiring_request_count,
            "interview_schedule_count": interview_schedule_count,
            "onboarding_count": onboarding_count,
            "active_employee": active_employee,
            "client_image": image_path,
        }

        return Response(data, status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Start_Hiring(APIView):
    @swagger_auto_schema(
        tags=["Hire & Onboard : Start Hiring"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                "role_type": openapi.Schema(type=openapi.TYPE_STRING),
                "gender": openapi.Schema(type=openapi.TYPE_STRING),
                "employment_term": openapi.Schema(type=openapi.TYPE_STRING),
                "salary_range": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "minimum": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "maximum": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "hiring_start_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
                "hiring_end_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
            },
            required=["email", "password"],
        ),
        responses={
            201: openapi.Response("Successful created"),
            400: openapi.Response("Bad request"),
            401: openapi.Response("UnAuthorize"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to create hiring request.",
        operation_id=".",
    )
    def post(self, request, *args, **kwargs):
        serializer = hiring_requestSerializer(data=request.data)
        if serializer.is_valid():
            client_1 = client.objects.get(email=request.user)
            hiring_request.objects.create(
                client=client_1,
                job_title=serializer.validated_data["job_title"],
                role_type=serializer.validated_data["role_type"],
                gender=serializer.validated_data["gender"],
                employment_term=serializer.validated_data["employment_term"],
                salary_range=serializer.validated_data["salary_range"],
                country=serializer.validated_data["country"],
                hiring_start_date=serializer.validated_data["hiring_start_date"],
                hiring_end_date=serializer.validated_data["hiring_end_date"],
            )
            return Response(
                {"message": "Resquest created"}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hiring_Resquest(APIView):
    @swagger_auto_schema(
        tags=["Hire & Onboard : Hiring Progress"],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                            "role_type": openapi.Schema(type=openapi.TYPE_STRING),
                            "gender": openapi.Schema(type=openapi.TYPE_STRING),
                            "employment_term": openapi.Schema(type=openapi.TYPE_STRING),
                            "salary_range": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "minimum": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                    "maximum": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                },
                            ),
                            "hiring_start_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "hiring_end_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                        },
                    ),
                ),
            ),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to retrieve hiring request data.",
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        hiring_requests = hiring_request.objects.filter(client__email=user)

        if hiring_requests:
            records = []
            for data in hiring_requests:
                record = {
                    "id": data.id,
                    "job_title": data.job_title,
                    "role_type": data.role_type,
                    "gender": data.gender,
                    "employment_term": data.employment_term,
                    "salary_range": data.salary_range,
                    "hiring_start_date": data.hiring_start_date,
                    "hiring_end_date": data.hiring_end_date,
                }
                records.append(record)

            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Hire & Onboard : Hiring Progress"],
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to delete",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful deletion"),
            204: openapi.Response(description="No content"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorize"),
        },
        operation_summary="Endpoint to delete a hiring request.",
        operation_id="2",
    )
    def delete(self, request, *args, **kwargs):
        user = request.user
        delete_id = request.query_params.get("id")
        try:
            hiring_request.objects.filter(id=delete_id).delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Interview_Schedule(APIView):
    @swagger_auto_schema(
        tags=["Hire & Onboard : Hiring Progress"],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "gender": openapi.Schema(type=openapi.TYPE_STRING),
                            "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                            "role_type": openapi.Schema(type=openapi.TYPE_STRING),
                            "employment_term": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "minimum": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                    "maximum": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                },
                            ),
                            "interview_date_time": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                            ),
                            "country": openapi.Schema(type=openapi.TYPE_STRING),
                            "status": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to retrieve interview schedule data.",
        operation_id="3",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        interview_schedules = interview_schedule.objects.filter(client__email=user)
        records = []
        if interview_schedules:
            for data in interview_schedules:
                record = {
                    "id": data.id,
                    "employee_name": data.employee.first_name
                    + " "
                    + data.employee.last_name,
                    "gender": data.gender,
                    "job_title": data.job_title,
                    "role_type": data.role_type,
                    "employment_term": data.employment_term,
                    "interview_date_time": data.interview_date_time,
                    "country": data.country,
                    "status": data.status,
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Hire & Onboard : Hiring Progress"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=["Pending", "Reject", "Short_list"]
                ),
            },
            required=["status"],
        ),
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful update"),
            204: openapi.Response(description="No content"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorize"),
        },
        operation_summary="Endpoint to update the status of an interview schedule.",
        operation_id="4",
    )

    ## on error

    def patch(self, request, *args, **kwargs):
        user = request.user
        request_id = request.query_params.get("id")
        to_update_status = request.data["status"]
        try:
            to_update_interview_status = interview_schedule.objects.get(id=request_id)
            if to_update_interview_status:
                to_update_interview_status.status = to_update_status
                to_update_interview_status.save()

                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Onboarding(APIView):
    @swagger_auto_schema(
        tags=["Hire & Onboard : Hiring Progress"],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "gender": openapi.Schema(type=openapi.TYPE_STRING),
                            "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                            "role_type": openapi.Schema(type=openapi.TYPE_STRING),
                            "employment_term": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "minimum": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                    "maximum": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                },
                            ),
                            "joining_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "notice_period": openapi.Schema(type=openapi.TYPE_STRING),
                            "salary": openapi.Schema(type=openapi.TYPE_INTEGER),
                        },
                    ),
                ),
            ),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to retrieve on-boarding data.",
        operation_id="5",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        onboardings = onboarding.objects.filter(client__email=user, status="onboard")
        records = []
        if onboardings:
            for data in onboardings:
                record = {
                    "employee_name": data.employee.first_name
                    + " "
                    + data.employee.last_name,
                    "gender": data.gender,
                    "country": data.country,
                    "job_title": data.job_title,
                    "role_type": data.role_type,
                    "employment_term": data.employment_term,
                    "joining_date": data.joining_date,
                    "notice_period": data.notice_period,
                    "salary": data.salary,
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Team_Member(APIView):
    @swagger_auto_schema(
        tags=["Team : Team Member"],
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Status filter (all, active, onboard, terminated)",
                type=openapi.TYPE_STRING,
                enum=["all", "active", "onboard", "terminated"],
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "country": openapi.Schema(type=openapi.TYPE_STRING),
                            "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                            "employment_term": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "minimum": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                    "maximum": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                },
                            ),
                            "joining_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "benefits": openapi.Schema(type=openapi.TYPE_OBJECT),
                        },
                    ),
                ),
            ),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_summary="Endpoint to retrieve team members data.",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        get_status = request.query_params.get("status")
        if (
            get_status == "active"
            or get_status == "onboard"
            or get_status == "terminated"
        ):
            onboardings = onboarding.objects.filter(
                client__email=user, status=get_status
            )
        elif get_status == "all":
            onboardings = onboarding.objects.filter(client__email=user)
        records = []
        if onboardings:
            for data in onboardings:
                record = {
                    "employee_name": data.employee.first_name
                    + " "
                    + data.employee.last_name,
                    "country": data.country,
                    "job_title": data.job_title,
                    "employment_term": data.employment_term,
                    "joining_date": data.joining_date,
                    "benefits": data.employee.benefits,
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Leave_Request(APIView):
    @swagger_auto_schema(
        tags=["Team : Time Off"],
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Status filter (all, pending, completed, rejected)",
                type=openapi.TYPE_STRING,
                enum=["all", "pending", "completed", "rejected"],
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                            "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "country": openapi.Schema(type=openapi.TYPE_STRING),
                            "department": openapi.Schema(type=openapi.TYPE_STRING),
                            "leave_type": openapi.Schema(type=openapi.TYPE_STRING),
                            "start_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "end_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "sandwich_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "total": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "reason": openapi.Schema(type=openapi.TYPE_STRING),
                            "requested_at": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                            ),
                            "status": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_summary="Endpoint to retrieve Leave request data.",
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        get_status = request.query_params.get("status")
        if (
            get_status == "pending"
            or get_status == "completed"
            or get_status == "rejected"
        ):
            leave_requests = leave_request.objects.filter(
                onboarding_id__client__email=user, status=get_status
            )
        elif get_status == "all":
            leave_requests = leave_request.objects.filter(
                onboarding_id__client__email=user
            )
        records = []

        if leave_requests:
            for data in leave_requests:
                employee_serializer = EmployeeSerializer(data.onboarding_id.employee)
                employee_data = employee_serializer.data

                record = {
                    "id": data.id,
                    "employee_id": employee_data.get("employee_id", ""),
                    "employee_name": employee_data.get("first_name", " "),
                    "country": data.onboarding_id.country,
                    "department": employee_data.get("department", ""),
                    "leave_type": data.leave_type,
                    "start_date": data.start_date,
                    "end_date": data.end_date,
                    "count": data.count,
                    "reason": data.reason,
                    "requested_at": data.created_at,
                    "status": data.status,
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Team : Time Off"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=["completed", "rejected"]
                ),
            },
            required=["status"],
        ),
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="id of the record",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful update"),
            204: openapi.Response(description="No content"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_summary="Endpoint to update the status of a leave request.",
        operation_id="2",
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        request_id = request.query_params.get("id")
        to_update_status = request.data["status"]
        try:
            to_update_leave_request = leave_request.objects.get(id=request_id)
            if to_update_leave_request:
                to_update_leave_request.status(to_update_status)
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
        tags=["Team : Time Off"],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "casual_leaves": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "sick_leaves": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "annual_leaves": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "taken": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "balance": openapi.Schema(type=openapi.TYPE_INTEGER),
                        },
                    ),
                ),
            ),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to retrieve leave balance data.",
        operation_id="3",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        leave_balances = leave_balance.objects.filter(onboarding_id__client__email=user)
        records = []

        if leave_balances:
            for data in leave_balances:
                employee_serializer = EmployeeSerializer(data.onboarding_id.employee)
                employee_data = employee_serializer.data
                print(employee_data)
                employee_name = f"{employee_data.get('first_name', '')} {employee_data.get('last_name', '')}"

                record = {
                    "employee_name": employee_name,
                    "casual_leaves": data.casual_leaves["balance"],
                    "sick_leaves": data.sick_leaves["balance"],
                    "annual_leaves": data.annual_leaves["balance"],
                    "taken": data.casual_leaves["availed"]
                    + data.sick_leaves["availed"]
                    + data.annual_leaves["availed"],
                    "balance": data.casual_leaves["balance"]
                    + data.sick_leaves["balance"]
                    + data.annual_leaves["balance"],
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ClockInOut_Request(APIView):
    @swagger_auto_schema(
        tags=["Team : Time Off"],
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Status filter (all, pending, completed, rejected)",
                type=openapi.TYPE_STRING,
                enum=["all", "pending", "completed", "rejected"],
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                            "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "punch_time": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                            ),
                            "punch_type": openapi.Schema(type=openapi.TYPE_STRING),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                            "status": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_summary="Endpoint to retrieve clock IN and OUT request data.",
        operation_id="4",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        get_status = request.query_params.get("status")
        if (
            get_status == "pending"
            or get_status == "completed"
            or get_status == "rejected"
        ):
            clockinout_requests = clockinout_request.objects.filter(
                onboarding_id__client__email=user, status=get_status
            )
        elif get_status == "all":
            clockinout_requests = clockinout_request.objects.filter(
                onboarding_id__client__email=user
            )
        records = []

        if clockinout_requests:
            for data in clockinout_requests:
                employee_serializer = EmployeeSerializer(data.onboarding_id.employee)
                employee_data = employee_serializer.data

                record = {
                    "id": data.id,
                    "employee_id": employee_data.get("employee_id", ""),
                    "employee_name": employee_data.get("username", ""),
                    "date": data.date,
                    "punch_time": data.punch_time,
                    "punch_type": data.punch_type,
                    "description": data.description,
                    "status": data.status,
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Team : Time Off"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=["completed", "rejected"]
                ),
            },
            required="status",
        ),
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="id of the record",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful update"),
            204: openapi.Response(description="No content"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_summary="Endpoint to update the status of a clock in/out record.",
        operation_id="5",
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        request_id = request.query_params.get("id")
        to_update_status = request.data["status"]
        try:
            to_update_clockinout_request = clockinout_request.objects.get(id=request_id)
            if to_update_clockinout_request:
                to_update_clockinout_request.status = to_update_status
                to_update_clockinout_request.save()

                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Download_Report(APIView):
    @swagger_auto_schema(
        tags=["Team : Time Off"],
        manual_parameters=[
            openapi.Parameter(
                "tab",
                openapi.IN_QUERY,
                description="Download tab filter",
                type=openapi.TYPE_STRING,
                enum=["lr", "lb", "cio"],
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response("Successful Download"),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_summary="Endpoint to download report.",
        operation_id="6",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        get_tab = request.query_params.get("tab")

        if get_tab not in ["lr", "lb", "cio"]:
            return Response(
                {"error": "Invalid 'tab' value."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if get_tab == "lr":
                records = leave_request.objects.filter(
                    onboarding_id__client__email=user
                )
                current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"leaveRequestReport_{current_datetime}.pdf"
                table_headers = [
                    "Employee ID",
                    "Employee Name",
                    "Country",
                    "Department",
                    "Leave Type",
                    "Count",
                    "Requested At",
                    "Status",
                ]
                FileHeading = "Leave Request"
                table_data = [table_headers]
                raw_data = []
                for data in records:
                    employee_serializer = EmployeeSerializer(
                        data.onboarding_id.employee
                    )
                    employee_data = employee_serializer.data

                    row_data = [
                        str(employee_data.get("employee_id", "")),
                        str(employee_data.get("username", "")),
                        str(data.onboarding_id.country),
                        str(employee_data.get("department", "")),
                        str(data.leave_type),
                        str(data.count),
                        str(data.created_at),
                        str(data.status),
                    ]
                    table_data.append(row_data)
                    raw_data.append(f"Raw Data for {get_tab}: {data}")
                col_widths = [65, 80, 70, 70, 60, 35, 150, 60]
            elif get_tab == "cio":
                records = clockinout_request.objects.filter(
                    onboarding_id__client__email=user
                )
                current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"ClockInOutReport{current_datetime}.pdf"
                table_headers = [
                    "Employee ID",
                    "Employee Name",
                    "Date",
                    "Punch Time",
                    "Punch Type",
                    "Status",
                ]
                FileHeading = "Clock In Out Request"
                table_data = [table_headers]
                raw_data = []
                for data in records:
                    employee_serializer = EmployeeSerializer(
                        data.onboarding_id.employee
                    )
                    employee_data = employee_serializer.data

                    row_data = [
                        str(employee_data.get("employee_id", "")),
                        str(employee_data.get("username", "")),
                        str(data.date),
                        str(data.punch_time),
                        str(data.punch_type),
                        str(data.status),
                    ]
                    table_data.append(row_data)
                    raw_data.append(f"Raw Data for {get_tab}: {data}")
                col_widths = [100, 100, 80, 80, 80, 80]
            elif get_tab == "lb":
                records = leave_balance.objects.filter(
                    onboarding_id__client__email=user
                )
                current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"leaveBalanceReport{current_datetime}.pdf"
                table_headers = [
                    "Employee Name",
                    "Casual Leave",
                    "Sick Leave",
                    "Annual Leave",
                    "Taken",
                    "Balance",
                ]
                FileHeading = "Leave Balance"
                table_data = [table_headers]
                raw_data = []
                for data in records:
                    employee_serializer = EmployeeSerializer(
                        data.onboarding_id.employee
                    )
                    employee_data = employee_serializer.data

                    row_data = [
                        str(employee_data.get("username", "")),
                        str(data.casual_leaves["balance"]),
                        str(data.sick_leaves["balance"]),
                        str(data.annual_leaves["balance"]),
                        str(
                            data.casual_leaves["availed"]
                            + data.sick_leaves["availed"]
                            + data.annual_leaves["availed"],
                        ),
                        str(
                            data.casual_leaves["balance"]
                            + data.sick_leaves["balance"]
                            + data.annual_leaves["balance"],
                        ),
                    ]
                    table_data.append(row_data)
                    raw_data.append(f"Raw Data for {get_tab}: {data}")
                col_widths = [100, 100, 80, 80, 80, 80]
            if records.exists():
                response = HttpResponse(content_type="application/pdf")
                response["Content-Disposition"] = f'attachment; filename="{filename}"'

                # Create PDF document
                pdf_buffer = HttpResponse(content_type="application/pdf")
                pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)

                # Create table and style
                pdf_table = Table(table_data, colWidths=col_widths)
                style = TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )

                pdf_table.setStyle(style)

                # Create paragraph for raw data
                styles = getSampleStyleSheet()

                # Build PDF document
                elements = []

                # Draw centered heading using the canvas object
                heading = FileHeading
                elements.append(Paragraph(heading, styles["Title"]))

                # Add a line break
                elements.append(Paragraph("<br/>", styles["Normal"]))

                # Add the table
                elements.append(pdf_table)

                # Add a line break
                elements.append(Paragraph("<br/>", styles["Normal"]))

                pdf.build(elements)

                response.write(pdf_buffer.getvalue())
                return response
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UpdateUserNameView(APIView):
    @swagger_auto_schema(
        tags=["Oragnization : Settings"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "companyName": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["companyName"],
        ),
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful update"),
            204: openapi.Response(description="No content"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="UnAuthorize"),
        },
        operation_summary="Update company name/user name in the database or settings.",
        operation_id="3",
    )
    def patch(self, request):
        user = request.user
        new_user_name = request.data.get("companyName")
        if new_user_name:
            record = end_user.objects.get(email=user)
            record.username = new_user_name
            record.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid data provided"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UploadPictureView(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Oragnization : Settings"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="picture",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful upload"),
            204: openapi.Response(description="No content"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="UnAuthorize"),
        },
        operation_summary="Upload a picture.",
        operation_id="2",
    )
    def post(self, request):
        picture_file = request.FILES.get("picture")
        if picture_file:
            file_name = default_storage.save(
                picture_file.name, ContentFile(picture_file.read())
            )
            return Response(
                {"message": "Picture uploaded successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"error": "No picture provided"}, status=status.HTTP_400_BAD_REQUEST
            )


class UpdatePasswordView(APIView):
    @swagger_auto_schema(
        tags=["Oragnization : Settings"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["password"],
        ),
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful update"),
            204: openapi.Response(description="No content"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="UnAuthorize"),
        },
        operation_summary="Update new password in the database or settings.",
        operation_id="1",
    )
    def patch(self, request):
        user = request.user
        new_password = request.data.get("password")
        if new_password:
            record = end_user.objects.get(email=user)
            record.set_password(new_password)
            record.save()
            return Response(
                {"message": "Password updated successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid data provided"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Time_Tracking(APIView):
    @swagger_auto_schema(
        tags=["Team : Time Tracking"],
        operation_summary="Get time tracking data",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "year",
                openapi.IN_QUERY,
                description="Filter by year",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "month",
                openapi.IN_QUERY,
                description="Filter by month",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "emp_id",
                openapi.IN_QUERY,
                description="Filter by employee ID",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "employees": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "employee_id": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                        ),
                        "time_sheet": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATE,
                                    ),
                                    "check_in": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATETIME,
                                    ),
                                    "check_out": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATETIME,
                                    ),
                                    "hours_worked": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATETIME,
                                    ),
                                    "over_time": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATETIME,
                                    ),
                                    "status": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "Present": openapi.Schema(
                                                type=openapi.TYPE_BOOLEAN
                                            ),
                                            "Missing": openapi.Schema(
                                                type=openapi.TYPE_BOOLEAN
                                            ),
                                            "Absent": openapi.Schema(
                                                type=openapi.TYPE_BOOLEAN
                                            ),
                                            "Short Duration": openapi.Schema(
                                                type=openapi.TYPE_BOOLEAN
                                            ),
                                            "Day Of": openapi.Schema(
                                                type=openapi.TYPE_BOOLEAN
                                            ),
                                            "Full Leave": openapi.Schema(
                                                type=openapi.TYPE_BOOLEAN
                                            ),
                                        },
                                    ),
                                },
                            ),
                        ),
                    },
                ),
            ),
            206: openapi.Response(description="Partial Content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        employee_id = request.query_params.get("emp_id")
        available_employees = onboarding.objects.filter(
            client__email=user, status="active"
        )
        serialized_available_employees = TimeSheetEmployeeSerializer(
            available_employees, many=True
        ).data
        for record in serialized_available_employees:
            emp_record = employee.objects.get(email=record["employee_id"])
            record["name"] = emp_record.first_name + " " + emp_record.last_name
        if month and year and employee_id:
            time_sheet_data = time_sheet.objects.filter(
                month=month, year=year, onboarding_id__employee__employee_id=employee_id
            )
            serialized_time_sheet_data = TimeSheetSerializer(
                time_sheet_data, many=True
            ).data
            if serialized_time_sheet_data:
                time_sheet_records = []
                record = serialized_time_sheet_data[0]["record"]
                keys = record.keys()
                for key in keys:
                    dic_record = {}
                    dic_record["date"] = key
                    dic_record.update(record[key])
                    time_sheet_records.append(dic_record)

                if serialized_time_sheet_data:
                    return Response(
                        {
                            "employees": serialized_available_employees,
                            "time_sheet": time_sheet_records,
                        },
                        status=status.HTTP_200_OK,
                    )
            else:
                return Response(
                    {"employees": serialized_available_employees, "time_sheet": {}},
                    status=status.HTTP_206_PARTIAL_CONTENT,
                )

        else:
            return Response(
                {"employees": serialized_available_employees, "time_sheet": {}},
                status=status.HTTP_200_OK,
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Invoice_Payments(APIView):
    @swagger_auto_schema(
        tags=["Payments : Invoice Payment"],
        operation_summary="Get invoice payment data",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "payment_status",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["Pending", "Processing", "Paid"],
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "employee_invoices": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "employee_name": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "invoice_date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATE,
                                    ),
                                    "due_date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATE,
                                    ),
                                    "invoice_amount": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                    "payment_status": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "download": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        ),
                        "other_payments": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "invoice_reference": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "invoice_date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATE,
                                    ),
                                    "due_date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATE,
                                    ),
                                    "invoice_amount": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                    "payment_status": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "download": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        ),
                    },
                ),
            ),
            204: openapi.Response(description="No content"),
            401: openapi.Response(description="UnAuthorize"),
        },
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        pay_status = request.query_params.get("payment_status")
        no_val = 0

        emp_invoices = employee_invoice.objects.filter(
            onboarding_id__client__email=user, payment_status=pay_status
        )
        other_pays = other_payment.objects.filter(
            client__email=user, payment_status=pay_status
        )
        records = {}
        if emp_invoices:
            emp_inv_records = []
            for data in emp_invoices:
                record = {
                    "id": data.id,
                    "employee_name": data.onboarding_id.employee.first_name
                    + " "
                    + data.onboarding_id.employee.last_name,
                    "invoice_date": data.invoice_date,
                    "due_date": data.due_date,
                    "invoice_amount": data.invoice_amount,
                    "payment_status": pay_status,
                    "download": data.invoice,
                }
                emp_inv_records.append(record)
            records["employee_invoices"] = emp_inv_records
        else:
            no_val += 1
            records["employee_invoices"] = []
        if other_pays:
            other_pays_records = []
            for data in other_pays:
                record = {
                    "id": data.id,
                    "invoice_reference": data.invoice_reference,
                    "invoice_date": data.invoice_date,
                    "due_date": data.due_date,
                    "invoice_amount": data.invoice_amount,
                    "payment_status": pay_status,
                    "download": data.invoice,
                }
            other_pays_records.append(record)
            records["other_payments"] = other_pays_records
        else:
            no_val += 1
            records["other_payments"] = []
        if no_val < 2:
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Payments : Invoice Payment"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "category": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=["employee_invoice", "other_payment"]
                ),
                "payment_status": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=["Pending", "Processing", "Paid"]
                ),
            },
            required=["category", "payment_status"],
        ),
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "id",
                in_=openapi.IN_QUERY,
                description="ID of the invoice payment to update",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response("Successfully updated invoice payment status"),
            400: openapi.Response("Bad request"),
            401: openapi.Response("Un Authorize"),
        },
        operation_id="2",
    )
    def patch(self, request, *args, **kwargs):

        user = request.user
        id = request.query_params.get("id")
        category = request.data["category"]
        new_pay_status = request.data["payment_status"]
        if category == "employee_invoice":
            try:
                to_update_invoice_payments = employee_invoice.objects.get(id=id)
                to_update_invoice_payments.payment_status = new_pay_status
                to_update_invoice_payments.save()
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif category == "other_payment":
            try:
                to_update_invoice_payments = other_payment.objects.get(id=id)
                to_update_invoice_payments.payment_status = new_pay_status
                to_update_invoice_payments.save()
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
