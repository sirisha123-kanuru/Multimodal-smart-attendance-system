import cv2
import os

VIDEO_PATH = "test_video.mp4"

# ---------------------------------
# CHECK VIDEO
# ---------------------------------

if not os.path.exists(VIDEO_PATH):
    print("ERROR: test_video.mp4 was not found.")
    exit()

# ---------------------------------
# LOAD FACE DETECTOR
# ---------------------------------

cascade_path = (
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)

face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    print("ERROR: Face detector could not be loaded.")
    exit()

# ---------------------------------
# OPEN VIDEO
# ---------------------------------

video = cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():
    print("ERROR: Could not open video.")
    exit()

print("Video opened successfully.")
print("Face detection started...")
print("Press Q to stop.")

frame_number = 0
detected_frames = 0

# ---------------------------------
# PROCESS VIDEO
# ---------------------------------

while True:

    success, frame = video.read()

    if not success:
        print("Video processing completed.")
        break

    frame_number += 1

    # Process only every 5th frame
    if frame_number % 5 != 0:
        continue

    # Reduce large video size for faster detection
    height, width = frame.shape[:2]

    max_width = 800

    if width > max_width:
        scale = max_width / width

        frame = cv2.resize(
            frame,
            None,
            fx=scale,
            fy=scale
        )

    # Convert to grayscale
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    # Improve contrast
    gray = cv2.equalizeHist(gray)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(60, 60)
    )

    if len(faces) > 0:
        detected_frames += 1

    # Draw detected faces
    for (x, y, w, h) in faces:

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Face Detected",
            (x, max(y - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    # Display information
    cv2.putText(
        frame,
        f"Faces: {len(faces)}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "Smart Attendance - Face Detection",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("Face detection stopped by user.")
        break


# ---------------------------------
# CLEANUP
# ---------------------------------

video.release()
cv2.destroyAllWindows()

print()
print("----- Detection Summary -----")
print("Frames checked:", frame_number // 5)
print("Frames containing faces:", detected_frames)
print("Step 4 finished.")