import cv2
import os
import sys
import json
from collections import defaultdict, Counter
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CASCADE_PATH = os.path.join(
    BASE_DIR,
    "haarcascade_frontalface_default.xml"
)

TRAINER_PATH = os.path.join(
    BASE_DIR,
    "trainer",
    "trainer.yml"
)

STUDENT_API_URL = "http://localhost:8081/students"
ATTENDANCE_API_URL = "http://localhost:8081/attendance"

RECOGNITION_THRESHOLD = 85
FRAME_SKIP = 2
MIN_OBSERVATIONS = 5
MIN_STABLE_VOTES = 5
HISTORY_SIZE = 15


# ============================================================
# CHECK FILES
# ============================================================

if not os.path.exists(CASCADE_PATH):
    print("ERROR: Haar Cascade not found.")
    print(CASCADE_PATH)
    sys.exit(1)

if not os.path.exists(TRAINER_PATH):
    print("ERROR: trainer.yml not found.")
    print("Run train_faces.py first.")
    sys.exit(1)


# ============================================================
# LOAD FACE MODEL
# ============================================================

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

if face_cascade.empty():
    print("ERROR: Could not load Haar Cascade.")
    sys.exit(1)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(TRAINER_PATH)

print("Haar Cascade loaded successfully.")
print("Face recognition model loaded successfully.")


# ============================================================
# LOAD REGISTERED STUDENTS
# ============================================================

print()
print("Loading registered students from Spring Boot...")

student_map = {}

try:

    with urlopen(
        STUDENT_API_URL,
        timeout=5
    ) as response:

        students = json.loads(
            response.read().decode("utf-8")
        )

    for student in students:

        face_label = student.get("faceLabel")

        if face_label is None:
            continue

        face_label = int(face_label)

        student_map[face_label] = {
            "id": student.get("id"),
            "name": student.get("name"),
            "rollNumber": student.get("rollNumber"),
            "department": student.get("department"),
            "year": student.get("year"),
            "section": student.get("section")
        }

    print(
        "Registered students loaded:",
        len(student_map)
    )

    for label, student in sorted(student_map.items()):

        print(
            f"Face Label {label} -> "
            f"{student['name']} -> "
            f"Roll Number {student['rollNumber']}"
        )

except Exception as e:

    print()
    print("ERROR: Cannot load students.")
    print("Make sure Spring Boot is running on port 8081.")
    print("Details:", e)
    sys.exit(1)


if not student_map:

    print("ERROR: No registered students found.")
    sys.exit(1)


# ============================================================
# VIDEO PATH
# ============================================================

if len(sys.argv) < 2:

    print()
    print("ERROR: Entry video path not provided.")
    print()
    print(
        'Example: python process_entry_video.py '
        '"C:\\Users\\Sirisha\\Desktop\\smart-attendance-ai\\entry_video_2.mp4"'
    )
    sys.exit(1)

VIDEO_PATH = sys.argv[1]

if not os.path.exists(VIDEO_PATH):

    print("ERROR: Entry video not found:")
    print(VIDEO_PATH)
    sys.exit(1)


# ============================================================
# OPEN VIDEO
# ============================================================

video = cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():

    print("ERROR: Could not open entry video.")
    sys.exit(1)

fps = video.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30

total_frames = int(
    video.get(cv2.CAP_PROP_FRAME_COUNT)
)

frame_width = int(
    video.get(cv2.CAP_PROP_FRAME_WIDTH)
)

frame_height = int(
    video.get(cv2.CAP_PROP_FRAME_HEIGHT)
)


# ============================================================
# VIDEO TIME FUNCTION
# ============================================================

def format_video_time(frame_number):

    total_seconds = frame_number / fps

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# ============================================================
# ATTENDANCE FUNCTIONS
# ============================================================

def get_today_attendance(student_id):

    try:

        url = (
            f"{ATTENDANCE_API_URL}"
            f"/student/{student_id}"
        )

        with urlopen(
            url,
            timeout=5
        ) as response:

            records = json.loads(
                response.read().decode("utf-8")
            )

        today = datetime.now().strftime("%Y-%m-%d")

        for record in records:

            if record.get("date") == today:
                return record

        return None

    except Exception as e:

        print(
            "ERROR getting attendance:",
            e
        )

        return None


def create_attendance(student_id, entry_time):

    today = datetime.now().strftime("%Y-%m-%d")

    data = {
        "studentId": student_id,
        "date": today,
        "entryTime": entry_time,
        "exitTime": None,
        "status": "Present"
    }

    body = json.dumps(data).encode("utf-8")

    request = Request(
        ATTENDANCE_API_URL,
        data=body,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:

        with urlopen(
            request,
            timeout=5
        ) as response:

            return json.loads(
                response.read().decode("utf-8")
            )

    except Exception as e:

        print(
            "ERROR creating attendance:",
            e
        )

        return None


def update_entry_time(
    attendance_record,
    entry_time
):

    attendance_id = attendance_record.get("id")

    data = {
        "id": attendance_id,
        "studentId": attendance_record.get("studentId"),
        "date": attendance_record.get("date"),
        "entryTime": entry_time,
        "exitTime": attendance_record.get("exitTime"),
        "status": attendance_record.get("status") or "Present"
    }

    body = json.dumps(data).encode("utf-8")

    url = (
        f"{ATTENDANCE_API_URL}"
        f"/{attendance_id}"
    )

    request = Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json"
        },
        method="PUT"
    )

    try:

        with urlopen(
            request,
            timeout=5
        ) as response:

            return json.loads(
                response.read().decode("utf-8")
            )

    except Exception as e:

        print(
            "ERROR updating attendance:",
            e
        )

        return None


# ============================================================
# START
# ============================================================

print()
print("==============================================")
print("PHASE 9 - ENTRY VIDEO PROCESSING")
print("==============================================")
print()

print("Video:", VIDEO_PATH)
print("FPS:", fps)
print(
    "Resolution:",
    frame_width,
    "x",
    frame_height
)
print("Total Frames:", total_frames)
print()
print("VIDEO TIMESTAMP MODE ENABLED")
print()


# ============================================================
# RECOGNITION DATA
# ============================================================

prediction_history = defaultdict(list)
score_history = defaultdict(list)
observation_count = defaultdict(int)

verified_labels = set()

# First stable detection frame
first_verified_frame = {}


# ============================================================
# FRAME VARIABLES
# ============================================================

frame_number = 0
processed_frames = 0
face_detections = 0


# ============================================================
# PROCESS VIDEO
# ============================================================

while True:

    ret, frame = video.read()

    if not ret:
        break

    frame_number += 1

    if frame_number % FRAME_SKIP != 0:
        continue

    processed_frames += 1

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.15,
        minNeighbors=5,
        minSize=(70, 70)
    )

    face_detections += len(faces)

    for x, y, w, h in faces:

        face_roi = gray[
            y:y + h,
            x:x + w
        ]

        face_roi = cv2.resize(
            face_roi,
            (200, 200)
        )

        label, confidence = recognizer.predict(
            face_roi
        )

        label = int(label)

        if (
            label in student_map
            and confidence <= RECOGNITION_THRESHOLD
        ):

            student = student_map[label]

            observation_count[label] += 1

            prediction_history[label].append(label)
            score_history[label].append(confidence)

            if len(prediction_history[label]) > HISTORY_SIZE:

                prediction_history[label].pop(0)
                score_history[label].pop(0)

            votes = Counter(
                prediction_history[label]
            )

            stable_votes = votes[label]

            if (
                observation_count[label] >= MIN_OBSERVATIONS
                and stable_votes >= MIN_STABLE_VOTES
            ):

                if label not in verified_labels:

                    verified_labels.add(label)

                    first_verified_frame[label] = frame_number

                    video_time = format_video_time(
                        frame_number
                    )

                    print()
                    print(
                        "STUDENT VERIFIED:"
                    )
                    print(
                        "Name       :",
                        student["name"]
                    )
                    print(
                        "Roll Number:",
                        student["rollNumber"]
                    )
                    print(
                        "Student ID :",
                        student["id"]
                    )
                    print(
                        "Video Entry:",
                        video_time
                    )

            display_text = (
                f"{student['name']} "
                f"({student['rollNumber']})"
            )

            box_color = (0, 255, 0)

        else:

            display_text = "Unknown"
            box_color = (0, 0, 255)

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            box_color,
            2
        )

        cv2.putText(
            frame,
            display_text,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            box_color,
            2
        )

        cv2.putText(
            frame,
            f"Score: {confidence:.1f}",
            (x, y + h + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            box_color,
            1
        )

    cv2.putText(
        frame,
        f"Video Time: {format_video_time(frame_number)}",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "Entry Video - Face Verification",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

video.release()
cv2.destroyAllWindows()


# ============================================================
# UPDATE DATABASE
# ============================================================

print()
print("==============================================")
print("ENTRY ATTENDANCE UPDATE")
print("==============================================")
print()


for label in sorted(verified_labels):

    student = student_map[label]

    frame = first_verified_frame[label]

    entry_time = format_video_time(frame)

    existing = get_today_attendance(
        student["id"]
    )

    if existing is None:

        result = create_attendance(
            student["id"],
            entry_time
        )

        if result:

            print(
                f"{student['name']} -> "
                f"ENTRY SAVED -> {entry_time}"
            )

    else:

        result = update_entry_time(
            existing,
            entry_time
        )

        if result:

            print(
                f"{student['name']} -> "
                f"ENTRY UPDATED -> {entry_time}"
            )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("==============================================")
print("ENTRY VIDEO FINAL RESULT")
print("==============================================")
print()

print(
    "Registered students:",
    len(student_map)
)

print(
    "Students detected:",
    len(verified_labels)
)

print()

for label, student in sorted(
    student_map.items()
):

    if label in verified_labels:

        entry_time = format_video_time(
            first_verified_frame[label]
        )

        print(
            f"{student['name']:<15} "
            f"-> PRESENT IN ENTRY VIDEO "
            f"-> {entry_time}"
        )

    else:

        print(
            f"{student['name']:<15} "
            f"-> NOT DETECTED"
        )

print()
print("ENTRY VIDEO PROCESSING COMPLETED.")
print()