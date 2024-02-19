from datetime import datetime, timedelta
import calendar
from .models import *

current_month = datetime.now().strftime("%B")
current_year = datetime.now().year
today = datetime.now().strftime("%d-%m-%Y")
date_today = datetime.now()
current_time = datetime.now().time()
_, last_day = calendar.monthrange(current_year, date_today.month)

total_weekdays = 0

for day in range(1, last_day + 1):
    weekday = calendar.weekday(current_year, date_today.month, day)
    total_weekdays += 1 if weekday < 5 else 0

weekdays_up_to_today = 0
for day in range(1, date_today.day + 1):
    weekday = calendar.weekday(current_year, date_today.month, day)
    weekdays_up_to_today += 1 if weekday < 5 else 0

start_of_week = date_today - timedelta(days=date_today.weekday())
end_of_week = start_of_week + timedelta(days=4)


def TodayActivity(e_email, workspace):
    today_activity = {
        "check_in": "-",
        "check_out": "-",
        "break": "-",
        "resume": "-",
    }
    try:
        time_sheet_record = time_sheet.objects.get(
            employee_id=e_email,
            client_id=workspace,
            month=current_month,
            year=current_year,
        )

        today_activity = {
            "check_in": "-",
            "check_out": "-",
            "break": "-",
            "resume": "-",
        }

        if today in time_sheet_record.record:
            if "check_in" in time_sheet_record.record[today]:
                today_activity["check_in"] = time_sheet_record.record[today]["check_in"]

            if "check_out" in time_sheet_record.record[today]:
                today_activity["check_out"] = time_sheet_record.record[today][
                    "check_out"
                ]

            if "break" in time_sheet_record.record[today]:
                today_activity["break"] = time_sheet_record.record[today]["break"]

            if "resume" in time_sheet_record.record[today]:
                today_activity["resume"] = time_sheet_record.record[today]["resume"]
    except:
        today_activity = {
            "check_in": "-",
            "check_out": "-",
            "break": "-",
            "resume": "-",
        }
    return today_activity


def Statistics(e_email, workspace):
    statistics = {
        "today": 0,
        "this_week": 0,
        "this_month": 0,
        "remaining": total_weekdays * 9,
        "overtime": 0,
    }
    w_hours_worked = 0
    minutes_worked = 0
    try:
        time_sheet_record = time_sheet.objects.get(
            employee_id=e_email,
            client_id=workspace,
            month=current_month,
            year=current_year,
        )

        if (
            today in time_sheet_record.record
            and time_sheet_record.record[today]["check_in"] != "-"
        ):
            check_in_time = datetime.strptime(
                time_sheet_record.record[today]["check_in"], "%H:%M:%S"
            ).time()

            time_difference = datetime.combine(
                datetime.today(), current_time
            ) - datetime.combine(datetime.today(), check_in_time)

            t_hours_worked = round(time_difference.total_seconds() / 3600, 2)
            statistics["today"] = t_hours_worked
        for value in time_sheet_record.record:
            if (
                time_sheet_record.record[value]["check_in"] != "-"
                and time_sheet_record.record[value]["check_out"] != "-"
            ):
                check_in_time = time_sheet_record.record[value]["check_in"]
                check_out_time = time_sheet_record.record[value]["check_out"]
                check_in_datetime = datetime.strptime(check_in_time, "%H:%M:%S")
                check_out_datetime = datetime.strptime(check_out_time, "%H:%M:%S")

                time_difference = check_out_datetime - check_in_datetime
                minutes_worked += time_difference.seconds // 60

            record_date = datetime.strptime(value, "%d-%m-%Y")
            if start_of_week <= record_date <= end_of_week:
                if (
                    time_sheet_record.record[value]["check_in"] != "-"
                    and time_sheet_record.record[value]["check_out"] != "-"
                ):
                    check_in_time = time_sheet_record.record[value]["check_in"]
                    check_out_time = time_sheet_record.record[value]["check_out"]
                    check_in_datetime = datetime.strptime(check_in_time, "%H:%M:%S")
                    check_out_datetime = datetime.strptime(check_out_time, "%H:%M:%S")

                    time_difference = check_out_datetime - check_in_datetime
                    w_hours_worked += time_difference.seconds / 3600

                elif (
                    value == today
                    and time_sheet_record.record[value]["check_in"] != "-"
                    and time_sheet_record.record[value]["check_out"] == "-"
                ):
                    check_in_time = time_sheet_record.record[value]["check_in"]
                    check_in_datetime = datetime.strptime(check_in_time, "%H:%M:%S")
                    time_difference = datetime.combine(
                        datetime.today(), current_time
                    ) - datetime.combine(datetime.today(), check_in_datetime.time())
                    w_hours_worked += time_difference.seconds / 3600

        statistics["this_week"] = round(w_hours_worked, 2)
        m_hours_worked = round(minutes_worked / 60, 2)
        statistics["this_month"] = m_hours_worked
        statistics["remaining"] = round((statistics["remaining"] - m_hours_worked), 2)
        overtime_threshold = weekdays_up_to_today * 9
        if m_hours_worked > overtime_threshold:
            statistics["overtime"] = round((m_hours_worked - overtime_threshold), 2)
    except:
        statistics = {
            "today": 0,
            "this_week": 0,
            "this_month": 0,
            "remaining": total_weekdays * 9,
            "overtime": 0,
        }
    return statistics


def AttendenceSummary(e_email, workspace):
    try:
        time_sheet_record = time_sheet.objects.get(
            employee_id=e_email,
            client_id=workspace,
            month=current_month,
            year=current_year,
        )

        punch_timings = employee.objects.get(email=e_email).punch_timings

        absents = 0
        presents = 0
        missings = 0
        days_off = 0
        overtimes = 0
        break_minutes = 0
        late_arrivals = 0
        short_durations = 0
        actual_shifts = 0
        minutes_worked = 0
        leave = 0

        for value in time_sheet_record.record:
            if (
                time_sheet_record.record[value]["check_in"] != "-"
                and time_sheet_record.record[value]["check_out"] != "-"
            ):
                check_in_time = time_sheet_record.record[value]["check_in"]
                check_out_time = time_sheet_record.record[value]["check_out"]
                check_in_datetime = datetime.strptime(check_in_time, "%H:%M:%S")
                check_out_datetime = datetime.strptime(check_out_time, "%H:%M:%S")
                time_difference = check_out_datetime - check_in_datetime
                if round(time_difference.seconds / 3600) > 9:
                    overtimes += 1

            if (
                "break" in time_sheet_record.record[value]
                and "resume" in time_sheet_record.record[value]
                and time_sheet_record.record[value]["break"] != "-"
                and time_sheet_record.record[value]["resume"] != "-"
            ):
                break_time = time_sheet_record.record[value]["break"]
                resume_time = time_sheet_record.record[value]["resume"]
                break_datetime = datetime.strptime(break_time, "%H:%M:%S")
                resume_datetime = datetime.strptime(resume_time, "%H:%M:%S")
                time_difference = resume_datetime - break_datetime
                break_minutes += round(time_difference.seconds / 60, 2)

            if (time_sheet_record.record[value]["check_in"] != "-") and datetime.strptime(
                time_sheet_record.record[value]["check_in"], "%H:%M:%S"
            ) > datetime.strptime(punch_timings["check_in"], "%H:%M:%S"):
                late_arrivals += 1

            if time_sheet_record.record[value]["status"]["Present"] == True:
                presents += 1

            if time_sheet_record.record[value]["status"]["Absent"] == True:
                absents += 1

            if time_sheet_record.record[value]["status"]["Missing"] == True:
                missings += 1

            if time_sheet_record.record[value]["status"]["Day Off"] == True:
                days_off += 1

            if time_sheet_record.record[value]["status"]["Short Duration"] == True:
                short_durations += 1

            if time_sheet_record.record[value]["status"]["Full Leave"] == True:
                leave += 1

            if (
                time_sheet_record.record[value]["check_in"] != "-"
                and time_sheet_record.record[value]["check_out"] != "-"
            ):
                check_in_time = time_sheet_record.record[value]["check_in"]
                check_out_time = time_sheet_record.record[value]["check_out"]
                check_in_datetime = datetime.strptime(check_in_time, "%H:%M:%S")
                check_out_datetime = datetime.strptime(check_out_time, "%H:%M:%S")

                time_difference = check_out_datetime - check_in_datetime
                minutes_worked += time_difference.seconds // 60

        workable_minutes = actual_shifts * 9 * 60
        worked_minutes = minutes_worked
        if workable_minutes > worked_minutes:
            short_minutes = workable_minutes - worked_minutes
        elif workable_minutes <= worked_minutes:
            short_minutes = "0m"

        attendence_summary = {
            "shifts": weekdays_up_to_today,
            "expected_minutes": workable_minutes,
            "worked_minutes": worked_minutes,
            "short_minutes": short_minutes,
            "leaves": leave,
            "absents":absents,
            "presents":presents,
            "missings":missings,
            "days_off":days_off,
            "overtimes":overtimes,
            "short_durations":short_durations,
            "late_arrivals":late_arrivals,
            "break_minutes":break_minutes,
        }


    except:
        attendence_summary = {}
    return attendence_summary
