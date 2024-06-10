from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from .models import *
from datetime import datetime
import time
from django.db.models import Q


class Check_Punches(BaseCommand):
    def check_punch(self, *args, **kwargs):
        while True:
            now = datetime.now()
            is_weekend = now.weekday() in [5, 6]

            employees = outsource_employees.objects.all()
            for emp in employees:
                p_time = employee.objects.get(email=emp.employee_id).punch_timings
                if p_time:
                    if is_weekend:
                        time_record = time_sheet.objects.filter(
                            employee_id=emp.employee_id,
                            client_id=emp.client_id,
                            month=now.strftime("%B"),
                            year=now.strftime("%Y"),
                        )
                        if time_record:
                            for rec in time_record:
                                if (
                                    now.date().strftime("%d-%m-%Y")
                                    not in rec.record.keys()
                                ):
                                    rec.record[now.date().strftime("%d-%m-%Y")] = {
                                        "check_in": "-",
                                        "check_out": "-",
                                        "hours_worked": "-",
                                        "overtime": "-",
                                        "status": {
                                            "Present": False,
                                            "Missing": False,
                                            "Absent": False,
                                            "Day Off": True,
                                            "Full Leave": False,
                                            "Short Duration": False,
                                        },
                                    }
                                    rec.save()
                        elif not time_record:
                            time_sheet.objects.create(
                                employee_id=emp.employee_id,
                                client_id=emp.client_id,
                                month=now.strftime("%B"),
                                year=now.strftime("%Y"),
                                record={
                                    now.date().strftime("%d-%m-%Y"): {
                                        "check_in": "-",
                                        "check_out": "-",
                                        "hours_worked": "-",
                                        "overtime": "-",
                                        "status": {
                                            "Present": False,
                                            "Missing": False,
                                            "Absent": False,
                                            "Day Off": True,
                                            "Full Leave": False,
                                            "Short Duration": False,
                                        },
                                    }
                                },
                            )
                    elif now >= datetime.strptime(
                        p_time["check_in"], "%I:%M %p"
                    ).replace(
                        year=now.year, month=now.month, day=now.day
                    ) and now < datetime.strptime(
                        p_time["check_out"], "%I:%M %p"
                    ).replace(
                        year=now.year, month=now.month, day=now.day
                    ):
                        leave_records = leave_request.objects.filter(
                            Q(
                                employee_id=emp.employee_id,
                                client_id=emp.client_id,
                                status="completed",
                            ),
                            Q(start_date__lte=now) & Q(end_date__gte=now),
                        )
                        time_record = time_sheet.objects.filter(
                            employee_id=emp.employee_id,
                            client_id=emp.client_id,
                            month=now.strftime("%B"),
                            year=now.strftime("%Y"),
                        )
                        if time_record:
                            for rec in time_record:
                                if (
                                    now.date().strftime("%d-%m-%Y")
                                    not in rec.record.keys()
                                    and leave_records
                                ):
                                    rec.record[now.date().strftime("%d-%m-%Y")] = {
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
                                    rec.save()

                                elif (
                                    now.date().strftime("%d-%m-%Y")
                                    not in rec.record.keys()
                                ):
                                    rec.record[now.date().strftime("%d-%m-%Y")] = {
                                        "check_in": "-",
                                        "check_out": "-",
                                        "hours_worked": "-",
                                        "overtime": "-",
                                        "status": {
                                            "Present": False,
                                            "Missing": True,
                                            "Absent": False,
                                            "Day Off": False,
                                            "Full Leave": False,
                                            "Short Duration": False,
                                        },
                                    }
                                    rec.save()
                        elif not time_record:
                            if leave_records:
                                time_sheet.objects.create(
                                    employee_id=emp.employee_id,
                                    client_id=emp.client_id,
                                    month=now.strftime("%B"),
                                    year=now.strftime("%Y"),
                                    record={
                                        now.date().strftime("%d-%m-%Y"): {
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
                                    },
                                )
                            else:
                                time_sheet.objects.create(
                                    employee_id=emp.employee_id,
                                    client_id=emp.client_id,
                                    month=now.strftime("%B"),
                                    year=now.strftime("%Y"),
                                    record={
                                        now.date().strftime("%d-%m-%Y"): {
                                            "check_in": "-",
                                            "check_out": "-",
                                            "hours_worked": "-",
                                            "overtime": "-",
                                            "status": {
                                                "Present": False,
                                                "Missing": True,
                                                "Absent": False,
                                                "Day Off": False,
                                                "Full Leave": False,
                                                "Short Duration": False,
                                            },
                                        }
                                    },
                                )
                    elif now >= datetime.strptime(
                        p_time["check_out"], "%I:%M %p"
                    ).replace(year=now.year, month=now.month, day=now.day):
                        time_record = time_sheet.objects.filter(
                            employee_id=emp.employee_id,
                            client_id=emp.client_id,
                            month=now.strftime("%B"),
                            year=now.strftime("%Y"),
                        )
                        if time_record and (
                            now.date().strftime("%d-%m-%Y")
                            in time_record[0].record.keys()
                            and time_record[0].record[now.date().strftime("%d-%m-%Y")][
                                "check_in"
                            ]
                            != "-"
                            and time_record[0].record[now.date().strftime("%d-%m-%Y")][
                                "check_out"
                            ]
                            == "-"
                            and time_record[0].record[now.date().strftime("%d-%m-%Y")][
                                "status"
                            ]["Full Leave"]
                            != True
                        ):
                            for rec in time_record:
                                rec.record[now.date().strftime("%d-%m-%Y")][
                                    "check_out"
                                ] = "-"
                                rec.record[now.date().strftime("%d-%m-%Y")][
                                    "hours_worked"
                                ] = "-"
                                rec.record[now.date().strftime("%d-%m-%Y")][
                                    "overtime"
                                ] = "-"
                                rec.record[now.date().strftime("%d-%m-%Y")]["status"][
                                    "Missing"
                                ] = True
                                rec.record[now.date().strftime("%d-%m-%Y")]["status"][
                                    "Short Duration"
                                ] = False
                                rec.save()
                        elif time_record and (
                            now.date().strftime("%d-%m-%Y")
                            in time_record[0].record.keys()
                            and time_record[0].record[now.date().strftime("%d-%m-%Y")][
                                "check_in"
                            ]
                            == "-"
                            and time_record[0].record[now.date().strftime("%d-%m-%Y")][
                                "check_out"
                            ]
                            == "-"
                            and time_record[0].record[now.date().strftime("%d-%m-%Y")][
                                "status"
                            ]["Full Leave"]
                            != True
                        ):
                            for rec in time_record:
                                rec.record[now.date().strftime("%d-%m-%Y")][
                                    "check_out"
                                ] = "-"
                                rec.record[now.date().strftime("%d-%m-%Y")][
                                    "hours_worked"
                                ] = "-"
                                rec.record[now.date().strftime("%d-%m-%Y")][
                                    "overtime"
                                ] = "-"
                                rec.record[now.date().strftime("%d-%m-%Y")]["status"][
                                    "Present"
                                ] = False
                                rec.record[now.date().strftime("%d-%m-%Y")]["status"][
                                    "Absent"
                                ] = True
                                rec.record[now.date().strftime("%d-%m-%Y")]["status"][
                                    "Missing"
                                ] = False
                                rec.record[now.date().strftime("%d-%m-%Y")]["status"][
                                    "Short Duration"
                                ] = False
                                rec.save()
                        elif time_record and (
                            now.date().strftime("%d-%m-%Y")
                            not in time_record[0].record.keys()
                        ):
                            for rec in time_record:
                                rec.record[now.date().strftime("%d-%m-%Y")] = {
                                    "check_in": "-",
                                    "check_out": "-",
                                    "hours_worked": "-",
                                    "overtime": "-",
                                    "status": {
                                        "Present": False,
                                        "Missing": False,
                                        "Absent": True,
                                        "Day Off": False,
                                        "Full Leave": False,
                                        "Short Duration": False,
                                    },
                                }
                                rec.save()
                        elif not time_record:
                            time_sheet.objects.create(
                                employee_id=emp.employee_id,
                                client_id=emp.client_id,
                                month=now.strftime("%B"),
                                year=now.strftime("%Y"),
                                record={
                                    now.date().strftime("%d-%m-%Y"): {
                                        "check_in": "-",
                                        "check_out": "-",
                                        "hours_worked": "-",
                                        "overtime": "-",
                                        "status": {
                                            "Present": False,
                                            "Missing": False,
                                            "Absent": True,
                                            "Day Off": False,
                                            "Full Leave": False,
                                            "Short Duration": False,
                                        },
                                    }
                                },
                            )

            time.sleep(30 * 60)
