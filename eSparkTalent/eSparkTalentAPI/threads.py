from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from .models import *
from datetime import datetime
import time
class Check_Punches(BaseCommand):

    def check_punch(self, *args, **kwargs):
        while True:
            now = datetime.now()
            is_weekend = now.weekday() in [5, 6]

            employees = outsource_employees.objects.all()
            for emp in employees:
                p_time = employee.objects.get(email=emp.employee_id).punch_timings

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
                                        "Present": "-",
                                        "Missing": "-",
                                        "Absent": "-",
                                        "Day Off": True,
                                        "Full Leave": "-",
                                        "Short Duration": "-",
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
                                        "Present": "-",
                                        "Missing": "-",
                                        "Absent": "-",
                                        "Day Off": True,
                                        "Full Leave": "-",
                                        "Short Duration": "-",
                                    },
                                }
                            },
                        )
                if now.strftime("%H:%M:%S") >= p_time["check_in"]:
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
                                        "Present": "-",
                                        "Missing": True,
                                        "Absent": "-",
                                        "Day Off": "-",
                                        "Full Leave": "-",
                                        "Short Duration": "-",
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
                                        "Present": "-",
                                        "Missing": True,
                                        "Absent": "-",
                                        "Day Off": "-",
                                        "Full Leave": "-",
                                        "Short Duration": "-",
                                    },
                                }
                            },
                        )
                if now.strftime("%H:%M:%S") >= p_time["check_out"]:
                    time_record = time_sheet.objects.filter(
                        employee_id=emp.employee_id,
                        client_id=emp.client_id,
                        month=now.strftime("%B"),
                        year=now.strftime("%Y"),
                    )
                    if (
                        now.date().strftime("%d-%m-%Y")
                        in time_record[0].record.keys()
                        and time_record[0].record[now.date().strftime("%d-%m-%Y")]["check_in"] != "-"
                    ):
                        for rec in time_record:
                            rec.record[now.date().strftime("%d-%m-%Y")]['check_out'] = "-"
                            rec.record[now.date().strftime("%d-%m-%Y")]['hours_worked'] = "-"
                            rec.record[now.date().strftime("%d-%m-%Y")]['overtime'] = "-"
                            rec.record[now.date().strftime("%d-%m-%Y")]['status']['Missing'] = True
                            rec.record[now.date().strftime("%d-%m-%Y")]['status']['Short Duration'] = "-"
                            rec.save()
                    elif (
                        now.date().strftime("%d-%m-%Y")
                        in time_record[0].record.keys()
                        and time_record[0].record[now.date().strftime("%d-%m-%Y")]["check_in"] == "-"
                    ):
                        for rec in time_record:
                            rec.record[now.date().strftime("%d-%m-%Y")]['check_out'] = "-"
                            rec.record[now.date().strftime("%d-%m-%Y")]['hours_worked'] = "-"
                            rec.record[now.date().strftime("%d-%m-%Y")]['overtime'] = "-"
                            rec.record[now.date().strftime("%d-%m-%Y")]['status']['Present'] = False
                            rec.record[now.date().strftime("%d-%m-%Y")]['status']['Absent'] = True
                            rec.record[now.date().strftime("%d-%m-%Y")]['status']['Missing'] = False
                            rec.record[now.date().strftime("%d-%m-%Y")]['status']['Short Duration'] = "-"
                            rec.save()
            time.sleep(20)