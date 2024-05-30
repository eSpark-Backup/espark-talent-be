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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from .emp_dash_funcs import *
from eSparkTalent.settings import talent_email
from .bucket_functions import remove_bucket_file


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Employee_Home(APIView):
    @swagger_auto_schema(
        tags=["Dashboard"],
        manual_parameters=[
            openapi.Parameter(
                "workspace",
                openapi.IN_QUERY,
                description="Specify current client email",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
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
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "leave_summary": openapi.Schema(
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
                        "attendance_summary": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "shifts": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "expected_minutes": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "worked_minutes": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "short_minutes": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "leaves": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "absents": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "presents": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "missings": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "days_off": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "overtimes": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "short_durations": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "late_arrivals": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "break_minutes": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                            },
                        ),
                        "statistics": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "today": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "this_week": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "this_month": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "remaining": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "overtime": openapi.Schema(type=openapi.TYPE_INTEGER),
                            },
                        ),
                        "today_activity": openapi.Schema(
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
                                "break": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="1:00 PM",
                                ),
                                "resume": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="2:00 PM",
                                ),
                            },
                        ),
                        "workspaces": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "email": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_EMAIL,
                                    ),
                                    "client_name": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "company_name": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        ),
                        "punch_timings": openapi.Schema(
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
                            },
                        ),
                        "employee_details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "employee_id": openapi.Schema(type=openapi.TYPE_STRING),
                                "employee_name": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "employee_email": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_EMAIL,
                                ),
                                "image": openapi.Schema(type=openapi.TYPE_FILE),
                                "job_title": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                        "company_image": openapi.Schema(type=openapi.TYPE_FILE),
                    },
                ),
            ),
            401: openapi.Response(description="UnAuthorize"),
            400: openapi.Response(description="Bad Request"),
        },
        operation_summary="Endpoint to employee home/dashboard.",
        operation_id="0",
    )
    def get(self, request, *args, **kwargs):
        e_email = request.user
        workspace = request.query_params.get("workspace")
        try:
            current_employee = employee.objects.get(email=e_email)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        employee_details = {
            "employee_id": current_employee.employee_id,
            "employee_name": current_employee.first_name
            + " "
            + current_employee.last_name,
            "employee_email": current_employee.email,
            "image": current_employee.image.url,
        }
        out_sourced_to = [
            w_space.client_id
            for w_space in outsource_employees.objects.filter(employee_id=e_email)
        ]
        clients = client.objects.filter(email__in=out_sourced_to)
        company = company_data.objects.all()
        if company:
            talent_company = company[0].company_name
        else:
            talent_company = "eSpark"
        workspaces = []
        workspaces.append(
            {
                "email": talent_email,
                "client_name": "eSpark Talent",
                "company_name": talent_company,
            }
        )
        if clients:
            for rec in clients:
                try:
                    is_active=end_user.objects.get(email=rec.email).is_active
                    if is_active:
                        record = {
                            "email": rec.email,
                            "client_name": rec.first_name + " " + rec.last_name,
                            "company_name": rec.company_name,
                        }
                        workspaces.append(record)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            annual_pending = leave_request.objects.filter(
                employee_id=e_email, client_id=workspace, leave_type="annual", status="pending",
            ).count()
            casual_pending = leave_request.objects.filter(
                employee_id=e_email, client_id=workspace, leave_type="casual", status="pending",
            ).count()
            sick_pending = leave_request.objects.filter(
                employee_id=e_email, client_id=workspace, leave_type="sick", status="pending",
            ).count()
            paid_pending = leave_request.objects.filter(
                employee_id=e_email, client_id=workspace, leave_type="paid", status="pending",
            ).count()
            unpaid_pending = leave_request.objects.filter(
                employee_id=e_email, client_id=workspace, leave_type="unpaid", status="pending",
            ).count()
            hajj_pending = leave_request.objects.filter(
                employee_id=e_email, client_id=workspace, leave_type="hajj", status="pending",
            ).count()
            leave_records = leave_balance.objects.get(employee_id=e_email)
            leave_records.casual_leaves["pending"]=casual_pending
            leave_records.annual_leaves["pending"]=annual_pending
            leave_records.sick_leaves["pending"]=sick_pending
            leave_records.paid_leaves["pending"]=paid_pending
            leave_records.unpaid_leaves["pending"]=unpaid_pending
            leave_records.hajj_leaves["pending"]=hajj_pending
            leave_summary = {
                "id": leave_records.id,
                "casual_leaves": leave_records.casual_leaves,
                "sick_leaves": leave_records.sick_leaves,
                "annual_leaves": leave_records.annual_leaves,
                "unpaid_leaves": leave_records.unpaid_leaves,
                "hajj_leaves": leave_records.hajj_leaves,
                "paid_leaves": leave_records.paid_leaves,
            }
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if workspace:
            today_activity = TodayActivity(e_email=e_email, workspace=workspace)
            statistics = Statistics(e_email=e_email, workspace=workspace)
            attendance_summary = AttendanceSummary(e_email=e_email, workspace=workspace)
            try:
                punch_timings = employee.objects.get(email=e_email).punch_timings
            except:
                punch_timings = {}
            try:
                company_image = company_data.objects.all()[0].image.url
            except:
                company_image = ""
            try:
                emp_job_title=outsource_employees.objects.get(employee_id=e_email, client_id=workspace).job_title
            except:
                emp_job_title=current_employee.job_title

            employee_details['job_title']=emp_job_title

            payload = {
                "employee_details": employee_details,
                "company_image": company_image,
                "workspaces": workspaces,
                "attendance_summary": attendance_summary,
                "punch_timings": punch_timings,
                "leave_summary": leave_summary,
                "statistics": statistics,
                "today_activity": today_activity,
            }
            return Response(payload, status=status.HTTP_200_OK)

        else:
            today_activity = TodayActivity(e_email=e_email, workspace=talent_email)
            statistics = Statistics(e_email=e_email, workspace=talent_email)
            attendance_summary = AttendanceSummary(
                e_email=e_email, workspace=talent_email
            )
            try:
                punch_timings = employee.objects.get(email=e_email).punch_timings
            except:
                punch_timings = {}
            try:
                company_image = company_data.objects.all()[0].image.url
            except:
                company_image = ""

            employee_details['job_title']=current_employee.job_title
            
            payload = {
                "employee_details": employee_details,
                "company_image": company_image,
                "workspaces": workspaces,
                "attendance_summary": attendance_summary,
                "punch_timings": punch_timings,
                "leave_summary": leave_summary,
                "statistics": statistics,
                "today_activity": today_activity,
            }
            return Response(payload, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Dashboard"],
        manual_parameters=[
            openapi.Parameter(
                "workspace",
                openapi.IN_QUERY,
                description="Specify current client email",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                "check_in",
                openapi.IN_QUERY,
                description="Punch check in",
                type=openapi.TYPE_STRING,
                example="10:00 AM",
            ),
            openapi.Parameter(
                "check_out",
                openapi.IN_QUERY,
                description="Punch check out",
                type=openapi.TYPE_STRING,
                example="10:00 PM",
            ),
            openapi.Parameter(
                "break",
                openapi.IN_QUERY,
                description="Punch break",
                type=openapi.TYPE_STRING,
                example="01:00 PM",
            ),
            openapi.Parameter(
                "resume",
                openapi.IN_QUERY,
                description="Punch resume",
                type=openapi.TYPE_STRING,
                example="02:00 PM",
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
            200: "Successful request",
            400: "Bad Request",
            401: "Unauthorized",
        },
        operation_summary="Endpoint to mark punches.",
        operation_id="1",
    )
    def patch(self, request, *args, **kwargs):
        e_email = request.user
        workspace = request.query_params.get("workspace")
        check_in = request.query_params.get("check_in")
        check_out = request.query_params.get("check_out")
        breaked = request.query_params.get("break")
        resumed = request.query_params.get("resume")
        now = datetime.now()
        if check_in:
            months_timesheet = time_sheet.objects.filter(
                month=now.strftime("%B"),
                employee_id=e_email,
                client_id=workspace,
                year=now.strftime("%Y"),
            )
            if months_timesheet:
                for rec in months_timesheet:

                    if (now.date().strftime("%d-%m-%Y") not in rec.record) or (
                        "check_in" in rec.record[now.date().strftime("%d-%m-%Y")]
                        and rec.record[now.date().strftime("%d-%m-%Y")]["check_in"]
                        == "-"
                    ):
                        rec.record[now.date().strftime("%d-%m-%Y")] = {
                            "check_in": check_in,
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
                        rec.save()
                        return Response(
                            {"message": "Check in punched"}, status=status.HTTP_200_OK
                        )
                    else:
                        return Response({"message":"Check in is already punched"}, status=status.HTTP_200_OK)
            else:
                time_sheet.objects.create(
                    month=now.strftime("%B"),
                    employee_id=e_email,
                    client_id=workspace,
                    year=now.year,
                    record={
                        now.date().strftime("%d-%m-%Y"): {
                            "check_in": check_in,
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
                    },
                )
                return Response(
                    {"message": "Check in punched"}, status=status.HTTP_200_OK
                )

        elif check_out:
            months_timesheet = time_sheet.objects.filter(
                month=now.strftime("%B"),
                employee_id=e_email,
                client_id=workspace,
                year=now.strftime("%Y"),
            )
            if (
                months_timesheet
                and months_timesheet[0].record[now.date().strftime("%d-%m-%Y")][
                    "check_out"
                ]
                == "-"
                and months_timesheet[0].record[now.date().strftime("%d-%m-%Y")][
                    "check_in"
                ]
                != "-"
            ):
                try:
                    emp=employee.objects.get(email=time_sheet.employee_id)
                    check_in=emp.punch_timings["check_in"]
                    check_out=emp.punch_timings["check_out"]
                    req_time=datetime.strptime(check_out, "%I:%M %p")-datetime.strptime(check_in, "%I:%M %p")
                    working_hours=int(req_time.total_seconds()//3600)
                except:
                    working_hours=9
                for rec in months_timesheet:
                    check_in_time = datetime.strptime(rec.record[now.date().strftime("%d-%m-%Y")][
                        "check_in"
                    ], "%I:%M:%S %p")
                    check_out_time = datetime.strptime(
                        check_out, "%I:%M:%S %p"
                    )
                    if check_out_time<check_in_time:
                        check_out_time = check_out_time + timedelta(days=1)

                    hours_worked=check_out_time-check_in_time

                    if hours_worked.total_seconds() // 3600 < working_hours:
                        rec.record[now.date().strftime("%d-%m-%Y")][
                            "check_out"
                        ] = check_out
                        rec.record[now.date().strftime("%d-%m-%Y")]["overtime"] = "0h"
                        rec.record[now.date().strftime("%d-%m-%Y")][
                            "hours_worked"
                        ] = f"{hours_worked.seconds//3600}h {(hours_worked.seconds //60) %60}m"
                        rec.record[now.date().strftime("%d-%m-%Y")]["status"][
                            "Short Duration"
                        ] = True
                        rec.record[now.date().strftime("%d-%m-%Y")]["status"][
                            "Missing"
                        ] = False
                        rec.save()
                        return Response(
                            {"message": "Check out punched"}, status=status.HTTP_200_OK
                        )

                    elif hours_worked.total_seconds() // 3600 >= working_hours:
                        overtime = hours_worked - timedelta(hours=working_hours)
                        overtime_min = (overtime.seconds // 60) % 60
                        overtime_hours = overtime.seconds // 3600
                        rec.record[now.date().strftime("%d-%m-%Y")][
                            "check_out"
                        ] = check_out
                        rec.record[now.date().strftime("%d-%m-%Y")][
                            "hours_worked"
                        ] = f"{hours_worked.seconds//3600}h {(hours_worked.seconds //60) %60}m"
                        rec.record[now.date().strftime("%d-%m-%Y")]["status"][
                            "Short Duration"
                        ] = False
                        rec.record[now.date().strftime("%d-%m-%Y")]["status"][
                            "Missing"
                        ] = False
                        if overtime_hours and overtime_min:
                            over_duration = f"{overtime_hours}h {overtime_min}m"
                        elif overtime_hours and not overtime_min:
                            over_duration = f"{overtime_hours}h"
                        elif not overtime_hours and overtime_min:
                            over_duration = f"{overtime_min}m"
                        else:
                            over_duration = "0h"

                        rec.record[now.date().strftime("%d-%m-%Y")][
                            "overtime"
                        ] = over_duration

                        rec.save()
                        return Response(
                            {"message": "Check out punched"}, status=status.HTTP_200_OK
                        )
            else:
                return Response({"message":"Check out is already punched"}, status=status.HTTP_200_OK)
        elif breaked:
            months_timesheet = time_sheet.objects.filter(
                month=now.strftime("%B"),
                employee_id=e_email,
                client_id=workspace,
                year=now.strftime("%Y"),
            )
            if months_timesheet:
                for rec in months_timesheet:
                    if (
                        now.date().strftime("%d-%m-%Y") in rec.record
                        and "break" not in rec.record[now.date().strftime("%d-%m-%Y")]
                        and (
                            "check_in" in rec.record[now.date().strftime("%d-%m-%Y")]
                            and rec.record[now.date().strftime("%d-%m-%Y")]["check_in"]
                            != "-"
                        )
                    ):
                        rec.record[now.date().strftime("%d-%m-%Y")]["break"] = breaked

                        rec.save()
                        return Response(
                            {"message": "Break punched"}, status=status.HTTP_200_OK
                        )
                    else:
                        return Response({"message":"Break is already punched"}, status=status.HTTP_200_OK)

        elif resumed:
            months_timesheet = time_sheet.objects.filter(
                month=now.strftime("%B"),
                employee_id=e_email,
                client_id=workspace,
                year=now.strftime("%Y"),
            )
            if months_timesheet:
                for rec in months_timesheet:
                    if (
                        now.date().strftime("%d-%m-%Y") in rec.record
                        and "break" in rec.record[now.date().strftime("%d-%m-%Y")]
                        and "resume" not in rec.record[now.date().strftime("%d-%m-%Y")]
                        and (
                            "check_in" in rec.record[now.date().strftime("%d-%m-%Y")]
                            and rec.record[now.date().strftime("%d-%m-%Y")]["check_in"]
                            != "-"
                        )
                    ):
                        rec.record[now.date().strftime("%d-%m-%Y")]["resume"] = resumed

                        rec.save()
                        return Response(
                            {"message": "Resuming punched"}, status=status.HTTP_200_OK
                        )
                    else:
                        return Response({"message":"Resuming is already punched"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid query parameter"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Company_Contract(APIView):
    @swagger_auto_schema(
        tags=["Administration : Contracts Signed : Company contracts"],
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
                            format=openapi.FORMAT_DATE,
                        ),
                    },
                ),
            ),
            204: openapi.Response(description="Empty Record"),
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
                }
                records.append(record)

            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Offshore_Contract(APIView):
    @swagger_auto_schema(
        tags=["Administration : Contracts Signed : Client contracts"],
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
                            format=openapi.FORMAT_DATE,
                        ),
                    },
                ),
            ),
            204: openapi.Response(description="Empty Record"),
            401: openapi.Response(description="Unauthorized"),
        },
        manual_parameters=[
            openapi.Parameter(
                "workspace",
                openapi.IN_QUERY,
                description="Specify current client email",
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
        operation_summary="Endpoint to retrieve offshore contracts.",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        e_email = request.user
        workspace = request.query_params.get("workspace")
        offsh_contract = offshore_contracts.objects.filter(
            employee_id=e_email, client_id=workspace
        )
        if offsh_contract:
            records = []
            for contract in offsh_contract:
                record = {
                    "id": contract.id,
                    "client_id": client.objects.get(email=workspace).client_id,
                    "employee_id": employee.objects.get(email=request.user).employee_id,
                    "contract_name": contract.contract_name,
                    "date": contract.date,
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Leave_Request(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Request : Leave"],
        manual_parameters=[
            openapi.Parameter(
                "workspace",
                openapi.IN_QUERY,
                description="Specify current client email",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                "tab",
                openapi.IN_QUERY,
                description="Status filter (pending, completed, rejected) otherwise all",
                type=openapi.TYPE_STRING,
                enum=["", "pending", "completed", "rejected"],
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
                                "year": openapi.Schema(type=openapi.TYPE_INTEGER),
                            },
                        ),
                        "punch_timings": openapi.Schema(
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
                                "employee_name": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
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
        operation_id="0",
    )
    def get(self, request, *args, **kwargs):
        e_email = request.user
        workspace = request.query_params.get("workspace")
        tab = request.query_params.get("tab")
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        if from_date and to_date:
            from_date_object = parser.parse(from_date)
            to_date_object = parser.parse(to_date)

            pending = leave_request.objects.filter(
                Q(employee_id=e_email, client_id=workspace),
                created_at__date__gte=from_date_object,
                created_at__date__lte=to_date_object,
                status="pending",
            ).count()
            rejected = leave_request.objects.filter(
                Q(employee_id=e_email, client_id=workspace),
                created_at__date__gte=from_date_object,
                created_at__date__lte=to_date_object,
                status="rejected",
            ).count()
            completed = leave_request.objects.filter(
                Q(employee_id=e_email, client_id=workspace),
                created_at__date__gte=from_date_object,
                created_at__date__lte=to_date_object,
                status="completed",
            ).count()
            all = leave_request.objects.filter(
                Q(employee_id=e_email, client_id=workspace),
                created_at__date__gte=from_date_object,
                created_at__date__lte=to_date_object,
            ).count()

            if tab == "pending" or tab == "completed" or tab == "rejected":
                l_request = leave_request.objects.filter(
                    Q(employee_id=e_email, client_id=workspace),
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
                    Q(employee_id=e_email, client_id=workspace),
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
                employee_id=e_email, client_id=workspace, status="pending"
            ).count()
            rejected = leave_request.objects.filter(
                employee_id=e_email, client_id=workspace, status="rejected"
            ).count()
            completed = leave_request.objects.filter(
                employee_id=e_email, client_id=workspace, status="completed"
            ).count()
            all = leave_request.objects.filter(
                employee_id=e_email, client_id=workspace
            ).count()
            try:
                l_balance = leave_balance.objects.get(employee_id=e_email)
                l_balance.casual_leaves["pending"] = leave_request.objects.filter(
                    employee_id=e_email,
                    client_id=workspace,
                    status="pending",
                    leave_type="casual",
                ).count()
                l_balance.sick_leaves["pending"] = leave_request.objects.filter(
                    employee_id=e_email,
                    client_id=workspace,
                    status="pending",
                    leave_type="sick",
                ).count()
                l_balance.annual_leaves["pending"] = leave_request.objects.filter(
                    employee_id=e_email,
                    client_id=workspace,
                    status="pending",
                    leave_type="annual",
                ).count()
                l_balance.unpaid_leaves["pending"] = leave_request.objects.filter(
                    employee_id=e_email,
                    client_id=workspace,
                    status="pending",
                    leave_type="unpaid",
                ).count()
                l_balance.paid_leaves["pending"] = leave_request.objects.filter(
                    employee_id=e_email,
                    client_id=workspace,
                    status="pending",
                    leave_type="paid",
                ).count()
                l_balance.hajj_leaves["pending"] = leave_request.objects.filter(
                    employee_id=e_email,
                    client_id=workspace,
                    status="pending",
                    leave_type="hajj",
                ).count()
                balance_record = {
                    "id": l_balance.id,
                    "casual_leaves": l_balance.casual_leaves,
                    "sick_leaves": l_balance.sick_leaves,
                    "annual_leaves": l_balance.annual_leaves,
                    "unpaid_leaves": l_balance.unpaid_leaves,
                    "paid_leaves": l_balance.paid_leaves,
                    "hajj_leaves": l_balance.hajj_leaves,
                }
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            if tab == "pending" or tab == "completed" or tab == "rejected":
                l_request = leave_request.objects.filter(
                    employee_id=e_email, client_id=workspace, status=tab
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
                    employee_id=e_email, client_id=workspace
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
        tags=["Request : Leave"],
        responses={
            201: openapi.Response(
                description="Request Created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"id": openapi.Schema(type=openapi.TYPE_OBJECT)},
                ),
            ),
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
                enum=["casual", "sick", "annual", "paid", "unpaid", "hajj"],
                required=True,
            ),
            openapi.Parameter(
                name="start_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                example="2024-02-29(Y:M:D)",
                required=True,
            ),
            openapi.Parameter(
                name="end_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                example="2024-02-29(Y:M:D)",
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
                name="attachment", in_=openapi.IN_FORM, type=openapi.TYPE_FILE
            ),
        ],
        operation_summary="Endpoint to create leave request.",
        operation_id="1",
    )
    def post(self, request, *args, **kwargs):
        e_email = request.user.email
        serializer = LeaveRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                result = leave_request.objects.create(
                    employee_id=e_email,
                    client_id=serializer.validated_data["client_id"],
                    leave_type=serializer.validated_data["leave_type"],
                    start_date=serializer.validated_data["start_date"],
                    end_date=serializer.validated_data["end_date"],
                    count=serializer.validated_data["count"],
                    reason=serializer.validated_data["reason"],
                    attachment=request.data.get("attachment"),
                    status="pending",
                )

                emp_data = end_user.objects.get(email=result.employee_id)
                notifications.objects.create(
                    ref_id=result.id,
                    email=result.client_id,
                    notification_type="leave_request",
                    status="added",
                    description=f"{emp_data.username} {result.leave_type} leave request is pending",
                )
                if result.attachment:
                    return Response(
                        {
                            "message": f"{result.leave_type} leave request is pending",
                            "id": result.id,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {
                            "message": f"{result.leave_type} leave request is pending",
                            "id": result.id,
                        },
                        status=status.HTTP_201_CREATED,
                    )
            except ValidationError as e:
                return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Request : Leave"],
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
        operation_id="2",
    )
    def delete(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        try:
            lr = leave_request.objects.get(id=id)
            removed = remove_bucket_file(lr.attachment.name)
            if removed:
                return Response(
                    {"error": str(removed)}, status=status.HTTP_400_BAD_REQUEST
                )
            notifications.objects.get(
                ref_id=lr.id, notification_type="leave_request"
            ).delete()
            lr.delete()
            return Response(
                {"message": "Leave request is successfully deleted"},
                status=status.HTTP_200_OK,
            )
        except leave_request.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Time_Sheet(APIView):
    @swagger_auto_schema(
        tags=["Attendance : Time sheet"],
        manual_parameters=[
            openapi.Parameter(
                "workspace",
                openapi.IN_QUERY,
                description="Specify current client email",
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
                                "year": openapi.Schema(type=openapi.TYPE_INTEGER),
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
                                "role_type": openapi.Schema(type=openapi.TYPE_STRING),
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
        workspace = request.query_params.get("workspace")
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
                Q(employee_id=e_email, client_id=workspace),
                Q(
                    month__gte=month_mapping[from_month],
                    year__gte=from_year,
                )
                & Q(
                    month__lte=month_mapping[to_month],
                    year__lte=to_year,
                ),
            )

            filtered_record = {}
            for record in time_sheet_records:
                for key, value in record.record.items():
                    date = datetime.strptime(key, "%d-%m-%Y")
                    if from_date_object <= date <= to_date_object:
                        filtered_record[key] = value

            if len(filtered_record) > 0:
                try:
                    emp=employee.objects.get(email=e_email)
                    check_in=datetime.strptime(emp.punch_timings["check_in"], "%I:%M %p")
                    check_out=datetime.strptime(emp.punch_timings["check_out"], "%I:%M %p")
                    if check_out<check_in:
                        check_out=check_out+timedelta(days=1)

                    req_time=check_out - check_in
                    working_hours=int(req_time.total_seconds()//3600)
                except employee.DoesNotExist:
                    working_hours=9
                hours_worked = 0
                minutes_worked = 0
                short_duration = 0
                present = 0
                missing_punch = 0
                leaves = 0
                day_off = 0
                absent = 0
                actual_shifts = 0
                for date, rec in filtered_record.items():
                    if rec["check_in"] != "-" and rec["check_out"] != "-":
                        check_in_time = rec["check_in"]
                        check_out_time = rec["check_out"]

                        check_in_datetime = datetime.strptime(check_in_time, "%I:%M:%S %p")
                        check_out_datetime = datetime.strptime(
                            check_out_time, "%I:%M:%S %p"
                        )
                        if check_out_datetime<check_in_datetime:
                            check_out_datetime=check_out_datetime+timedelta(days=1)

                        time_difference = check_out_datetime - check_in_datetime

                        hours_worked += time_difference.seconds // 3600
                        minutes_worked += (time_difference.seconds // 60) % 60

                    if rec["status"]["Short Duration"] == True:
                        short_duration += rec["status"]["Short Duration"]
                    if rec["status"]["Present"] == True:
                        present += rec["status"]["Present"]
                    if rec["status"]["Missing"] == True:
                        missing_punch += rec["status"]["Missing"]
                    if rec["status"]["Full Leave"] == True:
                        leaves += rec["status"]["Full Leave"]
                    if rec["status"]["Day Off"] == True:
                        day_off += rec["status"]["Day Off"]
                    if rec["status"]["Absent"] == True:
                        absent += rec["status"]["Absent"]
                    if (
                        rec["status"]["Day Off"] == False
                        and rec["status"]["Full Leave"] == False
                    ):
                        actual_shifts += 1
                if minutes_worked and hours_worked:
                    worked_hours = f"{hours_worked}h {minutes_worked}m"
                elif hours_worked and not minutes_worked:
                    worked_hours = f"{hours_worked}h"
                elif not hours_worked and minutes_worked:
                    worked_hours = f"{minutes_worked}m"
                else:
                    worked_hours = "0h"

                workable_minutes = actual_shifts * working_hours * 60
                worked_minutes = hours_worked * 60 + minutes_worked
                if workable_minutes > worked_minutes:
                    short_minutes = workable_minutes - worked_minutes
                    short_hours = f"{short_minutes // 60}h {short_minutes%60}m"
                    overtime_hours = "0h 0m"
                elif workable_minutes < worked_minutes:
                    overtime_minutes = worked_minutes - workable_minutes
                    overtime_hours = f"{overtime_minutes // 60}h {overtime_minutes%60}m"
                    short_hours = "0h 0m"
                else:
                    overtime_hours = "0h 0m"
                    short_hours = "0h 0m"

                summary = {
                    "workable_shifts": actual_shifts,
                    "workable_hours": f"{actual_shifts*working_hours}h",
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
                if workspace == talent_email:
                    company_name = "eSpark Talent"
                    location = "Karachi"
                else:
                    try:
                        clnt = client.objects.get(email=workspace)
                        company_name = clnt.company_name
                        location = clnt.address
                    except client.DoesNotExist:
                        company_name = "-"
                        location = "-"
                outsrc_emp = outsource_employees.objects.get(
                    employee_id=e_email, client_id=workspace
                )

                employee_details = {
                    "employee_id": emp.employee_id,
                    "employee_name": emp.first_name + " " + emp.last_name,
                    "company": company_name,
                    "location": location,
                    "role_type": outsrc_emp.role_type,
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
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            try:
                ts_record = time_sheet.objects.get(
                    employee_id=e_email,
                    client_id=workspace,
                    year=datetime.now().year,
                    month=datetime.now().strftime("%B"),
                )
                try:
                    emp=employee.objects.get(email=e_email)
                    check_in=datetime.strptime(emp.punch_timings["check_in"], "%I:%M %p")
                    check_out=datetime.strptime(emp.punch_timings["check_out"], "%I:%M %p")
                    if check_out<check_in:
                        check_out=check_out+timedelta(days=1)

                    req_time=check_out - check_in
                    working_hours=int(req_time.total_seconds()//3600)
                except employee.DoesNotExist:
                    working_hours=9
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
                short_duration = 0
                present = 0
                missing_punch = 0
                leaves = 0
                day_off = 0
                absent = 0
                for date, rec in record["record"].items():
                    if rec["check_in"] != "-" and rec["check_out"] != "-":
                        check_in_time = rec["check_in"]
                        check_out_time = rec["check_out"]
                        check_in_datetime = datetime.strptime(check_in_time, "%I:%M:%S %p")
                        check_out_datetime = datetime.strptime(
                            check_out_time, "%I:%M:%S %p"
                        )

                        if check_out_datetime<check_in_datetime:
                            check_out_datetime=check_out_datetime+timedelta(days=1)
                        time_difference = check_out_datetime - check_in_datetime

                        hours_worked += time_difference.seconds // 3600
                        minutes_worked += (time_difference.seconds // 60) % 60

                    if rec["status"]["Short Duration"] == True:
                        short_duration += rec["status"]["Short Duration"]
                    if rec["status"]["Present"] == True:
                        present += rec["status"]["Present"]
                    if rec["status"]["Missing"] == True:
                        missing_punch += rec["status"]["Missing"]
                    if rec["status"]["Full Leave"] == True:
                        leaves += rec["status"]["Full Leave"]
                    if rec["status"]["Day Off"] == True:
                        day_off += rec["status"]["Day Off"]
                    if rec["status"]["Absent"] == True:
                        absent += rec["status"]["Absent"]

                if minutes_worked and hours_worked:
                    worked_hours = f"{hours_worked}h {minutes_worked}m"
                elif hours_worked and not minutes_worked:
                    worked_hours = f"{hours_worked}h"
                elif not hours_worked and minutes_worked:
                    worked_hours = f"{minutes_worked}m"
                else:
                    worked_hours = "0h"
                current_year = datetime.now().year
                date_today = datetime.now()
                actual_shifts = 0
                for day in range(1, date_today.day + 1):
                    weekday = calendar.weekday(current_year, date_today.month, day)
                    actual_shifts += 1 if weekday < 5 else 0

                workable_minutes = actual_shifts * working_hours * 60
                worked_minutes = hours_worked * 60 + minutes_worked
                if workable_minutes > worked_minutes:
                    short_minutes = workable_minutes - worked_minutes
                    short_hours = f"{short_minutes // 60}h {short_minutes%60}m"
                    overtime_hours = "0h 0m"
                elif workable_minutes < worked_minutes:
                    overtime_minutes = worked_minutes - workable_minutes
                    short_hours = f"{overtime_minutes // 60}h {overtime_minutes%60}m"
                    short_hours = "0h 0m"
                else:
                    overtime_hours = "0h 0m"
                    short_hours = "0h 0m"

                summary = {
                    "workable_shifts": actual_shifts,
                    "workable_hours": f"{actual_shifts*working_hours}h",
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
                if workspace == talent_email:
                    company_name = "eSpark Talent"
                    location = "Karachi"
                else:
                    try:
                        clnt = client.objects.get(email=workspace)
                        company_name = clnt.company_name
                        location = clnt.address
                    except client.DoesNotExist:
                        company_name = "-"
                        location = "-"

                outsrc_emp = outsource_employees.objects.get(
                    employee_id=e_email, client_id=workspace
                )

                employee_details = {
                    "employee_id": emp.employee_id,
                    "employee_name": emp.first_name + " " + emp.last_name,
                    "company": company_name,
                    "location": location,
                    "role_type": outsrc_emp.role_type,
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
        tags=["Attendance : Punch requests"],
        manual_parameters=[
            openapi.Parameter(
                "workspace",
                openapi.IN_QUERY,
                description="Specify current client email",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                "tab",
                openapi.IN_QUERY,
                description="Status filter (pending, completed, rejected) otherwise all",
                type=openapi.TYPE_STRING,
                enum=["", "pending", "completed", "rejected"],
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
                                        example="2024-02-29(Y:M:D)",
                                    ),
                                    "punch_type": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "punch_time": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        example="10:00 AM",
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
        operation_id="0",
    )
    def get(self, request, *args, **kwargs):
        e_email = request.user
        workspace = request.query_params.get("workspace")
        tab = request.query_params.get("tab")
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        if from_date and to_date:
            from_date_object = parser.parse(from_date)
            to_date_object = parser.parse(to_date)

            pending = punch_request.objects.filter(
                Q(employee_id=e_email, client_id=workspace),
                date__gte=from_date_object,
                date__lte=to_date_object,
                status="pending",
            ).count()
            rejected = punch_request.objects.filter(
                Q(employee_id=e_email, client_id=workspace),
                date__gte=from_date_object,
                date__lte=to_date_object,
                status="rejected",
            ).count()
            completed = punch_request.objects.filter(
                Q(employee_id=e_email, client_id=workspace),
                date__gte=from_date_object,
                date__lte=to_date_object,
                status="completed",
            ).count()
            all = punch_request.objects.filter(
                Q(employee_id=e_email, client_id=workspace),
                date__gte=from_date_object,
                date__lte=to_date_object,
            ).count()

            if tab == "pending" or tab == "completed" or tab == "rejected":
                p_request = punch_request.objects.filter(
                    Q(employee_id=e_email, client_id=workspace),
                    date__gte=from_date_object,
                    date__lte=to_date_object,
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
                    Q(employee_id=e_email, client_id=workspace),
                    date__gte=from_date_object,
                    date__lte=to_date_object,
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
                employee_id=e_email, client_id=workspace, status="pending"
            ).count()
            rejected = punch_request.objects.filter(
                employee_id=e_email, client_id=workspace, status="rejected"
            ).count()
            completed = punch_request.objects.filter(
                employee_id=e_email, client_id=workspace, status="completed"
            ).count()
            all = punch_request.objects.filter(
                employee_id=e_email, client_id=workspace
            ).count()
            if tab == "pending" or tab == "completed" or tab == "rejected":
                p_request = punch_request.objects.filter(
                    employee_id=e_email, client_id=workspace, status=tab
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
                    employee_id=e_email, client_id=workspace
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
        tags=["Attendance : Punch requests"],
        responses={
            201: openapi.Response(
                description="Request Created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"id": openapi.Schema(type=openapi.TYPE_OBJECT)},
                ),
            ),
            400: "Bad Request",
            401: "Unauthorized",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "client_id": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
                "punch_type": openapi.Schema(type=openapi.TYPE_STRING),
                "punch_time": openapi.Schema(
                    type=openapi.TYPE_STRING, example="10:00 AM"
                ),
                "date": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    example="2024-02-29(Y:M:D)",
                ),
                "description": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=[
                "client_id",
                "punch_type",
                "punch_time",
                "date",
                "description",
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
        operation_summary="Endpoint to create punch request.",
        operation_id="1",
    )
    def post(self, request, *args, **kwargs):
        e_email = request.user
        serializer = PunchRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                result = punch_request.objects.create(
                    employee_id=e_email,
                    client_id=serializer.validated_data["client_id"],
                    punch_type=serializer.validated_data["punch_type"],
                    punch_time=serializer.validated_data["punch_time"],
                    date=serializer.validated_data["date"],
                    description=serializer.validated_data["description"],
                    status="pending",
                )

                emp_data = end_user.objects.get(email=result.employee_id)
                notifications.objects.create(
                    ref_id=result.id,
                    email=result.client_id,
                    notification_type="punch_request",
                    status="added",
                    description=f"{emp_data.username} {result.punch_type} request is pending",
                )

                return Response(
                    {
                        "message": f"{result.punch_type} request is pending",
                        "id": result.id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Attendance : Punch requests"],
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
        operation_id="2",
    )
    def delete(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        try:
            record = punch_request.objects.get(id=id)
            if record:
                notifications.objects.get(
                    ref_id=record.id, notification_type="punch_request"
                ).delete()
                record.delete()
            return Response(
                {"message": "Punch request is successfully deleted"},
                status=status.HTTP_200_OK,
            )
        except punch_request.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Policies(APIView):
    @swagger_auto_schema(
        tags=["Administration : Policies"],
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
        operation_summary="Endpoint to retrieve employee policies.",
        operation_id=".",
    )
    def get(self, request, *args, **kwargs):
        emp_policies = policy.objects.filter(employee=True)
        policies = []
        for emp_pol in emp_policies:
            record = {
                "id": emp_pol.id,
                "policy_name": emp_pol.policy_name,
            }
            policies.append(record)
        if len(policies) > 0:
            return Response(policies, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
