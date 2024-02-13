import threading
import time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from .models import *
from datetime import datetime, timedelta


class Check_Punches(BaseCommand):

    # def handle(self, *args, **kwargs):
    #     thread = threading.Thread(target=self.check_punches)
    #     thread.start()

    def check_punch(self, *args, **kwargs):
        # while True:
        now = datetime.now()
        if kwargs:
            if "check_in" in kwargs:
                months_timesheet = time_sheet.objects.filter(
                    month=now.strftime("%B"),
                    employee_id=kwargs["employee"],
                    client_id=kwargs["client"],
                    year=now.strftime("%Y"),
                )
                if months_timesheet:
                    for rec in months_timesheet:
                        print(
                            "check_in" in rec.record[now.date().strftime("%d-%m-%Y")]
                            and rec.record[now.date().strftime("%d-%m-%Y")]["check_in"]
                            == "-"
                        )

                        if (now.date().strftime("%d-%m-%Y") not in rec.record) or (
                            "check_in" in rec.record[now.date().strftime("%d-%m-%Y")]
                            and rec.record[now.date().strftime("%d-%m-%Y")]["check_in"]
                            == "-"
                        ):
                            rec.record[now.date().strftime("%d-%m-%Y")] = {
                                "check_in": kwargs["check_in"],
                                "status": {
                                    "Present": True,
                                    "Missing": False,
                                    "Absent": False,
                                    "Day_Off": False,
                                    "Full Leave": False,
                                    "Short Duration": False,
                                },
                            }
                            rec.save()
                else:
                    time_sheet.objects.create(
                        month=now.strftime("%B"),
                        employee_id=kwargs["employee"],
                        client_id=kwargs["client"],
                        year=now.year,
                        record={
                            now.date().strftime("%d-%m-%Y"): {
                                "check_in": kwargs["check_in"],
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
            elif "breaked" in kwargs:
                months_timesheet = time_sheet.objects.filter(
                    month=now.strftime("%B"),
                    employee_id=kwargs["employee"],
                    client_id=kwargs["client"],
                    year=now.strftime("%Y"),
                )
                if months_timesheet:
                    for rec in months_timesheet:
                        if (
                            now.date().strftime("%d-%m-%Y") in rec.record
                            and "break"
                            not in rec.record[now.date().strftime("%d-%m-%Y")]
                            and months_timesheet[0].record[
                                now.date().strftime("%d-%m-%Y")
                            ]["check_in"]
                            != "-"
                        ):
                            rec.record[now.date().strftime("%d-%m-%Y")]["break"] = (
                                kwargs["breaked"]
                            )

                            rec.save()

            elif "resumed" in kwargs:
                months_timesheet = time_sheet.objects.filter(
                    month=now.strftime("%B"),
                    employee_id=kwargs["employee"],
                    client_id=kwargs["client"],
                    year=now.strftime("%Y"),
                )
                if months_timesheet:
                    for rec in months_timesheet:
                        if (
                            now.date().strftime("%d-%m-%Y") in rec.record
                            and "resume"
                            not in rec.record[now.date().strftime("%d-%m-%Y")]
                            and months_timesheet[0].record[
                                now.date().strftime("%d-%m-%Y")
                            ]["check_in"]
                            != "-"
                        ):
                            rec.record[now.date().strftime("%d-%m-%Y")]["resume"] = (
                                kwargs["resumed"]
                            )

                            rec.save()

            elif "check_out" in kwargs:
                months_timesheet = time_sheet.objects.filter(
                    month=now.strftime("%B"),
                    employee_id=kwargs["employee"],
                    client_id=kwargs["client"],
                    year=now.strftime("%Y"),
                )

                if (
                    months_timesheet
                    and "check_out"
                    not in months_timesheet[0].record[now.date().strftime("%d-%m-%Y")]
                    and months_timesheet[0].record[now.date().strftime("%d-%m-%Y")][
                        "check_in"
                    ]
                    != "-"
                ):
                    check_in_time = months_timesheet[0].record[
                        now.date().strftime("%d-%m-%Y")
                    ]["check_in"]
                    hours_worked = datetime.strptime(
                        kwargs["check_out"], "%H:%M:%S"
                    ) - datetime.strptime(check_in_time, "%H:%M:%S")
                    if hours_worked.total_seconds() // 3600 < 9:
                        months_timesheet[0].record[now.date().strftime("%d-%m-%Y")][
                            "check_out"
                        ] = kwargs["check_out"]
                        months_timesheet[0].record[now.date().strftime("%d-%m-%Y")][
                            "overtime"
                        ] = "0h"
                        months_timesheet[0].record[now.date().strftime("%d-%m-%Y")][
                            "hours_worked"
                        ] = f"{hours_worked.seconds//3600}h {(hours_worked.seconds //60) %60}m"
                        months_timesheet[0].record[now.date().strftime("%d-%m-%Y")][
                            "status"
                        ]["Short Duration"] = True

                        months_timesheet[0].save()

                    elif hours_worked.total_seconds() // 3600 >= 9:
                        overtime = hours_worked - timedelta(hours=9)
                        overtime_min = (overtime.seconds // 60) % 60
                        overtime_hours = overtime.seconds // 3600
                        months_timesheet[0].record[now.date().strftime("%d-%m-%Y")][
                            "check_out"
                        ] = kwargs["check_out"]
                        months_timesheet[0].record[now.date().strftime("%d-%m-%Y")][
                            "hours_worked"
                        ] = f"{hours_worked.seconds//3600}h {(hours_worked.seconds //60) %60}m"
                        months_timesheet[0].record[now.date().strftime("%d-%m-%Y")][
                            "status"
                        ]["Short Duration"] = False
                        if overtime_hours and overtime_min:
                            over_duration = f"{overtime_hours}h {overtime_min}m"
                        elif overtime_hours and not overtime_min:
                            over_duration = f"{overtime_hours}h"
                        elif not overtime_hours and overtime_min:
                            over_duration = f"{overtime_min}m"

                        months_timesheet[0].record[now.date().strftime("%d-%m-%Y")][
                            "overtime"
                        ] = over_duration

                        months_timesheet[0].save()
            else:
                employees = employee.objects.all()
                for emp in employees:
                    time_record = time_sheet.objects.filter(
                        employee_id=emp.email,
                        month=now.strftime("%B"),
                        year=now.strftime("%Y"),
                    )
                    for rec in time_record:
                        if (
                            now.date().strftime("%d-%m-%Y") not in rec.record.keys()
                            and now.strftime("%H:%M:%S")
                            >= emp.punch_timings["check_in"]
                        ):
                            rec.record[now.date().strftime("%d-%m-%Y")] = {
                                "check_in": "-",
                                "status": {
                                    "Missing": True,
                                },
                            }
                            rec.save()
                        if (
                            now.date().strftime("%d-%m-%Y") in rec.record.keys()
                            and now.strftime("%H:%M:%S")
                            >= emp.punch_timings["check_out"]
                        ):
                            if (
                                "check_in"
                                in rec.record[now.date().strftime("%d-%m-%Y")]
                                and rec.record[now.date().strftime("%d-%m-%Y")][
                                    "check_in"
                                ]
                                != False
                            ):
                                rec.record[now.date().strftime("%d-%m-%Y")][
                                    "check_out"
                                ] = False
                                rec.record[now.date().strftime("%d-%m-%Y")][
                                    "status"
                                ] = {
                                    "Missing": True,
                                    "Short Duration": False,
                                    "Present": True,
                                    "Absent": False,
                                    "Day Off": False,
                                    "Full Leave": False,
                                }
                                rec.save()
                            elif (
                                "check_in"
                                in rec.record[now.date().strftime("%d-%m-%Y")]
                                and rec.record[now.date().strftime("%d-%m-%Y")][
                                    "check_in"
                                ]
                                == False
                            ):
                                rec.record[now.date().strftime("%d-%m-%Y")][
                                    "check_out"
                                ] = False
                                rec.record[now.date().strftime("%d-%m-%Y")][
                                    "status"
                                ] = {
                                    "Missing": False,
                                    "Short Duration": False,
                                    "Present": False,
                                    "Absent": True,
                                    "Day Off": False,
                                    "Full Leave": False,
                                }
                                rec.save()

        else:
            employees = employee.objects.all()
            for emp in employees:
                time_record = time_sheet.objects.filter(
                    employee_id=emp.email,
                    month=now.strftime("%B"),
                    year=now.strftime("%Y"),
                )
                for rec in time_record:
                    if (
                        now.date().strftime("%d-%m-%Y") not in rec.record.keys()
                        and now.strftime("%H:%M:%S") >= emp.punch_timings["check_in"]
                    ):
                        rec.record[now.date().strftime("%d-%m-%Y")] = {
                            "check_in": "-",
                            "status": {
                                "Missing": True,
                            },
                        }
                        rec.save()
                    if (
                        now.date().strftime("%d-%m-%Y") in rec.record.keys()
                        and now.strftime("%H:%M:%S") >= emp.punch_timings["check_out"]
                    ):
                        if (
                            "check_in" in rec.record[now.date().strftime("%d-%m-%Y")]
                            and rec.record[now.date().strftime("%d-%m-%Y")]["check_in"]
                            != False
                        ):
                            rec.record[now.date().strftime("%d-%m-%Y")][
                                "check_out"
                            ] = False
                            rec.record[now.date().strftime("%d-%m-%Y")]["status"] = {
                                "Missing": True,
                                "Short Duration": False,
                                "Present": True,
                                "Absent": False,
                                "Day Off": False,
                                "Full Leave": False,
                            }
                            rec.save()
                        elif (
                            "check_in" in rec.record[now.date().strftime("%d-%m-%Y")]
                            and rec.record[now.date().strftime("%d-%m-%Y")]["check_in"]
                            == False
                        ):
                            rec.record[now.date().strftime("%d-%m-%Y")][
                                "check_out"
                            ] = False
                            rec.record[now.date().strftime("%d-%m-%Y")]["status"] = {
                                "Missing": False,
                                "Short Duration": False,
                                "Present": False,
                                "Absent": True,
                                "Day Off": False,
                                "Full Leave": False,
                            }
                            rec.save()

        # time.sleep(3600)
