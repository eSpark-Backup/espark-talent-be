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


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Add_Employee(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Employee : Add Employee"],
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
                name="phone_no",
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
                name="designation",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="department",
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
                name="benefits",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_OBJECT,
                default={"health": True, "fuel": False},
                required=True,
            ),
            openapi.Parameter(
                name="punch_time",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_OBJECT,
                default={"check_in": "10:00", "check_out": "19:00"},
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
                employee.objects.create(
                    employee_id=serializer.validated_data["employee_id"],
                    first_name=serializer.validated_data["first_name"],
                    last_name=serializer.validated_data["last_name"],
                    gender=serializer.validated_data["gender"],
                    dob=serializer.validated_data["dob"],
                    phone_no=serializer.validated_data["phone_no"],
                    email=serializer.validated_data["email"],
                    marital_status=serializer.validated_data["marital_status"],
                    image=serializer.validated_data["image"],
                    emergency_no=serializer.validated_data["emergency_no"],
                    resume=serializer.validated_data["resume"],
                    emergency_contact=serializer.validated_data["emergency_contact"],
                    joining_date=serializer.validated_data["joining_date"],
                    designation=serializer.validated_data["designation"],
                    department=serializer.validated_data["department"],
                    company=serializer.validated_data["company"],
                    benefits=serializer.validated_data["benefits"],
                    punch_time=serializer.validated_data["punch_time"],
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
                    },
                    sick_leaves={
                        "total": sick_leaves,
                        "availed": 0,
                        "balance": sick_leaves,
                    },
                    annual_leaves={
                        "total": annual_leaves,
                        "availed": 0,
                        "balance": annual_leaves,
                    },
                    unpaid_leaves={
                        "total": unpaid_leaves,
                        "availed": 0,
                        "balance": unpaid_leaves,
                    },
                    hajj_leaves={
                        "total": hajj_leaves,
                        "availed": 0,
                        "balance": hajj_leaves,
                    },
                    paid_leaves={
                        "total": paid_leaves,
                        "availed": 0,
                        "balance": paid_leaves,
                    },
                )

                outsource_employees.objects.create(
                    client_id="talent@esparkconsultants.com",
                    employee_id=serializer.validated_data["email"],
                    job_title=serializer.validated_data["designation"],
                    country="Pakistan",
                    role_type="",
                    employment_term="",
                    joining_date=serializer.validated_data["joining_date"],
                    salary="",
                    benefits={},
                )
                return Response(
                    {"message": "Resquest created"}, status=status.HTTP_201_CREATED
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
        tags=["Employee: Add Asset"],
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


# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
# class Employee_Invoice(APIView):

#     parser_classes = (MultiPartParser,)

#     @swagger_auto_schema(
#         tags=["Client : Employee Invoice"],
#         responses={
#             201: "Request created",
#             400: "Bad Request",
#             401: "Unauthorized",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "Authorization",
#                 openapi.IN_HEADER,
#                 description="Bearer Token",
#                 type=openapi.TYPE_STRING,
#             ),
#             openapi.Parameter(
#                 name="onboarding_id",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_STRING,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 name="invoice_date",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_STRING,
#                 format=openapi.FORMAT_DATE,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 name="due_date",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_STRING,
#                 format=openapi.FORMAT_DATE,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 name="invoice_amount",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 name="invoice",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_FILE,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 "payment_status",
#                 openapi.IN_FORM,
#                 type=openapi.TYPE_STRING,
#                 enum=["Paid", "Pending", "Processing"],
#                 required=True,
#             ),
#             openapi.Parameter(
#                 name="employee_email",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_STRING,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 name="client_email",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_STRING,
#                 required=True,
#             ),
#         ],
#         operation_summary="Employee Invoice",
#         operation_id=".",
#     )
#     def post(self, request, *args, **kwargs):
#         posted_data = request.data
#         employee_mail = posted_data.pop("employee_email", None)[0]
#         client_mail = posted_data.pop("client_email", None)[0]
#         try:
#             onboards = onboarding.objects.get(
#                 client=client_mail, employee=employee_mail
#             )
#             onboard_id = onboards.id
#             posted_data["onboarding_id"] = onboard_id
#             serializer = EmployeeInvoiceSerializer(data=posted_data)
#             if serializer.is_valid():
#                 employee_invoice.objects.create(
#                     onboarding_id=serializer.validated_data["onboarding_id"],
#                     invoice_date=serializer.validated_data["invoice_date"],
#                     due_date=serializer.validated_data["due_date"],
#                     invoice_amount=serializer.validated_data["invoice_amount"],
#                     payment_status=serializer.validated_data["payment_status"],
#                     invoice=serializer.validated_data["invoice"],
#                 )
#                 return Response(
#                     {"message": "Resquest created"}, status=status.HTTP_201_CREATED
#                 )
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(
#         tags=["Client : Employee Invoice"],
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 "payment_status": openapi.Schema(
#                     type=openapi.TYPE_STRING, enum=["Pending", "Processing", "Paid"]
#                 ),
#             },
#             required=["payment_status"],
#         ),
#         manual_parameters=[
#             openapi.Parameter(
#                 "id",
#                 openapi.IN_QUERY,
#                 description="ID of the record",
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 "Authorization",
#                 openapi.IN_HEADER,
#                 description="Bearer Token",
#                 type=openapi.TYPE_STRING,
#             ),
#         ],
#         responses={
#             201: "Request created",
#             400: "Bad Request",
#             401: "Unauthorized",
#         },
#         operation_summary="Employee Invoice",
#         operation_id=".",
#     )

#     def patch(self, request, *args, **kwargs):
#         request_id = request.query_params.get("id")
#         to_update_status = request.data["payment_status"]
#         try:
#             to_update_emp_inv = employee_invoice.objects.get(id=request_id)
#             if to_update_emp_inv:
#                 to_update_emp_inv.payment_status = to_update_status
#                 to_update_emp_inv.save()

#                 return Response(status=status.HTTP_200_OK)
#             else:
#                 return Response(status=status.HTTP_204_NO_CONTENT)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
# class Other_Payment(APIView):
#     parser_classes = (MultiPartParser,)

#     @swagger_auto_schema(
#         tags=["Client : Other Invoice/payment"],
#         responses={
#             201: "Request created",
#             400: "Bad Request",
#             401: "Unauthorized",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "Authorization",
#                 openapi.IN_HEADER,
#                 description="Bearer Token",
#                 type=openapi.TYPE_STRING,
#             ),
#             openapi.Parameter(
#                 name="client",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_STRING,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 name="invoice_reference",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_STRING,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 name="invoice_date",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_STRING,
#                 format=openapi.FORMAT_DATE,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 name="due_date",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_STRING,
#                 format=openapi.FORMAT_DATE,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 name="invoice_amount",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 name="invoice",
#                 in_=openapi.IN_FORM,
#                 type=openapi.TYPE_FILE,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 "payment_status",
#                 openapi.IN_FORM,
#                 type=openapi.TYPE_STRING,
#                 enum=["Paid", "Pending", "Processing"],
#                 required=True,
#             ),
#         ],
#         operation_summary="Other Invoice/payment",
#         operation_id=".",
#     )
#     def post(self, request, *args, **kwargs):
#         serializer = OtherPaymentSerializer(data=request.data)
#         if serializer.is_valid():
#             other_payment.objects.create(
#                 client=serializer.validated_data["client"],
#                 invoice_reference=serializer.validated_data["invoice_reference"],
#                 invoice_date=serializer.validated_data["invoice_date"],
#                 due_date=serializer.validated_data["due_date"],
#                 invoice_amount=serializer.validated_data["invoice_amount"],
#                 payment_status=serializer.validated_data["payment_status"],
#                 invoice=serializer.validated_data["invoice"],
#             )
#             return Response(
#                 {"message": "Resquest created"}, status=status.HTTP_201_CREATED
#             )
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#     @swagger_auto_schema(
#         tags=["Client : Other Invoice/payment"],
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 "payment_status": openapi.Schema(
#                     type=openapi.TYPE_STRING, enum=["Pending", "Processing", "Paid"]
#                 ),
#             },
#             required=["payment_status"],
#         ),
#         manual_parameters=[
#             openapi.Parameter(
#                 "id",
#                 openapi.IN_QUERY,
#                 description="ID of the record",
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 "Authorization",
#                 openapi.IN_HEADER,
#                 description="Bearer Token",
#                 type=openapi.TYPE_STRING,
#             ),
#         ],
#         responses={
#             201: "Request created",
#             400: "Bad Request",
#             401: "Unauthorized",
#         },
#         operation_summary="Other Invoice/payment",
#         operation_id=".",
#     )
#     def patch(self, request, *args, **kwargs):
#         request_id = request.query_params.get("id")
#         to_update_status = request.data["payment_status"]
#         try:
#             to_update_otherpay = other_payment.objects.get(id=request_id)
#             if to_update_otherpay:
#                 to_update_otherpay.payment_status = to_update_status
#                 to_update_otherpay.save()

#                 return Response(status=status.HTTP_200_OK)
#             else:
#                 return Response(status=status.HTTP_204_NO_CONTENT)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hr_Home(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user.username
        record = {
            "user": user,
            "employees": employee.objects.all().count(),
            "clients": client.objects.all().count(),
            "hiring_requests": hiring_request.objects.all().count(),
            "interview_schedules": interview_schedule.objects.all().count(),
        }
        return Response(record, status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hr_Employees(APIView):
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
                                "image": e_user.image.url,
                                "designation": e_user.designation,
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
                                "image": emp.image.url,
                                "designation": emp.designation,
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
                    e_user = outsource_employees.objects.get(email=emp.email)
                    if not e_user:
                        company = emp.company
                        active = False
                    else:
                        c_user = client.objects.get(email=e_user.client_id)
                        company = c_user.company_name
                        active = True

                    record = {
                        "id": emp.id,
                        "employee_id": emp.employee_id,
                        "name": emp.first_name + " " + emp.last_name,
                        "image": emp.image.url,
                        "designation": emp.designation,
                        "company": company,
                        "active": active,
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hr_Employee(APIView):
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        tab = request.query_params.get("tab")
        employee_data = employee.objects.get(id=record_id)
        if tab == "client":
            active_clients = []
            terminated_clients = []
            contracts = []
            active = outsource_employees.objects.filter(
                employee_id=employee_data.email, status="active"
            )
            terminated = outsource_employees.objects.filter(
                employee_id=employee_data.email, status="terminated"
            )
            contract = employee_contract.objects.filter(employee_id=employee_data.email)
            if active and terminated and contract:
                for rec in active:
                    client_data = client.objects.get(email=rec.client_id)
                    record = {
                        "client_name": client_data.first_name
                        + " "
                        + client_data.last_name,
                        "client_id": client_data.client_id,
                        "job_title": rec.job_title,
                        "employeement_term": rec.employment_term,
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
                for rec in contract:
                    if rec.client_id != "talent@esparkconsultants.com":
                        client_data = client.objects.get(email=rec.client_id)
                        record = {
                            "contract_name": rec.contract_name,
                            "client_id": client_data.client_id,
                            "date": rec.date,
                            "download": rec.contract_doc.url,
                        }
                        contracts.append(record)

                data = {
                    "active_clients": active_clients,
                    "terminated_clients": terminated_clients,
                    "contract_signed": contracts,
                }
                return Response(data, status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        elif tab == "contract":
            contract = employee_contract.objects.filter(employee_id=employee_data.email)
            if contract:
                records = []
                for rec in contract:
                    if rec.client_id == "talent@esparkconsultants.com":
                        client_data = client.objects.get(email=rec.client_id)
                        record = {
                            "contract_name": rec.contract_name,
                            "client_id": client_data.client_id,
                            "date": rec.date,
                            "download": rec.contract_doc.url,
                        }
                        records.append(record)
                if len(records) > 0:
                    return Response(records, status=status.HTTP_200_OK)

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
                    "first_name": emp_record.first_name,
                    "last_name": emp_record.last_name,
                    "gender": emp_record.gender,
                    "dob": emp_record.dob,
                    "phone_no": emp_record.phone_no,
                    "email": emp_record.email,
                    "marital_status": emp_record.marital_status,
                    "image": emp_record.image.url,
                    "emergency_no": emp_record.emergency_no,
                    "resume": emp_record.resume.url,
                    "emergency_contact": emp_record.emergency_contact,
                    "joining_date": emp_record.joining_date,
                    "designation": emp_record.designation,
                    "department": emp_record.department,
                    "company": emp_record.company,
                }
                return Response(record, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Update_Emp_Person_Info(APIView):
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
class Start_Hiring(APIView):
    @swagger_auto_schema(
        tags=["Client : Hiring Request"],
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

    def get(self, request, *args, **kwargs):
        hiring_requests = hiring_request.objects.all()

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
        tags=["Client : Interview Schedule"],
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
        operation_summary="Endpoint to create interview request.",
        operation_id=".",
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

    def delete(self, request, *args, **kwargs):
        user = request.user
        delete_id = request.query_params.get("id")
        try:
            interview_schedule.objects.filter(id=delete_id).delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
