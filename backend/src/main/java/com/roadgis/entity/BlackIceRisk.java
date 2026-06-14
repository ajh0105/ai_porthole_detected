package com.roadgis.entity;

import jakarta.persistence.*;
import lombok.*;
import org.locationtech.jts.geom.Point;
import java.time.LocalDateTime;

@Entity
@Table(name = "blackice_risk")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class BlackIceRisk {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 20)
    private String stationId;

    @Column(nullable = false, columnDefinition = "GEOMETRY(Point, 4326)")
    private Point location;

    @Column(nullable = false)
    private Short riskLevel;    // 0:안전 1:관심 2:주의 3:위험

    @Column(nullable = false, length = 10)
    private String riskLabel;

    private Double temperature;
    private Double humidity;
    private Double precipitation;
    private Double windSpeed;
    private Double roadTemp;

    @Column(nullable = false)
    private LocalDateTime predictedAt;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public BlackIceRisk(String stationId, Point location, Short riskLevel, String riskLabel,
                        Double temperature, Double humidity, Double precipitation,
                        Double windSpeed, Double roadTemp, LocalDateTime predictedAt) {
        this.stationId = stationId;
        this.location = location;
        this.riskLevel = riskLevel;
        this.riskLabel = riskLabel;
        this.temperature = temperature;
        this.humidity = humidity;
        this.precipitation = precipitation;
        this.windSpeed = windSpeed;
        this.roadTemp = roadTemp;
        this.predictedAt = predictedAt != null ? predictedAt : LocalDateTime.now();
        this.createdAt = LocalDateTime.now();
    }
}
