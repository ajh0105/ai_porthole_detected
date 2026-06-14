package com.roadgis.repository;

import com.roadgis.entity.BlackIceRisk;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public interface BlackIceRiskRepository extends JpaRepository<BlackIceRisk, Long> {

    @Query("""
        SELECT b FROM BlackIceRisk b
        WHERE (:riskLevel IS NULL OR b.riskLevel = :riskLevel)
          AND (:stationId IS NULL OR b.stationId = :stationId)
          AND (:dateFrom IS NULL OR b.predictedAt >= :dateFrom)
          AND (:dateTo IS NULL OR b.predictedAt <= :dateTo)
        """)
    Page<BlackIceRisk> findWithFilters(
            @Param("riskLevel") Short riskLevel,
            @Param("stationId") String stationId,
            @Param("dateFrom") LocalDateTime dateFrom,
            @Param("dateTo") LocalDateTime dateTo,
            Pageable pageable
    );

    @Query(value = """
        SELECT * FROM blackice_risk
        WHERE ST_Within(location, ST_MakeEnvelope(:minLng, :minLat, :maxLng, :maxLat, 4326))
        """, nativeQuery = true)
    List<BlackIceRisk> findWithinBbox(
            @Param("minLng") double minLng,
            @Param("minLat") double minLat,
            @Param("maxLng") double maxLng,
            @Param("maxLat") double maxLat
    );

    @Query("SELECT b.riskLevel as level, b.riskLabel as label, COUNT(b) as count FROM BlackIceRisk b GROUP BY b.riskLevel, b.riskLabel ORDER BY b.riskLevel")
    List<Map<String, Object>> countByRiskLevel();

    List<BlackIceRisk> findByStationIdAndPredictedAtBetween(String stationId, LocalDateTime from, LocalDateTime to);

    // 관측소별 최신 예측 1건씩 (전체 관측소 현황)
    @Query(value = """
        SELECT DISTINCT ON (station_id) *
        FROM blackice_risk
        ORDER BY station_id, predicted_at DESC
        """, nativeQuery = true)
    List<BlackIceRisk> findLatestPerStation();

    // 특정 관측소의 가장 최근 예측 1건
    @Query(value = """
        SELECT * FROM blackice_risk
        WHERE station_id = :stationId
        ORDER BY predicted_at DESC
        LIMIT 1
        """, nativeQuery = true)
    Optional<BlackIceRisk> findLatestByStationId(@Param("stationId") String stationId);

    // 좌표에서 가장 가까운 관측소의 최신 예측 1건
    @Query(value = """
        SELECT b.* FROM blackice_risk b
        JOIN weather_station ws ON b.station_id = ws.station_id
        ORDER BY ST_Distance(ws.location, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)),
                 b.predicted_at DESC
        LIMIT 1
        """, nativeQuery = true)
    Optional<BlackIceRisk> findLatestNearestToPoint(@Param("lat") double lat, @Param("lng") double lng);
}
