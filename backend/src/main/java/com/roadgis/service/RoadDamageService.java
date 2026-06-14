package com.roadgis.service;

import com.roadgis.dto.response.RoadDamageResponse;
import com.roadgis.entity.RoadDamage;
import com.roadgis.exception.BusinessException;
import com.roadgis.repository.RoadDamageRepository;
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
public class RoadDamageService {

    private final RoadDamageRepository repository;

    public Page<RoadDamageResponse> findAll(String damageType, String district,
                                             LocalDateTime dateFrom, LocalDateTime dateTo,
                                             Pageable pageable) {
        validateDamageType(damageType);
        return repository.findWithFilters(damageType, district, dateFrom, dateTo, pageable)
                .map(RoadDamageResponse::new);
    }

    public RoadDamageResponse findById(Long id) {
        RoadDamage entity = repository.findById(id)
                .orElseThrow(() -> BusinessException.notFound("ID " + id + "에 해당하는 도로 파손 데이터가 없습니다."));
        return new RoadDamageResponse(entity);
    }

    public List<Map<String, Object>> getGeoJson(double minLng, double minLat, double maxLng, double maxLat) {
        validateBbox(minLng, minLat, maxLng, maxLat);
        List<RoadDamage> damages = repository.findWithinBbox(minLng, minLat, maxLng, maxLat);
        List<Map<String, Object>> features = new ArrayList<>();
        for (RoadDamage d : damages) {
            Map<String, Object> feature = new LinkedHashMap<>();
            feature.put("type", "Feature");
            feature.put("id", d.getId());

            Map<String, Object> geometry = new LinkedHashMap<>();
            geometry.put("type", "Point");
            geometry.put("coordinates", List.of(d.getLocation().getX(), d.getLocation().getY()));
            feature.put("geometry", geometry);

            Map<String, Object> props = new LinkedHashMap<>();
            props.put("damageType", d.getDamageType());
            props.put("confidence", d.getConfidence());
            props.put("roadName", d.getRoadName());
            props.put("district", d.getDistrict());
            props.put("detectedAt", d.getDetectedAt());
            feature.put("properties", props);
            features.add(feature);
        }
        return features;
    }

    public Map<String, Object> getStats() {
        Map<String, Object> stats = new LinkedHashMap<>();
        stats.put("totalCount", repository.count());
        stats.put("potholeCount", repository.countByDamageType("pothole"));
        stats.put("crackCount", repository.countByDamageType("crack"));
        stats.put("byType", repository.countByDamageType());
        stats.put("byDistrict", repository.countByDistrict());
        return stats;
    }

    public List<String> getDistricts() {
        return repository.findDistinctDistricts();
    }

    @Transactional
    public void delete(Long id) {
        if (!repository.existsById(id)) {
            throw BusinessException.notFound("ID " + id + "에 해당하는 데이터가 없습니다.");
        }
        repository.deleteById(id);
    }

    private void validateDamageType(String damageType) {
        if (damageType != null && !damageType.isBlank()
                && !damageType.equals("pothole") && !damageType.equals("crack")) {
            throw BusinessException.badRequest("유효하지 않은 파손 유형입니다. (pothole | crack)");
        }
    }

    private void validateBbox(double minLng, double minLat, double maxLng, double maxLat) {
        if (minLng >= maxLng || minLat >= maxLat) {
            throw BusinessException.badRequest("bbox 좌표가 올바르지 않습니다. (minLng < maxLng, minLat < maxLat)");
        }
        if (minLng < -180 || maxLng > 180 || minLat < -90 || maxLat > 90) {
            throw BusinessException.badRequest("bbox 좌표가 유효 범위를 벗어났습니다.");
        }
    }
}
