package com.roadgis.dto.response;

import com.roadgis.entity.BlackIceRisk;
import lombok.Getter;
import java.time.LocalDateTime;

@Getter
public class BlackIceRiskResponse {
    private final Long id;
    private final String stationId;
    private final Double latitude;
    private final Double longitude;
    private final Short riskLevel;
    private final String riskLabel;
    private final Double temperature;
    private final Double humidity;
    private final Double precipitation;
    private final Double windSpeed;
    private final Double roadTemp;
    private final LocalDateTime predictedAt;

    public BlackIceRiskResponse(BlackIceRisk entity) {
        this.id = entity.getId();
        this.stationId = entity.getStationId();
        this.latitude = entity.getLocation().getY();
        this.longitude = entity.getLocation().getX();
        this.riskLevel = entity.getRiskLevel();
        this.riskLabel = entity.getRiskLabel();
        this.temperature = entity.getTemperature();
        this.humidity = entity.getHumidity();
        this.precipitation = entity.getPrecipitation();
        this.windSpeed = entity.getWindSpeed();
        this.roadTemp = entity.getRoadTemp();
        this.predictedAt = entity.getPredictedAt();
    }
}
