package com.roadgis.service;

import com.roadgis.exception.BusinessException;
import com.roadgis.repository.RoadDamageRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

import java.util.Collections;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.BDDMockito.*;

@ExtendWith(MockitoExtension.class)
class RoadDamageServiceTest {

    @Mock RoadDamageRepository repository;
    @InjectMocks RoadDamageService service;

    @Test
    @DisplayName("유효하지 않은 damageType으로 조회 시 BAD_REQUEST")
    void findAll_invalidDamageType() {
        assertThatThrownBy(() ->
                service.findAll("invalid", null, null, null, PageRequest.of(0, 10)))
                .isInstanceOf(BusinessException.class)
                .hasMessageContaining("pothole | crack");
    }

    @Test
    @DisplayName("존재하지 않는 ID 조회 시 NOT_FOUND")
    void findById_notFound() {
        given(repository.findById(999L)).willReturn(Optional.empty());

        assertThatThrownBy(() -> service.findById(999L))
                .isInstanceOf(BusinessException.class)
                .hasMessageContaining("999");
    }

    @Test
    @DisplayName("잘못된 bbox 범위 시 BAD_REQUEST")
    void getGeoJson_invalidBbox() {
        // minLng >= maxLng
        assertThatThrownBy(() -> service.getGeoJson(130.0, 35.0, 125.0, 38.0))
                .isInstanceOf(BusinessException.class)
                .hasMessageContaining("bbox");
    }

    @Test
    @DisplayName("존재하지 않는 ID 삭제 시 NOT_FOUND")
    void delete_notFound() {
        given(repository.existsById(999L)).willReturn(false);

        assertThatThrownBy(() -> service.delete(999L))
                .isInstanceOf(BusinessException.class)
                .hasMessageContaining("999");
    }

    @Test
    @DisplayName("pothole 타입 필터 정상 조회")
    void findAll_potholeFilter() {
        given(repository.findWithFilters(eq("pothole"), any(), any(), any(), any()))
                .willReturn(new PageImpl<>(Collections.emptyList()));

        var result = service.findAll("pothole", null, null, null, PageRequest.of(0, 10));
        assertThat(result).isNotNull();
        assertThat(result.getTotalElements()).isZero();
    }
}
