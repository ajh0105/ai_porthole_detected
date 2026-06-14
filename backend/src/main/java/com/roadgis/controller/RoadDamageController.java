package com.roadgis.controller;

import com.roadgis.dto.response.ApiResponse;
import com.roadgis.dto.response.RoadDamageResponse;
import com.roadgis.service.AiPipelineService;
import com.roadgis.service.RoadDamageService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/road-damage")
@RequiredArgsConstructor
public class RoadDamageController {

    private final RoadDamageService roadDamageService;
    private final AiPipelineService aiPipelineService;

    @GetMapping
    public ResponseEntity<ApiResponse<Page<RoadDamageResponse>>> getList(
            @RequestParam(required = false) String damageType,
            @RequestParam(required = false) String district,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime dateFrom,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime dateTo,
            @PageableDefault(size = 20, sort = "detectedAt", direction = Sort.Direction.DESC) Pageable pageable) {
        return ResponseEntity.ok(ApiResponse.ok(
                roadDamageService.findAll(damageType, district, dateFrom, dateTo, pageable)));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<RoadDamageResponse>> getOne(@PathVariable Long id) {
        return ResponseEntity.ok(ApiResponse.ok(roadDamageService.findById(id)));
    }

    @GetMapping("/map")
    public ResponseEntity<ApiResponse<List<Map<String, Object>>>> getMapData(
            @RequestParam(defaultValue = "124.0") double minLng,
            @RequestParam(defaultValue = "33.0")  double minLat,
            @RequestParam(defaultValue = "132.0") double maxLng,
            @RequestParam(defaultValue = "39.0")  double maxLat) {
        return ResponseEntity.ok(ApiResponse.ok(roadDamageService.getGeoJson(minLng, minLat, maxLng, maxLat)));
    }

    @GetMapping("/stats")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getStats() {
        return ResponseEntity.ok(ApiResponse.ok(roadDamageService.getStats()));
    }

    @GetMapping("/districts")
    public ResponseEntity<ApiResponse<List<String>>> getDistricts() {
        return ResponseEntity.ok(ApiResponse.ok(roadDamageService.getDistricts()));
    }

    @PostMapping("/upload")
    public ResponseEntity<ApiResponse<Map<String, Object>>> upload(
            @RequestParam("files") List<MultipartFile> files) {
        Map<String, Object> result = aiPipelineService.triggerRoadDamageDetection(files);
        return ResponseEntity.ok(ApiResponse.ok(result, "AI 탐지 파이프라인 실행 완료"));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> delete(@PathVariable Long id) {
        roadDamageService.delete(id);
        return ResponseEntity.ok(ApiResponse.ok(null, "삭제되었습니다."));
    }
}
