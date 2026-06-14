package com.roadgis.dto.response;

import com.roadgis.entity.RoadDamage;
import lombok.Getter;
import java.time.LocalDateTime;

@Getter
public class RoadDamageResponse {
    private final Long id;
    private final String damageType;
    private final Double confidence;
    private final Double latitude;
    private final Double longitude;
    private final String imagePath;
    private final String roadName;
    private final String district;
    private final LocalDateTime detectedAt;

    public RoadDamageResponse(RoadDamage entity) {
        this.id = entity.getId();
        this.damageType = entity.getDamageType();
        this.confidence = entity.getConfidence();
        this.latitude = entity.getLocation().getY();
        this.longitude = entity.getLocation().getX();
        this.imagePath = entity.getImagePath();
        this.roadName = entity.getRoadName();
        this.district = entity.getDistrict();
        this.detectedAt = entity.getDetectedAt();
    }
}
