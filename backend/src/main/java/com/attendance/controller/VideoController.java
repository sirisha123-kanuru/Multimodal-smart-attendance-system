package com.attendance.controller;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicReference;

import org.springframework.core.io.FileSystemResource;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
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

    /*
     * FastAPI AI service running inside the same Railway container.
     */
    private static final String AI_SERVICE_URL =
            "http://127.0.0.1:8000";

    private final RestClient restClient;

    /*
     * Processing status:
     *
     * IDLE
     * PROCESSING
     * COMPLETED
     * FAILED
     */
    private final AtomicReference<String> processingStatus =
            new AtomicReference<>("IDLE");

    private volatile String lastError = "";

    public VideoController() {
        this.restClient = RestClient.builder()
                .baseUrl(AI_SERVICE_URL)
                .build();
    }

    // ==========================================================
    // UPLOAD ENTRY + EXIT VIDEOS
    // ==========================================================

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

            // --------------------------------------------------
            // STEP 1: VALIDATE VIDEOS
            // --------------------------------------------------

            if (entryVideo == null || entryVideo.isEmpty()) {
                return ResponseEntity
                        .badRequest()
                        .body("Entry video is required.");
            }

            if (exitVideo == null || exitVideo.isEmpty()) {
                return ResponseEntity
                        .badRequest()
                        .body("Exit video is required.");
            }

            // --------------------------------------------------
            // STEP 2: CREATE DIRECTORIES
            // --------------------------------------------------

            Path entryDirectory =
                    Paths.get(ENTRY_FOLDER).toAbsolutePath();

            Path exitDirectory =
                    Paths.get(EXIT_FOLDER).toAbsolutePath();

            Files.createDirectories(entryDirectory);
            Files.createDirectories(exitDirectory);

            // --------------------------------------------------
            // STEP 3: CREATE UNIQUE FILE NAMES
            // --------------------------------------------------

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

            // Prevent unsafe path names
            entryOriginalName =
                    Paths.get(entryOriginalName)
                            .getFileName()
                            .toString();

            exitOriginalName =
                    Paths.get(exitOriginalName)
                            .getFileName()
                            .toString();

            String entryFileName =
                    timestamp + "_entry_" + entryOriginalName;

            String exitFileName =
                    timestamp + "_exit_" + exitOriginalName;

            entryPath =
                    entryDirectory.resolve(entryFileName);

            exitPath =
                    exitDirectory.resolve(exitFileName);

            // --------------------------------------------------
            // STEP 4: SAVE ENTRY VIDEO
            // --------------------------------------------------

            Files.copy(
                    entryVideo.getInputStream(),
                    entryPath,
                    StandardCopyOption.REPLACE_EXISTING
            );

            // --------------------------------------------------
            // STEP 5: SAVE EXIT VIDEO
            // --------------------------------------------------

            Files.copy(
                    exitVideo.getInputStream(),
                    exitPath,
                    StandardCopyOption.REPLACE_EXISTING
            );

            System.out.println();
            System.out.println("========================================");
            System.out.println("VIDEOS UPLOADED SUCCESSFULLY");
            System.out.println("========================================");

            System.out.println(
                    "Entry Video: " + entryPath
            );

            System.out.println(
                    "Exit Video : " + exitPath
            );

            System.out.println(
                    "Entry Size : "
                            + Files.size(entryPath)
                            + " bytes"
            );

            System.out.println(
                    "Exit Size  : "
                            + Files.size(exitPath)
                            + " bytes"
            );

            // --------------------------------------------------
            // STEP 6: SET PROCESSING STATUS
            // --------------------------------------------------

            processingStatus.set("PROCESSING");
            lastError = "";

            /*
             * Final variables are required by CompletableFuture.
             */
            Path finalEntryPath = entryPath;
            Path finalExitPath = exitPath;

            // --------------------------------------------------
            // STEP 7: BACKGROUND AI PROCESSING
            // --------------------------------------------------

            CompletableFuture.runAsync(() -> {

                try {

                    System.out.println();
                    System.out.println(
                            "========================================"
                    );
                    System.out.println(
                            "BACKGROUND AI PROCESSING STARTED"
                    );
                    System.out.println(
                            "========================================"
                    );

                    // ==========================================
                    // ENTRY VIDEO
                    // ==========================================

                    System.out.println();
                    System.out.println(
                            "Starting Entry Video Face Recognition..."
                    );

                    String entryResponse =
                            sendVideoToAI(
                                    "/process/entry",
                                    "entry_video",
                                    finalEntryPath
                            );

                    System.out.println(
                            "[AI ENTRY] " + entryResponse
                    );

                    // ==========================================
                    // EXIT VIDEO
                    // ==========================================

                    System.out.println();
                    System.out.println(
                            "Starting Exit Video Face Recognition..."
                    );

                    String exitResponse =
                            sendVideoToAI(
                                    "/process/exit",
                                    "exit_video",
                                    finalExitPath
                            );

                    System.out.println(
                            "[AI EXIT] " + exitResponse
                    );

                    // ==========================================
                    // ATTENDANCE VALIDATION
                    // ==========================================

                    System.out.println();
                    System.out.println(
                            "Starting Attendance Validation..."
                    );

                    String durationResponse =
                            restClient.post()
                                    .uri("/process/duration")
                                    .retrieve()
                                    .body(String.class);

                    System.out.println(
                            "[AI DURATION] "
                                    + durationResponse
                    );

                    // ==========================================
                    // PROCESSING COMPLETED
                    // ==========================================

                    processingStatus.set("COMPLETED");

                    System.out.println();
                    System.out.println(
                            "========================================"
                    );
                    System.out.println(
                            "ATTENDANCE PROCESSING COMPLETED"
                    );
                    System.out.println(
                            "========================================"
                    );

                } catch (Exception e) {

                    e.printStackTrace();

                    lastError =
                            e.getMessage() != null
                                    ? e.getMessage()
                                    : "Unknown AI processing error";

                    processingStatus.set("FAILED");

                    System.out.println();
                    System.out.println(
                            "========================================"
                    );
                    System.out.println(
                            "AI PROCESSING FAILED"
                    );
                    System.out.println(
                            "========================================"
                    );

                } finally {

                    // ==========================================
                    // DELETE TEMPORARY VIDEOS
                    // ==========================================

                    deleteFile(finalEntryPath);
                    deleteFile(finalExitPath);
                }

            });

            // --------------------------------------------------
            // IMPORTANT:
            //
            // Return immediately instead of waiting for AI.
            //
            // This prevents Railway from waiting several minutes
            // and returning a 502 timeout.
            // --------------------------------------------------

            return ResponseEntity
                    .status(HttpStatus.ACCEPTED)
                    .body(
                            "Videos uploaded successfully. "
                                    + "AI processing started in background."
                    );

        } catch (Exception e) {

            e.printStackTrace();

            processingStatus.set("FAILED");

            lastError =
                    e.getMessage() != null
                            ? e.getMessage()
                            : "Video upload failed.";

            deleteFile(entryPath);
            deleteFile(exitPath);

            return ResponseEntity
                    .internalServerError()
                    .body(
                            "Failed to upload videos: "
                                    + lastError
                    );
        }
    }

    // ==========================================================
    // CHECK PROCESSING STATUS
    // ==========================================================

    @GetMapping("/status")
    public ResponseEntity<ProcessingStatusResponse>
    getProcessingStatus() {

        return ResponseEntity.ok(
                new ProcessingStatusResponse(
                        processingStatus.get(),
                        lastError
                )
        );
    }

    // ==========================================================
    // SEND VIDEO TO FASTAPI
    // ==========================================================

    private String sendVideoToAI(
            String endpoint,
            String fieldName,
            Path videoPath) {

        FileSystemResource videoResource =
                new FileSystemResource(
                        videoPath.toFile()
                );

        MultiValueMap<String, Object> body =
                new LinkedMultiValueMap<>();

        body.add(
                fieldName,
                videoResource
        );

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

            System.out.println(
                    "Temporary video deleted: " + path
            );

        } catch (IOException e) {

            System.out.println(
                    "Could not delete temporary video: "
                            + path
            );
        }
    }

    // ==========================================================
    // STATUS RESPONSE CLASS
    // ==========================================================

    public static class ProcessingStatusResponse {

        private final String status;
        private final String error;

        public ProcessingStatusResponse(
                String status,
                String error) {

            this.status = status;
            this.error = error;
        }

        public String getStatus() {
            return status;
        }

        public String getError() {
            return error;
        }
    }
}