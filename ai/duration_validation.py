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

ATTENDANCE_API_URL = (
    "https://multimodal-smart-attendance-system-production.up.railway.app/attendance"
)

STUDENTS_API_URL = (
    "https://multimodal-smart-attendance-system-production.up.railway.app/students"
)

# ============================================================
# DEMO ATTENDANCE LOGIC
# ============================================================
#
# This project uses DEMO MODE because the uploaded videos
# are only a few minutes long.
#
# DEMO RULE:
#
# Entry YES + Exit NO  -> PRESENT
# Entry YES + Exit YES -> ABSENT
# Entry NO             -> ABSENT
#
# Therefore:
#
# Student enters and is NOT seen in exit video:
# They are considered STILL INSIDE -> PRESENT
#
# No actual 45-minute calculation is performed.
#
# ============================================================


API_TIMEOUT = 15


# ============================================================
# PHASE HEADER
# ============================================================

print()
print("========================================")
print("PHASE 11 - DEMO ATTENDANCE VALIDATION")
print("========================================")
print()


# ============================================================
# GET REGISTERED STUDENTS
# ============================================================

print("Loading registered students from Spring Boot...")

try:

    student_response = requests.get(
        STUDENTS_API_URL,
        timeout=API_TIMEOUT
    )

    student_response.raise_for_status()

    students_data = student_response.json()

except Exception as e:

    print()
    print("ERROR: Cannot load students from Spring Boot.")
    print("Details:", e)

    sys.exit(1)


# ============================================================
# HANDLE POSSIBLE WRAPPED RESPONSE
# ============================================================

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
        timeout=API_TIMEOUT
    )

    attendance_response.raise_for_status()

    records = attendance_response.json()

except Exception as e:

    print()
    print("ERROR: Cannot connect to attendance API.")
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

today = datetime.now().strftime("%Y-%m-%d")


print(
    "Processing attendance date:",
    today
)


# ============================================================
# TODAY'S RECORDS
# ============================================================

today_records = [
    record
    for record in records
    if record.get("date") == today
]


print(
    "Attendance records for today:",
    len(today_records)
)

print()


# ============================================================
# STUDENT HELPERS
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
# UPDATE ATTENDANCE STATUS
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

            timeout=API_TIMEOUT
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
# CREATE ABSENT RECORD
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

            timeout=API_TIMEOUT
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
    # STUDENT NOT FOUND IN ATTENDANCE
    # ========================================================

    if student_id not in attendance_by_student:

        print()

        print(
            f"{name} -> NOT DETECTED IN ENTRY VIDEO"
        )

        print(
            f"{name} -> ABSENT"
        )


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

            "duration": "N/A",

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
    # CHECK ENTRY
    # --------------------------------------------------------

    entry_exists = (
        record.get("entryTime") is not None
        and str(record.get("entryTime")).strip() != ""
    )


    # --------------------------------------------------------
    # CHECK EXIT
    # --------------------------------------------------------

    exit_exists = has_exit(record)


    # ========================================================
    # DEMO ATTENDANCE DECISION
    # ========================================================

    if not entry_exists:

        status = "ABSENT"

        reason = "No entry detected"


    elif not exit_exists:

        # ====================================================
        # STUDENT ENTERED BUT DID NOT EXIT
        # ====================================================
        #
        # DEMO RULE:
        # Student is still inside the classroom.
        # Therefore mark PRESENT.
        #

        status = "PRESENT"

        reason = (
            "Entry detected and no exit detected - "
            "student is still inside"
        )


    else:

        # ====================================================
        # STUDENT ENTERED AND EXITED
        # ====================================================
        #
        # DEMO RULE:
        # Student has both entry and exit.
        # For this demonstration, mark ABSENT.
        #

        status = "ABSENT"

        reason = (
            "Entry and exit detected - "
            "demo rule marks ABSENT"
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

        "duration": "N/A",

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

    print(

        f"{result['name']:<18}"

        f"{result['entry']:<10}"

        f"{result['exit']:<10}"

        f"{result['duration']:<15}"

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
        f"{result['duration']}"
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
# DEMO ATTENDANCE RULE
# ============================================================

print("========================================")
print("DEMO ATTENDANCE RULE")
print("========================================")
print()


print(
    "Entry YES + Exit NO  -> PRESENT"
)


print(
    "Entry YES + Exit YES -> ABSENT"
)


print(
    "Entry NO             -> ABSENT"
)


print()


# ============================================================
# DEMO NOTE
# ============================================================

print("NOTE:")


print(
    "This project uses DEMO attendance logic."
)


print(
    "Actual 45-minute duration is NOT calculated."
)


print(
    "A student detected at entry but not at exit "
    "is considered STILL INSIDE and marked PRESENT."
)


print()


print("========================================")
print("PHASE 11 COMPLETED")
print("========================================")