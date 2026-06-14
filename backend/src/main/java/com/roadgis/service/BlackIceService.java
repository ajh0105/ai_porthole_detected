package com.roadgis.service;

import com.roadgis.dto.response.BlackIceRiskResponse;
import com.roadgis.entity.BlackIceRisk;
import com.roadgis.entity.WeatherStation;
import com.roadgis.exception.BusinessException;
import com.roadgis.repository.BlackIceRiskRepository;
import com.roadgis.repository.WeatherStationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class BlackIceService {

    private final BlackIceRiskRepository repository;
    private final WeatherStationRepository stationRepository;

    public Page<BlackIceRiskResponse> findAll(Short riskLevel, String stationId,
                                               LocalDateTime dateFrom, LocalDateTime dateTo,
                                               Pageable pageable) {
        if (riskLevel != null && (riskLevel < 0 || riskLevel > 3)) {
            throw BusinessException.badRequest("위험도는 0~3 사이여야 합니다.");
        }
        return repository.findWithFilters(riskLevel, stationId, dateFrom, dateTo, pageable)
                .map(BlackIceRiskResponse::new);
    }

    public List<Map<String, Object>> getGeoJson(double minLng, double minLat, double maxLng, double maxLat) {
        if (minLng >= maxLng || minLat >= maxLat) {
            throw BusinessException.badRequest("bbox 좌표가 올바르지 않습니다.");
        }
        List<BlackIceRisk> risks = repository.findWithinBbox(minLng, minLat, maxLng, maxLat);
        List<Map<String, Object>> features = new ArrayList<>();
        for (BlackIceRisk r : risks) {
            Map<String, Object> feature = new LinkedHashMap<>();
            feature.put("type", "Feature");
            feature.put("id", r.getId());

            Map<String, Object> geometry = new LinkedHashMap<>();
            geometry.put("type", "Point");
            geometry.put("coordinates", List.of(r.getLocation().getX(), r.getLocation().getY()));
            feature.put("geometry", geometry);

            Map<String, Object> props = new LinkedHashMap<>();
            props.put("stationId", r.getStationId());
            props.put("riskLevel", r.getRiskLevel());
            props.put("riskLabel", r.getRiskLabel());
            props.put("temperature", r.getTemperature());
            props.put("predictedAt", r.getPredictedAt());
            feature.put("properties", props);
            features.add(feature);
        }
        return features;
    }

    /** 관측소별 가장 최신 예측 데이터 목록 (현재 기상 현황). */
    public List<Map<String, Object>> getCurrentWeatherAll() {
        return repository.findLatestPerStation().stream().map(r -> {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("stationId", r.getStationId());
            m.put("riskLevel", r.getRiskLevel());
            m.put("riskLabel", r.getRiskLabel());
            m.put("temperature", r.getTemperature());
            m.put("humidity", r.getHumidity());
            m.put("precipitation", r.getPrecipitation());
            m.put("windSpeed", r.getWindSpeed());
            m.put("predictedAt", r.getPredictedAt());
            m.put("lat", r.getLocation().getY());
            m.put("lng", r.getLocation().getX());
            return m;
        }).toList();
    }

    /** 특정 좌표에서 가장 가까운 관측소의 최신 기상 데이터 반환. */
    public Map<String, Object> getRegionWeather(double lat, double lng) {
        BlackIceRisk risk = repository.findLatestNearestToPoint(lat, lng).orElse(null);
        if (risk == null) {
            return Map.of("message", "예측 데이터가 없습니다. 블랙아이스 예측을 먼저 실행하세요.");
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("stationId", risk.getStationId());
        result.put("riskLevel", risk.getRiskLevel());
        result.put("riskLabel", risk.getRiskLabel());
        result.put("temperature", risk.getTemperature());
        result.put("humidity", risk.getHumidity());
        result.put("precipitation", risk.getPrecipitation());
        result.put("windSpeed", risk.getWindSpeed());
        result.put("predictedAt", risk.getPredictedAt());
        return result;
    }

    /** 기상 관측소 목록 (id, name, region, lat, lng). */
    public List<Map<String, Object>> getStations() {
        return stationRepository.findAllOrderByName().stream().map(ws -> {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("stationId", ws.getStationId());
            m.put("stationName", ws.getStationName());
            m.put("region", ws.getRegion());
            m.put("lat", ws.getLocation().getY());
            m.put("lng", ws.getLocation().getX());
            return m;
        }).toList();
    }

    public Map<String, Object> getStats() {
        Map<String, Object> stats = new LinkedHashMap<>();
        stats.put("totalCount", repository.count());
        stats.put("byRiskLevel", repository.countByRiskLevel());
        return stats;
    }
}
