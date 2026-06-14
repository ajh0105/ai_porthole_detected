package com.roadgis.repository;

import com.roadgis.entity.RoadDamage;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

public interface RoadDamageRepository extends JpaRepository<RoadDamage, Long> {

    @Query("""
        SELECT r FROM RoadDamage r
        WHERE (:damageType IS NULL OR r.damageType = :damageType)
          AND (:district IS NULL OR r.district = :district)
          AND (:dateFrom IS NULL OR r.detectedAt >= :dateFrom)
          AND (:dateTo IS NULL OR r.detectedAt <= :dateTo)
        """)
    Page<RoadDamage> findWithFilters(
            @Param("damageType") String damageType,
            @Param("district") String district,
            @Param("dateFrom") LocalDateTime dateFrom,
            @Param("dateTo") LocalDateTime dateTo,
            Pageable pageable
    );

    // 지도용 bbox 내 데이터 조회 (PostGIS ST_Within)
    @Query(value = """
        SELECT * FROM road_damage
        WHERE ST_Within(location, ST_MakeEnvelope(:minLng, :minLat, :maxLng, :maxLat, 4326))
        """, nativeQuery = true)
    List<RoadDamage> findWithinBbox(
            @Param("minLng") double minLng,
            @Param("minLat") double minLat,
            @Param("maxLng") double maxLng,
            @Param("maxLat") double maxLat
    );

    // 유형별 통계
    @Query("SELECT r.damageType as type, COUNT(r) as count FROM RoadDamage r GROUP BY r.damageType")
    List<Map<String, Object>> countByDamageType();

    // 구역별 통계
    @Query("SELECT r.district as district, COUNT(r) as count FROM RoadDamage r GROUP BY r.district ORDER BY count DESC")
    List<Map<String, Object>> countByDistrict();

    long countByDamageType(String damageType);

    @Query("SELECT DISTINCT r.district FROM RoadDamage r WHERE r.district IS NOT NULL ORDER BY r.district")
    List<String> findDistinctDistricts();
}
