import { useEffect, useState } from 'react'
import { useMapStore } from '../../store/mapStore'
import { blackIceApi } from '../../api/blackIceApi'
import { roadDamageApi } from '../../api/roadDamageApi'
import './RegionFilter.css'

export default function RegionFilter() {
  const { selectedRegion, selectedDistrict, setSelectedRegion, setSelectedDistrict, setBbox } = useMapStore()
  const [stations, setStations] = useState([])
  const [districts, setDistricts] = useState([])

  useEffect(() => {
    blackIceApi.getStations().then((r) => setStations(r.data.data || [])).catch(() => {})
    roadDamageApi.getDistricts().then((r) => setDistricts(r.data.data || [])).catch(() => {})
  }, [])

  const handleRegionChange = (e) => {
    const stationId = e.target.value
    if (!stationId) {
      setSelectedRegion(null)
      setSelectedDistrict(null)
      return
    }
    const station = stations.find((s) => s.stationId === stationId)
    if (!station) return
    setSelectedRegion(station)
    setSelectedDistrict(null)
    // 선택 지역으로 지도 이동 (±0.5도 범위)
    setBbox([station.lng - 0.5, station.lat - 0.5, station.lng + 0.5, station.lat + 0.5])
  }

  const handleDistrictChange = (e) => {
    setSelectedDistrict(e.target.value || null)
  }

  const handleReset = () => {
    setSelectedRegion(null)
    setSelectedDistrict(null)
    setBbox([124.0, 33.0, 132.0, 39.0])
  }

  return (
    <div className="region-filter">
      <span className="region-filter-label">지역 필터</span>

      <select
        className="region-select"
        value={selectedRegion?.stationId || ''}
        onChange={handleRegionChange}
      >
        <option value="">시도 전체</option>
        {stations.map((s) => (
          <option key={s.stationId} value={s.stationId}>
            {s.region} ({s.stationName})
          </option>
        ))}
      </select>

      <select
        className="region-select"
        value={selectedDistrict || ''}
        onChange={handleDistrictChange}
        disabled={districts.length === 0}
      >
        <option value="">
          {districts.length === 0 ? '법정동 (탐지 데이터 없음)' : '법정동 전체'}
        </option>
        {districts.map((d) => (
          <option key={d} value={d}>{d}</option>
        ))}
      </select>

      {(selectedRegion || selectedDistrict) && (
        <button className="region-reset-btn" onClick={handleReset}>
          초기화
        </button>
      )}
    </div>
  )
}
