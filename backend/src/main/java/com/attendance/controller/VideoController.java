package com.attendance.controller;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/videos")
@CrossOrigin(origins = {
        "http://localhost:5173",
        "http://localhost:5174",
        "https://multimodal-smart-attendance-system.vercel.app"
})
public class VideoController {

    private static final String ENTRY_FOLDER = "uploads/entry/";
    private static final String EXIT_FOLDER = "uploads/exit/";

    // Python project
    private static final String AI_PROJECT =
            "C:\\Users\\Sirisha\\Desktop\\smart-attendance-ai";

    // Python inside your virtual environment
    private static final String PYTHON =
            AI_PROJECT + "\\venv\\Scripts\\python.exe";

    // Python scripts
    private static final String ENTRY_SCRIPT =
            AI_PROJECT + "\\process_entry_video.py";

    private static final String EXIT_SCRIPT =
            AI_PROJECT + "\\process_exit_video.py";

    private static final String DURATION_SCRIPT =
            AI_PROJECT + "\\duration_validation.py";


    @PostMapping("/upload")
    public ResponseEntity<String> uploadVideos(
            @RequestParam("entryVideo") MultipartFile entryVideo,
            @RequestParam("exitVideo") MultipartFile exitVideo) {

        try {

            // ==================================================
            // STEP 1: CREATE UPLOAD DIRECTORIES
            // ==================================================

            Path entryDirectory =
                    Paths.get(ENTRY_FOLDER).toAbsolutePath();

            Path exitDirectory =
                    Paths.get(EXIT_FOLDER).toAbsolutePath();

            Files.createDirectories(entryDirectory);
            Files.createDirectories(exitDirectory);


            // ==================================================
            // STEP 2: CREATE UNIQUE FILE NAMES
            // ==================================================

            String timestamp =
                    String.valueOf(System.currentTimeMillis());

            String entryOriginalName =
                    entryVideo.getOriginalFilename();

            String exitOriginalName =
                    exitVideo.getOriginalFilename();

            if (entryOriginalName == null) {
                entryOriginalName = "entry_video.mp4";
            }

            if (exitOriginalName == null) {
                exitOriginalName = "exit_video.mp4";
            }


            String entryFileName =
                    timestamp + "_entry_" + entryOriginalName;

            String exitFileName =
                    timestamp + "_exit_" + exitOriginalName;


            Path entryPath =
                    entryDirectory.resolve(entryFileName);

            Path exitPath =
                    exitDirectory.resolve(exitFileName);


            // ==================================================
            // STEP 3: SAVE ENTRY VIDEO
            // ==================================================

            Files.copy(
                    entryVideo.getInputStream(),
                    entryPath,
                    StandardCopyOption.REPLACE_EXISTING
            );


            // ==================================================
            // STEP 4: SAVE EXIT VIDEO
            // ==================================================

            Files.copy(
                    exitVideo.getInputStream(),
                    exitPath,
                    StandardCopyOption.REPLACE_EXISTING
            );


            System.out.println();
            System.out.println("========================================");
            System.out.println("VIDEOS UPLOADED");
            System.out.println("========================================");

            System.out.println(
                    "Entry Video: " + entryPath
            );

            System.out.println(
                    "Exit Video : " + exitPath
            );


            // ==================================================
            // STEP 5: ENTRY VIDEO FACE RECOGNITION
            // ==================================================

            System.out.println();
            System.out.println(
                    "Starting Entry Video Face Recognition..."
            );

            int entryResult = runPythonScript(
                    ENTRY_SCRIPT,
                    entryPath.toString()
            );


            if (entryResult != 0) {

                return ResponseEntity
                        .internalServerError()
                        .body(
                                "Entry video processing failed."
                        );
            }


            // ==================================================
            // STEP 6: EXIT VIDEO FACE RECOGNITION
            // ==================================================

            System.out.println();
            System.out.println(
                    "Starting Exit Video Face Recognition..."
            );

            int exitResult = runPythonScript(
                    EXIT_SCRIPT,
                    exitPath.toString()
            );


            if (exitResult != 0) {

                return ResponseEntity
                        .internalServerError()
                        .body(
                                "Exit video processing failed."
                        );
            }


            // ==================================================
            // STEP 7: DURATION VALIDATION
            // ==================================================

            System.out.println();
            System.out.println(
                    "Starting Duration Validation..."
            );

            int durationResult =
                    runPythonScript(DURATION_SCRIPT);


            if (durationResult != 0) {

                return ResponseEntity
                        .internalServerError()
                        .body(
                                "Duration validation failed."
                        );
            }


            // ==================================================
            // STEP 8: COMPLETED
            // ==================================================

            System.out.println();
            System.out.println("========================================");
            System.out.println(
                    "ATTENDANCE PROCESSING COMPLETED"
            );
            System.out.println("========================================");


            return ResponseEntity.ok(
                    "Entry video processed, Exit video processed, "
                    + "and Duration Validation completed successfully."
            );


        } catch (IOException e) {

            e.printStackTrace();

            return ResponseEntity
                    .internalServerError()
                    .body(
                            "Failed to upload/process videos: "
                                    + e.getMessage()
                    );

        } catch (InterruptedException e) {

            Thread.currentThread().interrupt();

            e.printStackTrace();

            return ResponseEntity
                    .internalServerError()
                    .body(
                            "Video processing was interrupted."
                    );
        }
    }


    // ==========================================================
    // RUN PYTHON SCRIPT
    // ==========================================================

    private int runPythonScript(
            String scriptPath,
            String... arguments)
            throws IOException, InterruptedException {


        // Check Python executable
        File pythonFile = new File(PYTHON);

        if (!pythonFile.exists()) {

            throw new IOException(
                    "Python executable not found: "
                            + PYTHON
            );
        }


        // Check Python script
        File scriptFile = new File(scriptPath);

        if (!scriptFile.exists()) {

            throw new IOException(
                    "Python script not found: "
                            + scriptPath
            );
        }


        ProcessBuilder processBuilder =
                new ProcessBuilder();


        // Python executable
        processBuilder.command().add(PYTHON);

        // Python script
        processBuilder.command().add(scriptPath);


        // Arguments
        for (String argument : arguments) {

            processBuilder.command().add(argument);
        }


        // Run from AI project directory
        processBuilder.directory(
                new File(AI_PROJECT)
        );


        // Combine stdout + stderr
        processBuilder.redirectErrorStream(true);


        Process process =
                processBuilder.start();


        // ======================================================
        // SHOW PYTHON OUTPUT IN SPRING BOOT TERMINAL
        // ======================================================

        try (
                BufferedReader reader =
                        new BufferedReader(
                                new InputStreamReader(
                                        process.getInputStream()
                                )
                        )
        ) {

            String line;

            while ((line = reader.readLine()) != null) {

                System.out.println(
                        "[PYTHON] " + line
                );
            }
        }


        return process.waitFor();
    }
}
