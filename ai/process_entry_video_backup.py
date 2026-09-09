import cv2
import os
import sys
import json
from collections import defaultdict, Counter
from urllib.request import urlopen
from urllib.error import URLError


# ============================================================
# PATHS
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


# ============================================================
# SPRING BOOT API
# ============================================================

STUDENT_API_URL = "http://localhost:8081/students"


# ============================================================
# RECOGNITION SETTINGS
# ============================================================

# LBPH:
# LOWER SCORE = BETTER MATCH

RECOGNITION_THRESHOLD = 85

# Process every 2nd frame
FRAME_SKIP = 2

# Minimum number of observations
MIN_OBSERVATIONS = 5

# Minimum number of votes for stable recognition
MIN_STABLE_VOTES = 5

# Keep recent predictions
HISTORY_SIZE = 15


# ============================================================
# CHECK REQUIRED FILES
# ============================================================

if not os.path.exists(CASCADE_PATH):

    print()
    print("ERROR: Haar Cascade file not found:")
    print(CASCADE_PATH)
    sys.exit()


if not os.path.exists(TRAINER_PATH):

    print()
    print("ERROR: trainer.yml not found.")
    print("Please run:")
    print("python train_faces.py")
    sys.exit()


# ============================================================
# LOAD HAAR CASCADE
# ============================================================

face_cascade = cv2.CascadeClassifier(
    CASCADE_PATH
)

if face_cascade.empty():

    print()
    print("ERROR: Could not load Haar Cascade.")
    sys.exit()


print("Haar Cascade loaded successfully.")


# ============================================================
# LOAD LBPH MODEL
# ============================================================

recognizer = cv2.face.LBPHFaceRecognizer_create()

recognizer.read(
    TRAINER_PATH
)

print("Face recognition model loaded successfully.")


# ============================================================
# LOAD REGISTERED STUDENTS FROM SPRING BOOT
# ============================================================

print()
print("Loading registered students from Spring Boot...")

student_map = {}

try:

    with urlopen(
        STUDENT_API_URL,
        timeout=5
    ) as response:

        data = response.read().decode(
            "utf-8"
        )

        students = json.loads(data)


    # --------------------------------------------------------
    # CREATE FACE LABEL -> STUDENT MAP
    # --------------------------------------------------------

    for student in students:

        face_label = student.get(
            "faceLabel"
        )

        if face_label is None:
            continue

        face_label = int(
            face_label
        )

        student_map[face_label] = {

            "id":
                student.get("id"),

            "name":
                student.get("name"),

            "rollNumber":
                student.get("rollNumber"),

            "email":
                student.get("email"),

            "department":
                student.get("department"),

            "year":
                student.get("year"),

            "section":
                student.get("section")
        }


    print(
        "Registered students loaded:",
        len(student_map)
    )

    print()

    # --------------------------------------------------------
    # DISPLAY REGISTERED STUDENT MAPPING
    # --------------------------------------------------------

    for label, student in sorted(
        student_map.items()
    ):

        print(
            f"Face Label {label} -> "
            f"{student['name']} -> "
            f"Roll Number {student['rollNumber']}"
        )


except URLError:

    print()
    print(
        "ERROR: Cannot connect to Spring Boot."
    )

    print(
        "Make sure Spring Boot is running on port 8081."
    )

    sys.exit()


except Exception as e:

    print()
    print(
        "ERROR: Could not load registered students."
    )

    print(
        "Details:",
        e
    )

    sys.exit()


# ============================================================
# CHECK REGISTERED STUDENTS
# ============================================================

if len(student_map) == 0:

    print()
    print("ERROR: No registered students found.")
    print("Register students in Spring Boot first.")
    sys.exit()


# ============================================================
# VIDEO PATH
# ============================================================

if len(sys.argv) < 2:

    print()
    print(
        "ERROR: Entry video path not provided."
    )

    print()

    print(
        "Example:"
    )

    print(
        'python process_entry_video.py '
        '"C:\\Users\\Sirisha\\Downloads\\entry_video_2.mp4"'
    )

    sys.exit()


VIDEO_PATH = sys.argv[1]


if not os.path.exists(VIDEO_PATH):

    print()
    print(
        "ERROR: Entry video not found:"
    )

    print(
        VIDEO_PATH
    )

    sys.exit()


# ============================================================
# OPEN VIDEO
# ============================================================

video = cv2.VideoCapture(
    VIDEO_PATH
)

if not video.isOpened():

    print()
    print(
        "ERROR: Could not open entry video."
    )

    sys.exit()


fps = video.get(
    cv2.CAP_PROP_FPS
)

if fps <= 0:
    fps = 30


total_frames = int(
    video.get(
        cv2.CAP_PROP_FRAME_COUNT
    )
)


frame_width = int(
    video.get(
        cv2.CAP_PROP_FRAME_WIDTH
    )
)


frame_height = int(
    video.get(
        cv2.CAP_PROP_FRAME_HEIGHT
    )
)


# ============================================================
# START
# ============================================================

print()

print(
    "======================================"
)

print(
    "ENTRY VIDEO - FACE VERIFICATION"
)

print(
    "======================================"
)

print()

print(
    "Video:",
    VIDEO_PATH
)

print(
    "FPS:",
    fps
)

print(
    "Resolution:",
    frame_width,
    "x",
    frame_height
)

print(
    "Total Frames:",
    total_frames
)

print()

print(
    "Recognition threshold:",
    RECOGNITION_THRESHOLD
)

print()

print(
    "Comparing video faces with"
)

print(
    "registered student face data..."
)

print()

print(
    "Press Q to stop."
)

print()


# ============================================================
# RECOGNITION DATA
# ============================================================

# Store predictions for every registered label

prediction_history = defaultdict(list)

score_history = defaultdict(list)

observation_count = defaultdict(int)


# ============================================================
# VERIFIED STUDENTS
# ============================================================

verified_labels = set()


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


    # --------------------------------------------------------
    # FRAME SKIP
    # --------------------------------------------------------

    if frame_number % FRAME_SKIP != 0:
        continue

    processed_frames += 1


    # ========================================================
    # GRAYSCALE
    # ========================================================

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )


    # ========================================================
    # DETECT FACES
    # ========================================================

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.15,
        minNeighbors=5,
        minSize=(70, 70)
    )

    face_detections += len(faces)


    # ========================================================
    # RECOGNIZE EACH FACE
    # ========================================================

    for (
        x,
        y,
        w,
        h
    ) in faces:


        # ----------------------------------------------------
        # EXTRACT FACE
        # ----------------------------------------------------

        face_roi = gray[
            y:y + h,
            x:x + w
        ]


        face_roi = cv2.resize(
            face_roi,
            (200, 200)
        )


        # ----------------------------------------------------
        # LBPH PREDICTION
        # ----------------------------------------------------

        label, confidence = recognizer.predict(
            face_roi
        )

        label = int(label)


        # ====================================================
        # REGISTERED STUDENT CHECK
        # ====================================================

        if (
            label in student_map
            and
            confidence <= RECOGNITION_THRESHOLD
        ):

            student = student_map[
                label
            ]


            # ------------------------------------------------
            # STORE OBSERVATION
            # ------------------------------------------------

            observation_count[
                label
            ] += 1


            prediction_history[
                label
            ].append(label)


            score_history[
                label
            ].append(confidence)


            # ------------------------------------------------
            # LIMIT HISTORY
            # ------------------------------------------------

            if len(
                prediction_history[label]
            ) > HISTORY_SIZE:

                prediction_history[
                    label
                ].pop(0)


                score_history[
                    label
                ].pop(0)


            # ------------------------------------------------
            # STABLE RECOGNITION
            # ------------------------------------------------

            votes = Counter(
                prediction_history[label]
            )

            stable_votes = votes[
                label
            ]


            if (
                observation_count[label]
                >= MIN_OBSERVATIONS
                and
                stable_votes
                >= MIN_STABLE_VOTES
            ):

                verified_labels.add(
                    label
                )


            # ------------------------------------------------
            # DISPLAY STUDENT NAME
            # ------------------------------------------------

            display_name = (
                student["name"]
            )

            display_text = (
                f"{display_name} "
                f"({student['rollNumber']})"
            )

            box_color = (
                0,
                255,
                0
            )


        else:

            display_text = "Unknown"

            box_color = (
                0,
                0,
                255
            )


        # ====================================================
        # DRAW FACE BOX
        # ====================================================

        cv2.rectangle(
            frame,
            (x, y),
            (
                x + w,
                y + h
            ),
            box_color,
            2
        )


        # ====================================================
        # DRAW NAME
        # ====================================================

        cv2.putText(
            frame,
            display_text,
            (
                x,
                y - 10
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            box_color,
            2
        )


        # ====================================================
        # DRAW SCORE
        # ====================================================

        cv2.putText(
            frame,
            f"Score: {confidence:.1f}",
            (
                x,
                y + h + 20
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            box_color,
            1
        )


    # ========================================================
    # SHOW VIDEO
    # ========================================================

    cv2.imshow(
        "Entry Video - Face Verification",
        frame
    )


    # ========================================================
    # PRESS Q TO STOP
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

video.release()

cv2.destroyAllWindows()


# ============================================================
# FINAL VERIFICATION
# ============================================================

print()

print(
    "======================================"
)

print(
    "ENTRY VIDEO VERIFICATION"
)

print(
    "======================================"
)

print()

print(
    "Frames processed:",
    processed_frames
)

print(
    "Face detections:",
    face_detections
)

print(
    "Registered students:",
    len(student_map)
)

print(
    "Verified students:",
    len(verified_labels)
)

print()


# ============================================================
# DISPLAY VERIFIED STUDENTS
# ============================================================

if len(verified_labels) == 0:

    print(
        "NO REGISTERED STUDENT VERIFIED."
    )

    print()

    print(
        "Try increasing the recognition threshold"
    )

    print(
        "or capture more face samples."
    )


else:

    # --------------------------------------------------------
    # IMPORTANT:
    # Sort by FACE LABEL.
    #
    # This is NOT physical entry order.
    # It is only used to display all verified
    # registered students consistently.
    # --------------------------------------------------------

    verified_sorted = sorted(
        verified_labels
    )


    for position, label in enumerate(
        verified_sorted,
        start=1
    ):

        student = student_map[
            label
        ]


        # ----------------------------------------------------
        # BEST LBPH SCORE
        # ----------------------------------------------------

        scores = score_history.get(
            label,
            []
        )


        if len(scores) > 0:

            best_score = min(
                scores
            )

        else:

            best_score = 0


        # ----------------------------------------------------
        # STUDENT RESULT
        # ----------------------------------------------------

        print(
            f"{position} VERIFIED STUDENT"
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
            "Department :",
            student["department"]
        )

        print(
            "Face Label :",
            label
        )

        print(
            "Status     : VERIFIED"
        )

        print(
            "Best Score :",
            f"{best_score:.2f}"
        )

        print(
            "Observations:",
            observation_count[label]
        )

        print(
            "--------------------------------------"
        )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()

print(
    "======================================"
)

print(
    "ENTRY VIDEO VERIFICATION COMPLETED"
)

print(
    "Total Verified Students:",
    len(verified_labels)
)

print(
    "======================================"
)