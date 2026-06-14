package com.roadgis.entity;

import jakarta.persistence.*;
import lombok.*;
import org.locationtech.jts.geom.Point;
import java.time.LocalDateTime;

@Entity
@Table(name = "weather_station")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class WeatherStation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false, length = 20)
    private String stationId;

    @Column(nullable = false, length = 100)
    private String stationName;

    @Column(nullable = false, length = 10)
    private String stationType;   // ASOS | AWS

    @Column(nullable = false, columnDefinition = "GEOMETRY(Point, 4326)")
    private Point location;

    @Column(length = 100)
    private String region;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public WeatherStation(String stationId, String stationName, String stationType,
                          Point location, String region) {
        this.stationId = stationId;
        this.stationName = stationName;
        this.stationType = stationType;
        this.location = location;
        this.region = region;
        this.createdAt = LocalDateTime.now();
    }
}
