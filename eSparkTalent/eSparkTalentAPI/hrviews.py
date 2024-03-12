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
import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from django.core.exceptions import ObjectDoesNotExist
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.db import transaction
import json

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
                type=openapi.TYPE_INTEGER,
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
                name="emergency_no",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
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
                    employee.objects.create(
                        employee_id=serializer.validated_data["employee_id"],
                        first_name=serializer.validated_data["first_name"],
                        last_name=serializer.validated_data["last_name"],
                        gender=serializer.validated_data["gender"],
                        dob=serializer.validated_data["dob"],
                        phone_number=serializer.validated_data["phone_number"],
                        email=serializer.validated_data["email"],
                        marital_status=serializer.validated_data["marital_status"],
                        image=serializer.validated_data["image"],
                        emergency_no=serializer.validated_data["emergency_no"],
                        resume=serializer.validated_data["resume"],
                        emergency_contact=serializer.validated_data["emergency_contact"],
                        joining_date=serializer.validated_data["joining_date"],
                        job_title=serializer.validated_data["job_title"],
                        role=serializer.validated_data["role"],
                        company=serializer.validated_data["company"],
                        punch_timings=serializer.validated_data["punch_timings"],
                    )

                    end_user.objects.create_user(
                        username=serializer.validated_data["first_name"]
                        + " "
                        + serializer.validated_data["last_name"],
                        role="employee",
                        email=serializer.validated_data["email"],
                        password=password,
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
                        client_id="talent@esparkconsultants.com",
                        employee_id=serializer.validated_data["email"],
                        job_title=serializer.validated_data["job_title"],
                        country="Pakistan",
                        role_type=serializer.validated_data["role"],
                        employment_term="",
                        joining_date=serializer.validated_data["joining_date"],
                        salary=0,
                        benefits={},
                    )
                    return Response(
                        {"message": "Resquest created"}, status=status.HTTP_201_CREATED
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
                type=openapi.TYPE_INTEGER,
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
                    client.objects.create(
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
                    end_user.objects.create_user(
                        username=serializer.validated_data["company_name"],
                        role="client",
                        email=serializer.validated_data["email"],
                        password=password,
                    )
                    return Response(
                        {"message": "Resquest created"}, status=status.HTTP_201_CREATED
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
        else:
            return Response(
                {"error": "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Add_Asset(APIView):
    @swagger_auto_schema(
        tags=["Employees : Add Asset"],
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
            asset.objects.create(
                asset_id=serializer.validated_data["asset_id"],
                employee_id=serializer.validated_data["employee_id"],
                gadget=serializer.validated_data["gadget"],
                assigned_date=serializer.validated_data["assigned_date"],
                assignee_name=serializer.validated_data["assignee_name"],
                assignee_email=serializer.validated_data["assignee_email"],
            )
            return Response(
                {"message": "Resquest created"}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
                format=openapi.FORMAT_DATE,
                required=True,
            ),
        ],
        operation_summary="Employee Invoice",
        operation_id="0",
    )
    def post(self, request, *args, **kwargs):
        posted_data = request.data
        id = posted_data.get("employee_id", None)
        employee_data = employee.objects.get(employee_id=id)
        posted_data["employee_id"] = employee_data.email
        try:
            serializer = EmployeeInvoiceSerializer(data=posted_data)

            if serializer.is_valid():
                try:
                    employee_invoice.objects.create(
                        client_id=serializer.validated_data["client_id"],
                        employee_id=serializer.validated_data["employee_id"],
                        invoice_date=serializer.validated_data["invoice_date"],
                        due_date=serializer.validated_data["due_date"],
                        invoice_amount=serializer.validated_data["invoice_amount"],
                        payment_status=serializer.validated_data["payment_status"],
                        invoice=serializer.validated_data["invoice"],
                    )
                    return Response(
                        {"message": "Request created"}, status=status.HTTP_201_CREATED
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
        except ObjectDoesNotExist:
            return Response(
                {"message": "Onboarding not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Client : Employee Invoice"],
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record",
                type=openapi.TYPE_INTEGER,
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
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        operation_summary="Employee Invoice",
        operation_id="1",
    )
    def patch(self, request, *args, **kwargs):
        request_id = request.query_params.get("id")
        to_update_status = request.data["payment_status"]
        try:
            to_update_emp_inv = employee_invoice.objects.get(id=request_id)
            if to_update_emp_inv:
                to_update_emp_inv.payment_status = to_update_status
                to_update_emp_inv.save()

                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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
                format=openapi.FORMAT_DATE,
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
                other_payment.objects.create(
                    client_id=serializer.validated_data["client_id"],
                    invoice_reference=serializer.validated_data["invoice_reference"],
                    invoice_date=serializer.validated_data["invoice_date"],
                    due_date=serializer.validated_data["due_date"],
                    invoice_amount=serializer.validated_data["invoice_amount"],
                    payment_status=serializer.validated_data["payment_status"],
                    invoice=serializer.validated_data["invoice"],
                )
                return Response(
                    {"message": "Resquest created"}, status=status.HTTP_201_CREATED
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
                "payment_status",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                enum=["pending", "paid", "processing"],
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
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        operation_summary="Other Invoice/payment",
        operation_id=".",
    )
    def patch(self, request, *args, **kwargs):
        request_id = request.query_params.get("id")
        to_update_status = request.data["payment_status"]
        try:
            to_update_otherpay = other_payment.objects.get(id=request_id)
            if to_update_otherpay:
                to_update_otherpay.payment_status = to_update_status
                to_update_otherpay.save()

                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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
                        "employee_perms":openapi.Schema(type=openapi.TYPE_OBJECT,properties={
                            "read":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "write":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "delete":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "download":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        }),
                        "client_perms":openapi.Schema(type=openapi.TYPE_OBJECT,properties={
                            "read":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "write":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "delete":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "download":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        }),
                        "leaves_perms":openapi.Schema(type=openapi.TYPE_OBJECT,properties={
                            "read":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "write":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "delete":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "download":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        }),
                        "invoices_perms":openapi.Schema(type=openapi.TYPE_OBJECT,properties={
                            "read":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "write":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "delete":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "download":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        }),
                        "policies_perms":openapi.Schema(type=openapi.TYPE_OBJECT,properties={
                            "read":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "write":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "delete":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "download":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        }),
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
        role=request.user.role
        if role=="super_admin":
            company=company_data.objects.all()
            if company:
                comp_image=company[0].image.path
            else:
                comp_image=''
            record = {
                "user": user,
                "company_image":comp_image,
                "employees": employee.objects.all().count(),
                "clients": client.objects.all().count(),
                "hiring_requests": hiring_request.objects.all().count(),
                "interview_schedules": interview_schedule.objects.all().count(),
            }
            return Response(record, status=status.HTTP_200_OK)
        else:
            company=company_data.objects.all()
            try:
                user_account=account_n_persmission.objects.get(email=request.user)
                user_image=user_account.image.path,
                employee_perms=user_account.employee_perms,
                client_perms=user_account.client_perms,
                leaves_perms=user_account.leaves_perms,
                invoices_perms=user_account.invoices_perms,
                policies_perms=user_account.policies_perms,
            except:
                user_image=''
                employee_perms={}
                client_perms={}
                leaves_perms={}
                invoices_perms={}
                policies_perms={}
            if company:
                comp_image=company[0].image.path
            else:
                comp_image=''
            record = {
                "user": user,
                "company_image":comp_image,
                "user_image":user_image,
                "employee_perms":employee_perms,
                "client_perms":client_perms,
                "leaves_perms":leaves_perms,
                "invoices_perms":invoices_perms,
                "policies_perms":policies_perms,
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
                        if e_user:
                            record = {
                                "id": e_user.id,
                                "employee_id": e_user.employee_id,
                                "name": e_user.first_name + " " + e_user.last_name,
                                "image_path": e_user.image.path,
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
                        e_user = outsource_employees.objects.get(employee_id=emp.email)
                        if not e_user:
                            record = {
                                "id": emp.id,
                                "employee_id": emp.employee_id,
                                "name": emp.first_name + " " + emp.last_name,
                                "image_path": emp.image.path,
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
                        e_user = outsource_employees.objects.get(client_id=emp.email)
                        c_user = client.objects.get(email=e_user.client_id)
                        company = c_user.company_name
                        active = True
                    except outsource_employees.DoesNotExist:
                        company = emp.company
                        active = False

                    record = {
                        "id": emp.id,
                        "employee_id": emp.employee_id,
                        "name": emp.first_name + " " + emp.last_name,
                        "image_path": emp.image.path,
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
            related_models = [outsource_employees, asset, employee_contract,time_sheet,employee_invoice, leave_balance, leave_request,punch_request,offshore_contracts,end_user ]
            with transaction.atomic(using='default'):  
                for model_class in related_models:
                    model_data = model_class.objects.filter(employee_id=emp.email)
                    if not model_data.exists():
                        model_data = model_class.objects.filter(email=emp.email)
                        model_data.delete()
                    else:
                        model_data.delete()
                emp.delete()

            return Response({"message": "Employee and associated data removed successfully"}, status=status.HTTP_200_OK)
        except employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

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
                                    "gadget": openapi.Schema(type=openapi.TYPE_STRING),
                                    "asset_id": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "assigned_date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATETIME,
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
                                "employee_name": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "gender": openapi.Schema(type=openapi.TYPE_STRING),
                                "dob": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATETIME,
                                ),
                                "email": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_EMAIL,
                                ),
                                "marital_status": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "image_path": openapi.Schema(type=openapi.TYPE_STRING),
                                "resume_path": openapi.Schema(type=openapi.TYPE_STRING),
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
                                    format=openapi.FORMAT_DATETIME,
                                ),
                                "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                                "role": openapi.Schema(type=openapi.TYPE_STRING),
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
    # error
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        tab = request.query_params.get("tab")
        employee_data = employee.objects.get(id=record_id)
        if tab == "client":
            active_clients = []
            terminated_clients = []

            active = outsource_employees.objects.filter(
                employee_id=employee_data.email, status="active"
            )
            terminated = outsource_employees.objects.filter(
                employee_id=employee_data.email, status="terminated"
            )

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
            emp_record = employee.objects.get(id=record_id)
            assets = asset.objects.filter(employee_id=emp_record.email)
            if assets:
                records = []
                for rec in assets:
                    record = {
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
                    "employee_name": emp_record.first_name + " " + emp_record.last_name,
                    "gender": emp_record.gender,
                    "dob": emp_record.dob,
                    "email": emp_record.email,
                    "marital_status": emp_record.marital_status,
                    "image_path": emp_record.image.path,
                    "resume_path": emp_record.resume.path,
                    "emergency_contact": emp_record.emergency_contact,
                    "joining_date": emp_record.joining_date,
                    "job_title": emp_record.job_title,
                    "role": emp_record.role,
                }
                return Response(record, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Update_Emp_Person_Info(APIView):
    @swagger_auto_schema(
        tags=["Employees"],
        operation_id="5",
        operation_summary="Update Employee Personal Information",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                "dob": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
                "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                "marital_status": openapi.Schema(type=openapi.TYPE_STRING),
                "gender": openapi.Schema(type=openapi.TYPE_STRING),
                "role": openapi.Schema(type=openapi.TYPE_STRING),
                "joining_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
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
        try:
            emp_record = employee.objects.get(id=record_id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        for key in updates:
            setattr(emp_record, key, updates[key])
        emp_record.save()
        return Response(status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Update_Emp_Emerg_Info(APIView):
    @swagger_auto_schema(
        tags=["Employees"],
        operation_id="3",
        operation_summary="Update Employee Emergency Information",
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
        try:
            emp_record = employee.objects.get(id=record_id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        for key in updates:
            setattr(emp_record, key, updates[key])
        emp_record.save()
        return Response(status=status.HTTP_200_OK)


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
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        for key in updates:
            setattr(emp_record, key, updates[key])
        try:
            emp_record.save()
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Edit_Cridentials(APIView):
    @swagger_auto_schema(
        tags=["Employees"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "employees_id": openapi.Schema(type=openapi.TYPE_STRING),
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
        except employees.DoesNotExist:
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
            {"message": "Password updated successfully"}, status=status.HTTP_200_OK
        )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Start_Hiring(APIView):
    @swagger_auto_schema(
        tags=["Clients : Hire & onBoard"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "client_id": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
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
                "client_id",
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
        operation_summary="Endpoint to create Start_Hiring.",
        operation_id="5",
    )
    def post(self, request, *args, **kwargs):
        serializer = start_requestSerializer(data=request.data)
        if serializer.is_valid():
            hiring_request.objects.create(
                client_id=serializer.validated_data["client_id"],
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
                            "salary_range": openapi.Schema(type=openapi.TYPE_STRING),
                            "hiring_start_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                            ),
                            "hiring_end_date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                            ),
                        },
                    ),
                ),
            ),
            204: openapi.Response(description="No Content"),
        },
        operation_id="4",
        operation_summary="Get Start_Hiring ",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        client_data = client.objects.get(id=record_id)
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
                    "hiring_start_date": data.hiring_start_date,
                    "hiring_end_date": data.hiring_end_date,
                }
                records.append(record)

            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

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
        operation_id="6",
    )
    def delete(self, request, *args, **kwargs):
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
            interview_schedule.objects.create(
                client_id=serializer.validated_data["client_id"],
                employee_name=serializer.validated_data["employee_name"],
                gender=serializer.validated_data["gender"],
                job_title=serializer.validated_data["job_title"],
                role_type=serializer.validated_data["role_type"],
                employment_term=serializer.validated_data["employment_term"],
                interview_date_time=serializer.validated_data["interview_date_time"],
                country=serializer.validated_data["country"],
            )
            return Response(
                {"message": "Resquest created"}, status=status.HTTP_201_CREATED
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
        ],
        operation_summary="Endpoint to retrieve hiring request data.",
        operation_id="1",
    )
    def get(self, request, *args, **kwargs):
        interview_records = interview_schedule.objects.all()

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
            interview_schedule.objects.filter(id=delete_id).delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                ),
                "notice_period": openapi.Schema(type=openapi.TYPE_STRING),
                "salary": openapi.Schema(type=openapi.TYPE_INTEGER),
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
        if serializer.is_valid():
            onboarding.objects.create(
                client_id=serializer.validated_data["client_id"],
                employee_name=serializer.validated_data["employee_name"],
                gender=serializer.validated_data["gender"],
                country=serializer.validated_data["country"],
                job_title=serializer.validated_data["job_title"],
                role_type=serializer.validated_data["role_type"],
                joining_date=serializer.validated_data["joining_date"],
                notice_period=serializer.validated_data["notice_period"],
                salary=serializer.validated_data["salary"],
                benefits=serializer.validated_data["benefits"],
            )
            return Response(
                {"message": "Resquest created"}, status=status.HTTP_201_CREATED
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
        operation_id="7",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.quary_params.get("id")
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
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

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
            onboarding.objects.filter(id=delete_id).delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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
        clients = client.objects.all()
        if clients:
            records = []
            for cl in clients:
                user = end_user.objects.get(email=cl.email)
                record = {
                    "id": cl.id,
                    "client_id": cl.client_id,
                    "name": cl.first_name + " " + cl.last_name,
                    "image_path": cl.image.path,
                    "company_name": cl.company_name,
                    "active": user.is_active,
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


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
        operation_id="1",
        operation_summary="Get Employee Details",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        client_data = client.objects.get(id=record_id)
        if client_data:
            try:
                record = {
                    "id": client_data.id,
                    "client_id": client_data.client_id,
                    "first_name": client_data.first_name,
                    "last_name": client_data.last_name,
                    "company_name": client_data.company_name,
                    "phone_number": client_data.phone_number,
                    "email": client_data.email,
                    "country": client_data.country,
                    "image_path": client_data.image.path,
                    "address": client_data.address,
                    "join_date": client_data.join_date,
                }
                return Response(record, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

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
                name="email",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
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
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        for key in updates:
            setattr(client_record, key, updates[key])
        try:
            client_record.save()
        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


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
        operation_id=".",
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
                "image": data.image.path,
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
        operation_id=".",
    )
    def patch(self, request, *args, **kwargs):
        updates = request.data
        comp_data = company_data.objects.all()
        if comp_data:
            try:
                comp_data = company_data.objects.all()[0]
                for key in updates:
                    setattr(comp_data, key, updates[key])
                try:
                    comp_data.save()                
                except ValidationError as e:
                    return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response(
                        {"error": "Invalid form fields"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = CompanyDataSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    company_data.objects.create(
                        company_name=serializer.validated_data["company_name"],
                        company_email=serializer.validated_data["company_email"],
                        website_url=serializer.validated_data["website_url"],
                        image=serializer.validated_data["image"],
                    )
                    return Response(status=status.HTTP_201_CREATED)
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
                    "image": account.image.path,
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
                        account_n_persmission.objects.create(
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
                            }
                        )

                        end_user.objects.create_user(
                            username=serializer.validated_data["account_name"],
                            role=serializer.validated_data["account_name"],
                            email=serializer.validated_data["email"],
                            password=password,
                        )

                        return Response(status=status.HTTP_201_CREATED)
                    except ValidationError as e:
                        return Response(
                            {"error": e}, status=status.HTTP_400_BAD_REQUEST
                        )
                    except:
                        return Response(
                            {"error": "Invalid form fields"},
                            status=status.HTTP_400_BAD_REQUEST,
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
        except:
            return Response(
                {"error": "Invalid form fields"}, status=status.HTTP_400_BAD_REQUEST
            )

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
            account.delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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
                return Response(status=status.HTTP_200_OK)
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
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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
    # request 1
    def get(self, request, *args, **kwargs):
        hr_policies = policy.objects.all()
        policies = []
        for hr_pol in hr_policies:
            record = {
                "id": hr_pol.id,
                "policy_name": hr_pol.policy_name,
                "employee": hr_pol.employee,
                "client": hr_pol.client,
            }
            policies.append(record)
        if len(policies) > 0:
            return Response(policies, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    # request 2
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
                policy.objects.create(
                    policy_name=serializer.validated_data["policy_name"],
                    policy_doc=serializer.validated_data["policy_doc"],
                    employee=False,
                    client=False,
                )
                return Response(
                    {"message": "Resquest created"}, status=status.HTTP_201_CREATED
                )
            except ValidationError as e:
                return Response(
                    {"error": e}, status=status.HTTP_400_BAD_REQUEST
                )
            except:
                return Response(
                    {"error": "Invalid form fields"},
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
            policy.objects.filter(id=delete_id).delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Policies_Edit(APIView):
    @swagger_auto_schema(
        tags=["Policies"],
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
        return Response(status=status.HTTP_200_OK)


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
                enum=["clients", "employees"],
                default="clients",
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
            if get_status == "clients":
                try:
                    serializer = ClientContractSerializers(data=posted_data)
                    if serializer.is_valid():
                        client_contract.objects.create(
                            client_id=serializer.validated_data["client_id"],
                            contract_name=serializer.validated_data["contract_name"],
                            date=serializer.validated_data["date"],
                            contract_doc=serializer.validated_data["contract_doc"],
                        )
                        return Response(
                            {"message": "Client contract created successfully"},
                            status=status.HTTP_201_CREATED,
                        )
                    else:
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )
                except serializers.ValidationError as e:
                    return Response(
                        {"message": "Invalid client contract data", "errors": e.detail},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            elif get_status == "employees":
                try:
                    serializer = EmployeeContractSerializers(data=posted_data)
                    if serializer.is_valid():
                        employee_contract.objects.create(
                            employee_id=serializer.validated_data["employee_id"],
                            contract_name=serializer.validated_data["contract_name"],
                            date=serializer.validated_data["date"],
                            contract_doc=serializer.validated_data["contract_doc"],
                        )
                        return Response(
                            {"message": "Employee contract created successfully"},
                            status=status.HTTP_201_CREATED,
                        )
                    else:
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )
                except serializers.ValidationError as e:
                    return Response(
                        {"message": "Invalid client contract data", "errors": e.detail},
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
                default="client",
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
                            "client_id/employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                            "date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "contract_doc": openapi.Schema(type=openapi.TYPE_STRING),
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
            if get_status == "clients":
                contracts = client_contract.objects.all()
                client_cont = []
                for contract in contracts:
                    record = {
                        "id": contract.id,
                        "contract_name": contract.contract_name,
                        "client_id": contract.client_id,
                        "date": contract.date,
                        "contract_doc": contract.contract_doc.path,
                    }
                if not client_cont:
                    return Response({"message": "No client contracts available"}, status=status.HTTP_204_NO_CONTENT)
                return Response(str(client_cont), status=status.HTTP_200_OK)

            elif get_status == "employees":
                contracts = employee_contract.objects.all()
                employee_cont = []
                for contract in contracts:
                    record = {
                        "id": contract.id,
                        "contract_name": contract.contract_name,
                        "employee_id": contract.employee_id,
                        "date": contract.date,
                        "contract_doc": contract.contract_doc.path,
                    }
                employee_cont.append(record)
                if not employee_cont:
                    return Response({"message": "No employee contracts available"}, status=status.HTTP_204_NO_CONTENT)
                return Response(str(employee_cont), status=status.HTTP_200_OK)
        return Response(
            {"message": "Invalid status parameter"}, status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        tags=["Comapny Contract"],
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
                client_contract.objects.filter(id=delete_id).delete()
            elif get_status == "employees":
                employee_contract.objects.filter(id=delete_id).delete()
            else:
                return Response(
                    {"message": "Invalid status parameter"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"message": "Contract deleted successfully"}, status=status.HTTP_200_OK
            )

        except client_contract.DoesNotExist:
            return Response(
                {"message": "Client contract not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except employee_contract.DoesNotExist:
            return Response(
                {"message": "Employee contract not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                name="employee_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
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
            serializer = OffshoreContractSerializers(data=posted_data)
            if serializer.is_valid():
                offshore_contracts.objects.create(
                    employee_id=serializer.validated_data["employee_id"],
                    client_id=serializer.validated_data["client_id"],
                    contract_name=serializer.validated_data["contract_name"],
                    date=serializer.validated_data["date"],
                    contract_doc=serializer.validated_data["contract_doc"],
                )
                return Response(
                    {"message": "offshore contract created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": "Invalid status parameter"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except serializers.ValidationError as e:
                    return Response(
                        {"message": "Invalid offshore contract data", "errors": e.detail},
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
                            "client_id": openapi.Schema(type=openapi.TYPE_STRING),
                            "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                            "date": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "contract_doc": openapi.Schema(type=openapi.TYPE_STRING),
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
            record = {
                "id": contract.id,
                "contract_name": contract.contract_name,
                "client_id": contract.client_id,
                "employee_id": contract.employee_id,
                "date": contract.date,
                "contract_doc": contract.contract_doc.path,
            }
        offshore_cont.append(record)
        if not offshore_cont:
            return Response({"message": "No offshore contracts available"}, status=status.HTTP_204_NO_CONTENT)
        return Response(str(offshore_cont), status=status.HTTP_200_OK)
    
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
            offshore_contracts.objects.filter(id=delete_id).delete()
            return Response(
                {"message": "Offshore Contract deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except offshore_contracts.DoesNotExist:
            return Response(
                {"message": "offshore contract not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
