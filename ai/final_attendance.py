import requests
from datetime import datetime


# ============================================================
# FINAL ATTENDANCE INTEGRATION
# ============================================================

ATTENDANCE_API_URL = "http://localhost:8081/attendance"

REQUIRED_DURATION_MINUTES = 45


# ============================================================
# STUDENT INFORMATION
# ============================================================

STUDENTS = {
    15: "Siri",
    16: "Praneetha",
    17: "Leela"
}


# ============================================================
# DEMO DURATION
# ============================================================
#
# IMPORTANT:
# Your current entry/exit videos are only 3:17.
# Therefore real 45-minute duration cannot be measured
# from these videos.
#
# For the current DEMO:
#
# Siri      -> 45+ minutes
# Praneetha -> 30 minutes
# Leela     -> 30 minutes
#
# Later, this section will be replaced by actual
# elapsed-time/re-verification data.
# ============================================================

DEMO_DURATION = {
    15: 45,
    16: 30,
    17: 30
}


# ============================================================
# GET ATTENDANCE FROM SPRING BOOT
# ============================================================

def get_attendance():

    print()
    print("Loading attendance records from Spring Boot...")

    try:

        response = requests.get(
            ATTENDANCE_API_URL,
            timeout=5
        )

        response.raise_for_status()

        records = response.json()

        print(
            "Attendance records loaded:",
            len(records)
        )

        return records

    except requests.exceptions.ConnectionError:

        print()
        print("ERROR: Cannot connect to Spring Boot.")
        print("Make sure Spring Boot is running on port 8081.")
        return None

    except Exception as e:

        print()
        print("ERROR while loading attendance:")
        print(e)
        return None


# ============================================================
# CHECK EXIT TIME
# ============================================================

def has_exit(record):

    exit_time = record.get("exitTime")

    if exit_time is None:
        return False

    if str(exit_time).strip() == "":
        return False

    if str(exit_time).lower() == "null":
        return False

    return True


# ============================================================
# MAIN
# ============================================================

print()
print("========================================")
print("SMART ATTENDANCE - FINAL INTEGRATION")
print("========================================")
print()


records = get_attendance()

if records is None:
    exit()


# ============================================================
# TODAY'S RECORDS
# ============================================================

today = datetime.now().strftime("%Y-%m-%d")

today_records = [
    record
    for record in records
    if record.get("date") == today
]


print(
    "Today's attendance records:",
    len(today_records)
)

print()


if len(today_records) == 0:

    print("No attendance records found for today.")
    print("Run the entry video first.")

    exit()


# ============================================================
# CREATE RECORD LOOKUP
# ============================================================

attendance_by_student = {}

for record in today_records:

    student_id = record.get("studentId")

    attendance_by_student[student_id] = record


# ============================================================
# FINAL RESULTS
# ============================================================

results = []


for student_id, student_name in STUDENTS.items():

    record = attendance_by_student.get(student_id)


    # --------------------------------------------------------
    # ENTRY
    # --------------------------------------------------------

    if record is None:

        entry = "NO"

        exit_status = "NO"

        duration = 0

        status = "ABSENT"

        reason = "No entry record found"


    else:

        entry_time = record.get("entryTime")

        entry = (
            "YES"
            if entry_time is not None
            else "NO"
        )


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if has_exit(record):

            exit_status = "YES"

        else:

            exit_status = "NO"


        # ----------------------------------------------------
        # DEMO DURATION
        # ----------------------------------------------------

        duration = DEMO_DURATION.get(
            student_id,
            0
        )


        # ----------------------------------------------------
        # FINAL STATUS
        # ----------------------------------------------------

        if entry == "NO":

            status = "ABSENT"

            reason = "Student did not enter"


        elif duration >= REQUIRED_DURATION_MINUTES:

            status = "PRESENT"

            if exit_status == "NO":

                reason = (
                    "45+ minutes completed; "
                    "student still inside"
                )

            else:

                reason = (
                    "45+ minutes completed"
                )


        else:

            status = "ABSENT"

            reason = (
                "Student left before "
                "45-minute requirement"
            )


    results.append({

        "student_id": student_id,

        "name": student_name,

        "entry": entry,

        "exit": exit_status,

        "duration": duration,

        "status": status,

        "reason": reason
    })


# ============================================================
# FINAL DASHBOARD TABLE
# ============================================================

print()
print("========================================")
print("SMART ATTENDANCE - FINAL DEMO")
print("========================================")
print()

print(
    f"{'Student':<15}"
    f"{'Entry':<10}"
    f"{'Exit':<10}"
    f"{'Duration':<15}"
    f"Status"
)

print("-" * 70)


for result in results:

    if result["duration"] >= 45:

        duration_text = "45+ min"

    else:

        duration_text = "<45 min"


    print(
        f"{result['name']:<15}"
        f"{result['entry']:<10}"
        f"{result['exit']:<10}"
        f"{duration_text:<15}"
        f"{result['status']}"
    )


# ============================================================
# DETAILED RESULTS
# ============================================================

print()
print("========================================")
print("DETAILED ATTENDANCE RESULT")
print("========================================")
print()


for result in results:

    print(
        f"Name       : {result['name']}"
    )

    print(
        f"Entry      : {result['entry']}"
    )

    print(
        f"Exit       : {result['exit']}"
    )

    if result["duration"] >= 45:

        print(
            "Duration   : 45+ min"
        )

    else:

        print(
            f"Duration   : {result['duration']} min"
        )

    print(
        f"Status     : {result['status']}"
    )

    print(
        f"Reason     : {result['reason']}"
    )

    print("----------------------------------------")


# ============================================================
# DEMO NOTICE
# ============================================================

print()
print("========================================")
print("DEMO MODE INFORMATION")
print("========================================")
print()

print(
    "Entry and exit information comes from"
)

print(
    "the actual Spring Boot/MySQL records."
)

print()

print(
    "Duration is currently simulated because"
)

print(
    "the uploaded videos are only 3:17."
)

print()

print(
    "For the final real-time system, duration"
)

print(
    "will come from actual elapsed time and"
)

print(
    "periodic face re-verification."
)

print()
print("========================================")
print("FINAL ATTENDANCE PROCESSING COMPLETED")
print("========================================")