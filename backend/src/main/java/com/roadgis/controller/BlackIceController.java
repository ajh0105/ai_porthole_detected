package com.roadgis.controller;

import com.roadgis.dto.response.ApiResponse;
import com.roadgis.dto.response.BlackIceRiskResponse;
import com.roadgis.service.AiPipelineService;
import com.roadgis.service.BlackIceService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/blackice")
@RequiredArgsConstructor
public class BlackIceController {

    private final BlackIceService blackIceService;
    private final AiPipelineService aiPipelineService;

    @GetMapping
    public ResponseEntity<ApiResponse<Page<BlackIceRiskResponse>>> getList(
            @RequestParam(required = false) Short riskLevel,
            @RequestParam(required = false) String stationId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime dateFrom,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime dateTo,
            @PageableDefault(size = 20, sort = "predictedAt", direction = Sort.Direction.DESC) Pageable pageable) {
        return ResponseEntity.ok(ApiResponse.ok(
                blackIceService.findAll(riskLevel, stationId, dateFrom, dateTo, pageable)));
    }

    @GetMapping("/map")
    public ResponseEntity<ApiResponse<List<Map<String, Object>>>> getMapData(
            @RequestParam(defaultValue = "124.0") double minLng,
            @RequestParam(defaultValue = "33.0")  double minLat,
            @RequestParam(defaultValue = "132.0") double maxLng,
            @RequestParam(defaultValue = "39.0")  double maxLat) {
        return ResponseEntity.ok(ApiResponse.ok(blackIceService.getGeoJson(minLng, minLat, maxLng, maxLat)));
    }

    @GetMapping("/stats")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getStats() {
        return ResponseEntity.ok(ApiResponse.ok(blackIceService.getStats()));
    }

    @GetMapping("/current-weather")
    public ResponseEntity<ApiResponse<List<Map<String, Object>>>> getCurrentWeather() {
        return ResponseEntity.ok(ApiResponse.ok(blackIceService.getCurrentWeatherAll()));
    }

    @GetMapping("/stations")
    public ResponseEntity<ApiResponse<List<Map<String, Object>>>> getStations() {
        return ResponseEntity.ok(ApiResponse.ok(blackIceService.getStations()));
    }

    @GetMapping("/region-weather")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getRegionWeather(
            @RequestParam double lat,
            @RequestParam double lng) {
        return ResponseEntity.ok(ApiResponse.ok(blackIceService.getRegionWeather(lat, lng)));
    }

    @PostMapping("/predict")
    public ResponseEntity<ApiResponse<Map<String, Object>>> predict() {
        Map<String, Object> result = aiPipelineService.triggerBlackIcePrediction();
        return ResponseEntity.ok(ApiResponse.ok(result, "블랙아이스 예측 완료"));
    }
}
