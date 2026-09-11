package com.attendance.controller;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

import org.springframework.core.io.FileSystemResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;
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

    // FastAPI AI service running inside the same Railway container
    private static final String AI_SERVICE_URL = "http://127.0.0.1:8000";

    private final RestClient restClient;

    public VideoController() {
        this.restClient = RestClient.builder()
                .baseUrl(AI_SERVICE_URL)
                .build();
    }

    @PostMapping(
            value = "/upload",
            consumes = MediaType.MULTIPART_FORM_DATA_VALUE
    )
    public ResponseEntity<String> uploadVideos(
            @RequestParam("entryVideo") MultipartFile entryVideo,
            @RequestParam("exitVideo") MultipartFile exitVideo) {

        Path entryPath = null;
        Path exitPath = null;

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

            if (entryOriginalName == null ||
                    entryOriginalName.isBlank()) {
                entryOriginalName = "entry_video.mp4";
            }

            if (exitOriginalName == null ||
                    exitOriginalName.isBlank()) {
                exitOriginalName = "exit_video.mp4";
            }

            String entryFileName =
                    timestamp + "_entry_" + entryOriginalName;

            String exitFileName =
                    timestamp + "_exit_" + exitOriginalName;

            entryPath =
                    entryDirectory.resolve(entryFileName);

            exitPath =
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
            System.out.println("Entry Video: " + entryPath);
            System.out.println("Exit Video : " + exitPath);

            // ==================================================
            // STEP 5: ENTRY VIDEO FACE RECOGNITION
            // ==================================================

            System.out.println();
            System.out.println(
                    "Starting Entry Video Face Recognition..."
            );

            String entryResponse =
                    sendVideoToAI(
                            "/process/entry",
                            "entry_video",
                            entryPath
                    );

            System.out.println("[AI ENTRY] " + entryResponse);

            // ==================================================
            // STEP 6: EXIT VIDEO FACE RECOGNITION
            // ==================================================

            System.out.println();
            System.out.println(
                    "Starting Exit Video Face Recognition..."
            );

            String exitResponse =
                    sendVideoToAI(
                            "/process/exit",
                            "exit_video",
                            exitPath
                    );

            System.out.println("[AI EXIT] " + exitResponse);

            // ==================================================
            // STEP 7: DURATION VALIDATION
            // ==================================================

            System.out.println();
            System.out.println(
                    "Starting Duration Validation..."
            );

            String durationResponse =
                    restClient.post()
                            .uri("/process/duration")
                            .retrieve()
                            .body(String.class);

            System.out.println(
                    "[AI DURATION] " + durationResponse
            );

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

        } catch (Exception e) {

            e.printStackTrace();

            return ResponseEntity
                    .internalServerError()
                    .body(
                            "Failed to upload/process videos: "
                                    + e.getMessage()
                    );

        } finally {

            // Delete temporary backend copies after processing
            deleteFile(entryPath);
            deleteFile(exitPath);
        }
    }

    // ==========================================================
    // SEND VIDEO TO FASTAPI AI SERVICE
    // ==========================================================

    private String sendVideoToAI(
            String endpoint,
            String fieldName,
            Path videoPath) {

        FileSystemResource videoResource =
                new FileSystemResource(videoPath.toFile());

        MultiValueMap<String, Object> body =
                new LinkedMultiValueMap<>();

        body.add(fieldName, videoResource);

        return restClient.post()
                .uri(endpoint)
                .contentType(
                        MediaType.MULTIPART_FORM_DATA
                )
                .body(body)
                .retrieve()
                .body(String.class);
    }

    // ==========================================================
    // DELETE TEMPORARY FILE
    // ==========================================================

    private void deleteFile(Path path) {

        if (path == null) {
            return;
        }

        try {

            Files.deleteIfExists(path);

        } catch (IOException e) {

            System.out.println(
                    "Could not delete temporary file: "
                            + path
            );
        }
    }
}