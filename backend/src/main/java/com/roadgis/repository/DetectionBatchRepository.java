package com.roadgis.repository;

import com.roadgis.entity.DetectionBatch;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface DetectionBatchRepository extends JpaRepository<DetectionBatch, Long> {
    List<DetectionBatch> findTop10ByOrderByCreatedAtDesc();
}
