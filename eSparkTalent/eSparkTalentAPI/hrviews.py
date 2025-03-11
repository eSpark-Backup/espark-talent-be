import json
from django.http import Http404
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from django.core.exceptions import ObjectDoesNotExist
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.db import transaction
import json
from dateutil import parser
from django.db.models import Q, IntegerField, Case, When, Value
from eSparkTalent.settings import talent_email
from .bucket_functions import remove_bucket_file
from django.db.models.fields.files import FileField
from calendar import month_name
from django.db.utils import IntegrityError
import calendar
from datetime import datetime


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Add_Employee(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Employees : Add Employee"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="employee_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="first_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="last_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="gender",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="dob",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="phone_number",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="email",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                name="personal_email",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                name="marital_status",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="image",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                name="resume",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                name="emergency_contact",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_OBJECT,
                default={
                    "primary": {
                        "name": "Rehman",
                        "relation": "Father",
                        "phone_number": "03323212345",
                    },
                    "secondary": {
                        "name": "Raheel",
                        "relation": "Brother",
                        "phone_number": "03323219087",
                    },
                },
                required=True,
            ),
            openapi.Parameter(
                name="joining_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="job_title",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="role",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="company",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="job_status",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="starting_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                name="ending_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                name="punch_timings",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_OBJECT,
                default={"check_in": "10:00 AM", "check_out": "07:00 PM"},
                required=True,
            ),
            openapi.Parameter(
                name="casual_leaves",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="sick_leaves",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="annual_leaves",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="hajj_leaves",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="paid_leaves",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="unpaid_leaves",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="password",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="confirm_password",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_summary="Add a new employee",
        operation_id=".",
    )
    def post(self, request, *args, **kwargs):
        posted_data = request.data
        password = posted_data.pop("password", None)[0]
        confirm_password = posted_data.pop("confirm_password", None)[0]
        casual_leaves = posted_data.pop("casual_leaves", None)[0]
        sick_leaves = posted_data.pop("sick_leaves", None)[0]
        annual_leaves = posted_data.pop("annual_leaves", None)[0]
        hajj_leaves = posted_data.pop("hajj_leaves", None)[0]
        paid_leaves = posted_data.pop("paid_leaves", None)[0]
        unpaid_leaves = posted_data.pop("unpaid_leaves", None)[0]
        if password == confirm_password:
            serializer = EmployeeSerializer(data=posted_data)
            if serializer.is_valid():
                try:
                    end_user.objects.create_user(
                        username=serializer.validated_data["first_name"]
                        + " "
                        + serializer.validated_data["last_name"],
                        role="employee",
                        email=serializer.validated_data["email"],
                        password=password,
                    )

                    emp = employee.objects.create(
                        employee_id=serializer.validated_data["employee_id"],
                        first_name=serializer.validated_data["first_name"],
                        last_name=serializer.validated_data["last_name"],
                        gender=serializer.validated_data["gender"],
                        dob=serializer.validated_data["dob"],
                        phone_number=serializer.validated_data["phone_number"],
                        email=serializer.validated_data["email"],
                        personal_email=serializer.validated_data["personal_email"],
                        marital_status=serializer.validated_data["marital_status"],
                        image=serializer.validated_data["image"],
                        resume=serializer.validated_data["resume"],
                        emergency_contact=serializer.validated_data[
                            "emergency_contact"
                        ],
                        joining_date=serializer.validated_data["joining_date"],
                        starting_date=serializer.validated_data.get("starting_date", None),
                        ending_date=serializer.validated_data.get("ending_date", None), 
                        job_title=serializer.validated_data["job_title"],
                        job_status=serializer.validated_data["job_status"],
                        role=serializer.validated_data["role"],
                        company=serializer.validated_data["company"],
                        punch_timings=serializer.validated_data["punch_timings"],
                    )

                    leave_balance.objects.create(
                        employee_id=serializer.validated_data["email"],
                        casual_leaves={
                            "total": casual_leaves,
                            "availed": 0,
                            "balance": casual_leaves,
                            "status": "enable",
                        },
                        sick_leaves={
                            "total": sick_leaves,
                            "availed": 0,
                            "balance": sick_leaves,
                            "status": "enable",
                        },
                        annual_leaves={
                            "total": annual_leaves,
                            "availed": 0,
                            "balance": annual_leaves,
                            "status": "enable",
                        },
                        unpaid_leaves={
                            "total": unpaid_leaves,
                            "availed": 0,
                            "balance": unpaid_leaves,
                            "status": "enable",
                        },
                        hajj_leaves={
                            "total": hajj_leaves,
                            "availed": 0,
                            "balance": hajj_leaves,
                            "status": "enable",
                        },
                        paid_leaves={
                            "total": paid_leaves,
                            "availed": 0,
                            "balance": paid_leaves,
                            "status": "enable",
                        },
                    )
                    outsource_employees.objects.create(
                        client_id=talent_email,
                        employee_id=serializer.validated_data["email"],
                        job_title=serializer.validated_data["job_title"],
                        country="Pakistan",
                        role_type=serializer.validated_data["role"],
                        employment_term="",
                        joining_date=serializer.validated_data["joining_date"],
                        salary=0,
                    )
                    return Response(
                        {
                            "message": f"{emp.first_name} {emp.last_name} is added successfully",
                            "id": emp.id,
                            "image": emp.image.url,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except ValidationError as e:
                    return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
                except IntegrityError as e:
                    if "UNIQUE constraint failed" in str(e):
                        return Response(
                            {"error": "Account already exists with this email"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    else:
                        return Response(
                            {"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Add_Client(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Clients : Add Client"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="client_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="first_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="last_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="company_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="email",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                name="phone_number",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="join_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="country",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="address",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="image",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                name="password",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="confirm_password",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_summary="Add a new client",
        operation_id=".",
    )
    def post(self, request, *args, **kwargs):
        posted_data = request.data
        password = posted_data.pop("password", None)[0]
        confirm_password = posted_data.pop("confirm_password", None)[0]
        if password == confirm_password:
            serializer = ClientSerializer(data=posted_data)
            if serializer.is_valid():
                try:
                    end_user.objects.create_user(
                        username=serializer.validated_data["company_name"],
                        role="client",
                        email=serializer.validated_data["email"],
                        password=password,
                    )

                    clnt = client.objects.create(
                        client_id=serializer.validated_data["client_id"],
                        first_name=serializer.validated_data["first_name"],
                        last_name=serializer.validated_data["last_name"],
                        company_name=serializer.validated_data["company_name"],
                        email=serializer.validated_data["email"],
                        phone_number=serializer.validated_data["phone_number"],
                        join_date=serializer.validated_data["join_date"],
                        country=serializer.validated_data["country"],
                        address=serializer.validated_data["address"],
                        image=serializer.validated_data["image"],
                    )
                    return Response(
                        {
                            "message": f"{clnt.first_name} {clnt.last_name} is added successfully",
                            "id": clnt.id,
                            "image": clnt.image.url,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except ValidationError as e:
                    return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
                except IntegrityError as e:
                    if "UNIQUE constraint failed" in str(e):
                        return Response(
                            {"error": "Account already exists with this email"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    else:
                        return Response(
                            {"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Add_Asset(APIView):
    @swagger_auto_schema(
        tags=["Employee : Asset"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "asset_id": openapi.Schema(type=openapi.TYPE_STRING),
                "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                "gadget": openapi.Schema(type=openapi.TYPE_STRING),
                "assigned_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
                "assignee_name": openapi.Schema(type=openapi.TYPE_STRING),
                "assignee_email": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
            },
            required=[
                "asset_id",
                "assignee_name",
                "gadget",
                "assigned_date",
                "employee_id",
                "assignee_email",
            ],
        ),
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Add new asset",
        operation_id=".",
    )
    def post(self, request, *args, **kwargs):
        serializer = AssetSerializer(data=request.data)
        if serializer.is_valid():
            ast = asset.objects.create(
                asset_id=serializer.validated_data["asset_id"],
                employee_id=serializer.validated_data["employee_id"],
                gadget=serializer.validated_data["gadget"],
                assigned_date=serializer.validated_data["assigned_date"],
                assignee_name=serializer.validated_data["assignee_name"],
                assignee_email=serializer.validated_data["assignee_email"],
            )
            return Response(
                {"message": "One new asset has been added", "id": ast.id},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Employee : Asset"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "asset_id": openapi.Schema(type=openapi.TYPE_STRING),
                "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                "gadget": openapi.Schema(type=openapi.TYPE_STRING),
                "assigned_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
                "assignee_name": openapi.Schema(type=openapi.TYPE_STRING),
                "assignee_email": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
            },
        ),
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to update",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful update"),
            400: openapi.Response(description="Bad Request"),
            401: openapi.Response(description="Unauthorize"),
            404: openapi.Response(description="Not Found"),
        },
        operation_summary="Endpoint to update an asset.",
        operation_id="3",
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates = request.data
        try:
            record = asset.objects.get(id=record_id)
            for key in updates:
                setattr(record, key, updates[key])
            record.save()
            return Response(
                {"message": "Asset record has been updated successfully"},
                status=status.HTTP_200_OK,
            )
        except asset.DoesNotExist:
            return Response(
                    {"error": "Asset record not found"}, status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Employee : Asset"],
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
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful deletion"),
            400: openapi.Response(description="Bad Request"),
            401: openapi.Response(description="Unauthorize"),
            404: openapi.Response(description="Not Found"),
        },
        operation_summary="Endpoint to delete a an asset.",
        operation_id=".",
    )
    def delete(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        if id:
            try:
                asset.objects.get(id=id).delete()
                return Response(
                    {"message": "Asset has been deleted"}, status=status.HTTP_200_OK
                )
            except asset.DoesNotExist:
                return Response(
                    {"error": "Asset not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "Id parameter required"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Employee_Invoice(APIView):

    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Client : Employee Invoice"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="employee_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="invoice_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="due_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="invoice_amount",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="currency",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="invoice",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                "payment_status",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                enum=["pending", "paid", "processing"],
                required=True,
            ),
            openapi.Parameter(
                name="client_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
        ],
        operation_summary="Employee Invoice",
        operation_id="0",
    )
    def post(self, request, *args, **kwargs):
        posted_data = request.data
        emp_id = posted_data.get("employee_id", None)
        try:
            employee_data = employee.objects.get(employee_id=emp_id)
            posted_data["employee_id"] = employee_data.email
            serializer = EmployeeInvoiceSerializer(data=posted_data)
            outsrc_emp = outsource_employees.objects.get(
                employee_id=posted_data["employee_id"],
                client_id=posted_data.get("client_id", None),
            )
            if outsrc_emp.status=="active":
                if serializer.is_valid():
                    try:
                        emp_inv = employee_invoice.objects.create(
                            client_id=serializer.validated_data["client_id"],
                            employee_id=serializer.validated_data["employee_id"],
                            invoice_date=serializer.validated_data["invoice_date"],
                            due_date=serializer.validated_data["due_date"],
                            invoice_amount=serializer.validated_data["invoice_amount"],
                            currency=serializer.validated_data["currency"],
                            payment_status=serializer.validated_data["payment_status"],
                            invoice=serializer.validated_data["invoice"],
                        )
                        notifications.objects.create(
                            email=emp_inv.client_id,
                            ref_id=emp_inv.id,
                            notification_type="employee_invoice",
                            status="added",
                            description=f"Invoice is added for {employee_data.first_name} {employee_data.last_name}",
                        )
                        return Response(
                            {
                                "message": "One new invoice is added",
                                "id": emp_inv.id,
                            },
                            status=status.HTTP_201_CREATED,
                        )
                    except ValidationError as e:
                        return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
                    except ObjectDoesNotExist as e:
                        return Response(
                            {"error": str(e)},
                            status=status.HTTP_404_NOT_FOUND,
                        )
                    except Exception as e:
                        return Response(
                            {"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error":"Cannot create invoice for terminated employee"}, status=status.HTTP_400_BAD_REQUEST)

        except employee.DoesNotExist:
            return Response(
                {"message": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Client : Employee Invoice"],
        responses={
            200: openapi.Response("Successfull"),
            400: openapi.Response("Bad request"),
            401: openapi.Response("UnAuthorize"),
            404: openapi.Response("Not Found"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required= True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "client_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
            ),
            openapi.Parameter(
                "employee_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
            ),
            openapi.Parameter(
                "invoice_date",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "due_date",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "invoice_amount",
                openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "currency",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "payment_status",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                enum=["pending", "paid", "processing"],
            ),
            openapi.Parameter(
                "invoice",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
            ),
        ],
        operation_summary="Endpoint to update invoice record.",
        operation_id="1",
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates = request.data
        try:
            record = employee_invoice.objects.get(id=record_id)
            keys = updates.keys()
            file_to_remove = ""
            send_notif = False
            for key in keys:
                if key == "invoice":
                    file_to_remove = record.invoice.name
                if key == "payment_status":
                    send_notif = True
                setattr(record, key, updates[key])

            record.save()

            if file_to_remove != "":
                removed = remove_bucket_file(file_to_remove)
                if removed:
                    return Response(
                        {"error": str(removed)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            if send_notif:
                employee_data = employee.objects.get(
                    email=record.employee_id
                )
                notif = notifications.objects.get(
                    ref_id=record.id,
                    notification_type=f"employee_invoice",
                )
                notif.status = updates['payment_status']
                notif.email = record.client_id
                notif.description = f"Invoice is {updates['payment_status']} for {employee_data.first_name} {employee_data.last_name}"
                notif.save()
            return Response(
                {"message": "Invoice record has been updated successfully"},
                status=status.HTTP_200_OK,
            )
        except employee_invoice.DoesNotExist:
            return Response(
                    {"error": "Invoice record not found"}, status=status.HTTP_404_NOT_FOUND
            )            
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Client : Employee Invoice"],
        manual_parameters=[
            openapi.Parameter(
                "client_id",
                openapi.IN_QUERY,
                description="client email",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                "tab",
                openapi.IN_QUERY,
                description="tab",
                type=openapi.TYPE_STRING,
                enum=["pending", "processing", "paid"],
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
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "invoice_date": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                        ),
                        "due_date": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                        ),
                        "invoice_amount": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "currency": openapi.Schema(type=openapi.TYPE_STRING),
                        "payment_status": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad Request",
            401: "Unauthorized",
        },
        operation_summary="Employee Invoice",
        operation_id="2",
    )
    def get(self, request, *args, **kwargs):
        client_id = request.query_params.get("client_id")
        tab = request.query_params.get("tab")
        try:
            records = []
            emp_inv = employee_invoice.objects.filter(
                client_id=client_id, payment_status=tab
            )
            if emp_inv:
                for inv in emp_inv:
                    emp = employee.objects.get(email=inv.employee_id)
                    record = {
                        "id": inv.id,
                        "employee_id": emp.employee_id,
                        "invoice_date": inv.invoice_date,
                        "due_date": inv.due_date,
                        "invoice_amount": inv.invoice_amount,
                        "currency": inv.currency,
                        "payment_status": inv.payment_status,
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Client : Employee Invoice"],
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
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful deletion"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorize"),
        },
        operation_summary="Endpoint to delete a Employee Invoice.",
        operation_id="3",
    )
    def delete(self, request, *args, **kwargs):
        delete_id = request.query_params.get("id")
        try:
            emp_inv = employee_invoice.objects.get(id=delete_id)
            removed = remove_bucket_file(emp_inv.invoice.name)
            if removed:
                return Response(
                    {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                )
            notifications.objects.get(
                ref_id=emp_inv.id,
                notification_type="employee_invoice",
            ).delete()
            emp_inv.delete()
            return Response(
                {"message": "One new invoice is removed"}, status=status.HTTP_200_OK
            )
        except employee_invoice.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Other_Payment(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Client : Other Invoice/payment"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="client_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                name="invoice_reference",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="invoice_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="due_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="invoice_amount",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="currency",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="invoice",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                "payment_status",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                enum=["pending", "paid", "processing"],
                required=True,
            ),
        ],
        operation_summary="Other Invoice/payment",
        operation_id="0",
    )
    def post(self, request, *args, **kwargs):
        serializer = OtherPaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                oth_pay = other_payment.objects.create(
                    client_id=serializer.validated_data["client_id"],
                    invoice_reference=serializer.validated_data["invoice_reference"],
                    invoice_date=serializer.validated_data["invoice_date"],
                    due_date=serializer.validated_data["due_date"],
                    invoice_amount=serializer.validated_data["invoice_amount"],
                    currency=serializer.validated_data["currency"],
                    payment_status=serializer.validated_data["payment_status"],
                    invoice=serializer.validated_data["invoice"],
                )
                notifications.objects.create(
                    email=oth_pay.client_id,
                    ref_id=oth_pay.id,
                    notification_type="other_payment",
                    status="added",
                    description=f"Invoice is added for {oth_pay.invoice_reference}",
                )
                return Response(
                    {
                        "message": "One new invoice is added",
                        "id": oth_pay.id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except ValidationError as e:
                return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist as e:
                        return Response(
                            {"error": str(e)},
                            status=status.HTTP_404_NOT_FOUND,
                        )
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Client : Other Invoice/payment"],
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "client_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
            ),
            openapi.Parameter(
                "invoice_reference",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "invoice_date",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "due_date",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "invoice_amount",
                openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "currency",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "payment_status",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                enum=["pending", "paid", "processing"],
            ),
            openapi.Parameter(
                "invoice",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
            404: openapi.Response("Not Found"),
        },
        operation_summary="Endpoint to update invoice record.",
        operation_id="1",
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates = request.data
        try:
            record = other_payment.objects.get(id=record_id)
            keys = updates.keys()
            file_to_remove = ""
            send_notif = False
            for key in keys:
                if key == "invoice":
                    file_to_remove = record.invoice.name
                if key == "payment_status":
                    send_notif = True
                setattr(record, key, updates[key])

            record.save()

            if file_to_remove != "":
                removed = remove_bucket_file(file_to_remove)
                if removed:
                    return Response(
                        {"error": str(removed)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            if send_notif:
                notif = notifications.objects.get(
                    ref_id=record.id,
                    notification_type="other_payment",
                )
                notif.status = updates['payment_status']
                notif.email = record.client_id
                notif.description = f"Invoice is {updates['payment_status']} for {record.invoice_reference}"
                notif.save()
            return Response(
                {"message": "Invoice record has been updated successfully"},
                status=status.HTTP_200_OK,
            )
        except other_payment.DoesNotExist:
            return Response(
                    {"error": "Invoice record not found"}, status=status.HTTP_404_NOT_FOUND
            )            
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Client : Other Invoice/payment"],
        manual_parameters=[
            openapi.Parameter(
                "client_id",
                openapi.IN_QUERY,
                description="client email",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                "tab",
                openapi.IN_QUERY,
                description="tab",
                type=openapi.TYPE_STRING,
                enum=["pending", "processing", "paid"],
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
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "invoice_reference": openapi.Schema(type=openapi.TYPE_STRING),
                        "invoice_date": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                        ),
                        "due_date": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                        ),
                        "invoice_amount": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "currency": openapi.Schema(type=openapi.TYPE_STRING),
                        "payment_status": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad Request",
            401: "Unauthorized",
        },
        operation_summary="Other Invoice/payment",
        operation_id="2",
    )
    def get(self, request, *args, **kwargs):
        client_id = request.query_params.get("client_id")
        tab = request.query_params.get("tab")
        try:
            records = []
            emp_inv = other_payment.objects.filter(
                client_id=client_id, payment_status=tab
            )
            if emp_inv:
                for inv in emp_inv:
                    record = {
                        "id": inv.id,
                        "invoice_reference": inv.invoice_reference,
                        "invoice_date": inv.invoice_date,
                        "due_date": inv.due_date,
                        "invoice_amount": inv.invoice_amount,
                        "currency": inv.currency,
                        "payment_status": inv.payment_status,
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Client : Other Invoice/payment"],
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
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful deletion"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorize"),
        },
        operation_summary="Endpoint to delete a Other Invoice.",
        operation_id="3",
    )
    def delete(self, request, *args, **kwargs):
        delete_id = request.query_params.get("id")
        try:
            oth_pay = other_payment.objects.get(id=delete_id)
            removed = remove_bucket_file(oth_pay.invoice.name)
            if removed:
                return Response(
                    {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                )
            notifications.objects.get(
                notification_type="other_payment",
                ref_id=oth_pay.id,
            ).delete()
            oth_pay.delete()
            return Response(
                {"message": "One new invoice is removed"}, status=status.HTTP_200_OK
            )
        except other_payment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hr_Home(APIView):
    @swagger_auto_schema(
        tags=["Dashboard"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "user": openapi.Schema(type=openapi.TYPE_STRING),
                        "company_image": openapi.Schema(type=openapi.TYPE_FILE),
                        "user_image": openapi.Schema(type=openapi.TYPE_FILE),
                        "employee_perms": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "download": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            },
                        ),
                        "client_perms": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "download": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            },
                        ),
                        "leaves_perms": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "download": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            },
                        ),
                        "invoices_perms": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "download": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            },
                        ),
                        "policies_perms": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "download": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            },
                        ),
                        "guides_perms": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "download": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            },
                        ),
                        "employees": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "clients": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "hiring_requests": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "interview_schedules": openapi.Schema(
                            type=openapi.TYPE_INTEGER
                        ),
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
        operation_summary="Endpoint to retrieve hr home data.",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        user = request.user.username
        role = request.user.role
        if role == "super_admin":
            company = company_data.objects.all()
            if company:
                comp_image = company[0].image.url
            else:
                comp_image = ""
            record = {
                "user": user,
                "company_image": comp_image,
                "employees": employee.objects.all().count(),
                "clients": client.objects.all().count(),
                "hiring_requests": hiring_request.objects.all().count(),
                "interview_schedules": interview_schedule.objects.all().count(),
            }
            return Response(record, status=status.HTTP_200_OK)
        else:
            company = company_data.objects.all()
            try:
                user_account = account_n_persmission.objects.get(email=request.user)
                user_image = (user_account.image.url,)
                employee_perms = (user_account.employee_perms,)
                client_perms = (user_account.client_perms,)
                leaves_perms = (user_account.leaves_perms,)
                invoices_perms = (user_account.invoices_perms,)
                policies_perms = (user_account.policies_perms,)
                guides_perms = (user_account.guides_perms,)
            except:
                user_image = ""
                employee_perms = {}
                client_perms = {}
                leaves_perms = {}
                invoices_perms = {}
                policies_perms = {}
                guides_perms = {}
            if company:
                comp_image = company[0].image.url
            else:
                comp_image = ""
            record = {
                "user": user,
                "company_image": comp_image,
                "user_image": user_image,
                "employee_perms": employee_perms,
                "client_perms": client_perms,
                "leaves_perms": leaves_perms,
                "invoices_perms": invoices_perms,
                "policies_perms": policies_perms,
                "guides_perms": guides_perms,
                "employees": employee.objects.all().count(),
                "clients": client.objects.all().count(),
                "hiring_requests": hiring_request.objects.all().count(),
                "interview_schedules": interview_schedule.objects.all().count(),
            }
            return Response(record, status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hr_Employees(APIView):
    @swagger_auto_schema(
        tags=["Employees"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "employees_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "image_path": openapi.Schema(type=openapi.TYPE_STRING),
                        "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                        "company": openapi.Schema(type=openapi.TYPE_STRING),
                        "active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                ),
            ),
            401: openapi.Response("Unauthorized"),
        },
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=[" ", "active", "inactive"],
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to retrieve hr Employees data.",
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        get_status = request.query_params.get("status")
        if get_status:
            if get_status == "active":
                outsource = outsource_employees.objects.all()
                records = []
                for emp in outsource:
                    try:
                        e_user = employee.objects.get(email=emp.employee_id)
                        c_user = client.objects.get(email=emp.client_id)
                        if e_user and c_user:
                            record = {
                                "id": e_user.id,
                                "employee_id": e_user.employee_id,
                                "name": e_user.first_name + " " + e_user.last_name,
                                "image_path": e_user.image.url,
                                "job_title": e_user.job_title,
                                "company": c_user.company_name,
                                "active": True,
                            }
                            records.append(record)
                    except:
                        continue
                if len(records) > 0:
                    return Response(records, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_204_NO_CONTENT)
            elif get_status == "inactive":
                employees = employee.objects.all()
                records = []
                for emp in employees:
                    try:
                        e_user = outsource_employees.objects.filter(
                            employee_id=emp.email
                        ).exclude(client_id=talent_email)
                        if not e_user:
                            record = {
                                "id": emp.id,
                                "employee_id": emp.employee_id,
                                "name": emp.first_name + " " + emp.last_name,
                                "image_path": emp.image.url,
                                "designation": emp.job_title,
                                "company": emp.company,
                                "active": False,
                            }
                            records.append(record)
                    except:
                        continue
                if len(records) > 0:
                    return Response(records, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            employees = employee.objects.all()
            if employees:
                records = []
                for emp in employees:
                    try:
                        e_user = outsource_employees.objects.filter(
                            employee_id=emp.email
                        ).exclude(client_id=talent_email)
                        if e_user:
                            c_user = client.objects.get(email=e_user[0].client_id)
                            company = c_user.company_name
                            active = True
                        else:
                            company = emp.company
                            active = False
                    except client.DoesNotExist:
                        company = emp.company
                        active = False

                    record = {
                        "id": emp.id,
                        "employee_id": emp.employee_id,
                        "name": emp.first_name + " " + emp.last_name,
                        "image_path": emp.image.url,
                        "designation": emp.job_title,
                        "company": company,
                        "active": active,
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Employees "],
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
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorize"),
        },
        operation_summary="Endpoint to delete an employee.",
        operation_id="3",
    )
    def delete(self, request, *args, **kwargs):
        employee_id = request.query_params.get("id")
        try:
            emp = employee.objects.get(id=employee_id)
            emp_name = f"{emp.first_name} {emp.last_name}"
            related_models = [
                outsource_employees,
                asset,
                employee_contract,
                time_sheet,
                employee_invoice,
                leave_balance,
                leave_request,
                punch_request,
                wfh_request,
                offshore_contracts,
                end_user,
                benefits,
                letter,
            ]
            with transaction.atomic(using="default"):
                for model_class in related_models:
                    try:
                        model_data = model_class.objects.filter(employee_id=emp.email)
                    except:
                        model_data = model_class.objects.filter(email=emp.email)

                    for instance in model_data:
                        for field in instance._meta.fields:
                            if isinstance(field, FileField):
                                file = getattr(instance, field.name)
                                removed = remove_bucket_file(file.name)
                                if removed:
                                    return Response(
                                        {"error": str(removed)},
                                        status=status.HTTP_400_BAD_REQUEST,
                                    )
                    model_data.delete()
                remove_image = remove_bucket_file(emp.image.name)
                if remove_image:
                    return Response(
                        {"error": str(remove_image)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                remove_resume = remove_bucket_file(emp.resume.name)
                if remove_resume:
                    return Response(
                        {"error": str(remove_resume)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                emp.delete()
            return Response(
                {"message": f"{emp_name} is removed successfully"},
                status=status.HTTP_200_OK,
            )
        except employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hr_Employee(APIView):
    @swagger_auto_schema(
        tags=["Employees : Profile, Client, Assets"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "active_clients": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "client_name": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "client_id": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "job_title": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "employeement_term": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "join_date": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        ),
                        "terminated_clients": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "client_name": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "client_id": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "job_title": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "employeement_term": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "join_date": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        ),
                        "assets": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "gadget": openapi.Schema(type=openapi.TYPE_STRING),
                                    "asset_id": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "assigned_date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATE,
                                    ),
                                    "assignee_name": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "assignee_email": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_EMAIL,
                                    ),
                                },
                            ),
                        ),
                        "employee_details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                                "first_name": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "last_name": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "gender": openapi.Schema(type=openapi.TYPE_STRING),
                                "dob": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATE,
                                ),
                                "email": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_EMAIL,
                                ),
                                "phone_number": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                ),
                                "personal_email": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_EMAIL,
                                ),
                                "marital_status": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "image_path": openapi.Schema(type=openapi.TYPE_STRING),
                                "emergency_contact": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "primary": openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                "name": openapi.Schema(
                                                    type=openapi.TYPE_STRING
                                                ),
                                                "relationship": openapi.Schema(
                                                    type=openapi.TYPE_STRING
                                                ),
                                                "phone": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER
                                                ),
                                            },
                                        ),
                                        "secondary": openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                "name": openapi.Schema(
                                                    type=openapi.TYPE_STRING
                                                ),
                                                "relationship": openapi.Schema(
                                                    type=openapi.TYPE_STRING
                                                ),
                                                "phone": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER
                                                ),
                                            },
                                        ),
                                    },
                                ),
                                "joining_date": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATE,
                                ),
                                "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                                "role": openapi.Schema(type=openapi.TYPE_STRING),
                                "status": openapi.Schema(type=openapi.TYPE_STRING),
                                "probation_started": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATE,
                                ),
                                "probation_ended": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATE,
                                ),
                            },
                        ),
                    },
                ),
            ),
            204: openapi.Response(description="No Content"),
            400: openapi.Response(description="Bad Request"),
            401: openapi.Response(description="Unauthorized"),
        },
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Employee record ID",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "tab",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=[" ", "client", "assets"],
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_id=".",
        operation_summary="Get Employee Details",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        tab = request.query_params.get("tab")
        try:
            employee_data = employee.objects.get(id=record_id)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if tab == "client":
            active_clients = []
            terminated_clients = []

            active = outsource_employees.objects.filter(
                employee_id=employee_data.email, status="active"
            ).exclude(client_id=talent_email)
            terminated = outsource_employees.objects.filter(
                employee_id=employee_data.email, status="terminated"
            ).exclude(client_id=talent_email)

            if active or terminated:
                for rec in active:
                    client_data = client.objects.get(email=rec.client_id)
                    record = {
                        "client_name": client_data.first_name
                        + " "
                        + client_data.last_name,
                        "client_id": client_data.client_id,
                        "job_title": rec.job_title,
                        "employeement_term": rec.employment_term,
                        "join_date": client_data.join_date,
                    }
                    active_clients.append(record)
                for rec in terminated:
                    client_data = client.objects.get(email=rec.client_id)
                    record = {
                        "client_name": client_data.first_name
                        + " "
                        + client_data.last_name,
                        "client_id": client_data.client_id,
                        "job_title": rec.job_title,
                        "employeement_term": rec.employment_term,
                        "join_date": client_data.join_date,
                    }
                    terminated_clients.append(record)

                data = {
                    "active_clients": active_clients,
                    "terminated_clients": terminated_clients,
                }
                return Response(data, status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        elif tab == "assets":
            try:
                emp_record = employee.objects.get(id=record_id)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            assets = asset.objects.filter(employee_id=emp_record.email)
            if assets:
                records = []
                for rec in assets:
                    record = {
                        "id": rec.id,
                        "gadget": rec.gadget,
                        "asset_id": rec.asset_id,
                        "assigned_date": rec.assigned_date,
                        "assignee_name": rec.assignee_name,
                        "assignee_email": rec.assignee_email,
                    }
                    records.append(record)
                if len(records) > 0:
                    return Response(records, status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        elif not tab:
            try:
                emp_record = employee.objects.get(id=record_id)
                record = {
                    "id": emp_record.id,
                    "employee_id": emp_record.employee_id,
                    "first_name": emp_record.first_name, 
                    "last_name": emp_record.last_name,
                    "gender": emp_record.gender,
                    "dob": emp_record.dob,
                    "phone_number":emp_record.phone_number,
                    "email": emp_record.email,
                    "personal_email": emp_record.personal_email,
                    "marital_status": emp_record.marital_status,
                    "image_path": emp_record.image.url,
                    "emergency_contact": emp_record.emergency_contact,
                    "joining_date": emp_record.joining_date,
                    "job_title": emp_record.job_title,
                    "role": emp_record.role,
                    "status": emp_record.job_status,
                    "probation_started": emp_record.starting_date,
                    "probation_ended": emp_record.ending_date,
                }
                return Response(record, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Time_and_leave(APIView):
    @swagger_auto_schema(
        tags=["Employees : Time & Leaves"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "time": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "check_in": openapi.Schema(type=openapi.TYPE_STRING),
                                "check_out": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                        "leaves": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "casual_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "total": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "balanced": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "status": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                    },
                                ),
                                "sick_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "total": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "balanced": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "status": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                    },
                                ),
                                "annual_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "total": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "balanced": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "status": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                    },
                                ),
                                "unpaid_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "total": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "balanced": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "status": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                    },
                                ),
                                "paid_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "total": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "balanced": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "status": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                    },
                                ),
                                "hajj_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "total": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "balanced": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "status": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                    },
                                ),
                            },
                        ),
                    },
                ),
            ),
            204: openapi.Response(description="No Content"),
            400: openapi.Response(description="Bad Request"),
            401: openapi.Response(description="Unauthorized"),
        },
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Employee record ID",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "tab",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["time", "leaves"],
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_id=".",
        operation_summary="Get Employee time and leaves Details",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        tab = request.query_params.get("tab")
        if tab == "time":
            try:
                employee_data = employee.objects.get(id=record_id)
                record = {
                    "id": employee_data.id,
                    "check_in": employee_data.punch_timings["check_in"],
                    "check_out": employee_data.punch_timings["check_out"],
                }
                return Response(record, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif tab == "leaves":
            try:
                employee_data = employee.objects.get(id=record_id)
                l_balance = leave_balance.objects.get(employee_id=employee_data.email)
                record = {
                    "id": l_balance.id,
                    "casual_leaves": l_balance.casual_leaves,
                    "sick_leaves": l_balance.sick_leaves,
                    "annual_leaves": l_balance.annual_leaves,
                    "unpaid_leaves": l_balance.unpaid_leaves,
                    "paid_leaves": l_balance.paid_leaves,
                    "hajj_leaves": l_balance.hajj_leaves,
                }
                return Response(record, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Employees : Time & Leaves"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "check_in": openapi.Schema(type=openapi.TYPE_STRING),
                "check_out": openapi.Schema(type=openapi.TYPE_STRING),
                "casual_leaves": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "balanced": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "availed": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, enum=["enable", "disable"]
                        ),
                    },
                ),
                "sick_leaves": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "balanced": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "availed": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, enum=["enable", "disable"]
                        ),
                    },
                ),
                "annual_leaves": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "balanced": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "availed": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, enum=["enable", "disable"]
                        ),
                    },
                ),
                "paid_leaves": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "balanced": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "availed": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, enum=["enable", "disable"]
                        ),
                    },
                ),
                "unpaid_leaves": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "balanced": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "availed": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, enum=["enable", "disable"]
                        ),
                    },
                ),
                "hajj_leaves": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "balanced": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "availed": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, enum=["enable", "disable"]
                        ),
                    },
                ),
            },
        ),
        responses={
            status.HTTP_200_OK: "Timings/leaves updated successfully",
            status.HTTP_400_BAD_REQUEST: "Bad request",
            status.HTTP_404_NOT_FOUND: "Employee record not found",
        },
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Employee record ID",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "tab",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["time", "leaves"],
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_id="1",
        operation_summary="Update Employee time and leaves details",
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        tab = request.query_params.get("tab")
        if tab == "time":
            try:
                check_in = request.data.get("check_in")
                check_out = request.data.get("check_out")
                employee_data = employee.objects.get(id=record_id)
                employee_data.punch_timings["check_in"] = check_in
                employee_data.punch_timings["check_out"] = check_out
                employee_data.save()
                return Response(
                    {"message": "Timings updated successfully"},
                    status=status.HTTP_200_OK,
                )
            except employee.DoesNotExist:
                return Response(
                    {"error": "Employee record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif tab == "leaves":
            updates = request.data
            try:
                emp_record = employee.objects.get(id=record_id)
                l_balance = leave_balance.objects.get(employee_id=emp_record.email)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            for key in updates:
                setattr(l_balance, key, updates[key])
            l_balance.save()
            return Response(
                {"message": "Leaves updated successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Update_Emp_Info(APIView):
    @swagger_auto_schema(
        tags=["Employees"],
        operation_id="3",
        operation_summary="Update Employee Information",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "emergency_contact": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "primary": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "name": openapi.Schema(type=openapi.TYPE_STRING),
                                "relationship": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "phone": openapi.Schema(type=openapi.TYPE_INTEGER),
                            },
                        ),
                        "secondary": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "name": openapi.Schema(type=openapi.TYPE_STRING),
                                "relationship": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "phone": openapi.Schema(type=openapi.TYPE_INTEGER),
                            },
                        ),
                    },
                ),
                "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                "dob": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    example="2024-02-24",
                ),
                "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                "marital_status": openapi.Schema(type=openapi.TYPE_STRING),
                "gender": openapi.Schema(type=openapi.TYPE_STRING),
                "role": openapi.Schema(type=openapi.TYPE_STRING),
                "joining_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
            },
        ),
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Employee record ID",
                type=openapi.TYPE_STRING,
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
            400: openapi.Response(description="Bad Request"),
        },
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates = request.data
        if "email" in updates:
            return Response({"error": "Email field cannnot be editted"}, status=status.HTTP_400_BAD_REQUEST)
        if "employee_name" in updates:
            name = updates["employee_name"]
            first_space_index = name.find(" ")

            updates["first_name"] = name[:first_space_index]
            updates["last_name"] = name[first_space_index + 1 :]
            del updates["employee_name"]

        try:
            emp_record = employee.objects.get(id=record_id)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for key in updates:
            setattr(emp_record, key, updates[key])
        try:
            emp_record.save()
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"message": "Personal information updated successfully"},
            status=status.HTTP_200_OK,
        )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Update_Emp_Profile_Pic(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Employees"],
        operation_id="4",
        operation_summary="Update Employee image",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Employee record ID",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="image",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
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
            400: openapi.Response(description="Bad Request"),
        },
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates = request.data
        try:
            emp_record = employee.objects.get(id=record_id)
        except employee.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


        if 'image' in updates:
            image_file = updates['image']
            try:
                img_ext_valid(image_file)
                valid_imgfile_type(image_file)
            except ValidationError as e:
                return Response({"error":e}, status=status.HTTP_400_BAD_REQUEST)
            
            removed = remove_bucket_file(emp_record.image.name)
            if removed:
                return Response({"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST)
            
        for key in updates:
            setattr(emp_record, key, updates[key])
        try:
            emp_record.save()
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "message": "Profile picture updated successfully",
                "image": emp_record.image.url,
            },
            status=status.HTTP_200_OK,
        )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Edit_Cridentials(APIView):
    @swagger_auto_schema(
        tags=["Employees"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                "current_password": openapi.Schema(type=openapi.TYPE_STRING),
                "new_password": openapi.Schema(type=openapi.TYPE_STRING),
                "confirm_password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=[
                "employees_id",
                "current_password",
                "new_password",
                "confirm_password",
            ],
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
        operation_summary="edit Credentials",
        operation_id="2",
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.data.get("employee_id")
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        try:
            employees = employee.objects.get(employee_id=record_id)
            end_user_instance = end_user.objects.get(email=employees.email)
        except employee.DoesNotExist:
            raise Http404("Employee does not exist")

        if not end_user_instance.check_password(current_password):
            return Response(
                {"error": "Incorrect current password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {"error": "New password and confirm password do not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        end_user_instance.set_password(new_password)
        end_user_instance.save()

        return Response(
            {"message": "Credentials have been updated"}, status=status.HTTP_200_OK
        )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Start_Hiring(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Clients : Hire & onBoard"],
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
            openapi.Parameter(
                "client_id",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required= True,
            ),
            openapi.Parameter(
                "job_title",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required= True,
            ),
            openapi.Parameter(
                "role_type",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required= True,
            ),
            openapi.Parameter(
                "gender",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required= True,
            ),
            openapi.Parameter(
                "employment_term",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required= True,
            ),
            openapi.Parameter(
                "salary_range",
                openapi.IN_FORM,
                type=openapi.TYPE_OBJECT,
                required= True,
            ),
            openapi.Parameter(
                "salary_currency",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required= True,
            ),
            openapi.Parameter(
                "country",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required= True,
            ),
            openapi.Parameter(
                "hiring_start_date",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required= True,
            ),
            openapi.Parameter(
                "hiring_end_date",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required= True,
            ),
            openapi.Parameter(
                "job_description",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required= True,
            ),
            openapi.Parameter(
                "comments",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to create Start_Hiring.",
        operation_id="9",
    )
    def post(self, request, *args, **kwargs):
        serializer = start_requestSerializer(data=request.data)
        try:
            if serializer.is_valid():
                hire_req = hiring_request.objects.create(
                    client_id=serializer.validated_data["client_id"],
                    job_title=serializer.validated_data["job_title"],
                    role_type=serializer.validated_data["role_type"],
                    gender=serializer.validated_data["gender"],
                    employment_term=serializer.validated_data["employment_term"],
                    salary_range=serializer.validated_data["salary_range"],
                    salary_currency=serializer.validated_data["salary_currency"],
                    country=serializer.validated_data["country"],
                    hiring_start_date=serializer.validated_data["hiring_start_date"],
                    hiring_end_date=serializer.validated_data["hiring_end_date"],
                    job_description=serializer.validated_data["job_description"],
                    comments=request.data.get("comments"),
                )
                notifications.objects.create(
                    email=talent_email,
                    ref_id=hire_req.id,
                    notification_type="hiring_request",
                    status="added",
                    description="A new hiring request created.",
                )
                return Response(
                    {
                        "message": "One new request is successfully added to hiring",
                        "id": hire_req.id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Clients : Hire & onBoard"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the client record",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
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
                            "salary_currency": openapi.Schema(type=openapi.TYPE_STRING),
                            "hiring_start_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "hiring_end_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "comments": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            204: openapi.Response(description="No Content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_id="10",
        operation_summary="Get Start_Hiring ",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            client_data = client.objects.get(id=record_id)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        hiring_requests = hiring_request.objects.filter(client_id=client_data.email)

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
                    "salary_currency": data.salary_currency,
                    "hiring_start_date": data.hiring_start_date,
                    "hiring_end_date": data.hiring_end_date,
                    "comments": data.comments,
                }
                records.append(record)

            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Clients : Hire & onBoard"],
        responses={
            200: openapi.Response("Successfull"),
            400: openapi.Response("Bad request"),
            401: openapi.Response("UnAuthorize"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required= True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required= True,
            ),
            openapi.Parameter(
                "job_title",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "role_type",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "gender",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "employment_term",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "salary_range",
                openapi.IN_FORM,
                type=openapi.TYPE_OBJECT,
            ),
            openapi.Parameter(
                "salary_currency",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "country",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "hiring_start_date",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "hiring_end_date",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "job_description",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
            ),
            openapi.Parameter(
                "comments",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to update hiring request.",
        operation_id="12",
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates = request.data
        try:
            record = hiring_request.objects.get(id=record_id)
            for key in updates:
                if key == "salary_range":
                    try:
                        salary_range = json.loads(updates["salary_range"])
                        record.salary_range = salary_range
                        continue
                    except Exception as e:
                        return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
                
                if key == "job_description":
                    removed = remove_bucket_file(record.job_description.name)
                    if removed:
                        return Response(
                            {"error": str(removed)},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                setattr(record, key, updates[key])
            try:
                record.save()
            except ValidationError as e:
                return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"message": "Hiring request has been updated successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Clients : Hire & onBoard"],
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
        operation_summary="Endpoint to delete a Start_Hiring.",
        operation_id="11",
    )
    def delete(self, request, *args, **kwargs):
        delete_id = request.query_params.get("id")
        try:
            hr_req = hiring_request.objects.get(id=delete_id)
            removed = remove_bucket_file(hr_req.job_description.name)
            if removed:
                return Response(
                    {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                )
            notifications.objects.filter(
                email=talent_email, ref_id=hr_req.id, notification_type="hiring_request"
            ).delete()
            hr_req.delete()
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
        tags=["Clients : Hire & onBoard"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "client_id": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
                "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                "gender": openapi.Schema(type=openapi.TYPE_STRING),
                "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                "role_type": openapi.Schema(type=openapi.TYPE_STRING),
                "employment_term": openapi.Schema(type=openapi.TYPE_STRING),
                "interview_date_time": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                ),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=[
                "client_id",
                "employee_name",
                "gender",
                "job_title",
                "role_type",
                "employment_term",
                "interview_date_time",
                "country",
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
        operation_summary="Endpoint to create interview request.",
        operation_id="2",
    )
    def post(self, request, *args, **kwargs):
        serializer = interview_requestSerializer(data=request.data)
        if serializer.is_valid():
            int_sch = interview_schedule.objects.create(
                client_id=serializer.validated_data["client_id"],
                employee_name=serializer.validated_data["employee_name"],
                gender=serializer.validated_data["gender"],
                job_title=serializer.validated_data["job_title"],
                role_type=serializer.validated_data["role_type"],
                employment_term=serializer.validated_data["employment_term"],
                interview_date_time=serializer.validated_data["interview_date_time"],
                country=serializer.validated_data["country"],
            )
            notifications.objects.create(
                email=int_sch.client_id,
                ref_id=int_sch.id,
                notification_type="interview_schedule",
                status="added",
                description=f"Interview of {int_sch.employee_name} is scheduled for {int_sch.job_title} position",
            )
            return Response(
                {"message": "Interview is successfully set", "id": int_sch.id},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Clients : Hire & onBoard"],
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
                            "role_type": openapi.Schema(type=openapi.TYPE_STRING),
                            "employment_term": openapi.Schema(type=openapi.TYPE_STRING),
                            "interview_date_time": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
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
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Client id record",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to retrieve interiew schedules.",
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            client_data = client.objects.get(id=record_id)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        interview_records = interview_schedule.objects.filter(
            client_id=client_data.email
        )

        if interview_records:
            records = []
            for data in interview_records:
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
        tags=["Clients : Hire & onBoard"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "client_id": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
                "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                "gender": openapi.Schema(type=openapi.TYPE_STRING),
                "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                "role_type": openapi.Schema(type=openapi.TYPE_STRING),
                "employment_term": openapi.Schema(type=openapi.TYPE_STRING),
                "interview_date_time": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                ),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response("Successful updated"),
            400: openapi.Response("Bad request"),
            401: openapi.Response("UnAuthorize"),
            404: openapi.Response(description="Not Found"),
        },
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Id of record to update",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_summary="Endpoint to update interview request.",
        operation_id="4",
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates = request.data
        try:
            record = interview_schedule.objects.get(id=record_id)
            for key in updates:
                setattr(record, key, updates[key])
            record.save()
            return Response(
                {"message": "Interview schedule record has been updated successfully"},
                status=status.HTTP_200_OK,
            )
        except interview_schedule.DoesNotExist:
            return Response(
                    {"error": "Interview schedule record not found"}, status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Clients : Hire & onBoard"],
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
        operation_id="3",
    )
    def delete(self, request, *args, **kwargs):
        user = request.user
        delete_id = request.query_params.get("id")
        try:
            int_sch = interview_schedule.objects.get(id=delete_id)
            notifications.objects.get(
                ref_id=int_sch.id,
                notification_type="interview_schedule",
            ).delete()
            int_sch.delete()
            return Response(
                {"message": "Interview is successfully deleted"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Onboarding(APIView):
    @swagger_auto_schema(
        tags=["Clients : Hire & onBoard"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "client_id": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
                "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                "gender": openapi.Schema(type=openapi.TYPE_STRING),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                "role_type": openapi.Schema(type=openapi.TYPE_STRING),
                "employment_term": openapi.Schema(type=openapi.TYPE_STRING),
                "joining_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
                "notice_period": openapi.Schema(type=openapi.TYPE_INTEGER),
                "salary": openapi.Schema(type=openapi.TYPE_INTEGER),
                "salary_currency": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=[
                "client_id",
                "employee_name",
                "gender",
                "country",
                "job_title",
                "role_type",
                "employment_term",
                "joining_date",
                "notice_period",
                "salary",
                "salary_currency",
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
        operation_summary="Endpoint to create onboarding request.",
        operation_id="6",
    )
    def post(self, request, *args, **kwargs):
        serializer = onboardingSerializer(data=request.data)
        try:
            if serializer.is_valid():
                onb = onboarding.objects.create(
                    client_id=serializer.validated_data["client_id"],
                    employee_name=serializer.validated_data["employee_name"],
                    gender=serializer.validated_data["gender"],
                    country=serializer.validated_data["country"],
                    job_title=serializer.validated_data["job_title"],
                    role_type=serializer.validated_data["role_type"],
                    joining_date=serializer.validated_data["joining_date"],
                    notice_period=serializer.validated_data["notice_period"],
                    salary=serializer.validated_data["salary"],
                    salary_currency=serializer.validated_data["salary_currency"],
                    employment_term=serializer.validated_data["employment_term"],
                )
                notifications.objects.create(
                    email=onb.client_id,
                    ref_id=onb.id,
                    notification_type="onboarding",
                    status="added",
                    description=f"{onb.employee_name} is onboard for {onb.job_title} position",
                )
                return Response(
                    {
                        "message": f"You have set {onb.employee_name} to onboarding",
                        "id": onb.id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Clients : Hire & onBoard"],
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
                            "salary_currency": openapi.Schema(type=openapi.TYPE_STRING),
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
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Client id record",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to retrieve on-boarding data.",
        operation_id="7",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            client_data = client.objects.get(id=record_id)
            onboardings = onboarding.objects.filter(client_id=client_data.email)
            records = []
            if onboardings:
                for data in onboardings:
                    record = {
                        "id": data.id,
                        "employee_name": data.employee_name,
                        "gender": data.gender,
                        "country": data.country,
                        "job_title": data.job_title,
                        "role_type": data.role_type,
                        "employment_term": data.employment_term,
                        "joining_date": data.joining_date,
                        "notice_period": data.notice_period,
                        "salary": data.salary,
                        "salary_currency": data.salary_currency,
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Clients : Hire & onBoard"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "client_id": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
                "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                "gender": openapi.Schema(type=openapi.TYPE_STRING),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                "role_type": openapi.Schema(type=openapi.TYPE_STRING),
                "employment_term": openapi.Schema(type=openapi.TYPE_STRING),
                "joining_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
                "notice_period": openapi.Schema(type=openapi.TYPE_INTEGER),
                "salary": openapi.Schema(type=openapi.TYPE_INTEGER),
                "salary_currency": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response("Successful updated"),
            400: openapi.Response("Bad request"),
            401: openapi.Response("UnAuthorize"),
            404: openapi.Response(description="Not Found"),
        },
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Id of record to update",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_summary="Endpoint to update onboarding request.",
        operation_id="5",
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates = request.data
        try:
            record = onboarding.objects.get(id=record_id)
            for key in updates:
                setattr(record, key, updates[key])
            record.save()
            return Response(
                {"message": "Onboarding record has been updated successfully"},
                status=status.HTTP_200_OK,
            )
        except onboarding.DoesNotExist:
            return Response(
                    {"error": "Onboarding record not found"}, status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Clients : Hire & onBoard"],
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
        operation_summary="Endpoint to delete a onboarding request.",
        operation_id="8",
    )
    def delete(self, request, *args, **kwargs):
        delete_id = request.query_params.get("id")
        try:
            onb = onboarding.objects.get(id=delete_id)
            employee_name = f"{onb.employee_name}"
            notifications.objects.get(
                email=onb.client_id, ref_id=onb.id, notification_type="onboarding"
            ).delete()
            onb.delete()
            return Response(
                {"message": f"{employee_name} is successfully removed from onboarding"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hr_Clients(APIView):
    @swagger_auto_schema(
        tags=["Clients"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "client_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "image_path": openapi.Schema(type=openapi.TYPE_STRING),
                        "company_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
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
        operation_summary="Endpoint to retrieve Clients data.",
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        try:
            clients = client.objects.all()
            if clients:
                records = []
                for cl in clients:
                    user = end_user.objects.get(email=cl.email)
                    record = {
                        "id": cl.id,
                        "client_id": cl.client_id,
                        "name": cl.first_name + " " + cl.last_name,
                        "image_path": cl.image.url,
                        "company_name": cl.company_name,
                        "active": user.is_active,
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except client.DoesNotExist:
            return Response(
                {"message": "Clients not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Clients"],
        responses={
            201: "Successful update Client Status",
            400: "Bad Request",
            401: "Unauthorized",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            },
            required=[
                "is_active",
            ],
        ),
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to update",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_summary="Endpoint to update client status.",
        operation_id="3",
    )
    def patch(self, request, *args, **kwargs):
        request_id = request.query_params.get("id")
        to_update_status = request.data["is_active"]
        try:
            client_data = client.objects.get(id=request_id)
            update_client_status = end_user.objects.get(email=client_data.email)
            if update_client_status:
                if to_update_status == True:
                    update_client_status.is_active = to_update_status
                    update_client_status.save()
                    return Response(
                        {
                            "message": f"{client_data.first_name} {client_data.last_name} is set to active"
                        },
                        status=status.HTTP_200_OK,
                    )
                elif to_update_status == False:
                    update_client_status.is_active = to_update_status
                    update_client_status.save()
                    return Response(
                        {
                            "message": f"{client_data.first_name} {client_data.last_name} is set to inactive"
                        },
                        status=status.HTTP_200_OK,
                    )
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Clients"],
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="client record ID",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful update"),
            400: openapi.Response(description="Bad Request"),
        },
        operation_id="3 ",
        operation_summary="Endpoint to remove client.",
    )
    def delete(self, request, *args, **kwargs):
        try:
            client_id = request.query_params.get("id")
            clt = client.objects.get(id=client_id)
            client_name = f"{clt.first_name} {clt.last_name}"
            related_models = [
                outsource_employees,
                employee_invoice,
                hiring_request,
                interview_schedule,
                client_contract,
                offshore_contracts,
                onboarding,
                other_payment,
                punch_request,
                time_sheet,
                leave_request,
                end_user,
            ]
            for model in related_models:
                try:
                    data = model.objects.filter(client_id=clt.email)
                except:
                    data = model.objects.filter(email=clt.email)

                for instance in data:
                    for field in instance._meta.fields:
                        if isinstance(field, FileField):
                            file = getattr(instance, field.name)
                            removed = remove_bucket_file(file.name)
                            if removed:
                                return Response(
                                    {"error": str(removed)},
                                    status=status.HTTP_400_BAD_REQUEST,
                                )
                data.delete()
            remove_image = remove_bucket_file(clt.image.name)
            if remove_image:
                return Response(
                    {"error": str(remove_image)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            clt.delete()
            return Response(
                {"message": f"{client_name} is removed successfully"},
                status=status.HTTP_200_OK,
            )
        except client.DoesNotExist:
            return Response(
                {"error": "client not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hr_Client(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Clients : Profile"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "client_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "company_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "phone_number": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                        ),
                        "country": openapi.Schema(type=openapi.TYPE_STRING),
                        "image_path": openapi.Schema(type=openapi.TYPE_STRING),
                        "address": openapi.Schema(type=openapi.TYPE_STRING),
                        "join_date": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            204: openapi.Response(description="No Content"),
            400: openapi.Response(description="Bad Request"),
            401: openapi.Response(description="Unauthorized"),
        },
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Client record ID",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_id="1",
        operation_summary="Get Client Details",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            client_data = client.objects.get(id=record_id)
            record = {
                "id": client_data.id,
                "client_id": client_data.client_id,
                "first_name": client_data.first_name,
                "last_name": client_data.last_name,
                "company_name": client_data.company_name,
                "phone_number": client_data.phone_number,
                "email": client_data.email,
                "country": client_data.country,
                "image_path": client_data.image.url,
                "address": client_data.address,
                "join_date": client_data.join_date,
            }
            return Response(record, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Clients : Profile"],
        operation_id="2",
        operation_summary="Update Clients Personal Information",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Employee record ID",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="client_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="first_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="last_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="company_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="phone_number",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                name="join_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                name="country",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="address",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="image",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful update"),
            400: openapi.Response(description="Bad Request"),
        },
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates = request.data
        try:
            client_record = client.objects.get(id=record_id)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if "email" in updates:
            return Response({"error": "Email field cannnot be editted"}, status=status.HTTP_400_BAD_REQUEST)

        if updates.get("image"):
            try:
                img_ext_valid(updates["image"])
                valid_imgfile_type(updates["image"])
            except ValidationError as e:
                return Response({"error":e}, status=status.HTTP_400_BAD_REQUEST)
            
            removed = remove_bucket_file(client_record.image.name)
            if removed:
                return Response(
                    {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                )
            
        for key in updates:
            if key=="company_name":
                clnt = client.objects.get(id=record_id)
                user_record = end_user.objects.get(email=clnt.email)
                user_record.username = updates[key]
                user_record.save()
            setattr(client_record, key, updates[key])
        try:
            client_record.save()
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "message": "Information updated successfully",
                "image": client_record.image.url,
            },
            status=status.HTTP_200_OK,
        )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Company_Settings(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Settings: Company settings"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "company_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "company_email": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                        ),
                        "website_url": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                        ),
                        "image": openapi.Schema(type=openapi.TYPE_FILE),
                    },
                ),
            ),
            204: openapi.Response(description="No content"),
            401: openapi.Response(description="Unauthorized"),
        },
        operation_id="0",
        operation_summary="Endpoint to retrieve company data",
    )
    def get(self, request, *args, **kwargs):
        company = company_data.objects.all()
        if company:
            data = company_data.objects.all()[0]
            record = {
                "id": data.id,
                "company_name": data.company_name,
                "company_email": data.company_email,
                "website_url": data.website_url,
                "image": data.image.url,
            }
            return Response(record, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Settings: Company settings"],
        responses={
            200: "Successful request",
            201: "Successful created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="company_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="company_email",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
            ),
            openapi.Parameter(
                name="website_url",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_URI,
            ),
            openapi.Parameter(
                name="image",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
            ),
        ],
        operation_summary="Endpoint to update company data.",
        operation_id="1",
    )
    def patch(self, request, *args, **kwargs):
        updates = request.data
        comp_datas = company_data.objects.all()
        if comp_datas:
            try:
                comp_data = comp_datas[0]
                for key in updates:
                    if key == "image":
                        try:
                            img_ext_valid(updates[key])
                            valid_imgfile_type(updates[key])
                        except ValidationError as e:
                            return Response({"error":e}, status=status.HTTP_400_BAD_REQUEST)
                        
                        removed = remove_bucket_file(comp_data.image.name)
                        if removed:
                            return Response(
                                {"error": str(removed)},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                    setattr(comp_data, key, updates[key])
                try:
                    comp_data.save()
                except ValidationError as e:
                    return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response(
                        {"error": str(e)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                return Response(
                    {
                        "message": "Company settings are successfully updated",
                        "image": comp_data.image.url,
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = CompanyDataSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    comp_data = company_data.objects.create(
                        company_name=serializer.validated_data["company_name"],
                        company_email=serializer.validated_data["company_email"],
                        website_url=serializer.validated_data["website_url"],
                        image=serializer.validated_data["image"],
                    )
                    return Response(
                        {
                            "message": "Company settings are successfully added",
                            "image": comp_data.image.url,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except ValidationError as e:
                    return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response(
                        {"error": "Invalid form fields"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Accounts(APIView):
    parser_classes = (MultiPartParser,)
    salt = b"\rN\xac\xec\xbd\xfc2\xbc^\xb69\xf6\x80&\x0b\x82{\xf7@\xd8\x14\x15\xca\xf9i\xfd0B\xf4|r\xea"
    iv = b'2\xd36mo\xe2\xae\x921\xf8\xa8\xfd9\xd8+"'
    pass_key = "admin@espark"

    @swagger_auto_schema(
        tags=["Settings: Accounts"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "account_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "email": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                            ),
                            "image": openapi.Schema(type=openapi.TYPE_FILE),
                            "password": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            204: openapi.Response(description="No content"),
            401: openapi.Response(description="Unauthorized"),
        },
        operation_id="1",
        operation_summary="Endpoint to retrieve accounts data",
    )
    def get(self, request, *args, **kwargs):
        accounts = account_n_persmission.objects.all()
        if accounts:
            accounts_record = []
            for account in accounts:
                key = PBKDF2(self.pass_key, self.salt, dkLen=32)
                de_cipher = AES.new(key, AES.MODE_CBC, iv=self.iv)
                unciphered_data = unpad(
                    de_cipher.decrypt(account.password), AES.block_size
                )
                record = {
                    "id": account.id,
                    "account_name": account.account_name,
                    "email": account.email,
                    "image": account.image.url,
                    "password": unciphered_data,
                }
                accounts_record.append(record)
            return Response(accounts_record, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Settings: Accounts"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="account_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="email",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                name="image",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                name="password",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="confirm_password",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_summary="Endpoint to create accounts record.",
        operation_id="2",
    )
    def post(self, request, *args, **kwargs):
        try:
            password = request.data["password"]
            confirm_password = request.data["confirm_password"]
            if password == confirm_password:
                serializer = AccountPermissionSerializer(data=request.data)
                if serializer.is_valid():
                    key = PBKDF2(self.pass_key, self.salt, dkLen=32)
                    message = password
                    message_bytes = message.encode("utf-8")
                    en_cipher = AES.new(key, AES.MODE_CBC, iv=self.iv)
                    ciphered_data = en_cipher.encrypt(
                        pad(message_bytes, AES.block_size)
                    )
                    try:
                        end_user.objects.create_user(
                            username=serializer.validated_data["account_name"],
                            role=serializer.validated_data["account_name"],
                            email=serializer.validated_data["email"],
                            password=password,
                        )

                        acc_n_perm = account_n_persmission.objects.create(
                            account_name=serializer.validated_data["account_name"],
                            email=serializer.validated_data["email"],
                            image=serializer.validated_data["image"],
                            password=ciphered_data,
                            employee_perms={
                                "read": False,
                                "write": False,
                                "delete": False,
                                "download": False,
                            },
                            client_perms={
                                "read": False,
                                "write": False,
                                "delete": False,
                                "download": False,
                            },
                            leaves_perms={
                                "read": False,
                                "write": False,
                                "delete": False,
                                "download": False,
                            },
                            invoices_perms={
                                "read": False,
                                "write": False,
                                "delete": False,
                                "download": False,
                            },
                            policies_perms={
                                "read": False,
                                "write": False,
                                "delete": False,
                                "download": False,
                            },
                            guides_perms={
                                "read": False,
                                "write": False,
                                "delete": False,
                                "download": False,
                            },
                        )

                        return Response(
                            {
                                "message": "Account has been added successfully",
                                "id": acc_n_perm.id,
                                "image": acc_n_perm.image.url,
                            },
                            status=status.HTTP_201_CREATED,
                        )
                    except ValidationError as e:
                        return Response(
                            {"error": e}, status=status.HTTP_400_BAD_REQUEST
                        )
                    except Exception as e:
                        return Response(
                            {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"error": "New password and confirm password must be same"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Settings: Accounts"],
        responses={
            200: openapi.Response("Successfull"),
            400: openapi.Response("Bad request"),
            401: openapi.Response("UnAuthorize"),
            404: openapi.Response("Not Found"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required= True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "account_name",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "email",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
            ),
            openapi.Parameter(
                "password",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "image",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
            ),
        ],
        operation_summary="Endpoint to update account record.",
        operation_id="4",
    )
    def patch(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        updates = request.data
        try:
            file_to_remove=""
            account = account_n_persmission.objects.get(id=id)
            for key in updates:
                if key == "password":
                    key = PBKDF2(self.pass_key, self.salt, dkLen=32)
                    message = updates["password"]
                    message_bytes = message.encode("utf-8")
                    en_cipher = AES.new(key, AES.MODE_CBC, iv=self.iv)
                    ciphered_data = en_cipher.encrypt(
                        pad(message_bytes, AES.block_size)
                    )
                    setattr(account, "password", ciphered_data)
                    continue
                if key == "image":
                    file_to_remove = account.image.name
                setattr(account, key, updates[key])
            account.save()
            if file_to_remove != "":
                    removed = remove_bucket_file(file_to_remove)
                    if removed:
                        return Response(
                            {"error": str(removed)},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
            return Response(
                {"message": "Changes have been saved successfully"},
                status=status.HTTP_200_OK,
            )
        except account_n_persmission.DoesNotExist:
            return Response({"error": "Account record not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Settings: Accounts"],
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
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorize"),
        },
        operation_summary="Endpoint to delete an account.",
        operation_id="3",
    )
    def delete(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        try:
            account = account_n_persmission.objects.get(id=id)
            end_user.objects.get(email=account.email).delete()
            removed = remove_bucket_file(account.image.name)
            if removed:
                return Response(
                    {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                )
            account.delete()
            return Response(
                {"message": "Account has been deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Change_Password(APIView):
    @swagger_auto_schema(
        tags=["Settings: Change password"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "current_password": openapi.Schema(type=openapi.TYPE_STRING),
                "new_password": openapi.Schema(type=openapi.TYPE_STRING),
                "confirm_password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=[
                "current_password",
                "new_password",
                "confirm_password",
            ],
        ),
        responses={
            201: "Successful request",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_summary="Endpoint to update password.",
        operation_id=".",
    )
    def patch(self, request, *args, **kwargs):
        current_password = request.data["current_password"]
        new_password = request.data["new_password"]
        confirm_password = request.data["confirm_password"]
        if new_password != confirm_password:
            return Response(
                {"error": "New password and confirm password must be same"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            end_user_instance = end_user.objects.get(email=request.user)
            if end_user_instance.check_password(current_password):
                end_user_instance.set_password(new_password)
                end_user_instance.save()
                return Response(
                    {"message": "Credentials have been updated successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid current password"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Roles_n_Permissions(APIView):
    @swagger_auto_schema(
        tags=["Settings: Roles & permissions"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "role": openapi.Schema(type=openapi.TYPE_STRING),
                            "employee_perms": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "download": openapi.Schema(
                                        type=openapi.TYPE_BOOLEAN
                                    ),
                                },
                            ),
                            "client_perms": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "download": openapi.Schema(
                                        type=openapi.TYPE_BOOLEAN
                                    ),
                                },
                            ),
                            "leaves_perms": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "download": openapi.Schema(
                                        type=openapi.TYPE_BOOLEAN
                                    ),
                                },
                            ),
                            "invoices_perms": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "download": openapi.Schema(
                                        type=openapi.TYPE_BOOLEAN
                                    ),
                                },
                            ),
                            "policies_perms": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "download": openapi.Schema(
                                        type=openapi.TYPE_BOOLEAN
                                    ),
                                },
                            ),
                            "guides_perms": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    "download": openapi.Schema(
                                        type=openapi.TYPE_BOOLEAN
                                    ),
                                },
                            ),
                        },
                    ),
                ),
            ),
            204: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
        },
        operation_id="1",
        operation_summary="Endpoint to retrieve account data",
    )
    def get(self, request, *args, **kwargs):
        permissions = account_n_persmission.objects.all()
        records = []
        for perm in permissions:
            record = {
                "id": perm.id,
                "role": perm.account_name,
                "employee_perms": perm.employee_perms,
                "client_perms": perm.client_perms,
                "leaves_perms": perm.leaves_perms,
                "invoices_perms": perm.invoices_perms,
                "policies_perms": perm.policies_perms,
                "guides_perms": perm.guides_perms,
            }
            records.append(record)
        if records:
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Settings: Roles & permissions"],
        responses={
            201: "Successful request",
            400: "Bad Request",
            401: "Unauthorized",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "employee_perms": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "download": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                ),
                "client_perms": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "download": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                ),
                "leaves_perms": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "download": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                ),
                "invoices_perms": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "download": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                ),
                "policies_perms": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "read": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "write": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "delete": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "download": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                ),
            },
            required=[
                "employee_perms",
                "client_perms",
                "leaves_perms",
                "invoices_perms",
                "policies_perms",
            ],
        ),
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to update",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_summary="Endpoint to update permissions record.",
        operation_id="2",
    )
    def patch(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        updates = request.data
        try:
            account = account_n_persmission.objects.get(id=id)
            for key in updates:
                setattr(account, key, updates[key])
            account.save()
            return Response(
                {"message": "Changes have been saved successfully"},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Policies(APIView):
    parser_classes = (MultiPartParser,)

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
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                            "employee": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "client": openapi.Schema(type=openapi.TYPE_BOOLEAN),
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
                required=True,
            ),
        ],
        operation_summary="Endpoint to retrieve HR policies",
        operation_id="2",
    )
    def get(self, request, *args, **kwargs):
        hr_policies = policy.objects.all()
        policies = []
        for hr_pol in hr_policies:
            record = {
                "id": hr_pol.id,
                "policy_name": hr_pol.policy_name,
                "description": hr_pol.description,
                "employee": hr_pol.employee,
                "client": hr_pol.client,
            }
            policies.append(record)
        if len(policies) > 0:
            return Response(policies, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Policies"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="policy_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="description",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="policy_doc",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ],
        operation_summary="Add a new Policy",
        operation_id="1",
    )
    def post(self, request, *args, **kwargs):
        serializer = PolicySerializer(data=request.data)
        if serializer.is_valid():
            try:
                pol = policy.objects.create(
                    policy_name=serializer.validated_data["policy_name"],
                    description=request.data.get("description"),
                    policy_doc=serializer.validated_data["policy_doc"],
                    employee=False,
                    client=False,
                )
                return Response(
                    {
                        "message": "New policy has been added successfully",
                        "id": pol.id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except ValidationError as e:
                return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Policies"],
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
        operation_summary="Endpoint to delete a policy request.",
        operation_id="4",
    )
    def delete(self, request, *args, **kwargs):
        delete_id = request.query_params.get("id")
        try:
            pol = policy.objects.get(id=delete_id)
            removed = remove_bucket_file(pol.policy_doc.name)
            if removed:
                return Response(
                    {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                )
            pol.delete()
            return Response(
                {"message": "Policy has been removed successfully"},
                status=status.HTTP_200_OK,
            )
        except policy.DoesNotExist:
            return Response({"error": "Policy record not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Policies"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Policy record id",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "policy_name",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "description",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "policy_doc",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
            ),
        ],
        responses={
            200: "Request processed successfully",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Policy not found",
        },
        operation_summary="Endpoint to edit a policy",
        operation_id="3",
    )
    def patch(self, request, *args, **kwargs):
        policy_id = request.query_params.get("id")
        updates = request.data
        try:
            policy_instance = policy.objects.get(id=policy_id)
            for key in updates:
                if key == "policy_doc":
                    policy_doc = updates['policy_doc']
                    try:
                        pdf_ext_valid(policy_doc)
                        valid_pdffile_type(policy_doc)
                    except ValidationError as e:
                        return Response({"error":e}, status=status.HTTP_400_BAD_REQUEST)
                    
                    removed = remove_bucket_file(policy_instance.policy_doc.name)
                    if removed:
                        return Response({"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST)
                setattr(policy_instance, key, updates[key])
            policy_instance.save()
            return Response(
                {"message": "Changes have been saved successfully"},
                status=status.HTTP_200_OK,
            )
        except policy.DoesNotExist:
            return Response(
                {"error": "Policy not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Policies_Edit(APIView):
    @swagger_auto_schema(
        tags=["Edit Policies"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "data": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "employee": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "client": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        },
                    ),
                ),
            },
            required=["data"],
        ),
        responses={
            200: "Request processed successfully",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Policy not found",
        },
        operation_summary="Endpoint to edit a policy",
        operation_id="3",
    )
    def patch(self, request, *args, **kwargs):
        policy_ids_array = json.loads(request.body)
        try:
            for policy_id_json in policy_ids_array["data"]:
                try:
                    policy_instance = policy.objects.get(id=policy_id_json["id"])
                except policy.DoesNotExist:
                    return Response(
                        {"error": "Policy not found"}, status=status.HTTP_404_NOT_FOUND
                    )
                del policy_id_json["id"]
                for key in policy_id_json:
                    setattr(policy_instance, key, policy_id_json[key])
                policy_instance.save()
            return Response(
                {"message": "Changes have been saved successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Company_Contract(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Company Contract"],
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["client", "employee"],
                default="client",
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="client_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="contract_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="contract_doc",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                name="employee_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        operation_id="1",
    )
    def post(self, request, *args, **kwargs):
        posted_data = request.data
        get_status = request.query_params.get("status")
        if get_status:
            if get_status == "client":
                try:
                    clnt = client.objects.get(client_id=posted_data["client_id"])
                    posted_data["client_id"] = clnt.email
                    serializer = ClientContractSerializers(data=posted_data)
                    if serializer.is_valid():
                        cl_contract = client_contract.objects.create(
                            client_id=serializer.validated_data["client_id"],
                            contract_name=serializer.validated_data["contract_name"],
                            date=serializer.validated_data["date"],
                            contract_doc=serializer.validated_data["contract_doc"],
                        )
                        notifications.objects.create(
                            email=cl_contract.client_id,
                            ref_id=cl_contract.id,
                            notification_type="client_contract",
                            status="added",
                            description=f"{cl_contract.contract_name} contract is added",
                        )
                        return Response(
                            {
                                "message": "One new contract has been added to company contracts",
                                "id": cl_contract.id,
                            },
                            status=status.HTTP_201_CREATED,
                        )
                    else:
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )
                except ValidationError as e:
                    return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response(
                        {"error": str(e)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            elif get_status == "employee":
                try:
                    emp = employee.objects.get(employee_id=posted_data["employee_id"])
                    posted_data["employee_id"] = emp.email
                    serializer = EmployeeContractSerializers(data=posted_data)
                    if serializer.is_valid():
                        emp_contract = employee_contract.objects.create(
                            employee_id=serializer.validated_data["employee_id"],
                            contract_name=serializer.validated_data["contract_name"],
                            date=serializer.validated_data["date"],
                            contract_doc=serializer.validated_data["contract_doc"],
                        )
                        notifications.objects.create(
                            email=emp_contract.employee_id,
                            ref_id=emp_contract.id,
                            notification_type="employee_contract",
                            status="added",
                            description=f"{emp_contract.contract_name} contract is added",
                        )
                        return Response(
                            {
                                "message": "One new contract has been added to company contracts",
                                "id": emp_contract.id,
                            },
                            status=status.HTTP_201_CREATED,
                        )
                    else:
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )
                except ValidationError as e:
                    return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response(
                        {"error": str(e)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        return Response(
            {"message": "Invalid status parameter"}, status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        tags=["Company Contract"],
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["clients", "employees"],
                default="clients",
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "contract_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "email": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                            ),
                            "client_id/employee_id": openapi.Schema(
                                type=openapi.TYPE_STRING
                            ),
                            "date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                        },
                    ),
                ),
            ),
            204: openapi.Response(description="No Content"),
            401: openapi.Response(description="Unauthorized"),
        },
        operation_id="2",
    )
    def get(self, request, *args, **kwargs):
        get_status = request.query_params.get("status")
        if get_status:
            try:
                if get_status == "clients":
                    contracts = client_contract.objects.all()
                    client_cont = []
                    for contract in contracts:
                        clnt = client.objects.get(email=contract.client_id)
                        record = {
                            "id": contract.id,
                            "contract_name": contract.contract_name,
                            "email": contract.client_id,
                            "client_id": clnt.client_id,
                            "date": contract.date,
                        }
                        client_cont.append(record)
                    if not client_cont:
                        return Response(
                            {"message": "No client contracts available"},
                            status=status.HTTP_204_NO_CONTENT,
                        )
                    return Response(client_cont, status=status.HTTP_200_OK)

                elif get_status == "employees":
                    contracts = employee_contract.objects.all()
                    employee_cont = []
                    for contract in contracts:
                        emp = employee.objects.get(email=contract.employee_id)
                        record = {
                            "id": contract.id,
                            "contract_name": contract.contract_name,
                            "email": contract.employee_id,
                            "employee_id": emp.employee_id,
                            "date": contract.date,
                        }
                        employee_cont.append(record)
                    if not employee_cont:
                        return Response(
                            {"message": "No employee contracts available"},
                            status=status.HTTP_204_NO_CONTENT,
                        )
                    return Response(employee_cont, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"error": "Invalid status parameter"}, status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        tags=["Company Contract"],
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["clients", "employees"],
                default="client",
            ),
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
        operation_summary="Endpoint to delete a company contract request.",
        operation_id="3",
    )
    def delete(self, request, *args, **kwargs):
        delete_id = request.query_params.get("id")
        get_status = request.query_params.get("status")
        try:
            if get_status == "clients":
                cl_contract = client_contract.objects.get(id=delete_id)
                removed = remove_bucket_file(cl_contract.contract_doc.name)
                if removed:
                    return Response(
                        {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                    )
                notifications.objects.get(
                    email=cl_contract.client_id,
                    ref_id=cl_contract.id,
                    notification_type="client_contract",
                ).delete()
                cl_contract.delete()
            elif get_status == "employees":
                emp_contract = employee_contract.objects.get(id=delete_id)
                removed = remove_bucket_file(emp_contract.contract_doc.name)
                if removed:
                    return Response(
                        {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                    )
                notifications.objects.get(
                    email=emp_contract.employee_id,
                    ref_id=emp_contract.id,
                    notification_type="employee_contract",
                ).delete()
                emp_contract.delete()
            else:
                return Response(
                    {"error": "Invalid status parameter"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"message": "One contract has been removed from company contracts"},
                status=status.HTTP_200_OK,
            )

        except client_contract.DoesNotExist:
            return Response(
                {"error": "Client contract not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except employee_contract.DoesNotExist:
            return Response(
                {"error": "Employee contract not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Company Contract"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Company Contract record id",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "tab",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["employee", "client"],
                required=True,
            ),
            openapi.Parameter(
                name="client_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL
            ),
            openapi.Parameter(
                name="employee_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL
            ),
            openapi.Parameter(
                name="contract_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                name="contract_doc",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
            ),
        ],
        responses={
            200: "Request processed successfully",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Contract not found",
        },
        operation_summary="Endpoint to edit a company contract",
        operation_id="4",
    )
    def patch(self, request, *args, **kwargs):
        contract_id = request.query_params.get("id")
        tab = request.query_params.get("tab")
        updates = request.data
        if tab == "employee":
            try:
                employee_contract_instance = employee_contract.objects.get(id=contract_id)
                for key in updates:
                    if key == "contract_doc":
                        contract_doc = updates['contract_doc']
                        try:
                            pdf_ext_valid(contract_doc)
                            valid_pdffile_type(contract_doc)
                        except ValidationError as e:
                            return Response({"error":e}, status=status.HTTP_400_BAD_REQUEST)
                        
                        removed = remove_bucket_file(employee_contract_instance.contract_doc.name)
                        if removed:
                            return Response({"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST)
                    setattr(employee_contract_instance, key, updates[key])
                employee_contract_instance.save()
                return Response(
                    {"message": "Changes have been saved successfully"},
                    status=status.HTTP_200_OK,
                )
            except employee_contract.DoesNotExist:
                return Response(
                    {"error": "Employee contract not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except ValidationError as e:
                return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif tab == "client":
            try:
                client_contract_instance = client_contract.objects.get(id=contract_id)
                for key in updates:
                    if key == "contract_doc":
                        contract_doc = updates['contract_doc']
                        try:
                            pdf_ext_valid(contract_doc)
                            valid_pdffile_type(contract_doc)
                        except ValidationError as e:
                            return Response({"error":e}, status=status.HTTP_400_BAD_REQUEST)
                        
                        removed = remove_bucket_file(client_contract_instance.contract_doc.name)
                        if removed:
                            return Response({"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST)
                    setattr(client_contract_instance, key, updates[key])
                client_contract_instance.save()
                return Response(
                    {"message": "Changes have been saved successfully"},
                    status=status.HTTP_200_OK,
                )
            except client_contract.DoesNotExist:
                return Response(
                    {"error": "Client contract not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except ValidationError as e:
                return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Offshore_Contract(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Offshore Contract"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="client_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="employee_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="contract_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="contract_doc",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        operation_id="1",
    )
    def post(self, request, *args, **kwargs):
        posted_data = request.data
        try:
            emp = employee.objects.get(employee_id=posted_data["employee_id"])
            posted_data["employee_id"] = emp.email
            clnt = client.objects.get(client_id=posted_data["client_id"])
            posted_data["client_id"] = clnt.email
            outsrc = outsource_employees.objects.get(client_id=posted_data["client_id"],employee_id=posted_data["employee_id"])
            if outsrc.status=="active":
                serializer = OffshoreContractSerializers(data=posted_data)
                if serializer.is_valid():
                    off_cont = offshore_contracts.objects.create(
                        employee_id=serializer.validated_data["employee_id"],
                        client_id=serializer.validated_data["client_id"],
                        contract_name=serializer.validated_data["contract_name"],
                        date=serializer.validated_data["date"],
                        contract_doc=serializer.validated_data["contract_doc"],
                    )
                    notifications.objects.create(
                        email=off_cont.client_id,
                        ref_id=off_cont.id,
                        notification_type="offshore_contracts",
                        status="added",
                        description=f"{off_cont.contract_name} contract is added",
                    )
                    notifications.objects.create(
                        email=off_cont.employee_id,
                        ref_id=off_cont.id,
                        notification_type="offshore_contracts",
                        status="added",
                        description=f"{off_cont.contract_name} contract is added",
                    )
                    return Response(
                        {
                            "message": "One new contract has been added to offshore contracts",
                            "id": off_cont.id,
                            "client_email": off_cont.client_id,
                            "employee_email": off_cont.employee_id,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {"error": "Invalid status parameter"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response({"error":"Cannot create contract for terminated employee"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(
                {"errors": e},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ObjectDoesNotExist as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        tags=["Offshore Contract"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "contract_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "client_email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                            "client_id": openapi.Schema(type=openapi.TYPE_STRING),
                            "employee_email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                            "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                            "date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                        },
                    ),
                ),
            ),
            204: openapi.Response(description="No Content"),
            401: openapi.Response(description="Unauthorized"),
        },
        operation_id="2",
    )
    def get(self, request, *args, **kwargs):
        contracts = offshore_contracts.objects.all()
        offshore_cont = []
        for contract in contracts:
            emp = employee.objects.get(email=contract.employee_id)
            clnt = client.objects.get(email=contract.client_id)
            record = {
                "id": contract.id,
                "contract_name": contract.contract_name,
                "client_email": contract.client_id,
                "client_id": clnt.client_id,
                "employee_email": contract.employee_id,
                "employee_id": emp.employee_id,
                "date": contract.date,
            }
            offshore_cont.append(record)
        if not offshore_cont:
            return Response(
                {"message": "No offshore contracts available"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(offshore_cont, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Offshore Contract"],
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
        operation_summary="Endpoint to delete a offshore contract request.",
        operation_id="3",
    )
    def delete(self, request, *args, **kwargs):
        delete_id = request.query_params.get("id")
        try:
            off_cont = offshore_contracts.objects.get(id=delete_id)
            removed = remove_bucket_file(off_cont.contract_doc.name)
            if removed:
                return Response(
                    {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                )

            notifications.objects.get(
                email=off_cont.client_id,
                ref_id=off_cont.id,
                notification_type="offshore_contracts",
            ).delete()

            notifications.objects.get(
                email=off_cont.employee_id,
                ref_id=off_cont.id,
                notification_type="offshore_contracts",
            ).delete()
            off_cont.delete()
            return Response(
                {"message": "One contract has been removed from offshore contracts"},
                status=status.HTTP_200_OK,
            )

        except offshore_contracts.DoesNotExist:
            return Response(
                {"error": "offshore contract not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Offshore Contract"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Offshore Contract record id",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="client_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="employee_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="contract_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                name="contract_doc",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
            ),
        ],
        responses={
            200: "Request processed successfully",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Contract not found",
        },
        operation_summary="Endpoint to edit a offshore contract",
        operation_id="4",
    )
    def patch(self, request, *args, **kwargs):
        offshore_contract_id = request.query_params.get("id")
        updates = request.data
        try:
            offshore_contract_instance = offshore_contracts.objects.get(id=offshore_contract_id)
            for key in updates:
                if key == "contract_doc":
                    contract_doc = updates['contract_doc']
                    try:
                        pdf_ext_valid(contract_doc)
                        valid_pdffile_type(contract_doc)
                    except ValidationError as e:
                        return Response({"error":e}, status=status.HTTP_400_BAD_REQUEST)
                    
                    removed = remove_bucket_file(offshore_contract_instance.contract_doc.name)
                    if removed:
                        return Response({"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST)
                setattr(offshore_contract_instance, key, updates[key])
            offshore_contract_instance.save()
            return Response(
                {"message": "Changes have been saved successfully"},
                status=status.HTTP_200_OK,
            )
        except offshore_contracts.DoesNotExist:
            return Response(
                {"error": "Offshore contract not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Invoices(APIView):
    @swagger_auto_schema(
        tags=["Invoices"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "company_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "client_id": openapi.Schema(type=openapi.TYPE_STRING),
                            "email": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                            ),
                            "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
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
                required=True,
            ),
        ],
        operation_summary="Endpoint to retrieve invoices",
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        client_users = client.objects.all()
        client_data = []
        try:
            for data in client_users:
                user = end_user.objects.get(email=data.email)
                record = {
                    "id": data.id,
                    "company_name": data.company_name,
                    "client_id": data.client_id,
                    "email": data.email,
                    "is_active": user.is_active,
                }
                client_data.append(record)
            if not client_data:
                return Response(
                    {"message": "No invoices available"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(client_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ClientEmployees(APIView):
    @swagger_auto_schema(
        tags=["Clients: Employees"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "emp_pk": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_EMAIL,
                        ),
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "image": openapi.Schema(type=openapi.TYPE_STRING),
                        "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                        "status": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            204: openapi.Response("No Content"),
            400: openapi.Response("Bad Request"),
            401: openapi.Response("Unauthorized"),
        },
        manual_parameters=[
            openapi.Parameter(
                "c_email",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
            ),
            openapi.Parameter(
                "tab",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["all", "active", "terminated"],
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to retrieve outsourced employees under specified client",
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        c_email = request.query_params.get("c_email")
        tab = request.query_params.get("tab")
        if c_email and tab == "active" or tab == "terminated":
            c_emps = outsource_employees.objects.filter(client_id=c_email, status=tab)
            if c_emps:
                records = []
                for c_emp in c_emps:
                    try:
                        emp = employee.objects.get(email=c_emp.employee_id)
                        record = {
                            "id": c_emp.id,
                            "emp_pk": emp.id,
                            "email": emp.email,
                            "image": emp.image.url,
                            "name": emp.first_name + " " + emp.last_name,
                            "job_title": c_emp.job_title,
                            "status": c_emp.status,
                        }
                        records.append(record)
                    except:
                        continue
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        elif c_email and tab == "all":
            c_emps = outsource_employees.objects.filter(client_id=c_email)
            if c_emps:
                records = []
                for c_emp in c_emps:
                    try:
                        emp = employee.objects.get(email=c_emp.employee_id)
                        record = {
                            "id": c_emp.id,
                            "emp_pk": emp.id,
                            "email": emp.email,
                            "image": emp.image.url,
                            "name": emp.first_name + " " + emp.last_name,
                            "job_title": c_emp.job_title,
                            "status": c_emp.status,
                        }
                        records.append(record)
                    except:
                        continue
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Clients: Employees"],
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=["active", "terminated"]
                )
            },
            required=["status"],
        ),
        responses={
            200: "Successful Request",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
        },
        operation_summary="Endpoint to edit outsource employee status",
        operation_id="2",
    )
    def patch(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        new_status = request.data.get("status")
        if new_status and id:
            try:
                c_emp = outsource_employees.objects.get(id=id)
                c_emp.status = new_status
                emp = employee.objects.get(email=c_emp.employee_id)                
                notif = notifications.objects.get(
                    email=c_emp.client_id,
                    ref_id=c_emp.id,
                    notification_type="team_member",
                )
                if new_status == "terminated":
                    notif.status = "removed"
                    notif.description = (
                        f"{emp.first_name} {emp.last_name} is removed from your team"
                    )
                    notif.save()
                if new_status == "active":
                    notif.status = "added"
                    notif.description = (
                        f"{emp.first_name} {emp.last_name} is added to your team"
                    )
                    notif.save()
                c_emp.save()
                return Response(
                    {
                        "message": f"{emp.first_name} {emp.last_name} is set to {new_status}"
                    },
                    status=status.HTTP_200_OK,
                )
            except outsource_employees.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "Invalid query parameters"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ClientAddEmployee(APIView):
    @swagger_auto_schema(
        tags=["Clients: Employees: Add Employee"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "employee_id": openapi.Schema(type=openapi.TYPE_INTEGER, format=openapi.FORMAT_EMAIL),
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "image": openapi.Schema(type=openapi.TYPE_STRING),
                        "gender": openapi.Schema(type=openapi.TYPE_STRING),
                        "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            204: openapi.Response("No Content"),
            401: openapi.Response("Unauthorized"),
        },
        manual_parameters=[
            openapi.Parameter(
                "c_email",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to retrieve employees available to be outsourced",
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        c_email = request.query_params.get("c_email")
        outsourced_employees = outsource_employees.objects.filter(
            client_id=talent_email
        )
        c_outsourced_employees = outsource_employees.objects.filter(client_id=c_email)
        if outsourced_employees and c_outsourced_employees:
            records = []
            for outsrcd_emp in outsourced_employees:
                is_present = False
                for c_outsrcd_emp in c_outsourced_employees:
                    if c_outsrcd_emp.employee_id == outsrcd_emp.employee_id:
                        is_present = True
                if not is_present:
                    try:
                        emp = employee.objects.get(email=outsrcd_emp.employee_id)
                        record = {
                            "image": emp.image.url,
                            "name": emp.first_name + " " + emp.last_name,
                            "id": emp.id,
                            "employee_id": emp.employee_id,
                            "gender": emp.gender,
                            "job_title": outsrcd_emp.job_title,
                            "status": "active",
                        }
                        records.append(record)
                    except:
                        continue
            if records:
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        elif outsourced_employees:
            records = []
            for outsrcd_emp in outsourced_employees:
                try:
                    emp = employee.objects.get(email=outsrcd_emp.employee_id)
                    record = {
                        "image": emp.image.url,
                        "name": emp.first_name + " " + emp.last_name,
                        "id": emp.id,
                        "employee_id": emp.employee_id,
                        "gender": emp.gender,
                        "job_title": outsrcd_emp.job_title,
                        "status": "active",
                    }
                    records.append(record)
                except:
                    continue
            if records:
                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Clients: Employees: Add Employee"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                "role_type": openapi.Schema(type=openapi.TYPE_STRING),
                "employment_term": openapi.Schema(type=openapi.TYPE_STRING),
                "joining_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
                "salary": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=[
                "id",
                "country",
                "job_title",
                "role_type",
                "employment_term",
                "joining_date",
                "salary",
            ],
        ),
        responses={
            201: openapi.Response("Successful created"),
            400: openapi.Response("Bad request"),
            401: openapi.Response("UnAuthorize"),
        },
        manual_parameters=[
            openapi.Parameter(
                "c_email",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Endpoint to add outsource employee for specified client",
        operation_id="2",
    )
    def post(self, request, *args, **kwargs):
        c_email = request.query_params.get("c_email")
        id = request.data.get("id")
        job_title = request.data.get("job_title")
        country = request.data.get("country")
        role_type = request.data.get("role_type")
        employment_term = request.data.get("employment_term")
        joining_date = request.data.get("joining_date")
        salary = request.data.get("salary")
        if id and c_email:
            try:
                emp = employee.objects.get(id=id)
            except employee.DoesNotExist:
                return Response(
                    {"error": "Employee does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            try:
                out_emp = outsource_employees.objects.create(
                    client_id=c_email,
                    employee_id=emp.email,
                    job_title=job_title,
                    country=country,
                    role_type=role_type,
                    employment_term=employment_term,
                    joining_date=joining_date,
                    salary=salary,
                )
                notifications.objects.create(
                        email=out_emp.client_id,
                        ref_id=out_emp.id,
                        notification_type="team_member",
                        status="added",
                        description=f"{emp.first_name} {emp.last_name} have been added to your team",
                    )
                return Response(
                    {
                        "message": f"{emp.first_name} {emp.last_name} is added successfully",
                        "id": out_emp.id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except ValidationError as e:
                return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "Invalid query parmeters"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Attendance_Report(APIView):
    @swagger_auto_schema(
        tags=["Employee: Attendence reports"],
        manual_parameters=[
            openapi.Parameter(
                "e_email",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                "from",
                openapi.IN_QUERY,
                description="Date filter",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                example="December 21, 2023 or 12-21-2023",
            ),
            openapi.Parameter(
                "to",
                openapi.IN_QUERY,
                description="Date filter",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                example="December 21, 2023 or 12-21-2023",
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
                            "client_name": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "time_sheet": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER
                                            ),
                                            "month": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "record": openapi.Schema(
                                                type=openapi.TYPE_OBJECT,
                                                properties={
                                                    "13-02-2024": openapi.Schema(
                                                        type=openapi.TYPE_OBJECT,
                                                        properties={
                                                            "check_in": openapi.Schema(
                                                                type=openapi.TYPE_STRING,
                                                                example="10:00 AM",
                                                            ),
                                                            "check_out": openapi.Schema(
                                                                type=openapi.TYPE_STRING,
                                                                example="10:00 PM",
                                                            ),
                                                            "breaK": openapi.Schema(
                                                                type=openapi.TYPE_STRING,
                                                                example="1:00 PM",
                                                            ),
                                                            "resume": openapi.Schema(
                                                                type=openapi.TYPE_STRING,
                                                                example="2:00 PM",
                                                            ),
                                                            "hours_worked": openapi.Schema(
                                                                type=openapi.TYPE_STRING
                                                            ),
                                                            "overtime": openapi.Schema(
                                                                type=openapi.TYPE_STRING
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
                                                                    "Day Off": openapi.Schema(
                                                                        type=openapi.TYPE_BOOLEAN
                                                                    ),
                                                                    "Full Leave": openapi.Schema(
                                                                        type=openapi.TYPE_BOOLEAN
                                                                    ),
                                                                },
                                                            ),
                                                        },
                                                    ),
                                                    # Same structure for all dates
                                                },
                                            ),
                                            "year": openapi.Schema(
                                                type=openapi.TYPE_INTEGER
                                            ),
                                            "expect_check_in": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                example="10:00 AM",
                                            ),
                                            "expect_check_out": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                example="10:00 PM",
                                            ),
                                        },
                                    ),
                                    "employee_details": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "employee_id": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "employee_name": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "company": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "company_email": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                format=openapi.FORMAT_EMAIL,
                                            ),
                                            "location": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "role_type": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "job_title": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "joining_date": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                format=openapi.FORMAT_DATE,
                                            ),
                                        },
                                    ),
                                },
                            )
                        },
                    ),
                ),
            ),
            204: openapi.Response(description="No content"),
            401: openapi.Response(description="UnAuthorize"),
            400: openapi.Response(description="Bad Request"),
        },
        operation_summary="Endpoint to retrieve employee attendance report",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        e_email = request.query_params.get("e_email")
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")

        if e_email and from_date and to_date:
            from_date_object = parser.parse(from_date)
            to_date_object = parser.parse(to_date)
            from_month = from_date_object.strftime("%B")
            from_year = from_date_object.year
            to_month = to_date_object.strftime("%B")
            to_year = to_date_object.year
            month_mapping = {
                month_name: month_number
                for month_number, (month_name, _) in enumerate(
                    time_sheet.months, start=1
                )
            }

            annotated_time_sheets = time_sheet.objects.annotate(
                month_num=Case(
                    *(When(month=month_name[i], then=Value(i)) for i in range(1, 13)),
                    output_field=IntegerField(),
                )
            )
            time_sheet_records = annotated_time_sheets.filter(
                Q(employee_id=e_email),
                Q(
                    month_num__gte=month_mapping[from_month],
                    year__gte=from_year,
                )
                & Q(
                    month_num__lte=month_mapping[to_month],
                    year__lte=to_year,
                ),
            )

            filtered_records = {}
            for record in time_sheet_records:
                if record.client_id in filtered_records.keys():
                    for key, value in record.record.items():
                        date = datetime.strptime(key, "%d-%m-%Y")
                        if from_date_object <= date <= to_date_object:
                            filtered_records[record.client_id][key] = value
                else:
                    rec = {}
                    for key, value in record.record.items():
                        date = datetime.strptime(key, "%d-%m-%Y")
                        if from_date_object <= date <= to_date_object:
                            rec[key] = value
                    filtered_records[record.client_id] = rec

            if len(filtered_records) > 0:
                records = []
                for key, value in filtered_records.items():
                    if key == talent_email:
                        company_name = "eSpark Talent"
                        company_email = talent_email
                        location = "Karachi"
                    else:
                        try:
                            clnt = client.objects.get(email=key)
                            company_name = clnt.company_name
                            company_email = clnt.email
                            location = clnt.address
                        except client.DoesNotExist:
                            company_name = "-"
                            company_email = "-"
                            location = "-"

                    outsrc_emp = outsource_employees.objects.get(
                        employee_id=e_email, client_id=key
                    )
                    emp = employee.objects.get(email=e_email)

                    employee_details = {
                        "employee_id": emp.employee_id,
                        "employee_name": emp.first_name + " " + emp.last_name,
                        "company": company_name,
                        "company_email": company_email,
                        "location": location,
                        "role_type": outsrc_emp.role_type,
                        "job_title": outsrc_emp.job_title,
                        "joining_date": outsrc_emp.joining_date,
                    }
                    new_value = {"record": value}
                    new_value["expected_check_in"] = emp.punch_timings["check_in"]
                    new_value["expected_check_out"] = emp.punch_timings["check_out"]
                    record = {
                        "time_sheet": new_value,
                        "employee_details": employee_details,
                    }
                    records.append({company_name: record})

                # Sort records by company name or any other criteria
                records = sorted(records, key=lambda x: list(x.keys())[0])

                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        elif e_email:
            ts_records = time_sheet.objects.filter(
                employee_id=e_email,
                year=datetime.now().year,
                month=datetime.now().strftime("%B"),
            )
            if ts_records:
                records = []
                for ts_record in ts_records:
                    ts_rec = {
                        "id": ts_record.id,
                        "month": ts_record.month,
                        "record": ts_record.record,
                        "year": ts_record.year,
                        "expect_check_in": employee.objects.get(
                            email=e_email
                        ).punch_timings["check_in"],
                        "expect_check_out": employee.objects.get(
                            email=e_email
                        ).punch_timings["check_out"],
                    }

                    emp = employee.objects.get(email=e_email)
                    if ts_record.client_id == talent_email:
                        company_name = "eSpark Talent"
                        company_email = talent_email
                        location = "Karachi"
                    else:
                        try:
                            clnt = client.objects.get(email=ts_record.client_id)
                            company_name = clnt.company_name
                            company_email = clnt.email
                            location = clnt.address
                        except client.DoesNotExist:
                            company_name = "-"
                            company_email = "-"
                            location = "-"

                    outsrc_emp = outsource_employees.objects.get(
                        employee_id=e_email, client_id=ts_record.client_id
                    )

                    employee_details = {
                        "employee_id": emp.employee_id,
                        "employee_name": emp.first_name + " " + emp.last_name,
                        "company": company_name,
                        "company_email": company_email,
                        "location": location,
                        "role_type": outsrc_emp.role_type,
                        "job_title": outsrc_emp.job_title,
                        "joining_date": outsrc_emp.joining_date,
                    }

                    record = {
                        company_name: {
                            "time_sheet": ts_rec,
                            "employee_details": employee_details,
                        }
                    }
                    records.append(record)

                # Sort records by company name or any other criteria
                records = sorted(records, key=lambda x: list(x.keys())[0])

                return Response(records, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Employee_WFH_Request(APIView):

    @swagger_auto_schema(
        tags=["Request : WFH requests"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "e_email",
                openapi.IN_QUERY,
                description="Employee email",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
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
                            "department": openapi.Schema(type=openapi.TYPE_STRING),
                            "start_date": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format=openapi.FORMAT_DATE,
                                example="2024-02-29(Y:M:D)",
                            ),
                            "end_date": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format=openapi.FORMAT_DATE,
                                example="2024-02-29(Y:M:D)",
                            ),
                            "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "reason": openapi.Schema(type=openapi.TYPE_STRING),
                            "status": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            204: openapi.Response(description="No content"),
            206: openapi.Response(description="Partial content"),
            401: openapi.Response(description="UnAuthorize"),
            400: openapi.Response(description="Bad Request"),
        },
        operation_summary="Endpoint to retrieve punch request data.",
        operation_id="0",
    )
    def get(self, request, *args, **kwargs):
        e_email=request.query_params.get("e_email")
        from_date_object = datetime.today().replace(day=1).date()
        last_day = calendar.monthrange(from_date_object.year, from_date_object.month)[1]
        to_date_object = datetime.today().replace(day=last_day).date()
        requests = wfh_request.objects.filter(
                Q(employee_id=e_email),
                start_date__gte=from_date_object,
                start_date__lte=to_date_object,
            )
        serializer = WFHRequestSerializerHR(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Request : WFH requests"],
        operation_summary="Update WFH request status",
        operation_id="1",
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
            200: "WFH request status updated successfully.",
            204: "WFH request not found or no content.",
            400: "Bad request.",
        },
    )
    def patch(self, request,*args, **kwargs):
        record_id = request.query_params.get("id")
        to_update_status = request.data.get("status")
        try:
            wfh_req= wfh_request.objects.get(id=record_id)
            wfh_req.status=to_update_status
            wfh_req.save()
            notifi = notifications.objects.get(
                ref_id=record_id,
                notification_type="wfh_request",
            )
            notifi.email = wfh_req.employee_id
            notifi.status = to_update_status
            notifi.description = f"WFH request has been {to_update_status}"
            notifi.save()
            return Response(
                {"message":f"WFH request is {to_update_status}"}, status=status.HTTP_200_OK
            )
        except wfh_request.DoesNotExist():
            return Response(
                {
                    "error": "WFH request does not exists"
                },
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error":e}, status=status.HTTP_400_BAD_REQUEST
            )

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Leave_Request(APIView):
    @swagger_auto_schema(
        tags=["Request : Leave requests"],
        manual_parameters=[
            openapi.Parameter(
                "emp_email",
                openapi.IN_QUERY,
                description="email of the employee",
                type=openapi.TYPE_STRING,
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
                            "department": openapi.Schema(type=openapi.TYPE_STRING),
                            "leave_type": openapi.Schema(type=openapi.TYPE_STRING),
                            "start_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "end_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
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
            404: openapi.Response("Not Found"),
        },
        operation_summary="Endpoint to retrieve current month Leave request data.",
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        emp_email = request.query_params.get("emp_email")
        
        today = datetime.today()
        current_month_start = today.replace(day=1)
        if today.month == 12:
            next_month_start = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month_start = today.replace(month=today.month + 1, day=1)


        leave_requests = leave_request.objects.filter(
            employee_id=emp_email,
            created_at__gte=current_month_start,
            created_at__lt=next_month_start,
        )

        records = []
        try:
            employee_data = employee.objects.get(email=emp_email)
            employee_name = f"{employee_data.first_name} {employee_data.last_name}"
        except employee.DoesNotExist:
            return Response(
                {"error": "Employee does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        if leave_requests:
            for data in leave_requests:
                record = {
                    "id": data.id,
                    "employee_id": employee_data.employee_id,
                    "employee_name": employee_name,
                    "department": employee_data.job_title,
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


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ClockInOut_Request(APIView):
    @swagger_auto_schema(
       tags=["Request : Punch requests"],
        manual_parameters=[
            openapi.Parameter(
                "emp_email",
                openapi.IN_QUERY,
                description="email of the employee",
                type=openapi.TYPE_STRING,
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
            404: openapi.Response("Not Found"),
        },
        operation_summary="Endpoint to retrieve Punch request data.",
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        emp_email = request.query_params.get("emp_email")
        
        today = datetime.today()
        current_month_start = today.replace(day=1)
        if today.month == 12:
            next_month_start = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month_start = today.replace(month=today.month + 1, day=1)


        clockinout_requests = punch_request.objects.filter(
            employee_id=emp_email,
            created_at__gte=current_month_start,
            created_at__lt=next_month_start,
        )
        
        try:
            employee_data = employee.objects.get(email=emp_email)
            employee_name = f"{employee_data.first_name} {employee_data.last_name}"
        except employee.DoesNotExist:
            return Response(
                {"error": "Employee does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        records = []

        if clockinout_requests:
            for data in clockinout_requests:
                record = {
                    "id": data.id,
                    "employee_id": employee_data.employee_id,
                    "employee_name": employee_name,
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


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Emp_Benefits(APIView):
    @swagger_auto_schema(
       tags=["Employee : Benefits"],
        manual_parameters=[
            openapi.Parameter(
                "emp_email",
                openapi.IN_QUERY,
                description="email of the employee",
                type=openapi.TYPE_STRING,
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
                            "card_id": openapi.Schema(type=openapi.TYPE_STRING),
                            "employee_id": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                            "benefit": openapi.Schema(type=openapi.TYPE_STRING),
                            "issue_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
            404: openapi.Response("Not Found"),
        },
        operation_summary="Endpoint to retrieve employee benefits.",
        operation_id="2",
    )
    def get(self, request, *args, **kwargs):
        emp_email = request.query_params.get("emp_email")
        benefits_data = benefits.objects.filter(
            employee_id=emp_email,
        )
        
        records = []

        if benefits_data:
            for data in benefits_data:
                record = {
                    "id": data.id,
                    "card_id": data.card_id,
                    "benefit": data.benefit,
                    "issue_date": data.issue_date,
                    "description": data.description,
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    @swagger_auto_schema(
        tags=["Employee : Benefits"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "card_id": openapi.Schema(type=openapi.TYPE_STRING),
                "employee_id": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                "benefit": openapi.Schema(type=openapi.TYPE_STRING),
                "issue_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
                "description": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=[
                "card_id",
                "employee_id",
                "benefit",
                "issue_date",
            ],
        ),
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Add new benefit",
        operation_id=".",
    )
    def post(self, request, *args, **kwargs):
        serializer = BenefitsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                employee_data = employee.objects.get(email=serializer.validated_data["employee_id"])
            except employee.DoesNotExist:
                return Response(
                    {"error": "Employee does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            record = benefits.objects.create(
                card_id=serializer.validated_data["card_id"],
                employee_id=serializer.validated_data["employee_id"],
                benefit=serializer.validated_data["benefit"],
                issue_date=serializer.validated_data["issue_date"],
                description=serializer.validated_data.get("description", None),
            )
            benefit = serializer.validated_data["benefit"]
            notifications.objects.create(
                        email=employee_data.email,
                        ref_id=record.id,
                        notification_type="benefit",
                        status="added",
                        description=f"{benefit} benefit is added in Benefits tab",
                    )
            return Response(
                {"message": "One new benefit has been added", "id": record.id},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Employee : Benefits"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "card_id": openapi.Schema(type=openapi.TYPE_STRING),
                "description": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to update",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful update"),
            400: openapi.Response(description="Bad Request"),
            401: openapi.Response(description="Unauthorize"),
            404: openapi.Response(description="Not Found"),
        },
        operation_summary="Endpoint to update a benefit.",
        operation_id="3",
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            card_id = request.data.get("card_id")
            description = request.data.get("description")
            benefits_data = benefits.objects.get(id=record_id)
            benefits_data.card_id = card_id
            benefits_data.description = description
            benefits_data.save()
            return Response(
                {"message": "Benefit updated successfully"},
                status=status.HTTP_200_OK,
            )
        except benefits.DoesNotExist:
            return Response(
                {"error": "Benefit record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Employee : Benefits"],
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
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful deletion"),
            400: openapi.Response(description="Bad Request"),
            401: openapi.Response(description="Unauthorize"),
            404: openapi.Response(description="Not Found"),
        },
        operation_summary="Endpoint to delete a benefit.",
        operation_id="1",
    )
    def delete(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        if id:
            try:
                notifications.objects.get(ref_id=id, notification_type="benefit").delete()
                benefits.objects.get(id=id).delete()
                return Response(
                    {"message": "Benefit has been deleted"}, status=status.HTTP_200_OK
                )
            except benefits.DoesNotExist:
                return Response(
                    {"error": "Benefit not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except notifications.DoesNotExist:
                return Response(
                    {"error": "Notifications record not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "Id parameter required"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Letters(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
       tags=["Employees : Letters"],
        manual_parameters=[
            openapi.Parameter(
                "email",
                openapi.IN_QUERY,
                description="email of the employee",
                type=openapi.TYPE_STRING,
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
                            "objective": openapi.Schema(type=openapi.TYPE_STRING),
                            "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                            "issue_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "reason": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
            404: openapi.Response("Not Found"),
        },
        operation_summary="Endpoint to retrieve employee letters.",
        operation_id="0",
    )
    def get(self, request, *args, **kwargs):
        email = request.query_params.get("email")
        letters = letter.objects.filter(
            email=email,
        )

        records = []

        if letters:
            for data in letters:
                record = {
                    "id": data.id,
                    "objective": data.objective,
                    "email": data.email,
                    "issue_date": data.issue_date,
                    "reason": data.reason,
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Employees : Letters"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="objective",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="email",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                name="letter",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                name="issue_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="reason",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Add a new letter",
        operation_id="1",
    )
    def post(self, request, *args, **kwargs):
        serializer = LetterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                employee_data = employee.objects.get(email=serializer.validated_data["email"])
            except employee.DoesNotExist:
                return Response(
                    {"error": "Employee does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            record = letter.objects.create(
                objective=serializer.validated_data["objective"],
                email=serializer.validated_data["email"],
                letter=serializer.validated_data["letter"],
                issue_date=serializer.validated_data["issue_date"],
                reason=serializer.validated_data.get("reason", None),
            )
            objective = serializer.validated_data["objective"]
            notifications.objects.create(
                        email=employee_data.email,
                        ref_id=record.id,
                        notification_type="letter",
                        status="added",
                        description=f"New {objective} is uploaded for you",
                    )
            return Response(
                {"message": "One new letter has been added", "id": record.id},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Employees : Letters"],
        responses={
            200: openapi.Response("Successfull"),
            400: openapi.Response("Bad request"),
            401: openapi.Response("UnAuthorize"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required= True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required= True,
            ),
            openapi.Parameter(
                "reason",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "letter",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
            ),
        ],
        operation_summary="Endpoint to update letter record.",
        operation_id="2",
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates = request.data
        try:
            record = letter.objects.get(id=record_id)
            keys = updates.keys()   
            if "letter" in keys:
                removed = remove_bucket_file(record.letter.name)
                if removed:
                    return Response(
                        {"error": str(removed)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                setattr(record, "letter", updates["letter"])
            if "reason" in keys: 
                setattr(record, "reason", updates["reason"])
            try:
                record.save()
            except ValidationError as e:
                return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"message": "Letter record has been updated successfully"},
                status=status.HTTP_200_OK,
            )
        except letter.DoesNotExist:
            return Response(
                    {"error": "Letter record not found"}, status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Employees : Letters"],
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
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful deletion"),
            400: openapi.Response(description="Bad Request"),
            401: openapi.Response(description="Unauthorize"),
            404: openapi.Response(description="Not Found"),
        },
        operation_summary="Endpoint to delete a letter.",
        operation_id="3",
    )
    def delete(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        if id:
            try:
                letter_record = letter.objects.get(id=id)
                notifi = notifications.objects.get(ref_id=id, notification_type="letter")
                removed = remove_bucket_file(letter_record.letter.name)
                if removed:
                    return Response(
                        {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                    )
                letter_record.delete()
                notifi.delete()
                return Response(
                    {"message": "Letter record has been deleted"}, status=status.HTTP_200_OK
                )
            except notifications.DoesNotExist:
                return Response(
                    {"error": "Notification record not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except letter.DoesNotExist:
                return Response(
                    {"error": "Letter record not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                 {"error": "Id parameter required"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Salary(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Employees : Salary"],
        manual_parameters=[
            openapi.Parameter(
                "month",
                openapi.IN_QUERY,
                description="month for filtering records (e.g. January)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "year",
                openapi.IN_QUERY,
                description="year for filtering records",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "employee_id",
                openapi.IN_QUERY,
                description="email of the employee",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
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
                            "job_status": openapi.Schema(type=openapi.TYPE_STRING),
                            "gross_salary": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "tax_deduction": openapi.Schema(type=openapi.TYPE_NUMBER),
                            "net_salary": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                        },
                    ),
                ),
            ),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
            404: openapi.Response("Not Found"),
        },
        operation_summary="Endpoint to retrieve employee salary.",
        operation_id="0",
    )
    def get(self, request, *args, **kwargs):
        employee_id = request.query_params.get("employee_id")
        month = request.query_params.get("month")
        year = request.query_params.get("year")
        if month and year:
            year = int(year)
            try:
                month_number = datetime.strptime(month, '%B').month
            except Exception as e:
                return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            first_date = datetime(year, month_number, 1)
            days_in_month = calendar.monthrange(year, month_number)[1]
            last_date = datetime(year, month_number, days_in_month)
            try:
                from_date = datetime.today().replace(month=1, day=1).date()
                today = datetime.today().date()
                salary_records = salary.objects.filter(
                    Q(employee_id=employee_id),
                    date__gte=first_date,
                    date__lte=last_date,
                )
                if salary_records:
                    records=[]
                    for rec in salary_records:
                        records.append({
                            "id":rec.id,
                            "job_status":rec.job_status,
                            "gross_salary":rec.gross_salary,
                            "tax_deduction":rec.tax_deduction,
                            "net_salary":rec.net_salary,
                            "date":rec.date
                        })
                    return Response(records, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_204_NO_CONTENT)

            except salary.DoesNotExist:
                return Response({"error":"Salary record does not exist"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            try:
                from_date = datetime.today().replace(month=1, day=1).date()
                today = datetime.today().date()
                salary_records = salary.objects.filter(
                    Q(employee_id=employee_id),
                    date__gte=from_date,
                    date__lte=today,
                )
                if salary_records:
                    records=[]
                    for rec in salary_records:
                        records.append({
                            "id":rec.id,
                            "job_status":rec.job_status,
                            "gross_salary":rec.gross_salary,
                            "tax_deduction":rec.tax_deduction,
                            "net_salary":rec.net_salary,
                            "date":rec.date
                        })
                    return Response(records, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_204_NO_CONTENT)

            except salary.DoesNotExist:
                return Response({"error":"Salary record does not exist"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Employees : Salary"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="employee_id",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                name="job_status",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="gross_salary",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="tax_deduction",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
            openapi.Parameter(
                name="net_salary",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="pay_slip",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                name="date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
        ],
        operation_summary="Add a new salary record",
        operation_id="1",
    )
    def post(self, request, *args, **kwargs):
        employee_id = request.query_params.get("employee_id")
        serializer = SalarySerializer(data=request.data)
        if serializer.is_valid():
            try:
                record = salary.objects.create(
                    employee_id=employee_id,
                    job_status= serializer.validated_data["job_status"],
                    gross_salary= serializer.validated_data["gross_salary"],
                    tax_deduction= serializer.validated_data["tax_deduction"],
                    net_salary= serializer.validated_data["net_salary"],
                    pay_slip= serializer.validated_data["pay_slip"],
                    date= serializer.validated_data["date"],
                )
                return Response({"message":"Salary record added successfully", "id": record.id}, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Employees : Salary"],
        responses={
            200: openapi.Response("Successfull"),
            400: openapi.Response("Bad request"),
            401: openapi.Response("UnAuthorize"),
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required= True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required= True,
            ),
            openapi.Parameter(
                "job_status",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "gross_salary",
                openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "tax_deduction",
                openapi.IN_FORM,
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "net_salary",
                openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
            ), 
            openapi.Parameter(
                "date",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "pay_slip",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
            ),
        ],
        operation_summary="Endpoint to update salary record.",
        operation_id="2",
    )
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates = request.data
        try:
            record = salary.objects.get(id=record_id)
            for key in updates:
                if key == "pay_slip":
                    removed = remove_bucket_file(record.pay_slip.name)
                    if removed:
                        return Response(
                            {"error": str(removed)},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                setattr(record, key, updates[key])

            try:
                record.save()
            except ValidationError as e:
                return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"message": "Salary record has been updated successfully"},
                status=status.HTTP_200_OK,
            )
        except salary.DoesNotExist:
            return Response(
                    {"error": "Salary record not found"}, status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Employees : Salary"],
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
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="Successful deletion"),
            400: openapi.Response(description="Bad Request"),
            401: openapi.Response(description="Unauthorize"),
            404: openapi.Response(description="Not Found"),
        },
        operation_summary="Endpoint to delete a salary record.",
        operation_id="3",
    )
    def delete(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        if id:
            try:
                salary_record = salary.objects.get(id=id)
                removed = remove_bucket_file(salary_record.pay_slip.name)
                if removed:
                    return Response(
                        {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                    )
                salary_record.delete()
                return Response(
                    {"message": "Salary record has been deleted"}, status=status.HTTP_200_OK
                )
            except salary.DoesNotExist:
                return Response(
                    {"error": "Salary record not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                 {"error": "Id parameter required"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Guide(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Guide"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="guide_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="description",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="language",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="guide_doc",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ],
        operation_summary="Add a new Guide",
        operation_id="1",
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = GuideSerializer(data=request.data)
            if serializer.is_valid():
                guide_record=guide.objects.create(
                    guide_name=serializer.validated_data["guide_name"],
                    language=serializer.validated_data["language"],
                    guide_doc=serializer.validated_data["guide_doc"],
                    description=request.data.get("description"),
                    employee=False,
                    client=False,
                )
                return Response(
                    {
                        "message": "New guide has been added successfully",
                        "id": guide_record.id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        tags=["Guide"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "guide_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                            "language": openapi.Schema(type=openapi.TYPE_STRING),
                            "employee": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "client": openapi.Schema(type=openapi.TYPE_BOOLEAN),
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
                required=True,
            ),
        ],
        operation_summary="Endpoint to retrieve guides",
        operation_id="2",
    )
    def get(self, request, *args, **kwargs):
        hr_guides = guide.objects.all()
        guides = []
        for hr_pol in hr_guides:
            record = {
                "id": hr_pol.id,
                "guide_name": hr_pol.guide_name,
                "description": hr_pol.description,
                "language": hr_pol.language,
                "employee": hr_pol.employee,
                "client": hr_pol.client,
            }
            guides.append(record)
        if len(guides) > 0:
            return Response(guides, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Guide"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Record id",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "guide_name",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "description",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "language",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "guide_doc",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
            ),
        ],
        responses={
            200: "Request processed successfully",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Record not found",
        },
        operation_summary="Endpoint to edit a guide",
        operation_id="3",
    )
    def patch(self, request, *args, **kwargs):
        guide_id = request.query_params.get("id")
        updates = request.data
        try:
            guide_instance = guide.objects.get(id=guide_id)
            for key in updates:
                if key == "guide_doc":
                    guide_doc = updates['guide_doc']
                    try:
                        pdf_ext_valid(guide_doc)
                        valid_pdffile_type(guide_doc)
                    except ValidationError as e:
                        return Response({"error":e}, status=status.HTTP_400_BAD_REQUEST)
                    
                    removed = remove_bucket_file(guide_instance.guide_doc.name)
                    if removed:
                        return Response({"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST)
                setattr(guide_instance, key, updates[key])
            guide_instance.save()
            return Response(
                {"message": "Changes have been saved successfully"},
                status=status.HTTP_200_OK,
            )
        except guide.DoesNotExist:
            return Response(
                {"error": "Guide not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Guide"],
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
        operation_summary="Endpoint to delete a guide request.",
        operation_id="4",
    )
    def delete(self, request, *args, **kwargs):
        delete_id = request.query_params.get("id")
        try:
            pol = guide.objects.get(id=delete_id)
            removed = remove_bucket_file(pol.guide_doc.name)
            if removed:
                return Response(
                    {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                )
            pol.delete()
            return Response(
                {"message": "Guide has been removed successfully"},
                status=status.HTTP_200_OK,
            )
        except guide.DoesNotExist:
            return Response({"error": "Guide record not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Guides_Edit(APIView):
    @swagger_auto_schema(
        tags=["Edit Guides"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "data": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "employee": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "client": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        },
                    ),
                ),
            },
            required=["data"],
        ),
        responses={
            200: "Request processed successfully",
            400: "Bad Request",
            401: "Unauthorized",
        },
        operation_summary="Endpoint to edit a guide",
        operation_id="3",
    )
    def patch(self, request, *args, **kwargs):
        guide_ids_array = json.loads(request.body)
        try:
            for guide_id_json in guide_ids_array["data"]:
                try:
                    guide_instance = guide.objects.get(id=guide_id_json["id"])
                except guide.DoesNotExist:
                    return Response(
                        {"error": "Guide not found"}, status=status.HTTP_404_NOT_FOUND
                    )
                del guide_id_json["id"]
                for key in guide_id_json:
                    setattr(guide_instance, key, guide_id_json[key])
                guide_instance.save()
            return Response(
                {"message": "Changes have been saved successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



