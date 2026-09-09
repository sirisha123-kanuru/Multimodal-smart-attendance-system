import cv2
import os

# ==========================================
# PATHS
# ==========================================

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

# ==========================================
# CHECK FILES
# ==========================================

if not os.path.exists(CASCADE_PATH):
    print("ERROR: Haar Cascade file not found.")
    print(CASCADE_PATH)
    exit()

if not os.path.exists(TRAINER_PATH):
    print("ERROR: trainer.yml not found.")
    print("Run train_faces.py first.")
    exit()

# ==========================================
# LOAD FACE DETECTOR
# ==========================================

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

if face_cascade.empty():
    print("ERROR: Could not load Haar Cascade.")
    exit()

print("Haar Cascade loaded successfully.")

# ==========================================
# LOAD FACE RECOGNITION MODEL
# ==========================================

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(TRAINER_PATH)

print("Face recognition model loaded successfully.")

# ==========================================
# STUDENT LABELS
# ==========================================

student_names = {
    1: "Student 1"
}

# ==========================================
# OPEN CAMERA
# ==========================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open webcam.")
    exit()

print()
print("======================================")
print("SMART ATTENDANCE - FACE RECOGNITION")
print("======================================")
print()
print("Webcam opened successfully.")
print("Face recognition started...")
print("Look directly at the camera.")
print("Press Q to stop.")
print()

frame_count = 0
face_count = 0

# Prevent terminal from printing every single frame
last_result = ""

# ==========================================
# RECOGNITION LOOP
# ==========================================

while True:

    ret, frame = camera.read()

    if not ret:
        print("ERROR: Could not read webcam frame.")
        break

    frame_count += 1

    # ======================================
    # GRAYSCALE
    # ======================================

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    # Improve contrast slightly
    gray = cv2.equalizeHist(gray)

    # ======================================
    # FACE DETECTION
    # ======================================

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(60, 60)
    )

    # Display number of detected faces
    cv2.putText(
        frame,
        f"Faces detected: {len(faces)}",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2
    )

    # ======================================
    # PROCESS DETECTED FACES
    # ======================================

    for (x, y, w, h) in faces:

        face_count += 1

        face_roi = gray[
            y:y + h,
            x:x + w
        ]

        # Same size used during training
        face_roi = cv2.resize(
            face_roi,
            (200, 200)
        )

        # ==================================
        # PREDICTION
        # ==================================

        label, confidence = recognizer.predict(
            face_roi
        )

        # IMPORTANT:
        # Smaller LBPH value = better match

        print_result = (
            f"Detected -> Label: {label}, "
            f"Score: {confidence:.2f}"
        )

        # Don't print exactly the same message
        # continuously
        if print_result != last_result:
            print(print_result)
            last_result = print_result

        # ==================================
        # RECOGNIZED
        # ==================================

        if confidence < 70:

            name = student_names.get(
                label,
                f"Student {label}"
            )

            display_text = (
                f"{name} | Roll No: {label}"
            )

            box_color = (0, 255, 0)

        # ==================================
        # UNKNOWN
        # ==================================

        else:

            display_text = (
                f"Unknown | Score: {confidence:.1f}"
            )

            box_color = (0, 0, 255)

        # ==================================
        # RECTANGLE
        # ==================================

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            box_color,
            2
        )

        # ==================================
        # NAME
        # ==================================

        text_y = y - 10

        if text_y < 20:
            text_y = y + 25

        cv2.putText(
            frame,
            display_text,
            (x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            box_color,
            2
        )

        # ==================================
        # SCORE
        # ==================================

        cv2.putText(
            frame,
            f"LBPH Score: {confidence:.1f}",
            (x, y + h + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            box_color,
            2
        )

    # ======================================
    # SHOW CAMERA
    # ======================================

    cv2.imshow(
        "Smart Attendance - Face Recognition",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

# ==========================================
# CLEANUP
# ==========================================

camera.release()
cv2.destroyAllWindows()

print()
print("======================================")
print("RECOGNITION SUMMARY")
print("======================================")
print(f"Frames processed: {frame_count}")
print(f"Face detections: {face_count}")
print()
print("Face recognition stopped.")
print("Step 6 completed.")