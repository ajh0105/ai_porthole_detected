package com.roadgis.service;

import com.roadgis.entity.DetectionBatch;
import com.roadgis.repository.DetectionBatchRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class AiPipelineService {

    private final DetectionBatchRepository batchRepository;
    private final RestTemplate restTemplate;

    @Value("${ai.pipeline.url}")
    private String aiPipelineUrl;

    @Value("${file.upload-dir}")
    private String uploadDir;

    @Transactional
    public Map<String, Object> triggerRoadDamageDetection(List<MultipartFile> files) {
        DetectionBatch batch = DetectionBatch.builder().batchType("ROAD_DAMAGE").build();
        batchRepository.save(batch);

        try {
            List<String> savedPaths = saveFiles(files);
            batch.start(savedPaths.size());
            batchRepository.save(batch);

            // Python AI 서버 호출
            Map<String, Object> payload = new HashMap<>();
            payload.put("batchId", batch.getId());
            payload.put("filePaths", savedPaths);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(payload, headers);

            ResponseEntity<Map> response = restTemplate.postForEntity(
                    aiPipelineUrl + "/detect/road", request, Map.class);

            if (response.getStatusCode().is2xxSuccessful()) {
                batch.complete();
            } else {
                batch.fail("AI 서버 응답 오류: " + response.getStatusCode());
            }
            batchRepository.save(batch);

            return Map.of("batchId", batch.getId(), "status", batch.getStatus(), "files", savedPaths.size());

        } catch (Exception e) {
            log.error("Road damage detection failed", e);
            batch.fail(e.getMessage());
            batchRepository.save(batch);
            throw new IllegalStateException("AI 탐지 파이프라인 실행 중 오류가 발생했습니다.");
        }
    }

    @Transactional
    public Map<String, Object> triggerBlackIcePrediction() {
        DetectionBatch batch = DetectionBatch.builder().batchType("BLACKICE").build();
        batchRepository.save(batch);

        try {
            batch.start(1);
            batchRepository.save(batch);

            ResponseEntity<Map> response = restTemplate.postForEntity(
                    aiPipelineUrl + "/predict/blackice", null, Map.class);

            if (response.getStatusCode().is2xxSuccessful()) {
                batch.complete();
            } else {
                batch.fail("AI 서버 응답 오류: " + response.getStatusCode());
            }
            batchRepository.save(batch);

            return Map.of("batchId", batch.getId(), "status", batch.getStatus());

        } catch (Exception e) {
            log.error("Black ice prediction failed", e);
            batch.fail(e.getMessage());
            batchRepository.save(batch);
            throw new IllegalStateException("블랙아이스 예측 파이프라인 실행 중 오류가 발생했습니다.");
        }
    }

    public List<Map<String, Object>> getBatchHistory() {
        return batchRepository.findTop10ByOrderByCreatedAtDesc().stream()
                .map(b -> {
                    Map<String, Object> m = new LinkedHashMap<>();
                    m.put("id", b.getId());
                    m.put("batchType", b.getBatchType());
                    m.put("status", b.getStatus());
                    m.put("totalFiles", b.getTotalFiles());
                    m.put("processed", b.getProcessed());
                    m.put("startedAt", b.getStartedAt());
                    m.put("finishedAt", b.getFinishedAt());
                    return m;
                }).toList();
    }

    private List<String> saveFiles(List<MultipartFile> files) throws IOException {
        Path dir = Paths.get(uploadDir);
        Files.createDirectories(dir);
        List<String> paths = new ArrayList<>();
        for (MultipartFile file : files) {
            String filename = UUID.randomUUID() + "_" + file.getOriginalFilename();
            Path target = dir.resolve(filename);
            Files.copy(file.getInputStream(), target, StandardCopyOption.REPLACE_EXISTING);
            paths.add(target.toAbsolutePath().toString());
        }
        return paths;
    }
}
