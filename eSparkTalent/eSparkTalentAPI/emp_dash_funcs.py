from datetime import datetime, timedelta
import calendar
from .models import *


def TodayActivity(e_email, workspace):
    current_month = datetime.now().strftime("%B")
    current_year = datetime.now().year
    today = datetime.now().strftime("%d-%m-%Y")
    date_today = datetime.now()
    _, last_day = calendar.monthrange(current_year, date_today.month)

    total_weekdays = 0

    for day in range(1, last_day + 1):
        weekday = calendar.weekday(current_year, date_today.month, day)
        total_weekdays += 1 if weekday < 5 else 0

    weekdays_up_to_today = 0
    for day in range(1, date_today.day + 1):
        weekday = calendar.weekday(current_year, date_today.month, day)
        weekdays_up_to_today += 1 if weekday < 5 else 0

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

    start_of_week = (date_today - timedelta(days=date_today.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_of_week = (start_of_week + timedelta(days=4)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    statistics = {
        "today": "0/9 hrs",
        "this_week": "0/45 hrs",
        "this_month": f"0/{total_weekdays} hrs",
        "remaining": f"{total_weekdays*9}/{total_weekdays*9} hrs",
        "overtime": "0 hrs",
    }
    w_hours_worked = 0
    minutes_worked = 0
    overtime_threshold = weekdays_up_to_today * 9
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
            and time_sheet_record.record[today]["check_out"] == "-"
        ):
            check_in_time = datetime.strptime(
                time_sheet_record.record[today]["check_in"], "%I:%M:%S %p"
            ).time()

            time_difference = datetime.combine(
                datetime.today(), current_time
            ) - datetime.combine(datetime.today(), check_in_time)

            t_hours_worked = round(time_difference.total_seconds() / 3600, 2)
            statistics["today"] = f"{t_hours_worked}/9 hrs"
        elif (
            today in time_sheet_record.record
            and time_sheet_record.record[today]["check_in"] != "-"
            and time_sheet_record.record[today]["check_out"] != "-"
        ):
            check_in_time = datetime.strptime(
                time_sheet_record.record[today]["check_in"], "%I:%M:%S %p"
            ).time()
            check_out_time = datetime.strptime(
                time_sheet_record.record[today]["check_out"], "%I:%M:%S %p"
            ).time()

            time_difference = datetime.combine(
                datetime.today(), check_out_time
            ) - datetime.combine(datetime.today(), check_in_time)

            t_hours_worked = round(time_difference.total_seconds() / 3600, 2)
            statistics["today"] = f"{t_hours_worked}/9 hrs"
        for value in time_sheet_record.record:
            if (
                time_sheet_record.record[value]["check_in"] != "-"
                and time_sheet_record.record[value]["check_out"] != "-"
            ):
                check_in_time = time_sheet_record.record[value]["check_in"]
                check_out_time = time_sheet_record.record[value]["check_out"]
                check_in_datetime = datetime.strptime(check_in_time, "%I:%M:%S %p")
                check_out_datetime = datetime.strptime(check_out_time, "%I:%M:%S %p")

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
                    check_in_datetime = datetime.strptime(check_in_time, "%I:%M:%S %p")
                    check_out_datetime = datetime.strptime(check_out_time, "%I:%M:%S %p")

                    time_difference = check_out_datetime - check_in_datetime
                    w_hours_worked += time_difference.seconds / 3600

                elif (
                    value == today
                    and time_sheet_record.record[value]["check_in"] != "-"
                    and time_sheet_record.record[value]["check_out"] == "-"
                ):
                    check_in_time = time_sheet_record.record[value]["check_in"]
                    check_in_datetime = datetime.strptime(check_in_time, "%I:%M:%S %p")
                    time_difference = datetime.combine(
                        datetime.today(), current_time
                    ) - datetime.combine(datetime.today(), check_in_datetime.time())
                    w_hours_worked += time_difference.seconds / 3600

        statistics["this_week"] = f"{round(w_hours_worked, 2)}/45 hrs"
        m_hours_worked = round(minutes_worked / 60, 2)
        statistics["this_month"] = f"{m_hours_worked}/{total_weekdays*9} hrs"
        remains = round(((total_weekdays * 9) - m_hours_worked), 2)
        statistics["remaining"] = f"{remains}/{total_weekdays * 9} hrs"
        if m_hours_worked > overtime_threshold:
            overtime = m_hours_worked - overtime_threshold
            statistics["overtime"] = f"{overtime} hrs"
    except:
        statistics = {
            "today": "0/9 hrs",
            "this_week": "0/45 hrs",
            "this_month": f"0/{total_weekdays*9} hrs",
            "remaining": f"{total_weekdays*9}/{total_weekdays*9} hrs",
            "overtime": "0 hrs",
        }
    return statistics


def AttendanceSummary(e_email, workspace):
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

    start_of_week = (date_today - timedelta(days=date_today.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_of_week = (start_of_week + timedelta(days=4)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

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
        minutes_worked = 0
        leave = 0

        for value in time_sheet_record.record:
            if (
                time_sheet_record.record[value]["check_in"] != "-"
                and time_sheet_record.record[value]["check_out"] != "-"
            ):
                check_in_time = time_sheet_record.record[value]["check_in"]
                check_out_time = time_sheet_record.record[value]["check_out"]
                check_in_datetime = datetime.strptime(check_in_time, "%I:%M:%S %p")
                check_out_datetime = datetime.strptime(check_out_time, "%I:%M:%S %p")
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
                break_datetime = datetime.strptime(break_time, "%I:%M:%S %p")
                resume_datetime = datetime.strptime(resume_time, "%I:%M:%S %p")
                time_difference = resume_datetime - break_datetime
                break_minutes += round(time_difference.seconds / 60, 2)

            if (
                time_sheet_record.record[value]["check_in"] != "-"
            ) and datetime.strptime(
                time_sheet_record.record[value]["check_in"], "%I:%M:%S %p"
            ) > datetime.strptime(
                punch_timings["check_in"], "%I:%M %p"
            ):
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
                check_in_datetime = datetime.strptime(check_in_time, "%I:%M:%S %p")
                check_out_datetime = datetime.strptime(check_out_time, "%I:%M:%S %p")

                time_difference = check_out_datetime - check_in_datetime
                minutes_worked += time_difference.seconds // 60

        workable_minutes = weekdays_up_to_today * 9 * 60
        worked_minutes = minutes_worked
        if workable_minutes > worked_minutes:
            short_minutes = workable_minutes - worked_minutes
        elif workable_minutes <= worked_minutes:
            short_minutes = 0

        attendence_summary = {
            "shifts": weekdays_up_to_today,
            "expected_minutes": workable_minutes,
            "worked_minutes": worked_minutes,
            "short_minutes": short_minutes,
            "leaves": leave,
            "absents": absents,
            "presents": presents,
            "missings": missings,
            "days_off": days_off,
            "overtimes": overtimes,
            "short_durations": short_durations,
            "late_arrivals": late_arrivals,
            "break_minutes": break_minutes,
        }

    except:
        attendence_summary = {
            "shifts": 0,
            "expected_minutes": 0,
            "worked_minutes": 0,
            "short_minutes": 0,
            "leaves": 0,
            "absents": 0,
            "presents": 0,
            "missings": 0,
            "days_off": 0,
            "overtimes": 0,
            "short_durations": 0,
            "late_arrivals": 0,
            "break_minutes": 0,
        }
    return attendence_summary