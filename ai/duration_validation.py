import requests
import sys
from datetime import datetime


# ============================================================
# WINDOWS UNICODE SUPPORT
# ============================================================

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================
# CONFIGURATION
# ============================================================

ATTENDANCE_API_URL = "https://multimodal-smart-attendance-system-production.up.railway.app/attendance"

# Spring Boot Student API
STUDENTS_API_URL = "https://multimodal-smart-attendance-system-production.up.railway.app/students"

REQUIRED_DURATION = 45


# ============================================================
# PHASE HEADER
# ============================================================

print()
print("========================================")
print("PHASE 11 - DURATION VALIDATION")
print("========================================")
print()


# ============================================================
# GET REGISTERED STUDENTS
# ============================================================

print("Loading registered students from Spring Boot...")

try:

    student_response = requests.get(
        STUDENTS_API_URL,
        timeout=5
    )

    student_response.raise_for_status()

    students_data = student_response.json()

except Exception as e:

    print()
    print("ERROR: Cannot load students from Spring Boot.")
    print("Make sure Spring Boot is running on port 8081.")
    print("Details:", e)

    sys.exit(1)


# ------------------------------------------------------------
# HANDLE POSSIBLE WRAPPED RESPONSE
# ------------------------------------------------------------

if isinstance(students_data, dict):

    if "value" in students_data:
        students = students_data["value"]

    else:
        students = []

else:

    students = students_data


if not isinstance(students, list):

    print()
    print("ERROR: Invalid student data received.")
    sys.exit(1)


print(
    "Registered students:",
    len(students)
)

print()


# ============================================================
# GET ATTENDANCE DATA
# ============================================================

print("Loading attendance records from Spring Boot...")

try:

    attendance_response = requests.get(
        ATTENDANCE_API_URL,
        timeout=5
    )

    attendance_response.raise_for_status()

    records = attendance_response.json()

except Exception as e:

    print()
    print("ERROR: Cannot connect to attendance API.")
    print("Make sure Spring Boot is running on port 8081.")
    print("Details:", e)

    sys.exit(1)


# ============================================================
# HANDLE ATTENDANCE RESPONSE
# ============================================================

if isinstance(records, dict):

    if "value" in records:
        records = records["value"]

    else:
        records = []


if not isinstance(records, list):

    print()
    print("ERROR: Invalid attendance data received.")
    sys.exit(1)


print(
    "Attendance records loaded:",
    len(records)
)

print()


# ============================================================
# DETERMINE PROCESSING DATE
# ============================================================

# Prefer today's date.
today = datetime.now().strftime("%Y-%m-%d")


# Check whether today's records exist.
today_records = [
    record
    for record in records
    if record.get("date") == today
]


# ------------------------------------------------------------
# IF TODAY HAS NO RECORDS
# ------------------------------------------------------------

# This is not necessarily an error anymore.
#
# A newly registered student may have no attendance record.
#
# We still need to mark that student ABSENT.

print(
    "Processing attendance date:",
    today
)

print(
    "Attendance records for today:",
    len(today_records)
)

print()


# ============================================================
# STUDENT NAME HELPER
# ============================================================

def get_student_id(student):

    value = student.get("id")

    if value is None:
        value = student.get("studentId")

    return value


def get_student_name(student):

    name = student.get("name")

    if name is None or str(name).strip() == "":
        student_id = get_student_id(student)

        return f"Student {student_id}"

    return name


# ============================================================
# DEMO DURATION
# ============================================================

# IMPORTANT:
#
# Your uploaded videos are only 3:17.
#
# Therefore actual 45-minute classroom duration cannot
# currently be measured from these short videos.
#
# We keep DEMO MODE for the moment.
#
# IMPORTANT:
# Unknown/new students are NOT included here.
#
# Their absence is decided from the fact that they have
# no entry attendance record.

demo_duration = {
    15: 45,
    16: 30,
    17: 30
}


# ============================================================
# CHECK EXIT
# ============================================================

def has_exit(record):

    exit_time = record.get("exitTime")

    return (
        exit_time is not None
        and str(exit_time).strip() != ""
        and str(exit_time).lower() != "null"
    )


# ============================================================
# UPDATE EXISTING ATTENDANCE
# ============================================================

def update_attendance_status(record, status):

    record_id = record.get("id")

    if record_id is None:

        print(
            "WARNING: Attendance record has no ID."
        )

        return False


    update_url = (
        f"{ATTENDANCE_API_URL}/{record_id}"
    )


    update_data = {

        "id": record.get("id"),

        "studentId": record.get("studentId"),

        "date": record.get("date"),

        "entryTime": record.get("entryTime"),

        "exitTime": record.get("exitTime"),

        "status": status
    }


    try:

        update_response = requests.put(

            update_url,

            json=update_data,

            timeout=5
        )


        update_response.raise_for_status()


        print(
            f"Database updated -> "
            f"Record ID {record_id} -> {status}"
        )


        return True


    except Exception as e:

        print(
            f"ERROR updating Record ID "
            f"{record_id}: {e}"
        )

        return False


# ============================================================
# CREATE ABSENT ATTENDANCE FOR MISSING STUDENT
# ============================================================

def create_absent_record(student_id, date):

    absent_data = {

        "studentId": student_id,

        "date": date,

        "entryTime": None,

        "exitTime": None,

        "status": "ABSENT"
    }


    try:

        response = requests.post(

            ATTENDANCE_API_URL,

            json=absent_data,

            timeout=5
        )


        response.raise_for_status()


        created_record = response.json()


        print(
            f"Database created -> "
            f"Student ID {student_id} -> ABSENT"
        )


        return created_record


    except Exception as e:

        print(
            f"ERROR creating ABSENT record "
            f"for Student ID {student_id}: {e}"
        )

        return None


# ============================================================
# BUILD ATTENDANCE MAP
# ============================================================

attendance_by_student = {}


for record in today_records:

    student_id = record.get("studentId")

    if student_id is not None:

        attendance_by_student[student_id] = record


# ============================================================
# PROCESS ALL REGISTERED STUDENTS
# ============================================================

results = []


for student in students:

    student_id = get_student_id(student)

    name = get_student_name(student)


    if student_id is None:

        print(
            f"WARNING: Student '{name}' "
            f"does not have an ID."
        )

        continue


    # ========================================================
    # CASE 1:
    # STUDENT NOT FOUND IN TODAY'S ATTENDANCE
    # ========================================================

    if student_id not in attendance_by_student:

        print()
        print(
            f"{name} -> NOT DETECTED IN ENTRY VIDEO"
        )

        print(
            f"{name} -> ABSENT"
        )


        # ----------------------------------------------------
        # CREATE ABSENT RECORD
        # ----------------------------------------------------

        new_record = create_absent_record(
            student_id,
            today
        )


        database_updated = (
            new_record is not None
        )


        results.append({

            "id": (
                new_record.get("id")
                if new_record
                else None
            ),

            "studentId": student_id,

            "name": name,

            "entry": "NO",

            "exit": "NO",

            "duration": 0,

            "status": "ABSENT",

            "reason": "Student not detected in entry video",

            "databaseUpdated": database_updated
        })


        continue


    # ========================================================
    # CASE 2:
    # STUDENT HAS ATTENDANCE RECORD
    # ========================================================

    record = attendance_by_student[student_id]


    # --------------------------------------------------------
    # ENTRY
    # --------------------------------------------------------

    entry_exists = (
        record.get("entryTime") is not None
    )


    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    exit_exists = has_exit(record)


    # --------------------------------------------------------
    # DEMO DURATION
    # --------------------------------------------------------

    duration = demo_duration.get(
        student_id,
        0
    )


    # ========================================================
    # FINAL ATTENDANCE DECISION
    # ========================================================

    if not entry_exists:

        status = "ABSENT"

        reason = "No entry detected"


    elif exit_exists:

        if duration >= REQUIRED_DURATION:

            status = "PRESENT"

            reason = "Required duration completed"

        else:

            status = "ABSENT"

            reason = "Duration below 45 minutes"


    else:

        # Student entered but did not appear
        # in the exit video.
        #
        # DEMO MODE:
        # Treat student as still inside.

        if duration >= REQUIRED_DURATION:

            status = "PRESENT"

            reason = (
                "45+ minutes verified "
                "and still inside the classroom"
            )

        else:

            status = "ABSENT"

            reason = (
                "Required duration not completed"
            )


    # ========================================================
    # UPDATE DATABASE
    # ========================================================

    database_updated = update_attendance_status(

        record,

        status
    )


    # ========================================================
    # SAVE RESULT
    # ========================================================

    results.append({

        "id": record.get("id"),

        "studentId": student_id,

        "name": name,

        "entry": (
            "YES"
            if entry_exists
            else "NO"
        ),

        "exit": (
            "YES"
            if exit_exists
            else "NO"
        ),

        "duration": duration,

        "status": status,

        "reason": reason,

        "databaseUpdated": database_updated
    })


# ============================================================
# FINAL RESULT TABLE
# ============================================================

print()
print("========================================")
print("SMART ATTENDANCE - FINAL RESULT")
print("========================================")
print()


print(
    f"{'Student':<18}"
    f"{'Entry':<10}"
    f"{'Exit':<10}"
    f"{'Duration':<15}"
    f"Status"
)


print("-" * 75)


for result in results:

    if result["duration"] >= REQUIRED_DURATION:

        duration_text = "45+ min"

    else:

        duration_text = (
            f"{result['duration']} min"
        )


    print(

        f"{result['name']:<18}"

        f"{result['entry']:<10}"

        f"{result['exit']:<10}"

        f"{duration_text:<15}"

        f"{result['status']}"
    )


# ============================================================
# DETAILED RESULT
# ============================================================

print()
print("========================================")
print("FINAL ATTENDANCE RESULT")
print("========================================")
print()


for result in results:

    print(
        f"{result['name']} -> "
        f"{result['status']}"
    )


    print(
        f"Entry      -> "
        f"{result['entry']}"
    )


    print(
        f"Exit       -> "
        f"{result['exit']}"
    )


    print(
        f"Duration   -> "
        f"{result['duration']} minutes"
    )


    print(
        f"Reason     -> "
        f"{result['reason']}"
    )


    if result["databaseUpdated"]:

        print(
            "Database   -> UPDATED"
        )

    else:

        print(
            "Database   -> UPDATE FAILED"
        )


    print()


# ============================================================
# ATTENDANCE COUNTS
# ============================================================

present_count = sum(
    1
    for result in results
    if result["status"].upper() == "PRESENT"
)


absent_count = sum(
    1
    for result in results
    if result["status"].upper() == "ABSENT"
)


print("========================================")
print("ATTENDANCE SUMMARY")
print("========================================")
print()


print(
    f"Total Registered Students -> "
    f"{len(students)}"
)


print(
    f"Present                  -> "
    f"{present_count}"
)


print(
    f"Absent                   -> "
    f"{absent_count}"
)


print()


# ============================================================
# RULE
# ============================================================

print("========================================")
print("ATTENDANCE RULE")
print("========================================")
print()


print(
    "Student not detected in entry -> ABSENT"
)


print(
    "Duration >= 45 minutes -> PRESENT"
)


print(
    "Duration < 45 minutes -> ABSENT"
)


print()


# ============================================================
# DEMO NOTE
# ============================================================

print("NOTE:")

print(
    "Duration is currently DEMO MODE "
    "because the uploaded videos are only 3:17."
)


print(
    "The registered-student absence check "
    "is NOT simulated."
)


print(
    "A student who is not detected in the "
    "entry video is automatically marked ABSENT."
)


print()


print("========================================")
print("PHASE 11 COMPLETED")
print("========================================")
