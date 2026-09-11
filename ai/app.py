from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import shutil
import subprocess
import sys

app = FastAPI(title="Multimodal Smart Attendance AI")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ENTRY_SCRIPT = os.path.join(BASE_DIR, "process_entry_video.py")
EXIT_SCRIPT = os.path.join(BASE_DIR, "process_exit_video.py")
DURATION_SCRIPT = os.path.join(BASE_DIR, "duration_validation.py")


def run_script(script_path, video_path=None):
    command = [sys.executable, script_path]

    if video_path:
        command.append(video_path)

    result = subprocess.run(
        command,
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )

    return {
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


@app.get("/")
def root():
    return {
        "service": "Multimodal Smart Attendance AI",
        "status": "running"
    }


@app.get("/health")
def health():
    trainer_path = os.path.join(BASE_DIR, "trainer", "trainer.yml")

    return {
        "status": "ok",
        "trainer_exists": os.path.exists(trainer_path)
    }


@app.post("/process/entry")
async def process_entry(entry_video: UploadFile = File(...)):
    video_path = os.path.join(
        "/tmp",
        "entry_video.mp4"
    )

    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(entry_video.file, buffer)

        result = run_script(
            ENTRY_SCRIPT,
            video_path
        )

        if result["return_code"] != 0:
            raise HTTPException(
                status_code=500,
                detail=result
            )

        return {
            "message": "Entry video processed successfully",
            "result": result
        }

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


@app.post("/process/exit")
async def process_exit(exit_video: UploadFile = File(...)):
    video_path = os.path.join(
        "/tmp",
        "exit_video.mp4"
    )

    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(exit_video.file, buffer)

        result = run_script(
            EXIT_SCRIPT,
            video_path
        )

        if result["return_code"] != 0:
            raise HTTPException(
                status_code=500,
                detail=result
            )

        return {
            "message": "Exit video processed successfully",
            "result": result
        }

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


@app.post("/process/duration")
def process_duration():
    result = run_script(
        DURATION_SCRIPT
    )

    if result["return_code"] != 0:
        raise HTTPException(
            status_code=500,
            detail=result
        )

    return {
        "message": "Duration validation completed successfully",
        "result": result
    }