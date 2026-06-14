package com.roadgis.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "detection_batch")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class DetectionBatch {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 20)
    private String batchType;   // ROAD_DAMAGE | BLACKICE

    @Column(nullable = false, length = 20)
    private String status;      // PENDING | RUNNING | DONE | FAILED

    private Integer totalFiles;
    private Integer processed;

    @Column(columnDefinition = "TEXT")
    private String errorMsg;

    private LocalDateTime startedAt;
    private LocalDateTime finishedAt;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public DetectionBatch(String batchType) {
        this.batchType = batchType;
        this.status = "PENDING";
        this.totalFiles = 0;
        this.processed = 0;
        this.createdAt = LocalDateTime.now();
    }

    public void start(int totalFiles) {
        this.status = "RUNNING";
        this.totalFiles = totalFiles;
        this.startedAt = LocalDateTime.now();
    }

    public void incrementProcessed() {
        this.processed++;
    }

    public void complete() {
        this.status = "DONE";
        this.finishedAt = LocalDateTime.now();
    }

    public void fail(String errorMsg) {
        this.status = "FAILED";
        this.errorMsg = errorMsg;
        this.finishedAt = LocalDateTime.now();
    }
}
