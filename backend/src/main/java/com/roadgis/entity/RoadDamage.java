package com.roadgis.entity;

import jakarta.persistence.*;
import lombok.*;
import org.locationtech.jts.geom.Point;
import java.time.LocalDateTime;

@Entity
@Table(name = "road_damage")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class RoadDamage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 20)
    private String damageType;   // pothole | crack

    @Column(nullable = false)
    private Double confidence;

    @Column(nullable = false, columnDefinition = "GEOMETRY(Point, 4326)")
    private Point location;

    @Column(length = 500)
    private String imagePath;

    @Column(name = "bbox_x") private Double bboxX;
    @Column(name = "bbox_y") private Double bboxY;
    @Column(name = "bbox_w") private Double bboxW;
    @Column(name = "bbox_h") private Double bboxH;

    @Column(length = 200)
    private String roadName;

    @Column(length = 100)
    private String district;

    @Column(nullable = false)
    private LocalDateTime detectedAt;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public RoadDamage(String damageType, Double confidence, Point location,
                      String imagePath, Double bboxX, Double bboxY, Double bboxW, Double bboxH,
                      String roadName, String district, LocalDateTime detectedAt) {
        this.damageType = damageType;
        this.confidence = confidence;
        this.location = location;
        this.imagePath = imagePath;
        this.bboxX = bboxX;
        this.bboxY = bboxY;
        this.bboxW = bboxW;
        this.bboxH = bboxH;
        this.roadName = roadName;
        this.district = district;
        this.detectedAt = detectedAt != null ? detectedAt : LocalDateTime.now();
        this.createdAt = LocalDateTime.now();
    }
}
