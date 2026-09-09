import requests
from datetime import datetime


# ============================================================
# PHASE 11
# SMART ATTENDANCE - DURATION VALIDATION
# ============================================================

ATTENDANCE_API_URL = "http://localhost:8081/attendance"

REQUIRED_DURATION_MINUTES = 45


# ============================================================
# GET ATTENDANCE DATA
# ============================================================

print()
print("========================================")
print("PHASE 11 - DURATION VALIDATION")
print("========================================")
print()

print("Loading attendance records from Spring Boot...")


try:
    response = requests.get(
        ATTENDANCE_API_URL,
        timeout=5
    )

    response.raise_for_status()

    attendance_records = response.json()

except Exception as e:

    print()
    print("ERROR: Cannot connect to Spring Boot.")
    print("Make sure Spring Boot is running on port 8081.")
    print()
    print("Details:", e)

    exit()


print(
    "Attendance records loaded:",
    len(attendance_records)
)

print()


# ============================================================
# TODAY'S RECORDS
# ============================================================

today = datetime.now().strftime("%Y-%m-%d")

today_records = []

for record in attendance_records:

    if record.get("date") == today:

        today_records.append(record)


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
# STUDENT NAME MAPPING
# ============================================================
#
# These IDs come from your current Spring Boot registration:
#
# 15 -> Siri
# 16 -> Praneetha
# 17 -> Leela
#
# This mapping is only used to display the name.
# Attendance itself comes from Spring Boot/MySQL.
# ============================================================

student_names = {

    15: "Siri",

    16: "Praneetha",

    17: "Leela"
}


# ============================================================
# DEMO MODE
# ============================================================
#
# Your uploaded videos are only a few minutes long.
#
# Therefore we cannot calculate a real 45-minute lecture
# duration from the video itself.
#
# For demonstration:
#
# Praneetha -> 30 minutes
# Leela     -> 30 minutes
# Siri      -> 45+ minutes
#
# The ENTRY/EXIT information comes from MySQL.
# Only the demo duration is simulated.
# ============================================================

DEMO_DURATION = {

    15: 45,   # Siri

    16: 30,   # Praneetha

    17: 30    # Leela
}


# ============================================================
# DETERMINE EXIT STATUS
# ============================================================

def has_exit(record):

    exit_time = record.get("exitTime")

    return (
        exit_time is not None
        and
        str(exit_time).strip() != ""
        and
        str(exit_time).lower() != "null"
    )


# ============================================================
# CALCULATE FINAL STATUS
# ============================================================

results = []


for record in today_records:

    student_id = record.get("studentId")

    name = student_names.get(
        student_id,
        f"Student {student_id}"
    )


    entry_exists = (
        record.get("entryTime") is not None
    )


    exit_exists = has_exit(record)


    # --------------------------------------------------------
    # DEMO DURATION
    # --------------------------------------------------------

    duration = DEMO_DURATION.get(
        student_id,
        0
    )


    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    if not entry_exists:

        status = "ABSENT"

        reason = (
            "No entry detected"
        )


    elif exit_exists:

        if duration >= REQUIRED_DURATION_MINUTES:

            status = "PRESENT"

            reason = (
                "Required duration completed"
            )

        else:

            status = "ABSENT"

            reason = (
                "Duration below 45 minutes"
            )


    else:

        # Student entered but no exit detected.
        #
        # In DEMO MODE, we simulate continued
        # classroom presence.

        if duration >= REQUIRED_DURATION_MINUTES:

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


    results.append({

        "studentId": student_id,

        "name": name,

        "entry": "YES" if entry_exists else "NO",

        "exit": "YES" if exit_exists else "NO",

        "duration": duration,

        "status": status,

        "reason": reason
    })


# ============================================================
# SORT BY NAME
# ============================================================

results.sort(
    key=lambda x: x["name"].lower()
)


# ============================================================
# FINAL DEMO TABLE
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

print(
    "-" * 70
)


for result in results:

    if result["duration"] >= 45:

        duration_text = "45+ min"

    else:

        duration_text = (
            f"{result['duration']} min"
        )


    print(
        f"{result['name']:<15}"
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
        f"{result['name']} → "
        f"{result['status']}"
    )

    print(
        f"Reason     → "
        f"{result['reason']}"
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
    "Minimum required duration:",
    REQUIRED_DURATION_MINUTES,
    "minutes"
)

print(
    "Duration >= 45 minutes → PRESENT"
)

print(
    "Duration < 45 minutes  → ABSENT"
)

print()

print("DEMO MODE:")
print(
    "Duration values are simulated because"
)

print(
    "your uploaded videos are short."
)

print()

print("========================================")
print("PHASE 11 COMPLETED")
print("========================================")