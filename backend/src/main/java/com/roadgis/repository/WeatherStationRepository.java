package com.roadgis.repository;

import com.roadgis.entity.WeatherStation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface WeatherStationRepository extends JpaRepository<WeatherStation, Long> {
    Optional<WeatherStation> findByStationId(String stationId);

    @Query("SELECT ws FROM WeatherStation ws ORDER BY ws.stationName")
    List<WeatherStation> findAllOrderByName();
}
