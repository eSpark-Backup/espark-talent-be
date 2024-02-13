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
from datetime import datetime, timedelta
from dateutil import parser
from django.db.models import Q
from .threads import Check_Punches
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Employee_Home(APIView):
    @swagger_auto_schema(
        tags=["Dashboard"],
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
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "leave_summaries": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "casual_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "balance": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "available": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "pending": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                    },
                                ),
                                "sick_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "balance": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "available": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "pending": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                    },
                                ),
                                "annual_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "balance": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "available": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "pending": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                    },
                                ),
                                "unpaid_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "balance": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "available": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "pending": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                    },
                                ),
                                "paid_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "balance": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "available": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "pending": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                    },
                                ),
                                "hajj_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "balance": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "available": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "pending": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                    },
                                ),
                            },
                        ),
                        "workspaces": openapi.Schema(type=openapi.TYPE_OBJECT),
                        "requests": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "employee_id": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "employee_name": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "department": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "leave_type": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "requested_at": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATETIME,
                                    ),
                                    "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "status": openapi.Schema(type=openapi.TYPE_STRING),
                                    "start_date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATE,
                                    ),
                                    "end_date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATE,
                                    ),
                                    "reason": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                        ),
                        "pending": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "rejected": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "completed": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "all": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            204: openapi.Response(description="No content"),
            206: openapi.Response(description="Partial content"),
            401: openapi.Response(description="UnAuthorize"),
            400: openapi.Response(description="Bad Request"),
        },
        operation_summary="Endpoint to employee home/dashboard.",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        e_email = request.user
        workspace = request.query_params.get("workspace")
        current_employee = employee.objects.get(email=e_email)
        employee_details = {
            "employee_id": current_employee.employee_id,
            "employee_name": current_employee.first_name
            + " "
            + current_employee.last_name,
            "employee_email": current_employee.email,
            "image": current_employee.image.path,
        }
        try:
            current_client = client.objects.get(email=workspace)
            current_workspace = {
                "clinet_id": current_client.client_id,
                "client_email": current_client.email,
                "company_name": current_client.company_name,
                "client_name": current_client.first_name
                + " "
                + current_client.last_name,
                "image": current_client.image.path,
            }
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            leave_records = leave_balance.objects.get(employee_id=e_email)
            leave_summary = {
                "id": leave_records.id,
                "casual_leaves": leave_records.casual_leaves,
                "sick_leaves": leave_records.sick_leaves,
                "annual_leaves": leave_records.annual_leaves,
                "unpaid_leaves": leave_records.unpaid_leaves,
                "hajj_leaves": leave_records.hajj_leaves,
                "paid_leaves": leave_records.paid_leaves,
            }
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        out_sourced_to = [
            workspace.client_id
            for workspace in outsource_employees.objects.filter(employee_id=e_email)
        ]
        clients = client.objects.filter(email__in=out_sourced_to)
        if clients:
            workspaces = {}
            for rec in clients:
                workspaces[rec.email] = rec.company_name

        current_month = datetime.now().strftime("%B")
        current_year = datetime.now().year
        try:
            time_sheet_record = time_sheet.objects.get(
                employee_id=e_email,
                client_id=workspace,
                month=current_month,
                year=current_year,
            )
            month_timesheet = {
                "id": time_sheet_record.id,
                "client_id": time_sheet_record.client_id,
                "employee_id": time_sheet_record.employee_id,
                "month": time_sheet_record.month,
                "record": time_sheet_record.record,
                "year": time_sheet_record.year,
            }
        except:
            month_timesheet = {}
        punch_timings = employee.objects.get(email=e_email).punch_timings
        payload = {
            "leave_summaries": leave_summary,
            "workspaces": workspaces,
            "months_timesheet": month_timesheet,
            "punch_timings": punch_timings,
            "current_workspace": current_workspace,
            "employee_details": employee_details,
        }
        return Response(payload, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        e_email = request.user
        workspace = request.query_params.get("workspace")
        check_in = request.query_params.get("check_in")
        check_out = request.query_params.get("check_out")
        breaked = request.query_params.get("break")
        resumed = request.query_params.get("resume")
        if check_in:
            punch_check_in = Check_Punches()
            punch_check_in.check_punch(
                employee=e_email, client=workspace, check_in=check_in
            )

        if check_out:
            punch_check_out = Check_Punches()
            punch_check_out.check_punch(
                employee=e_email, client=workspace, check_out=check_out
            )

        if breaked:
            punch_breaked = Check_Punches()
            punch_breaked.check_punch(
                employee=e_email, client=workspace, breaked=breaked
            )

        if resumed:
            punch_resumed = Check_Punches()
            punch_resumed.check_punch(
                employee=e_email, client=workspace, resumed=resumed
            )

        else:
            no_punch=Check_Punches()
            no_punch.check_punch(
                employee=e_email, client=workspace
            )

        
        return Response(status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Company_Contract(APIView):
    @swagger_auto_schema(
        tags=["Company contracts"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "contract_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "date": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                        ),
                        "contract_doc": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response(description="Bad Request"),
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
        operation_summary="Endpoint to retrieve employee contracts.",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        e_email = request.user
        emp_contract = employee_contract.objects.filter(employee_id=e_email)
        if emp_contract:
            records = []
            for contract in emp_contract:
                record = {
                    "id": contract.id,
                    "employee_id": employee.objects.get(email=request.user).employee_id,
                    "contract_name": contract.contract_name,
                    "date": contract.date,
                    "contract_doc": contract.contract_doc.path,
                }
                records.append(record)

            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Offshore_Contract(APIView):
    @swagger_auto_schema(
        tags=["Client contracts"],
        responses={
            200: openapi.Response(
                description="Successful request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "client_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "contract_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "date": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                        ),
                        "contract_doc": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response(description="Bad Request"),
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
        operation_summary="Endpoint to retrieve offshore contracts.",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        e_email = request.user
        c_email = request.query_params.get("c_email")
        offsh_contract = offshore_contracts.objects.filter(
            employee_id=e_email, client_id=c_email
        )
        if offsh_contract:
            records = []
            for contract in offsh_contract:
                record = {
                    "id": contract.id,
                    "client_id": client.objects.get(email=c_email).client_id,
                    "employee_id": employee.objects.get(email=request.user).employee_id,
                    "contract_name": contract.contract_name,
                    "date": contract.date,
                    "contract_doc": contract.contract_doc.path,
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Leave_Request(APIView):
    @swagger_auto_schema(
        tags=["Leave"],
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
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "balance": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "casual_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "balance": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "available": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "pending": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                    },
                                ),
                                "sick_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "balance": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "available": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "pending": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                    },
                                ),
                                "annual_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "balance": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "available": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "pending": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                    },
                                ),
                                "unpaid_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "balance": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "available": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "pending": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                    },
                                ),
                                "paid_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "balance": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "available": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "pending": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                    },
                                ),
                                "hajj_leaves": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "balance": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "available": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "availed": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                        "pending": openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),
                                    },
                                ),
                            },
                        ),
                        "months_timesheet": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "client_id": openapi.Schema(type=openapi.TYPE_STRING),
                                "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                                "month": openapi.Schema(type=openapi.TYPE_STRING),
                                "record": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "1-2-2024": openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                "check_in": openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    format=openapi.FORMAT_DATETIME,
                                                ),
                                                "check_out": openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    format=openapi.FORMAT_DATETIME,
                                                ),
                                                "breaK": openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    format=openapi.FORMAT_DATETIME,
                                                ),
                                                "resume": openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    format=openapi.FORMAT_DATETIME,
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
                                "year": openapi.Schema(type=openapi.TYPE_INTEGER),
                            },
                        ),
                        "punch_timings": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "check_in": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATETIME,
                                ),
                                "check_out": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATETIME,
                                ),
                            },
                        ),
                        "current_workspace": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "client_id": openapi.Schema(type=openapi.TYPE_STRING),
                                "client_email": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_EMAIL,
                                ),
                                "company_name": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "client_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "image": openapi.Schema(type=openapi.TYPE_FILE),
                            },
                        ),
                        "employee_details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                                "employee_email": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_EMAIL,
                                ),
                                "employee_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "image": openapi.Schema(type=openapi.TYPE_FILE),
                            },
                        ),
                    },
                ),
            ),
            204: openapi.Response(description="No content"),
            206: openapi.Response(description="Partial content"),
            401: openapi.Response(description="UnAuthorize"),
            400: openapi.Response(description="Bad Request"),
        },
        operation_summary="Endpoint to retrieve leave request and leave balance data.",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        e_email = request.user
        c_email = request.query_params.get("c_email")
        tab = request.query_params.get("tab")
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        if from_date and to_date:
            from_date_object = parser.parse(from_date)
            to_date_object = parser.parse(to_date)

            pending = leave_request.objects.filter(
                Q(employee_id=e_email, client_id=c_email),
                created_at__date__gte=from_date_object,
                created_at__date__lte=to_date_object,
                status="pending",
            ).count()
            rejected = leave_request.objects.filter(
                Q(employee_id=e_email, client_id=c_email),
                created_at__date__gte=from_date_object,
                created_at__date__lte=to_date_object,
                status="rejected",
            ).count()
            completed = leave_request.objects.filter(
                Q(employee_id=e_email, client_id=c_email),
                created_at__date__gte=from_date_object,
                created_at__date__lte=to_date_object,
                status="completed",
            ).count()
            all = leave_request.objects.filter(
                Q(employee_id=e_email, client_id=c_email),
                created_at__date__gte=from_date_object,
                created_at__date__lte=to_date_object,
            ).count()

            if tab == "pending" or tab == "completed" or tab == "rejected":
                l_request = leave_request.objects.filter(
                    Q(employee_id=e_email, client_id=c_email),
                    created_at__date__gte=from_date_object,
                    created_at__date__lte=to_date_object,
                    status=tab,
                )
                request_record = []
                if l_request:
                    for req in l_request:
                        record = {
                            "id": req.id,
                            "employee_id": employee.objects.get(
                                email=request.user
                            ).employee_id,
                            "employee_name": employee.objects.get(
                                email=request.user
                            ).first_name
                            + " "
                            + employee.objects.get(email=request.user).last_name,
                            "department": employee.objects.get(
                                email=request.user
                            ).job_title,
                            "leave_type": req.leave_type,
                            "requested_at": req.created_at,
                            "count": req.count,
                            "status": req.status,
                            "start_date": req.start_date,
                            "end_date": req.end_date,
                            "reason": req.reason,
                        }
                        request_record.append(record)
                else:
                    request_record = []
            elif not tab:
                l_request = leave_request.objects.filter(
                    Q(employee_id=e_email, client_id=c_email),
                    created_at__date__gte=from_date_object,
                    created_at__date__lte=to_date_object,
                )
                request_record = []
                if l_request:
                    for req in l_request:
                        record = {
                            "id": req.id,
                            "employee_id": employee.objects.get(
                                email=request.user
                            ).employee_id,
                            "employee_name": employee.objects.get(
                                email=request.user
                            ).first_name
                            + " "
                            + employee.objects.get(email=request.user).last_name,
                            "department": employee.objects.get(
                                email=request.user
                            ).job_title,
                            "leave_type": req.leave_type,
                            "requested_at": req.created_at,
                            "count": req.count,
                            "status": req.status,
                            "start_date": req.start_date,
                            "end_date": req.end_date,
                            "reason": req.reason,
                        }
                        request_record.append(record)
                else:
                    request_record = []
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if request_record:
                records = {
                    "requests": request_record,
                    "pending": pending,
                    "rejected": rejected,
                    "completed": completed,
                    "all": all,
                }
                return Response(records, status=status.HTTP_200_OK)
            else:
                records = {
                    "requests": [],
                    "pending": pending,
                    "rejected": rejected,
                    "completed": completed,
                    "all": all,
                }
                return Response(records, status=status.HTTP_204_NO_CONTENT)
        else:
            pending = leave_request.objects.filter(
                employee_id=e_email, client_id=c_email, status="pending"
            ).count()
            rejected = leave_request.objects.filter(
                employee_id=e_email, client_id=c_email, status="rejected"
            ).count()
            completed = leave_request.objects.filter(
                employee_id=e_email, client_id=c_email, status="completed"
            ).count()
            all = leave_request.objects.filter(
                employee_id=e_email, client_id=c_email
            ).count()
            try:
                l_balance = leave_balance.objects.get(employee_id=e_email)
                balance_record = {
                    "id": l_balance.id,
                    "casual_leaves": l_balance.casual_leaves,
                    "sick_leaves": l_balance.sick_leaves,
                    "annual_leaves": l_balance.annual_leaves,
                    "unpaid_leaves": l_balance.unpaid_leaves,
                    "paid_leaves": l_balance.paid_leaves,
                    "hajj_leaves": l_balance.hajj_leaves,
                }
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if tab == "pending" or tab == "completed" or tab == "rejected":
                l_request = leave_request.objects.filter(
                    employee_id=e_email, client_id=c_email, status=tab
                )
                request_record = []
                if l_request:
                    for req in l_request:
                        record = {
                            "id": req.id,
                            "employee_id": employee.objects.get(
                                email=request.user
                            ).employee_id,
                            "employee_name": employee.objects.get(
                                email=request.user
                            ).first_name
                            + " "
                            + employee.objects.get(email=request.user).last_name,
                            "department": employee.objects.get(
                                email=request.user
                            ).job_title,
                            "leave_type": req.leave_type,
                            "requested_at": req.created_at,
                            "count": req.count,
                            "status": req.status,
                            "start_date": req.start_date,
                            "end_date": req.end_date,
                            "reason": req.reason,
                        }
                        request_record.append(record)
                else:
                    request_record = []
            elif not tab:
                l_request = leave_request.objects.filter(
                    employee_id=e_email, client_id=c_email
                )
                request_record = []
                if l_request:
                    for req in l_request:
                        record = {
                            "id": req.id,
                            "employee_id": employee.objects.get(
                                email=request.user
                            ).employee_id,
                            "employee_name": employee.objects.get(
                                email=request.user
                            ).first_name
                            + " "
                            + employee.objects.get(email=request.user).last_name,
                            "department": employee.objects.get(
                                email=request.user
                            ).job_title,
                            "leave_type": req.leave_type,
                            "requested_at": req.created_at,
                            "count": req.count,
                            "status": req.status,
                            "start_date": req.start_date,
                            "end_date": req.end_date,
                            "reason": req.reason,
                        }
                        request_record.append(record)
                else:
                    request_record = []
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if request_record:
                records = {
                    "balance": balance_record,
                    "requests": request_record,
                    "pending": pending,
                    "rejected": rejected,
                    "completed": completed,
                    "all": all,
                }
                return Response(records, status=status.HTTP_200_OK)
            elif not request_record:
                records = {
                    "balance": balance_record,
                    "requests": [],
                    "pending": pending,
                    "rejected": rejected,
                    "completed": completed,
                    "all": all,
                }
                return Response(records, status=status.HTTP_206_PARTIAL_CONTENT)

    @swagger_auto_schema(
        tags=["Leave : Create"],
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
                name="leave_type",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="start_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="end_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="count",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="reason",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="attachment",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ],
        operation_summary="Create leave request.",
        operation_id=".",
    )
    def post(self, request, *args, **kwargs):

        e_email = request.user
        try:
            client_email = request.data["client_id"]
            leave_type = request.data["leave_type"]
            start_date = request.data["start_date"]
            end_date = request.data["end_date"]
            count = request.data["count"]
            reason = request.data["reason"]
            attachment = request.data["attachment"]
            leave_request.objects.create(
                employee_id=e_email,
                client_id=client_email,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                count=count,
                reason=reason,
                attachment=attachment,
                status="pending",
            )
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Leave : Actions : Delete"],
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
        operation_summary="Endpoint to delete a leave request.",
        operation_id=".",
    )
    def delete(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        try:
            leave_request.objects.get(id=id).delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Time_Sheet(APIView):
    @swagger_auto_schema(
        tags=["Time sheet"],
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
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "time_sheet": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "month": openapi.Schema(type=openapi.TYPE_STRING),
                                "record": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "1-2-2024": openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                "check_in": openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    format=openapi.FORMAT_DATETIME,
                                                ),
                                                "check_out": openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    format=openapi.FORMAT_DATETIME,
                                                ),
                                                "breaK": openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    format=openapi.FORMAT_DATETIME,
                                                ),
                                                "resume": openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    format=openapi.FORMAT_DATETIME,
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
                                "year": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "expect_check_in": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATETIME,
                                ),
                                "expect_check_out": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATETIME,
                                ),
                            },
                        ),
                        "time_sheet_summary": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "workable_shifts": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "workable_hours": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "worked_hours": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "short_hours": openapi.Schema(type=openapi.TYPE_STRING),
                                "overtime_hours": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "short_duration": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "present": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "absent": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "day_off": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "missing_punch": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "leaves": openapi.Schema(type=openapi.TYPE_INTEGER),
                            },
                        ),
                        "employee_details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                                "employee_name": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "company": openapi.Schema(type=openapi.TYPE_STRING),
                                "location": openapi.Schema(type=openapi.TYPE_STRING),
                                "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                                "joining_date": openapi.Schema(
                                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                                ),
                            },
                        ),
                    },
                ),
            ),
            204: openapi.Response(description="No content"),
            401: openapi.Response(description="UnAuthorize"),
            400: openapi.Response(description="Bad Request"),
        },
        operation_summary="Endpoint to retrieve timesheet data.",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        e_email = request.user
        c_email = request.query_params.get("c_email")
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")

        if from_date and to_date:
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
            time_sheet_records = time_sheet.objects.filter(
                Q(employee_id=e_email, client_id=c_email),
                Q(
                    month__gte=month_mapping[from_month],
                    year__gte=from_year,
                )
                & Q(
                    month__gte=month_mapping[to_month],
                    year__lte=to_year,
                ),
            )

            filtered_record = {}
            for record in time_sheet_records:
                for key, value in record.record.items():
                    key_date = datetime.strptime(key, "%d-%m-%Y")
                    date = key_date.day
                    month = key_date.month
                    if (
                        from_date_object.day <= date and month == from_date_object.month
                    ) or (date <= to_date_object.day and month == to_date_object.month):
                        filtered_record[key] = value
            if len(filtered_record) > 0:
                hours_worked = 0
                minutes_worked = 0
                short_hours = 0
                short_minutes = 0
                short_duration = 0
                overtime_hours = 0
                overtime_minutes = 0
                present = 0
                missing_punch = 0
                leaves = 0
                day_off = 0
                absent = 0
                overtime_threshold = timedelta(hours=9)
                for date, rec in filtered_record.items():
                    check_in_time = rec["check_in"]
                    check_out_time = rec["check_out"]

                    check_in_datetime = datetime.strptime(check_in_time, "%H:%M:%S")
                    check_out_datetime = datetime.strptime(check_out_time, "%H:%M:%S")

                    time_difference = check_out_datetime - check_in_datetime

                    hours_worked += time_difference.seconds // 3600
                    minutes_worked += (time_difference.seconds // 60) % 60

                    if (time_difference.total_seconds() // 3600) < 9:
                        short_time = (
                            datetime.strptime("09:00:00", "%H:%M:%S") - time_difference
                        )
                        short_minutes += short_time.minute
                        short_hours += short_time.hour

                    if (time_difference.total_seconds() / 3600) > 9:
                        overtime = time_difference - overtime_threshold
                        overtime_hours += overtime.seconds // 3600
                        overtime_minutes += (overtime.seconds // 60) % 60

                    short_duration += rec["status"]["Short Duration"]
                    present += rec["status"]["Present"]
                    missing_punch += rec["status"]["Missing"]
                    leaves += rec["status"]["Full Leave"]
                    day_off += rec["status"]["Day Off"]
                    absent += rec["status"]["Absent"]

                if short_hours and short_minutes:
                    short_hours = f"{short_hours}h {short_minutes}m"
                elif short_hours and not short_minutes:
                    short_hours = f"{short_hours}h"
                elif not short_hours and short_minutes:
                    short_hours = f"{short_minutes}m"
                else:
                    short_hours = "0h"

                if overtime_hours and overtime_minutes:
                    overtime_hours = f"{overtime_hours}h {overtime_minutes}m"
                elif overtime_hours and not overtime_minutes:
                    overtime_hours = f"{overtime_hours}h"
                elif not overtime_hours and overtime_minutes:
                    overtime_hours = f"{overtime_minutes}m"
                else:
                    overtime_hours = "0h"

                if minutes_worked and hours_worked:
                    worked_hours = f"{hours_worked}h {minutes_worked}m"
                elif hours_worked and not minutes_worked:
                    worked_hours = f"{hours_worked}h"
                elif not hours_worked and minutes_worked:
                    worked_hours = f"{minutes_worked}m"
                else:
                    worked_hours = "0h"

                summary = {
                    "workable_shifts": len(filtered_record),
                    "workable_hours": f"{len(filtered_record)*9}h",
                    "worked_hours": worked_hours,
                    "short_hours": short_hours,
                    "overtime_hours": overtime_hours,
                    "short_duration": short_duration,
                    "present": present,
                    "absent": absent,
                    "day_off": day_off,
                    "missing_punch": missing_punch,
                    "leaves": leaves,
                }
                emp = employee.objects.get(email=e_email)
                clnt = client.objects.get(email=c_email)
                outsrc_emp = outsource_employees.objects.get(
                    employee_id=e_email, client_id=c_email
                )

                employee_details = {
                    "employee_id": emp.employee_id,
                    "employee_name": emp.first_name + " " + emp.last_name,
                    "company": clnt.company_name,
                    "location": clnt.address,
                    "job_title": outsrc_emp.job_title,
                    "joining_date": outsrc_emp.joining_date,
                }

                records = {
                    "time_sheet": filtered_record,
                    "time_sheet_summary": summary,
                    "employee_details": employee_details,
                }

            return Response(records, status=status.HTTP_200_OK)
        else:
            try:
                ts_record = time_sheet.objects.get(
                    employee_id=e_email,
                    client_id=c_email,
                    year=datetime.now().year,
                    month=datetime.now().strftime("%B"),
                )
                record = {
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
                hours_worked = 0
                minutes_worked = 0
                short_hours = 0
                short_minutes = 0
                short_duration = 0
                overtime_hours = 0
                overtime_minutes = 0
                present = 0
                missing_punch = 0
                leaves = 0
                day_off = 0
                absent = 0
                overtime_threshold = timedelta(hours=9)
                for date, rec in record["record"].items():
                    check_in_time = rec["check_in"]
                    check_out_time = rec["check_out"]
                    check_in_datetime = datetime.strptime(check_in_time, "%H:%M:%S")
                    check_out_datetime = datetime.strptime(check_out_time, "%H:%M:%S")

                    time_difference = check_out_datetime - check_in_datetime

                    hours_worked += time_difference.seconds // 3600
                    minutes_worked += (time_difference.seconds // 60) % 60

                    if (time_difference.total_seconds() // 3600) < 9:
                        short_time = (
                            datetime.strptime("09:00:00", "%H:%M:%S") - time_difference
                        )
                        short_minutes += short_time.minute
                        short_hours += short_time.hour

                    if (time_difference.total_seconds() / 3600) > 9:
                        overtime = time_difference - overtime_threshold
                        overtime_hours += overtime.seconds // 3600
                        overtime_minutes += (overtime.seconds // 60) % 60
                    short_duration += rec["status"]["Short Duration"]
                    present += rec["status"]["Present"]
                    missing_punch += rec["status"]["Missing"]
                    leaves += rec["status"]["Full Leave"]
                    day_off += rec["status"]["Day Off"]
                    absent += rec["status"]["Absent"]

                if short_hours and short_minutes:
                    short_hours = f"{short_hours}h {short_minutes}m"
                elif short_hours and not short_minutes:
                    short_hours = f"{short_hours}h"
                elif not short_hours and short_minutes:
                    short_hours = f"{short_minutes}m"
                else:
                    short_hours = "0h"
                if overtime_hours and overtime_minutes:
                    overtime_hours = f"{overtime_hours}h {overtime_minutes}m"
                elif overtime_hours and not overtime_minutes:
                    overtime_hours = f"{overtime_hours}h"
                elif not overtime_hours and overtime_minutes:
                    overtime_hours = f"{overtime_minutes}m"
                else:
                    overtime_hours = "0h"

                if minutes_worked and hours_worked:
                    worked_hours = f"{hours_worked}h {minutes_worked}m"
                elif hours_worked and not minutes_worked:
                    worked_hours = f"{hours_worked}h"
                elif not hours_worked and minutes_worked:
                    worked_hours = f"{minutes_worked}m"
                else:
                    worked_hours = "0h"

                summary = {
                    "workable_shifts": len(ts_record.record),
                    "workable_hours": f"{len(ts_record.record)*9}h",
                    "worked_hours": worked_hours,
                    "short_hours": short_hours,
                    "overtime_hours": overtime_hours,
                    "short_duration": short_duration,
                    "present": present,
                    "absent": absent,
                    "day_off": day_off,
                    "missing_punch": missing_punch,
                    "leaves": leaves,
                }

                emp = employee.objects.get(email=e_email)
                clnt = client.objects.get(email=c_email)
                outsrc_emp = outsource_employees.objects.get(
                    employee_id=e_email, client_id=c_email
                )

                employee_details = {
                    "employee_id": emp.employee_id,
                    "employee_name": emp.first_name + " " + emp.last_name,
                    "company": clnt.company_name,
                    "location": clnt.address,
                    "job_title": outsrc_emp.job_title,
                    "joining_date": outsrc_emp.joining_date,
                }

                records = {
                    "time_sheet": record,
                    "time_sheet_summary": summary,
                    "employee_details": employee_details,
                }
                return Response(records, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Punch_Request(APIView):
    @swagger_auto_schema(
        tags=["Leave"],
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
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "requests": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "employee_id": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "employee_name": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATE,
                                    ),
                                    "punch_type": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "punch_time": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATETIME,
                                    ),
                                    "description": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "status": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                        ),
                        "pending": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "rejected": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "completed": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "all": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            204: openapi.Response(description="No content"),
            206: openapi.Response(description="Partial content"),
            401: openapi.Response(description="UnAuthorize"),
            400: openapi.Response(description="Bad Request"),
        },
        operation_summary="Endpoint to retrieve punch request data.",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        e_email = request.user
        c_email = request.query_params.get("c_email")
        tab = request.query_params.get("tab")
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        if from_date and to_date:
            from_date_object = parser.parse(from_date)
            to_date_object = parser.parse(to_date)

            pending = punch_request.objects.filter(
                Q(employee_id=e_email, client_id=c_email),
                created_at__date__gte=from_date_object,
                created_at__date__lte=to_date_object,
                status="pending",
            ).count()
            rejected = punch_request.objects.filter(
                Q(employee_id=e_email, client_id=c_email),
                created_at__date__gte=from_date_object,
                created_at__date__lte=to_date_object,
                status="rejected",
            ).count()
            completed = punch_request.objects.filter(
                Q(employee_id=e_email, client_id=c_email),
                created_at__date__gte=from_date_object,
                created_at__date__lte=to_date_object,
                status="completed",
            ).count()
            all = punch_request.objects.filter(
                Q(employee_id=e_email, client_id=c_email),
                created_at__date__gte=from_date_object,
                created_at__date__lte=to_date_object,
            ).count()

            if tab == "pending" or tab == "completed" or tab == "rejected":
                p_request = punch_request.objects.filter(
                    Q(employee_id=e_email, client_id=c_email),
                    created_at__date__gte=from_date_object,
                    created_at__date__lte=to_date_object,
                    status=tab,
                )
                req_record = []
                if p_request:
                    for req in p_request:
                        record = {
                            "id": req.id,
                            "employee_id": employee.objects.get(
                                email=request.user
                            ).employee_id,
                            "employee_name": employee.objects.get(
                                email=request.user
                            ).first_name
                            + " "
                            + employee.objects.get(email=request.user).last_name,
                            "date": req.date,
                            "punch_type": req.punch_type,
                            "punch_time": req.punch_time,
                            "description": req.description,
                            "status": req.status,
                        }
                        req_record.append(record)
                else:
                    req_record = []
            elif not tab:
                p_request = punch_request.objects.filter(
                    Q(employee_id=e_email, client_id=c_email),
                    created_at__date__gte=from_date_object,
                    created_at__date__lte=to_date_object,
                )
                req_record = []
                if p_request:
                    for req in p_request:
                        record = {
                            "id": req.id,
                            "employee_id": employee.objects.get(
                                email=request.user
                            ).employee_id,
                            "employee_name": employee.objects.get(
                                email=request.user
                            ).first_name
                            + " "
                            + employee.objects.get(email=request.user).last_name,
                            "date": req.date,
                            "punch_type": req.punch_type,
                            "punch_time": req.punch_time,
                            "description": req.description,
                            "status": req.status,
                        }
                        req_record.append(record)
                else:
                    req_record = []
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if req_record:
                records = {
                    "requests": req_record,
                    "pending": pending,
                    "rejected": rejected,
                    "completed": completed,
                    "all": all,
                }
                return Response(records, status=status.HTTP_200_OK)
            else:
                records = {
                    "requests": [],
                    "pending": pending,
                    "rejected": rejected,
                    "completed": completed,
                    "all": all,
                }
                return Response(records, status=status.HTTP_204_NO_CONTENT)
        else:
            req_record = []
            pending = punch_request.objects.filter(
                employee_id=e_email, client_id=c_email, status="pending"
            ).count()
            rejected = punch_request.objects.filter(
                employee_id=e_email, client_id=c_email, status="rejected"
            ).count()
            completed = punch_request.objects.filter(
                employee_id=e_email, client_id=c_email, status="completed"
            ).count()
            all = punch_request.objects.filter(
                employee_id=e_email, client_id=c_email
            ).count()
            print(pending, rejected)
            if tab == "pending" or tab == "completed" or tab == "rejected":
                p_request = punch_request.objects.filter(
                    employee_id=e_email, client_id=c_email, status=tab
                )
                if p_request:
                    for req in p_request:
                        record = {
                            "id": req.id,
                            "employee_id": employee.objects.get(
                                email=request.user
                            ).employee_id,
                            "employee_name": employee.objects.get(
                                email=request.user
                            ).first_name
                            + " "
                            + employee.objects.get(email=request.user).last_name,
                            "date": req.date,
                            "punch_type": req.punch_type,
                            "punch_time": req.punch_time,
                            "description": req.description,
                            "status": req.status,
                        }
                        req_record.append(record)
                else:
                    req_record = []
            elif not tab:
                p_request = punch_request.objects.filter(
                    employee_id=e_email, client_id=c_email
                )
                if p_request:
                    for req in p_request:
                        record = {
                            "id": req.id,
                            "employee_id": employee.objects.get(
                                email=request.user
                            ).employee_id,
                            "employee_name": employee.objects.get(
                                email=request.user
                            ).first_name
                            + " "
                            + employee.objects.get(email=request.user).last_name,
                            "date": req.date,
                            "punch_type": req.punch_type,
                            "punch_time": req.punch_time,
                            "description": req.description,
                            "status": req.status,
                        }
                        req_record.append(record)
                else:
                    req_record = []
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if req_record:
                records = {
                    "requests": req_record,
                    "pending": pending,
                    "rejected": rejected,
                    "completed": completed,
                    "all": all,
                }
                return Response(records, status=status.HTTP_200_OK)
            elif not req_record:
                records = {
                    "requests": req_record,
                    "pending": pending,
                    "rejected": rejected,
                    "completed": completed,
                    "all": all,
                }
                return Response(records, status=status.HTTP_206_PARTIAL_CONTENT)

    @swagger_auto_schema(
        tags=["Punch requests : Create"],
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
                name="punch_type",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="punch_time",
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
                name="description",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_summary="Create punch request.",
        operation_id=".",
    )
    def post(self, request, *args, **kwargs):
        e_email = request.user
        try:
            client_email = request.data["client_id"]
            punch_type = request.data["punch_type"]
            punch_time = request.data["punch_time"]
            date = request.data["date"]
            description = request.data["description"]
            punch_request.objects.create(
                employee_id=e_email,
                client_id=client_email,
                punch_type=punch_type,
                punch_time=punch_time,
                date=date,
                description=description,
                status="pending",
            )
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Punch requests : Actions : Delete"],
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
        operation_summary="Endpoint to delete a punch request.",
        operation_id=".",
    )
    def delete(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        try:
            punch_request.objects.get(id=id).delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
