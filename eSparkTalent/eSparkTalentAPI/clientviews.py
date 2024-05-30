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
from django.http import Http404, HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.parsers import MultiPartParser
from eSparkTalent.settings import talent_email
import calendar
from datetime import datetime, timedelta
from .bucket_functions import remove_bucket_file
import datetime
from django.utils import timezone
from django.db.models import Q
from string import capwords
import os
from django.conf import settings


class LoginView(APIView):
    @swagger_auto_schema(
        tags=["Authentication Login"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    default="superadmin@esparkconsultants.com",
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    default="super@espark",
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
                        "client_image": openapi.Schema(type=openapi.TYPE_FILE),
                        "company_image": openapi.Schema(type=openapi.TYPE_FILE),
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
        hiring_request_count = hiring_request.objects.filter(client_id=user).count()
        interview_schedule_count = interview_schedule.objects.filter(
            client_id=user
        ).count()
        onboarding_count = onboarding.objects.filter(client_id=user).count()
        active_employee = outsource_employees.objects.filter(
            client_id=user, status="active"
        ).count()

        try:
            client_data = client.objects.get(email=user)
            image_path = client_data.image.url
            c_email = client_data.email
        except client.DoesNotExist:
            c_email = ""
            image_path = None

        try:
            company_record = company_data.objects.get(id=1)
            company_image = company_record.image.url
        except company_data.DoesNotExist:
            company_image = ""

        data = {
            "username": user.username,
            "c_email": c_email,
            "hiring_request_count": hiring_request_count,
            "interview_schedule_count": interview_schedule_count,
            "onboarding_count": onboarding_count,
            "active_employee": active_employee,
            "client_image": image_path,
            "company_image": company_image,
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
            required=[
                "job_title",
                "role_type",
                "gender",
                "employment_term",
                "salary_range",
                "country",
                "hiring_start_date",
                "hiring_end_date",
            ],
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
            try:
                client_1 = client.objects.get(email=request.user)
                hr_req = hiring_request.objects.create(
                    client_id=client_1.email,
                    job_title=serializer.validated_data["job_title"],
                    role_type=serializer.validated_data["role_type"],
                    gender=serializer.validated_data["gender"],
                    employment_term=serializer.validated_data["employment_term"],
                    salary_range=serializer.validated_data["salary_range"],
                    country=serializer.validated_data["country"],
                    hiring_start_date=serializer.validated_data["hiring_start_date"],
                    hiring_end_date=serializer.validated_data["hiring_end_date"],
                )

                notifications.objects.create(
                    email=talent_email,
                    ref_id=hr_req.id,
                    notification_type="hiring_request",
                    status="added",
                    description="A new hiring request created.",
                )
                return Response(
                    {
                        "message": "One new request is successfully added to hiring.",
                        "id": hr_req.id,
                    },
                    status=status.HTTP_201_CREATED,
                )

            except client.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
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
                        required=[
                            "job_title",
                            "role_type",
                            "gender",
                            "employment_term",
                            "salary_range",
                            "country",
                            "hiring_start_date",
                            "hiring_end_date",
                        ],
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
        hiring_requests = hiring_request.objects.filter(client_id=user)

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
            hiring_request.objects.get(id=delete_id).delete()
            notifications.objects.get(
                ref_id=delete_id, notification_type="hiring_request"
            ).delete()
            return Response(
                {"message": "Hiring request is successfully deleted"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
                                type=openapi.TYPE_STRING,
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
        interview_schedules = interview_schedule.objects.filter(client_id=user)
        records = []
        if interview_schedules:
            for data in interview_schedules:
                record = {
                    "id": data.id,
                    "employee_name": data.employee_name,
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
                    type=openapi.TYPE_STRING,
                    enum=["pending", "rejected", "short_list", "hold"],
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
    def patch(self, request, *args, **kwargs):
        user = request.user
        request_id = request.query_params.get("id")
        to_update_status = request.data["status"]
        try:
            to_update_interview_status = interview_schedule.objects.get(id=request_id)
            if to_update_interview_status:
                to_update_interview_status.status = to_update_status
                to_update_interview_status.save()
                notifi = notifications.objects.get(
                    ref_id=request_id,
                    notification_type="interview_schedule",
                )
                notifi.email = talent_email
                notifi.status = to_update_status
                notifi.description = f"Candidate has been {to_update_status}"
                notifi.save()

                return Response(
                    {"message": f"One new interviewee is {to_update_status}"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        except interview_schedule.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
                                type=openapi.TYPE_STRING,
                            ),
                            "joining_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "notice_period": openapi.Schema(type=openapi.TYPE_INTEGER),
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
        onboardings = onboarding.objects.filter(client_id=user)
        records = []
        if onboardings:
            for data in onboardings:
                record = {
                    "employee_name": data.employee_name,
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
                            "role_type": openapi.Schema(type=openapi.TYPE_STRING),
                            "employment_term": openapi.Schema(
                                type=openapi.TYPE_STRING,
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
        records = []
        get_status = request.query_params.get("status")
        if get_status == "active" or get_status == "terminated":
            onboardings = outsource_employees.objects.filter(
                client_id=user, status=get_status
            )
            if onboardings:
                for data in onboardings:
                    employee_data = employee.objects.get(email=data.employee_id)
                    record = {
                        "employee_name": employee_data.first_name
                        + " "
                        + employee_data.last_name,
                        "country": data.country,
                        "job_title": data.job_title,
                        "employment_term": data.employment_term,
                        "joining_date": data.joining_date,
                        "benefits": data.benefits,
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        elif get_status == "onboard":
            onboardings = onboarding.objects.filter(client_id=user)
            if onboardings:
                for data in onboardings:
                    record = {
                        "employee_name": data.employee_name,
                        "country": data.country,
                        "role_type": data.role_type,
                        "job_title": data.job_title,
                        "joining_date": data.joining_date,
                        "benefits": data.benefits,
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        elif get_status == "all":
            onboardings = onboarding.objects.filter(client_id=user)
            outsource = outsource_employees.objects.filter(client_id=user)
            if onboardings or outsource:
                for data in onboardings:
                    record = {
                        "employee_name": data.employee_name,
                        "country": data.country,
                        "job_title": data.job_title,
                        "employment_term": data.employment_term,
                        "joining_date": data.joining_date,
                        "benefits": data.benefits,
                    }
                    records.append(record)
                for data in outsource:
                    employee_data = employee.objects.get(email=data.employee_id)
                    record = {
                        "employee_name": employee_data.first_name
                        + " "
                        + employee_data.last_name,
                        "country": data.country,
                        "job_title": data.job_title,
                        "employment_term": data.employment_term,
                        "joining_date": data.joining_date,
                        "benefits": data.benefits,
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "Invalid status parameter"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
                            "check_in": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                            ),
                            "check_out": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                            ),
                            "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "reason": openapi.Schema(type=openapi.TYPE_STRING),
                            "requested_at": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
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
                client_id=user, status=get_status
            )
        elif get_status == "all":
            leave_requests = leave_request.objects.filter(client_id=user)
        records = []

        if leave_requests:
            for data in leave_requests:
                user = request.user
                employee_serializer = EmployeeSerializer(
                    employee.objects.get(email=data.employee_id)
                )
                employee_data = employee_serializer.data
                outsource = outsource_employees.objects.get(
                    employee_id=data.employee_id, client_id=user
                )

                try:
                    check_in = employee_data.get("punch_timings")["check_in"]
                    check_out = employee_data.get("punch_timings")["check_out"]
                except:
                    check_in = ""
                    check_out = ""

                employee_name = f"{employee_data.get('first_name', '')} {employee_data.get('last_name', '')}"
                record = {
                    "id": data.id,
                    "employee_id": employee_data.get("employee_id"),
                    "employee_name": employee_name,
                    "country": outsource.country,
                    "department": outsource.job_title,
                    "leave_type": data.leave_type,
                    "start_date": data.start_date,
                    "end_date": data.end_date,
                    "check_in": check_in,
                    "check_out": check_out,
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
        operation_summary="Update leave request status",
        operation_id="2",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=["completed", "rejected"]
                ),
            },
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
            200: "Leave request status updated successfully.",
            204: "Leave request not found or no content.",
            400: "Bad request.",
        },
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        request_id = request.query_params.get("id")
        to_update_status = request.data.get("status")

        try:
            to_update_leave_request = leave_request.objects.get(id=request_id)

            if to_update_leave_request and to_update_leave_request.status == "pending":
                to_update_leave_request.status = to_update_status
                emp_rec = employee.objects.get(
                    email=to_update_leave_request.employee_id
                )

                if to_update_status == "completed":
                    try:
                        leave_balances_instance = leave_balance.objects.get(
                            employee_id=to_update_leave_request.employee_id
                        )
                        now = datetime.datetime.now().date()
                        start_date = to_update_leave_request.start_date
                        end_date = to_update_leave_request.end_date

                        start_month = start_date.strftime("%B")
                        end_month = end_date.strftime("%B")

                        start_year = start_date.strftime("%Y")
                        end_year = end_date.strftime("%Y")

                        time_sheet_record=time_sheet.objects.filter(
                            Q(employee_id= to_update_leave_request.employee_id, client_id= to_update_leave_request.client_id),
                            Q(
                                month__gte=start_month,
                                year__gte=start_year,
                            )
                            & Q(
                                month__lte=end_month,
                                year__lte=end_year,
                            ),
                        )
                        if now >= start_date:
                            for timesheet in time_sheet_record:
                                for key in timesheet.record:
                                    if datetime.datetime.strptime(key, "%d-%m-%Y") >= datetime.datetime.strptime(start_date.strftime("%d-%m-%Y"), "%d-%m-%Y") and datetime.datetime.strptime(key, "%d-%m-%Y") <= datetime.datetime.strptime(end_date.strftime("%d-%m-%Y"), "%d-%m-%Y"):
                                        if timesheet.record[key]["status"]["Day Off"] == False:
                                            timesheet.record[key]={
                                                "check_in": "-",
                                                "check_out": "-",
                                                "hours_worked": "-",
                                                "overtime": "-",
                                                "status": {
                                                    "Present": False,
                                                    "Missing": False,
                                                    "Absent": False,
                                                    "Day Off": False,
                                                    "Full Leave": True,
                                                    "Short Duration": False,
                                                },
                                            }
                                timesheet.save()
                        leave_records=leave_request.objects.filter(
                            Q(employee_id = to_update_leave_request.employee_id,
                                client_id = to_update_leave_request.client_id,
                                leave_type = to_update_leave_request.leave_type,
                                status = "completed"),
                            Q(
                                start_date__lte = to_update_leave_request.end_date
                            ) &
                            Q(
                                end_date__gte = to_update_leave_request.start_date
                            )
                        ).exclude(id=to_update_leave_request.id)

                        current_leaves_diff = to_update_leave_request.end_date - to_update_leave_request.start_date
                        current_leaves_days = [to_update_leave_request.start_date + timedelta(days=i) for i in range(current_leaves_diff.days + 1)]

                        if leave_records:
                            for leave in leave_records:
                                leaves_diff = leave.end_date - leave.start_date
                                leaves_days = [leave.start_date + timedelta(days=i) for i in range(leaves_diff.days+1)]
                                if leave.count!=0:
                                    count_minus=0
                                    for i in current_leaves_days:
                                        if i in leaves_days:
                                            count_minus += 1
                                            current_leaves_days.remove(i)
                                    to_update_leave_request.count -= count_minus
                        if to_update_leave_request.leave_type == "casual":
                            leave_balances_instance.casual_leaves["balance"] = int(
                                leave_balances_instance.casual_leaves["balance"]
                            ) - int(to_update_leave_request.count)
                            leave_balances_instance.casual_leaves["availed"] = int(
                                leave_balances_instance.casual_leaves["availed"]
                            ) + int(to_update_leave_request.count)
                        elif to_update_leave_request.leave_type == "sick":
                            leave_balances_instance.sick_leaves["balance"] = int(
                                leave_balances_instance.sick_leaves["balance"]
                            ) - int(to_update_leave_request.count)
                            leave_balances_instance.sick_leaves["availed"] = int(
                                leave_balances_instance.sick_leaves["availed"]
                            ) + int(to_update_leave_request.count)
                        elif to_update_leave_request.leave_type == "annual":
                            leave_balances_instance.annual_leaves["balance"] = int(
                                leave_balances_instance.annual_leaves["balance"]
                            ) - int(to_update_leave_request.count)
                            leave_balances_instance.annual_leaves["availed"] = int(
                                leave_balances_instance.annual_leaves["availed"]
                            ) + int(to_update_leave_request.count)
                        elif to_update_leave_request.leave_type == "hajj":
                            leave_balances_instance.hajj_leaves["balance"] = int(
                                leave_balances_instance.hajj_leaves["balance"]
                            ) - int(to_update_leave_request.count)
                            leave_balances_instance.hajj_leaves["availed"] = int(
                                leave_balances_instance.hajj_leaves["availed"]
                            ) + int(to_update_leave_request.count)
                        elif to_update_leave_request.leave_type == "paid":
                            leave_balances_instance.paid_leaves["balance"] = int(
                                leave_balances_instance.paid_leaves["balance"]
                            ) - int(to_update_leave_request.count)
                            leave_balances_instance.paid_leaves["availed"] = int(
                                leave_balances_instance.paid_leaves["availed"]
                            ) + int(to_update_leave_request.count)
                        elif to_update_leave_request.leave_type == "unpaid":
                            leave_balances_instance.unpaid_leaves["balance"] = int(
                                leave_balances_instance.unpaid_leaves["balance"]
                            ) - int(to_update_leave_request.count)
                            leave_balances_instance.unpaid_leaves["availed"] = int(
                                leave_balances_instance.unpaid_leaves["availed"]
                            ) + int(to_update_leave_request.count)

                        leave_balances_instance.save()
                        to_update_leave_request.save()
                        message = f"{emp_rec.first_name} {emp_rec.last_name} {to_update_leave_request.leave_type} leave request is accepted"

                    except leave_balance.DoesNotExist:
                        return Response(
                            {
                                "error": "No leave_balance record found for the specified employee_id"
                            },
                            status=status.HTTP_404_NOT_FOUND,
                        )
                else:
                    message = f"{emp_rec.first_name} {emp_rec.last_name} {to_update_leave_request.leave_type} leave request is {to_update_status}"
                    to_update_leave_request.save()
                notifi = notifications.objects.get(
                    ref_id=request_id, notification_type="leave_request"
                )
                notifi.email = to_update_leave_request.employee_id
                notifi.status = to_update_status
                notifi.description = f"leave request has been {to_update_status}"
                notifi.save()

                return Response({"message": message}, status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        except leave_request.DoesNotExist:
            return Response(
                {"error": "No leave_request record found for the specified id"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
        outsource = outsource_employees.objects.filter(client_id=user)

        records = []

        if outsource:
            for data in outsource:
                leave_balances_queryset = leave_balance.objects.get(
                    employee_id=data.employee_id
                )
                if leave_balances_queryset:
                    leave_balances = leave_balances_queryset
                    employee_serializer = EmployeeSerializer(
                        employee.objects.get(email=data.employee_id)
                    )
                    employee_data = employee_serializer.data
                    employee_name = f"{employee_data.get('first_name', '')} {employee_data.get('last_name', '')}"

                    record = {
                        "employee_name": employee_name,
                        "casual_leaves": leave_balances_queryset.casual_leaves[
                            "balance"
                        ],
                        "sick_leaves": leave_balances.sick_leaves["balance"],
                        "annual_leaves": leave_balances.annual_leaves["balance"],
                        "taken": int(leave_balances.casual_leaves["availed"])
                        + int(leave_balances.sick_leaves["availed"])
                        + int(leave_balances.annual_leaves["availed"]),
                        "balance": int(leave_balances.casual_leaves["balance"])
                        + int(leave_balances.sick_leaves["balance"])
                        + int(leave_balances.annual_leaves["balance"]),
                    }
                    records.append(record)
                else:
                    raise Http404(
                        "No leave_balance records for the specified employee_id"
                    )

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
                            "punch_time": openapi.Schema(type=openapi.TYPE_STRING),
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
            clockinout_requests = punch_request.objects.filter(
                client_id=user, status=get_status
            )
        elif get_status == "all":
            clockinout_requests = punch_request.objects.filter(client_id=user)
        records = []

        if clockinout_requests:
            for data in clockinout_requests:
                employee_serializer = EmployeeSerializer(
                    employee.objects.get(email=data.employee_id)
                )
                employee_data = employee_serializer.data

                record = {
                    "id": data.id,
                    "employee_id": employee_data.get("employee_id", ""),
                    "employee_name": employee_data.get("first_name", "")
                    + " "
                    + employee_data.get("last_name", ""),
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
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="UnAuthorize"),
            404: openapi.Response(description="Not Found"),
        },
        operation_summary="Endpoint to update the status of a clock in/out record.",
        operation_id="5",
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        request_id = request.query_params.get("id")
        to_update_status = request.data.get("status")
        if to_update_status == "completed":
            try:
                to_update_clockinout_request = punch_request.objects.get(id=request_id)
                if to_update_clockinout_request.status == "pending":
                    emp_req = employee.objects.get(
                        email=to_update_clockinout_request.employee_id
                    )
                    check_in = emp_req.punch_timings["check_in"]
                    check_out = emp_req.punch_timings["check_out"]
                    working_hours = datetime.datetime.strptime(
                        check_out, "%I:%M %p"
                    ) - datetime.datetime.strptime(check_in, "%I:%M %p")
                    try:
                        record_punch_type = to_update_clockinout_request.punch_type
                        if record_punch_type == "check_in":
                            try:
                                timesheet_record = time_sheet.objects.get(
                                    employee_id=to_update_clockinout_request.employee_id,
                                    client_id=user,
                                    month=calendar.month_name[
                                        to_update_clockinout_request.date.month
                                    ],
                                    year=to_update_clockinout_request.date.year,
                                )
                                if (
                                    to_update_clockinout_request.date.strftime(
                                        "%d-%m-%Y"
                                    )
                                    in timesheet_record.record
                                ):
                                    timesheet_record.record[
                                        to_update_clockinout_request.date.strftime(
                                            "%d-%m-%Y"
                                        )
                                    ][
                                        "check_in"
                                    ] = to_update_clockinout_request.punch_time
                                    timesheet_record.record[
                                        to_update_clockinout_request.date.strftime(
                                            "%d-%m-%Y"
                                        )
                                    ]["status"]["Present"] = True
                                    timesheet_record.record[
                                        to_update_clockinout_request.date.strftime(
                                            "%d-%m-%Y"
                                        )
                                    ]["status"]["Absent"] = False
                                    if (
                                        timesheet_record.record[
                                            to_update_clockinout_request.date.strftime(
                                                "%d-%m-%Y"
                                            )
                                        ]["check_out"]
                                        == "-"
                                    ):
                                        if datetime.datetime.strptime(
                                            to_update_clockinout_request.date.strftime(
                                                "%d-%m-%Y"
                                            ),
                                            "%d-%m-%Y",
                                        ) < datetime.datetime.strptime(
                                            datetime.datetime.now()
                                            .date()
                                            .strftime("%d-%m-%Y"),
                                            "%d-%m-%Y",
                                        ):
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["status"]["Missing"] = True
                                            timesheet_record.save()
                                            to_update_clockinout_request.status = (
                                                to_update_status
                                            )
                                            to_update_clockinout_request.save()
                                            notifi = notifications.objects.get(
                                                ref_id=request_id,
                                                notification_type="punch_request",
                                            )
                                            notifi.email = (
                                                to_update_clockinout_request.employee_id
                                            )
                                            notifi.status = to_update_status
                                            notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                            notifi.save()
                                            return Response(
                                                {
                                                    "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                                },
                                                status=status.HTTP_200_OK,
                                            )

                                        elif datetime.datetime.strptime(
                                            to_update_clockinout_request.date.strftime(
                                                "%d-%m-%Y"
                                            ),
                                            "%d-%m-%Y",
                                        ) == datetime.datetime.strptime(
                                            datetime.datetime.now()
                                            .date()
                                            .strftime("%d-%m-%Y"),
                                            "%d-%m-%Y",
                                        ):
                                            check_out_time = employee.objects.get(
                                                email=to_update_clockinout_request.employee_id
                                            ).punch_timings["check_out"]
                                            if (
                                                datetime.datetime.strptime(
                                                    check_out_time, "%I:%M %p"
                                                ).time()
                                                > datetime.datetime.now().time()
                                            ):
                                                timesheet_record.record[
                                                    to_update_clockinout_request.date.strftime(
                                                        "%d-%m-%Y"
                                                    )
                                                ]["status"]["Missing"] = False
                                                timesheet_record.save()
                                                to_update_clockinout_request.status = (
                                                    to_update_status
                                                )
                                                to_update_clockinout_request.save()
                                                notifi = notifications.objects.get(
                                                    ref_id=request_id,
                                                    notification_type="punch_request",
                                                )
                                                notifi.email = (
                                                    to_update_clockinout_request.employee_id
                                                )
                                                notifi.status = to_update_status
                                                notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                                notifi.save()
                                                return Response(
                                                    {
                                                        "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                                    },
                                                    status=status.HTTP_200_OK,
                                                )
                                            else:
                                                timesheet_record.record[
                                                    to_update_clockinout_request.date.strftime(
                                                        "%d-%m-%Y"
                                                    )
                                                ]["status"]["Missing"] = True
                                                timesheet_record.save()
                                                to_update_clockinout_request.status = (
                                                    to_update_status
                                                )
                                                to_update_clockinout_request.save()
                                                notifi = notifications.objects.get(
                                                    ref_id=request_id,
                                                    notification_type="punch_request",
                                                )
                                                notifi.email = (
                                                    to_update_clockinout_request.employee_id
                                                )
                                                notifi.status = to_update_status
                                                notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                                notifi.save()
                                                return Response(
                                                    {
                                                        "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                                    },
                                                    status=status.HTTP_200_OK,
                                                )

                                    else:
                                        check_out_time = datetime.datetime.strptime(
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["check_out"],
                                            "%I:%M:%S %p",
                                        )
                                        check_in_time = datetime.datetime.strptime(
                                            to_update_clockinout_request.punch_time,
                                            "%I:%M:%S %p",
                                        )

                                        if check_out_time < check_in_time:
                                            check_out_time = check_out_time + timedelta(
                                                days=1
                                            )

                                        hours_worked = check_out_time - check_in_time

                                        if hours_worked.total_seconds() // 3600 < int(
                                            working_hours.total_seconds() // 3600
                                        ):
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["overtime"] = "0h"
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ][
                                                "hours_worked"
                                            ] = f"{hours_worked.seconds//3600}h {(hours_worked.seconds //60) %60}m"
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["status"]["Short Duration"] = True
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["status"]["Missing"] = False
                                            timesheet_record.save()
                                            to_update_clockinout_request.status = (
                                                to_update_status
                                            )
                                            to_update_clockinout_request.save()
                                            notifi = notifications.objects.get(
                                                ref_id=request_id,
                                                notification_type="punch_request",
                                            )
                                            notifi.email = (
                                                to_update_clockinout_request.employee_id
                                            )
                                            notifi.status = to_update_status
                                            notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                            notifi.save()
                                            return Response(
                                                {
                                                    "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                                },
                                                status=status.HTTP_200_OK,
                                            )
                                        elif (
                                            hours_worked.total_seconds() // 3600
                                            >= int(
                                                working_hours.total_seconds() // 3600
                                            )
                                        ):
                                            overtime = (
                                                hours_worked
                                                - datetime.timedelta(
                                                    hours=int(
                                                        working_hours.total_seconds()
                                                        // 3600
                                                    )
                                                )
                                            )
                                            overtime_min = (overtime.seconds // 60) % 60
                                            overtime_hours = overtime.seconds // 3600
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ][
                                                "hours_worked"
                                            ] = f"{hours_worked.seconds//3600}h {(hours_worked.seconds //60) %60}m"
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["status"]["Short Duration"] = False
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["status"]["Missing"] = False
                                            if overtime_hours and overtime_min:
                                                over_duration = (
                                                    f"{overtime_hours}h {overtime_min}m"
                                                )
                                            elif overtime_hours and not overtime_min:
                                                over_duration = f"{overtime_hours}h"
                                            elif not overtime_hours and overtime_min:
                                                over_duration = f"{overtime_min}m"
                                            else:
                                                over_duration = "0h"
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["overtime"] = over_duration
                                            timesheet_record.save()
                                            to_update_clockinout_request.status = (
                                                to_update_status
                                            )
                                            to_update_clockinout_request.save()
                                            notifi = notifications.objects.get(
                                                ref_id=request_id,
                                                notification_type="punch_request",
                                            )
                                            notifi.email = (
                                                to_update_clockinout_request.employee_id
                                            )
                                            notifi.status = to_update_status
                                            notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                            notifi.save()
                                            return Response(
                                                {
                                                    "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                                },
                                                status=status.HTTP_200_OK,
                                            )

                                else:
                                    timesheet_record.record[
                                        to_update_clockinout_request.date.strftime(
                                            "%d-%m-%Y"
                                        )
                                    ] = {
                                        "check_in": to_update_clockinout_request.punch_time,
                                        "check_out": "-",
                                        "hours_worked": "-",
                                        "overtime": "-",
                                        "status": {
                                            "Present": True,
                                            "Missing": False,
                                            "Absent": False,
                                            "Day Off": False,
                                            "Full Leave": False,
                                            "Short Duration": False,
                                        },
                                    }
                                    timesheet_record.save()
                                    to_update_clockinout_request.status = (
                                        to_update_status
                                    )
                                    to_update_clockinout_request.save()
                                    notifi = notifications.objects.get(
                                        ref_id=request_id,
                                        notification_type="punch_request",
                                    )
                                    notifi.email = (
                                        to_update_clockinout_request.employee_id
                                    )
                                    notifi.status = to_update_status
                                    notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                    notifi.save()
                                    return Response(
                                        {
                                            "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                        },
                                        status=status.HTTP_200_OK,
                                    )

                            except:
                                if datetime.datetime.strptime(
                                    to_update_clockinout_request.date.strftime(
                                        "%d-%m-%Y"
                                    ),
                                    "%d-%m-%Y",
                                ) == datetime.datetime.strptime(
                                    datetime.datetime.now().date().strftime("%d-%m-%Y"),
                                    "%d-%m-%Y",
                                ):
                                    check_out_time = employee.objects.get(
                                        email=to_update_clockinout_request.employee_id
                                    ).punch_timings["check_out"]
                                    if (
                                        datetime.datetime.strptime(
                                            check_out_time, "%I:%M %p"
                                        ).time()
                                        > datetime.datetime.now().time()
                                    ):
                                        timesheet_record = time_sheet.objects.create(
                                            employee_id=to_update_clockinout_request.employee_id,
                                            client_id=user,
                                            month=calendar.month_name[
                                                to_update_clockinout_request.date.month
                                            ],
                                            year=to_update_clockinout_request.date.year,
                                            record={
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                ): {
                                                    "check_in": to_update_clockinout_request.punch_time,
                                                    "check_out": "-",
                                                    "hours_worked": "-",
                                                    "overtime": "-",
                                                    "status": {
                                                        "Present": True,
                                                        "Missing": False,
                                                        "Absent": False,
                                                        "Day Off": False,
                                                        "Full Leave": False,
                                                        "Short Duration": False,
                                                    },
                                                },
                                            },
                                        )
                                        to_update_clockinout_request.status = (
                                            to_update_status
                                        )
                                        to_update_clockinout_request.save()
                                        notifi = notifications.objects.get(
                                            ref_id=request_id,
                                            notification_type="punch_request",
                                        )
                                        notifi.email = (
                                            to_update_clockinout_request.employee_id
                                        )
                                        notifi.status = to_update_status
                                        notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                        notifi.save()
                                        return Response(
                                            {
                                                "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                            },
                                            status=status.HTTP_200_OK,
                                        )
                                    else:
                                        timesheet_record = time_sheet.objects.create(
                                            employee_id=to_update_clockinout_request.employee_id,
                                            client_id=user,
                                            month=calendar.month_name[
                                                to_update_clockinout_request.date.month
                                            ],
                                            year=to_update_clockinout_request.date.year,
                                            record={
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                ): {
                                                    "check_in": to_update_clockinout_request.punch_time,
                                                    "check_out": "-",
                                                    "hours_worked": "-",
                                                    "overtime": "-",
                                                    "status": {
                                                        "Present": True,
                                                        "Missing": True,
                                                        "Absent": False,
                                                        "Day Off": False,
                                                        "Full Leave": False,
                                                        "Short Duration": False,
                                                    },
                                                },
                                            },
                                        )
                                        to_update_clockinout_request.status = (
                                            to_update_status
                                        )
                                        to_update_clockinout_request.save()
                                        notifi = notifications.objects.get(
                                            ref_id=request_id,
                                            notification_type="punch_request",
                                        )
                                        notifi.email = (
                                            to_update_clockinout_request.employee_id
                                        )
                                        notifi.status = to_update_status
                                        notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                        notifi.save()
                                        return Response(
                                            {
                                                "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                            },
                                            status=status.HTTP_200_OK,
                                        )
                                elif datetime.datetime.strptime(
                                    to_update_clockinout_request.date.strftime(
                                        "%d-%m-%Y"
                                    ),
                                    "%d-%m-%Y",
                                ) < datetime.datetime.strptime(
                                    datetime.datetime.now().date().strftime("%d-%m-%Y"),
                                    "%d-%m-%Y",
                                ):
                                    timesheet_record = time_sheet.objects.create(
                                        employee_id=to_update_clockinout_request.employee_id,
                                        client_id=user,
                                        month=calendar.month_name[
                                            to_update_clockinout_request.date.month
                                        ],
                                        year=to_update_clockinout_request.date.year,
                                        record={
                                            to_update_clockinout_request.date.strftime(
                                                "%d-%m-%Y"
                                            ): {
                                                "check_in": to_update_clockinout_request.punch_time,
                                                "check_out": "-",
                                                "hours_worked": "-",
                                                "overtime": "-",
                                                "status": {
                                                    "Present": True,
                                                    "Missing": True,
                                                    "Absent": False,
                                                    "Day Off": False,
                                                    "Full Leave": False,
                                                    "Short Duration": False,
                                                },
                                            },
                                        },
                                    )
                                to_update_clockinout_request.status = to_update_status
                                to_update_clockinout_request.save()
                                notifi = notifications.objects.get(
                                    ref_id=request_id,
                                    notification_type="punch_request",
                                )
                                notifi.email = to_update_clockinout_request.employee_id
                                notifi.status = to_update_status
                                notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                notifi.save()
                                return Response(
                                    {
                                        "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                    },
                                    status=status.HTTP_200_OK,
                                )

                        elif record_punch_type == "check_out":
                            try:
                                timesheet_record = time_sheet.objects.get(
                                    employee_id=to_update_clockinout_request.employee_id,
                                    client_id=user,
                                    month=calendar.month_name[
                                        to_update_clockinout_request.date.month
                                    ],
                                    year=to_update_clockinout_request.date.year,
                                )
                                if (
                                    to_update_clockinout_request.date.strftime(
                                        "%d-%m-%Y"
                                    )
                                    in timesheet_record.record
                                ):
                                    timesheet_record.record[
                                        to_update_clockinout_request.date.strftime(
                                            "%d-%m-%Y"
                                        )
                                    ][
                                        "check_out"
                                    ] = to_update_clockinout_request.punch_time
                                    timesheet_record.record[
                                        to_update_clockinout_request.date.strftime(
                                            "%d-%m-%Y"
                                        )
                                    ]["status"]["Present"] = True
                                    timesheet_record.record[
                                        to_update_clockinout_request.date.strftime(
                                            "%d-%m-%Y"
                                        )
                                    ]["status"]["Absent"] = False
                                    if (
                                        timesheet_record.record[
                                            to_update_clockinout_request.date.strftime(
                                                "%d-%m-%Y"
                                            )
                                        ]["check_in"]
                                        == "-"
                                    ):
                                        timesheet_record.record[
                                            to_update_clockinout_request.date.strftime(
                                                "%d-%m-%Y"
                                            )
                                        ]["status"]["Missing"] = True
                                        timesheet_record.save()
                                        to_update_clockinout_request.status = (
                                            to_update_status
                                        )
                                        to_update_clockinout_request.save()
                                        notifi = notifications.objects.get(
                                            ref_id=request_id,
                                            notification_type="punch_request",
                                        )
                                        notifi.email = (
                                            to_update_clockinout_request.employee_id
                                        )
                                        notifi.status = to_update_status
                                        notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                        notifi.save()
                                        return Response(
                                            {
                                                "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                            },
                                            status=status.HTTP_200_OK,
                                        )

                                    else:
                                        check_in_time = datetime.datetime.strptime(
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["check_in"],
                                            "%I:%M:%S %p",
                                        )
                                        check_out_time = datetime.datetime.strptime(
                                            to_update_clockinout_request.punch_time,
                                            "%I:%M:%S %p",
                                        )

                                        if check_out_time < check_in_time:
                                            check_out_time = check_out_time + timedelta(
                                                days=1
                                            )

                                        hours_worked = check_out_time - check_in_time
                                        if hours_worked.total_seconds() // 3600 < int(
                                            working_hours.total_seconds() // 3600
                                        ):
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["overtime"] = "0h"
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ][
                                                "hours_worked"
                                            ] = f"{hours_worked.seconds//3600}h {(hours_worked.seconds //60) %60}m"
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["status"]["Short Duration"] = True
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["status"]["Missing"] = False
                                            timesheet_record.save()
                                            to_update_clockinout_request.status = (
                                                to_update_status
                                            )
                                            to_update_clockinout_request.save()
                                            notifi = notifications.objects.get(
                                                ref_id=request_id,
                                                notification_type="punch_request",
                                            )
                                            notifi.email = (
                                                to_update_clockinout_request.employee_id
                                            )
                                            notifi.status = to_update_status
                                            notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                            notifi.save()
                                            return Response(
                                                {
                                                    "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                                },
                                                status=status.HTTP_200_OK,
                                            )
                                        elif (
                                            hours_worked.total_seconds() // 3600
                                            >= int(
                                                working_hours.total_seconds() // 3600
                                            )
                                        ):
                                            overtime = (
                                                hours_worked
                                                - datetime.timedelta(
                                                    hours=int(
                                                        working_hours.total_seconds()
                                                        // 3600
                                                    )
                                                )
                                            )
                                            overtime_min = (overtime.seconds // 60) % 60
                                            overtime_hours = overtime.seconds // 3600
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ][
                                                "hours_worked"
                                            ] = f"{hours_worked.seconds//3600}h {(hours_worked.seconds //60) %60}m"
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["status"]["Short Duration"] = False
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["status"]["Missing"] = False
                                            if overtime_hours and overtime_min:
                                                over_duration = (
                                                    f"{overtime_hours}h {overtime_min}m"
                                                )
                                            elif overtime_hours and not overtime_min:
                                                over_duration = f"{overtime_hours}h"
                                            elif not overtime_hours and overtime_min:
                                                over_duration = f"{overtime_min}m"
                                            else:
                                                over_duration = "0h"
                                            timesheet_record.record[
                                                to_update_clockinout_request.date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ]["overtime"] = over_duration
                                            timesheet_record.save()
                                            to_update_clockinout_request.status = (
                                                to_update_status
                                            )
                                            to_update_clockinout_request.save()
                                            notifi = notifications.objects.get(
                                                ref_id=request_id,
                                                notification_type="punch_request",
                                            )
                                            notifi.email = (
                                                to_update_clockinout_request.employee_id
                                            )
                                            notifi.status = to_update_status
                                            notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                            notifi.save()
                                            return Response(
                                                {
                                                    "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                                },
                                                status=status.HTTP_200_OK,
                                            )

                                else:
                                    timesheet_record.record[
                                        to_update_clockinout_request.date.strftime(
                                            "%d-%m-%Y"
                                        )
                                    ] = {
                                        "check_in": "-",
                                        "check_out": to_update_clockinout_request.punch_time,
                                        "hours_worked": "-",
                                        "overtime": "-",
                                        "status": {
                                            "Present": True,
                                            "Missing": True,
                                            "Absent": False,
                                            "Day Off": False,
                                            "Full Leave": False,
                                            "Short Duration": False,
                                        },
                                    }
                                    timesheet_record.save()
                                    to_update_clockinout_request.status = (
                                        to_update_status
                                    )
                                    to_update_clockinout_request.save()
                                    notifi = notifications.objects.get(
                                        ref_id=request_id,
                                        notification_type="punch_request",
                                    )
                                    notifi.email = (
                                        to_update_clockinout_request.employee_id
                                    )
                                    notifi.status = to_update_status
                                    notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                    notifi.save()
                                    return Response(
                                        {
                                            "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                        },
                                        status=status.HTTP_200_OK,
                                    )
                            except:
                                timesheet_record = time_sheet.objects.create(
                                    employee_id=to_update_clockinout_request.employee_id,
                                    client_id=user,
                                    month=calendar.month_name[
                                        to_update_clockinout_request.date.month
                                    ],
                                    year=to_update_clockinout_request.date.year,
                                    record={
                                        to_update_clockinout_request.date.strftime(
                                            "%d-%m-%Y"
                                        ): {
                                            "check_in": "-",
                                            "check_out": to_update_clockinout_request.punch_time,
                                            "hours_worked": "-",
                                            "overtime": "-",
                                            "status": {
                                                "Present": True,
                                                "Missing": True,
                                                "Absent": False,
                                                "Day Off": False,
                                                "Full Leave": False,
                                                "Short Duration": False,
                                            },
                                        },
                                    },
                                )
                                to_update_clockinout_request.status = to_update_status
                                to_update_clockinout_request.save()
                                notifi = notifications.objects.get(
                                    ref_id=request_id,
                                    notification_type="punch_request",
                                )
                                notifi.email = to_update_clockinout_request.employee_id
                                notifi.status = to_update_status
                                notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                                notifi.save()
                                return Response(
                                    {
                                        "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                                    },
                                    status=status.HTTP_200_OK,
                                )

                    except Exception as e:
                        return Response(
                            {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    return Response(
                        {"message": "This request is closed"}, status=status.HTTP_200_OK
                    )
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)

        elif to_update_status == "rejected":
            try:
                to_update_clockinout_request = punch_request.objects.get(id=request_id)
                emp_req = employee.objects.get(
                    email=to_update_clockinout_request.employee_id
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
            if to_update_clockinout_request.status == "pending":
                to_update_clockinout_request.status = to_update_status
                to_update_clockinout_request.save()
                notifi = notifications.objects.get(
                    ref_id=request_id, notification_type="punch_request"
                )
                notifi.email = to_update_clockinout_request.employee_id
                notifi.status = to_update_status
                notifi.description = f"{to_update_clockinout_request.punch_type} punch request has been {to_update_status}"
                notifi.save()

                return Response(
                    {
                        "message": f"{emp_req.first_name} {emp_req.last_name} {to_update_clockinout_request.punch_type} request is {to_update_status}"
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "This request is closed"}, status=status.HTTP_200_OK
                )
        else:
            return Response(
                {"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST
            )


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
                records = leave_request.objects.filter(client_id=user)
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
                        employee.objects.get(email=data.employee_id)
                    )
                    employee_data = employee_serializer.data
                    outsource = outsource_employees.objects.get(
                        client_id=data.client_id, employee_id=employee_data["email"]
                    )

                    row_data = [
                        str(employee_data.get("employee_id", "")),
                        str(
                            employee_data.get("first_name", "")
                            + " "
                            + employee_data.get("last_name", ""),
                        ),
                        str(outsource.country),
                        str(outsource.job_title),
                        str(data.leave_type),
                        str(data.count),
                        str(data.created_at.date()),
                        str(data.status),
                    ]
                    table_data.append(row_data)
                    raw_data.append(f"Raw Data for {get_tab}: {data}")
                col_widths = [65, 90, 70, 90, 60, 35, 100, 60]
            elif get_tab == "cio":
                records = punch_request.objects.filter(client_id=user)
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
                        employee.objects.get(email=data.employee_id)
                    )
                    employee_data = employee_serializer.data

                    row_data = [
                        str(employee_data.get("employee_id", "")),
                        str(
                            employee_data.get("first_name", "")
                            + " "
                            + employee_data.get("last_name", ""),
                        ),
                        str(data.date),
                        str(data.punch_time),
                        str(data.punch_type),
                        str(data.status),
                    ]
                    table_data.append(row_data)
                    raw_data.append(f"Raw Data for {get_tab}: {data}")
                col_widths = [100, 100, 80, 80, 80, 80]
            elif get_tab == "lb":
                records = outsource_employees.objects.filter(client_id=user)
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
                        employee.objects.get(email=data.employee_id)
                    )
                    employee_data = employee_serializer.data
                    leaves = leave_balance.objects.get(employee_id=data.employee_id)
                    row_data = [
                        str(
                            employee_data.get("first_name", "")
                            + " "
                            + employee_data.get("last_name", ""),
                        ),
                        str(leaves.casual_leaves["balance"]),
                        str(leaves.sick_leaves["balance"]),
                        str(leaves.annual_leaves["balance"]),
                        str(
                            int(leaves.casual_leaves["availed"])
                            + int(leaves.sick_leaves["availed"])
                            + int(leaves.annual_leaves["availed"]),
                        ),
                        str(
                            (
                                int(leaves.casual_leaves["balance"])
                                + int(leaves.sick_leaves["balance"])
                                + int(leaves.annual_leaves["balance"])
                            )
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
                styles = getSampleStyleSheet()
                elements = []
                heading = FileHeading
                elements.append(Paragraph(heading, styles["Title"]))
                elements.append(Paragraph("<br/>", styles["Normal"]))

                elements.append(pdf_table)
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
class Download_Attendance_Report(APIView):
    @swagger_auto_schema(
        tags=["Team : Time Tracking"],
        manual_parameters=[
            openapi.Parameter(
                "e_email",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                "month",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "year",
                openapi.IN_QUERY,
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
            200: openapi.Response("Successful Download"),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_summary="Endpoint to download attendance report.",
        operation_id="6",
    )
   
    def get(self, request, *args, **kwargs):
        e_email=request.query_params.get("e_email")
        month=request.query_params.get("month")
        year=request.query_params.get("year")
        try:
            try:
                rec = time_sheet.objects.get(client_id=request.user, employee_id=e_email, month=month, year=year)
                emp=employee.objects.get(email=rec.employee_id)
            except time_sheet.DoesNotExist:
                return Response({"error": "No record found"}, status=status.HTTP_204_NO_CONTENT)
            current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"AttendanceReport_{current_datetime}.pdf"
            table_headers = [
                "Date",
                "Day",
                "Check-in",
                "Check-out",
                "Hours worked",
                "Overtime",
                "Status",
            ]
            FileHeading = "Attendance Report"
            table_data = [table_headers]
            images_folder = os.path.join(settings.BASE_DIR, 'images')
            status_images = {
                "P": os.path.join(images_folder, "P.jpg"),
                "M": os.path.join(images_folder, "M.jpg"),
                "A": os.path.join(images_folder, "A.jpg"),
                "S": os.path.join(images_folder, "S.jpg"),
                "D": os.path.join(images_folder, "D.jpg"),
                "L": os.path.join(images_folder, "L.jpg"),
            }
            status_flags = ["Present", "Missing", "Absent", "Short Duration", "Day Off", "Full Leave"]
            status_map = {"Present": "P", "Missing": "M", "Absent": "A", "Short Duration": "S", "Day Off": "D", "Full Leave": "L"}
            for key in rec.record:
                date_obj = datetime.datetime.strptime(key, "%d-%m-%Y")
                day = date_obj.strftime("%A")
                status_symbols = ""
                status_images_list = []
                
                for status_flag in status_flags:
                    if rec.record[key]["status"].get(status_flag):
                        symbol = status_map[status_flag]
                        status_images_list.append(status_images[symbol])
                status_image_objects = [Image(img_path, width=17, height=17) for img_path in status_images_list]

                status_image_table = Table([status_image_objects], colWidths=[22] * len(status_image_objects))
                row_data = [
                    str(key),
                    str(day),
                    str(rec.record[key]["check_in"]),
                    str(rec.record[key]["check_out"]),
                    str(rec.record[key]["hours_worked"]),
                    str(rec.record[key]["overtime"]),
                    status_image_table,
                ]
                table_data.append(row_data)
            col_widths_attend = [80, 80, 80, 80, 80, 80, 80]

            status_table_data = [[]]
            for stat, pic in status_map.items():
                status_table_data[0].append(Image(status_images[pic], width=15, height=15))
                status_table_data[0].append(stat)
            status_table_data[0].append("")
            col_width_stat_table=[21.5,45,21.5,45,21.5,40,21.5,80,21.5,50,21.5,60,120]

            pdf_table_status=Table(status_table_data, colWidths=col_width_stat_table)

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'

            pdf_buffer = HttpResponse(content_type="application/pdf")
            pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)

            pdf_table_attend = Table(table_data, colWidths=col_widths_attend)
            style_attend = TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
                    ("TOPPADDING", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 1), (-2, -1), 9),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )

            pdf_table_attend.setStyle(style_attend)

            name_id=[f"Employee Name: {emp.first_name} {emp.last_name}", f"Employee ID: {emp.employee_id}"]
            design_comp=[f"Email: {emp.email}", f"Designation : {emp.job_title}"]
            month_year=[f"Month: {rec.month}", f"Year: {rec.year}"]
            desc_table=[name_id, design_comp, month_year]
            col_width_desc=[320,240]
            
            pdf_table_desc= Table(desc_table, colWidths=col_width_desc)

            style_desc= TableStyle(
                [
                    ("BACKGROUND", (0,0), (-1,-1), colors.white),
                    ("GRID", (0, 0), (-1, -1),1, colors.white),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ]
            )

            style_stat= TableStyle(
                [
                    ("BACKGROUND", (0,0), (-1,-1), colors.white),
                    ("GRID", (0, 0), (-1, -1),1, colors.white),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ]
            )

            pdf_table_desc.setStyle(style_desc)
            pdf_table_status.setStyle(style_stat)

            styles = getSampleStyleSheet()
            elements = []
            heading = FileHeading

            elements.append(Paragraph(heading, styles["Title"]))
            elements.append(Paragraph("<br/>", styles["Normal"]))

            elements.append(pdf_table_desc)
            elements.append(Paragraph("<br/>", styles["Normal"]))

            elements.append(pdf_table_status)
            elements.append(Paragraph("<br/>", styles["Normal"]))

            elements.append(pdf_table_attend)
            elements.append(Paragraph("<br/>", styles["Normal"]))

            pdf.build(elements)

            response.write(pdf_buffer.getvalue())
            return response
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UpdateCompanyNameView(APIView):
    @swagger_auto_schema(
        tags=["Oragnization : Settings"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "company_name": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["company_name"],
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
        operation_summary="Update company name.",
        operation_id="3",
    )
    def patch(self, request):
        user = request.user
        new_company_name = request.data.get("company_name")
        if new_company_name:
            try:
                record = client.objects.get(email=user)
                record.company_name = new_company_name
                record.save()
                user_record = end_user.objects.get(email=user)
                user_record.username = new_company_name
                user_record.save()
                return Response(
                    {"message": "Company name is successfully updated"},
                    status=status.HTTP_200_OK,
                )
            except client.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
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
        user = request.user
        picture_file = request.FILES.get("picture")
        if picture_file:
            record = client.objects.get(email=user)
            removed = remove_bucket_file(record.image.name)
            if removed:
                return Response(
                    {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                )
            record.image = picture_file
            try:
                record.save()
                return Response(
                    {
                        "message": "Profile picture is successfully updated",
                        "image": record.image.url,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except ValidationError as e:
                return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "No picture provided"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UpdatePasswordView(APIView):
    @swagger_auto_schema(
        tags=["Oragnization : Settings"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "current_password": openapi.Schema(type=openapi.TYPE_STRING),
                "new_password": openapi.Schema(type=openapi.TYPE_STRING),
                "confirm_password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["current_password,new_password,confirm_password"],
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
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        try:
            record = end_user.objects.get(email=user)
        except end_user.DoesNotExist:
            raise Http404("User does not exist")

        if not record.check_password(current_password):
            return Response(
                {"error": "Incorrect current password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password == confirm_password:
            record.set_password(new_password)
            record.save()
            return Response(
                {"message": "Password is successfully updated"},
                status=status.HTTP_200_OK,
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
                format=openapi.FORMAT_EMAIL,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
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
                                    ),
                                    "check_out": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                    ),
                                    "hours_worked": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                    ),
                                    "over_time": openapi.Schema(
                                        type=openapi.TYPE_STRING,
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
        operation_id="2",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        employee_id = request.query_params.get("emp_id")

        if month and year and employee_id:
            time_sheet_data = time_sheet.objects.filter(
                month=month, year=year, employee_id=employee_id, client_id=user
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
                            "time_sheet": time_sheet_records,
                        },
                        status=status.HTTP_200_OK,
                    )
            else:
                return Response(
                    status=status.HTTP_204_NO_CONTENT,
                )

        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Available_Employees(APIView):
    @swagger_auto_schema(
        tags=["Team : Time Tracking"],
        operation_summary="Get available employees",
        manual_parameters=[
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
                    },
                ),
            ),
            204: openapi.Response(description="No Content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        user = request.user

        available_employees = outsource_employees.objects.filter(
            client_id=user, status="active"
        )
        serialized_available_employees = TimeSheetEmployeeSerializer(
            available_employees, many=True
        ).data
        for record in serialized_available_employees:
            emp_record = employee.objects.get(email=record["employee_id"])
            record["name"] = emp_record.first_name + " " + emp_record.last_name

        if serialized_available_employees:
            return Response(
                {"employees": serialized_available_employees},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


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
                enum=["pending", "processing", "paid"],
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
            client_id=user, payment_status=pay_status
        )
        other_pays = other_payment.objects.filter(
            client_id=user, payment_status=pay_status
        )
        records = {}
        if emp_invoices:
            emp_inv_records = []
            for data in emp_invoices:
                employee_data = employee.objects.get(email=data.employee_id)
                record = {
                    "id": data.id,
                    "employee_name": employee_data.first_name
                    + " "
                    + employee_data.last_name,
                    "invoice_date": data.invoice_date,
                    "due_date": data.due_date,
                    "invoice_amount": data.invoice_amount,
                    "payment_status": pay_status,
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
                    type=openapi.TYPE_STRING, enum=["pending", "processing", "paid"]
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
        try:
            if category == "employee_invoice":
                try:
                    to_update_invoice_payments = employee_invoice.objects.get(id=id)
                    to_update_invoice_payments.payment_status = new_pay_status
                    to_update_invoice_payments.save()
                    notifi = notifications.objects.get(
                        ref_id=id, notification_type="employee_invoice"
                    )
                    notifi.email = talent_email
                    notifi.status = new_pay_status
                    notifi.description = f"employee invoice has been {new_pay_status}"
                    notifi.save()

                except Exception as e:
                    return Response(
                        {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
                    )
            elif category == "other_payment":
                try:
                    to_update_invoice_payments = other_payment.objects.get(id=id)
                    to_update_invoice_payments.payment_status = new_pay_status
                    to_update_invoice_payments.save()
                    notifi = notifications.objects.get(
                        ref_id=id, notification_type="other_payment"
                    )
                    notifi.email = talent_email
                    notifi.status = new_pay_status
                    notifi.description = f"other invoice has been {new_pay_status}"
                    notifi.save()

                except Exception as e:
                    return Response(
                        {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(
                {"message": f"One new invoice is {new_pay_status}"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Client_contract(APIView):
    @swagger_auto_schema(
        tags=["Company Contract"],
        operation_summary="Get client contract data",
        operation_id=".",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                "Successful response with contract data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "contract_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "client_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "date": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                        ),
                    },
                ),
            ),
            204: "No content",
        },
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        clnt_contract = client_contract.objects.filter(client_id=user)
        records = []

        if clnt_contract:
            for data in clnt_contract:
                record = {
                    "id": data.id,
                    "contract_name": data.contract_name,
                    "client_id": data.client_id,
                    "date": data.date,
                }
                records.append(record)

            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Employee_Contract(APIView):
    @swagger_auto_schema(
        tags=["Employee Contract"],
        operation_summary="Get employee data",
        operation_id=".",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                "Successful response with contract data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "contract_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "date": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                        ),
                    },
                ),
            ),
            204: "No content",
        },
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        emp_contract = offshore_contracts.objects.filter(client_id=user)
        records = []
        if emp_contract:
            for data in emp_contract:
                record = {
                    "id": data.id,
                    "contract_name": data.contract_name,
                    "employee_id": data.employee_id,
                    "date": data.date,
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Policies(APIView):
    @swagger_auto_schema(
        tags=["Policies"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "policy_name": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            204: openapi.Response(description="No Content"),
            401: openapi.Response(description="Unauthorized"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to retrieve Client policies",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        client_policies = policy.objects.filter(client=True)
        policies = []
        for client_pol in client_policies:
            record = {
                "id": client_pol.id,
                "policy_name": client_pol.policy_name,
            }
            policies.append(record)
        if len(policies) > 0:
            return Response(policies, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Notifications(APIView):
    @swagger_auto_schema(
        tags=["Notifications"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "type": openapi.Schema(type=openapi.TYPE_STRING),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                            "date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "time": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                            ),
                        },
                    ),
                ),
            ),
            204: openapi.Response(description="No Content"),
            401: openapi.Response(description="Unauthorized"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to retrieve Notifications",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        user_email = request.user
        user = end_user.objects.get(email=user_email)
        noti_array = []
        if user.role == "employee":
            current_time = timezone.now()
            one_week_ago = current_time - timedelta(days=5)
            notifications_data = (
                notifications.objects.filter(
                    email=user_email, updated_at__gte=one_week_ago
                )
                .exclude(notification_type="employee_contract")
                .exclude(notification_type="offshore_contracts")
            )
            emp_contract = notifications.objects.filter(
                email=user_email,
                notification_type="employee_contract",
                created_at__gte=one_week_ago,
            ).order_by("-created_at")
            off_contract = notifications.objects.filter(
                email=user_email,
                notification_type="offshore_contracts",
                created_at__gte=one_week_ago,
            ).order_by("-created_at")
            policies = policy.objects.filter(
                employee=True, created_at__gte=one_week_ago
            ).order_by("-created_at")
            for data in notifications_data:
                record = {
                    "type": capwords(data.notification_type.replace("_", " ")),
                    "description": data.description,
                    "date": data.updated_at.date(),
                    "time": data.updated_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)
            if emp_contract:
                record = {
                    "type": "Company Contracts",
                    "description": f"{emp_contract.count()} new contract has been added to company contracts.",
                    "date": emp_contract[0].created_at.date(),
                    "time": emp_contract[0].updated_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)
            if off_contract:
                record = {
                    "type": "Client Contracts",
                    "description": f"{off_contract.count()} new contract has been added to client contracts.",
                    "date": off_contract[0].created_at.date(),
                    "time": off_contract[0].created_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)
            if policies:
                if policies.count() == 1:
                    record = {
                        "type": "Policy",
                        "description": f"1 new policy have been added.",
                        "date": policies[0].created_at.date(),
                        "time": policies[0].created_at.strftime("%H:%M:%S"),
                    }
                else:
                    record = {
                        "type": "Policy",
                        "description": f"{policies.count()} new policies have been added.",
                        "date": policies[0].created_at.date(),
                        "time": policies[0].created_at.strftime("%H:%M:%S"),
                    }
                noti_array.append(record)

        elif user.role == "client":
            current_time = timezone.now()
            one_week_ago = current_time - timedelta(days=5)
            notifications_data = (
                notifications.objects.filter(
                    email=user_email, updated_at__gte=one_week_ago
                )
                .exclude(notification_type="client_contract")
                .exclude(notification_type="offshore_contracts")
                .exclude(notification_type="interview_schedule")
                .exclude(notification_type="onboarding")
                .exclude(notification_type="other_payment")
                .exclude(notification_type="employee_invoice")
            )
            int_sch = notifications.objects.filter(
                email=user_email, notification_type="interview_schedule", status="added"
            ).order_by("-created_at")
            onboard = notifications.objects.filter(
                email=user_email, notification_type="onboarding", status="added"
            ).order_by("-created_at")
            invoice = notifications.objects.filter(
                Q(notification_type="employee_invoice")
                | Q(notification_type="other_payment"),
                email=user_email,
                status="added",
            ).order_by("-created_at")
            current_time = timezone.now()
            one_week_ago = current_time - timedelta(days=5)
            clt_contract = notifications.objects.filter(
                email=user_email,
                notification_type="client_contract",
                created_at__gte=one_week_ago,
            ).order_by("-created_at")
            off_contract = notifications.objects.filter(
                email=user_email,
                notification_type="offshore_contracts",
                created_at__gte=one_week_ago,
            ).order_by("-created_at")
            policies = policy.objects.filter(
                client=True, created_at__gte=one_week_ago
            ).order_by("-created_at")
            for data in notifications_data:
                record = {
                    "type": capwords(data.notification_type.replace("_", " ")),
                    "description": data.description,
                    "date": data.updated_at.date(),
                    "time": data.updated_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)
            if clt_contract:
                record = {
                    "type": "Company Contracts",
                    "description": f"{clt_contract.count()} new contract has been added to company contracts.",
                    "date": clt_contract[0].created_at.date(),
                    "time": clt_contract[0].created_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)
            if off_contract:
                record = {
                    "type": "Employee Contracts",
                    "description": f"{off_contract.count()} new contract has been added to employee contracts.",
                    "date": off_contract[0].created_at.date(),
                    "time": off_contract[0].created_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)
            if policies:
                if policies.count() == 1:
                    record = {
                        "type": "Policy",
                        "description": f"1 new policy have been added.",
                        "date": policies[0].created_at.date(),
                        "time": policies[0].created_at.strftime("%H:%M:%S"),
                    }
                else:
                    record = {
                        "type": "Policy",
                        "description": f"{policies.count()} new policies have been added.",
                        "date": policies[0].created_at.date(),
                        "time": policies[0].created_at.strftime("%H:%M:%S"),
                    }
                noti_array.append(record)
            if int_sch:
                record = {
                    "type": "Interview Schedule",
                    "description": f"You have {int_sch.count()} new interview scheduled.",
                    "date": int_sch[0].created_at.date(),
                    "time": int_sch[0].created_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)

            if onboard:
                onboard_count = onboard.count()
                if onboard_count == 1:
                    description = "1 new employee is added"
                else:
                    description = f"{onboard_count} new employees are added"
                record = {
                    "type": "Onboarding",
                    "description": description,
                    "date": onboard[0].created_at.date(),
                    "time": onboard[0].created_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)

            if invoice:
                if invoice.count() == 1:
                    description = "1 new invoice is added"
                else:
                    description = f"{invoice.count()} new invoices are added"
                record = {
                    "type": "Invoice",
                    "description": description,
                    "date": invoice[0].created_at.date(),
                    "time": invoice[0].created_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)

        else:
            current_time = timezone.now()
            one_week_ago = current_time - timedelta(days=5)
            hire_req = notifications.objects.filter(
                email=talent_email,
                notification_type="hiring_request",
                status="added",
                created_at__gte=one_week_ago,
            ).order_by("-created_at")
            short_int = notifications.objects.filter(
                email=talent_email,
                notification_type="interview_schedule",
                status="short_list",
                updated_at__gte=one_week_ago,
            ).order_by("-updated_at")
            rej_int = notifications.objects.filter(
                email=talent_email,
                notification_type="interview_schedule",
                status="rejected",
                updated_at__gte=one_week_ago,
            ).order_by("-updated_at")
            process_inv = notifications.objects.filter(
                Q(notification_type="employee_invoice")
                | Q(notification_type="other_payment"),
                email=talent_email,
                status="processing",
                updated_at__gte=one_week_ago,
            ).order_by("-updated_at")
            paid_inv = notifications.objects.filter(
                Q(notification_type="employee_invoice")
                | Q(notification_type="other_payment"),
                email=talent_email,
                status="paid",
                updated_at__gte=one_week_ago,
            ).order_by("-updated_at")
            if hire_req:
                if hire_req.count() == 1:
                    description = "You got 1 new hiring request"
                else:
                    description = f"You got {hire_req.count()} new hiring requests"
                record = {
                    "type": "Hiring Request",
                    "description": description,
                    "date": hire_req[0].created_at.date(),
                    "time": hire_req[0].created_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)
            if short_int:
                if short_int.count() == 1:
                    description = "1 interviewee is shortlisted"
                else:
                    description = f"{short_int.count()} interviewees are shortlisted"
                record = {
                    "type": "Interview Schedule",
                    "description": description,
                    "date": short_int[0].updated_at.date(),
                    "time": short_int[0].updated_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)
            if rej_int:
                if rej_int.count() == 1:
                    description = "1 interviewee is rejected"
                else:
                    description = f"{rej_int.count()} interviewees are rejected"
                record = {
                    "type": "Interview Schedule",
                    "description": description,
                    "date": rej_int[0].updated_at.date(),
                    "time": rej_int[0].updated_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)
            if process_inv:
                if process_inv.count() == 1:
                    description = "1 new invoice is processing"
                else:
                    description = f"{process_inv.count()} new invoices are processing"
                record = {
                    "type": "Invoice",
                    "description": description,
                    "date": process_inv[0].updated_at.date(),
                    "time": process_inv[0].updated_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)
            if paid_inv:
                if paid_inv.count() == 1:
                    description = "1 new invoice is paid"
                else:
                    description = f"{paid_inv.count()} new invoices are paid"
                record = {
                    "type": "Invoice",
                    "description": description,
                    "date": paid_inv[0].updated_at.date(),
                    "time": paid_inv[0].updated_at.strftime("%H:%M:%S"),
                }
                noti_array.append(record)
        if len(noti_array) > 0:
            return Response(noti_array, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
