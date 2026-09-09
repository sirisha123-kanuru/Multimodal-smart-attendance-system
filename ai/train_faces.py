import cv2
import os
import numpy as np

# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset"
)

CASCADE_PATH = os.path.join(
    BASE_DIR,
    "haarcascade_frontalface_default.xml"
)

TRAINER_DIR = os.path.join(
    BASE_DIR,
    "trainer"
)

TRAINER_PATH = os.path.join(
    TRAINER_DIR,
    "trainer.yml"
)

# ==========================================
# CHECK FILES / FOLDERS
# ==========================================

if not os.path.exists(DATASET_DIR):
    print("ERROR: dataset folder not found.")
    exit()

if not os.path.exists(CASCADE_PATH):
    print("ERROR: Haar Cascade file not found.")
    exit()

os.makedirs(TRAINER_DIR, exist_ok=True)

# ==========================================
# LOAD HAAR CASCADE
# ==========================================

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

if face_cascade.empty():
    print("ERROR: Could not load Haar Cascade.")
    exit()

print("Haar Cascade loaded successfully.")

# ==========================================
# PREPARE TRAINING DATA
# ==========================================

faces = []
labels = []

print()
print("======================================")
print("SMART ATTENDANCE - FACE TRAINING")
print("======================================")
print()

# Each folder inside dataset represents
# one student's roll number.
#
# Example:
# dataset/1/
# dataset/2/
# dataset/3/

for student_folder in os.listdir(DATASET_DIR):

    student_path = os.path.join(
        DATASET_DIR,
        student_folder
    )

    if not os.path.isdir(student_path):
        continue

    # Folder name must be roll number
    try:
        roll_number = int(student_folder)
    except ValueError:
        print(
            f"Skipping invalid folder: {student_folder}"
        )
        continue

    print(
        f"Loading samples for Roll Number: {roll_number}"
    )

    sample_count = 0

    for file_name in os.listdir(student_path):

        if not file_name.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):
            continue

        image_path = os.path.join(
            student_path,
            file_name
        )

        image = cv2.imread(
            image_path,
            cv2.IMREAD_GRAYSCALE
        )

        if image is None:
            print(
                f"Could not read: {file_name}"
            )
            continue

        # Images from capture_faces.py are
        # already cropped faces.
        image = cv2.resize(
            image,
            (200, 200)
        )

        # Improve lighting/contrast consistency
        image = cv2.equalizeHist(image)

        faces.append(image)
        labels.append(roll_number)

        sample_count += 1

    print(
        f"Loaded {sample_count} samples."
    )

# ==========================================
# CHECK TRAINING DATA
# ==========================================

print()
print("--------------------------------------")
print(f"Total face samples: {len(faces)}")
print(f"Total labels: {len(labels)}")
print("--------------------------------------")

if len(faces) == 0:
    print("ERROR: No face samples found.")
    exit()

# ==========================================
# TRAIN LBPH MODEL
# ==========================================

print()
print("Training LBPH face recognition model...")

recognizer = cv2.face.LBPHFaceRecognizer_create()

recognizer.train(
    faces,
    np.array(labels)
)

# ==========================================
# SAVE MODEL
# ==========================================

recognizer.write(TRAINER_PATH)

print()
print("======================================")
print("TRAINING COMPLETED SUCCESSFULLY")
print("======================================")
print()
print(f"Faces used: {len(faces)}")
print(
    f"Students trained: {len(set(labels))}"
)
print(
    f"Roll Numbers: {sorted(set(labels))}"
)
print(
    f"Model saved at: {TRAINER_PATH}"
)
print()
print("Step 6B completed.")