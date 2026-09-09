import cv2
import os

# ==========================================
# SETTINGS
# ==========================================

ROLL_NUMBER = 3
TOTAL_SAMPLES = 30

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CASCADE_PATH = os.path.join(
    BASE_DIR,
    "haarcascade_frontalface_default.xml"
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset",
    str(ROLL_NUMBER)
)

os.makedirs(DATASET_DIR, exist_ok=True)

# ==========================================
# LOAD FACE DETECTOR
# ==========================================

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

if face_cascade.empty():
    print("ERROR: Could not load Haar Cascade.")
    exit()

print("Haar Cascade loaded successfully.")

# ==========================================
# OPEN CAMERA
# ==========================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open webcam.")
    exit()

count = 0

print()
print("======================================")
print("SMART ATTENDANCE - FACE CAPTURE")
print("======================================")
print()
print(f"Roll Number: {ROLL_NUMBER}")
print(f"Capturing {TOTAL_SAMPLES} face samples.")
print()
print("Look directly at the camera.")
print("Slowly move your face left/right.")
print("Slightly move closer/farther.")
print("Press Q to stop.")
print()

# ==========================================
# CAPTURE LOOP
# ==========================================

while True:

    ret, frame = camera.read()

    if not ret:
        print("ERROR: Could not read camera.")
        break

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(100, 100)
    )

    for (x, y, w, h) in faces:

        face = gray[
            y:y + h,
            x:x + w
        ]

        face = cv2.resize(
            face,
            (200, 200)
        )

        count += 1

        file_path = os.path.join(
            DATASET_DIR,
            f"face_{count}.jpg"
        )

        cv2.imwrite(
            file_path,
            face
        )

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Captured: {count}/{TOTAL_SAMPLES}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # Small delay so images are not identical
        cv2.waitKey(120)

    cv2.imshow(
        "Face Sample Capture",
        frame
    )

    if count >= TOTAL_SAMPLES:
        break

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ==========================================
# CLEANUP
# ==========================================

camera.release()
cv2.destroyAllWindows()

print()
print("======================================")
print("FACE CAPTURE COMPLETED")
print("======================================")
print(f"Roll Number: {ROLL_NUMBER}")
print(f"Samples captured: {count}")
print(f"Saved in: {DATASET_DIR}")