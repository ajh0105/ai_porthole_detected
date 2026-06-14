import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMapEvents } from 'react-leaflet'
import { useMapStore } from '../../store/mapStore'
import { roadDamageApi } from '../../api/roadDamageApi'
import { blackIceApi } from '../../api/blackIceApi'
import 'leaflet/dist/leaflet.css'
import './RoadMap.css'

const DAMAGE_COLOR  = { pothole: '#c62828', crack: '#e65100' }
const BLACKICE_COLOR = ['#90a4ae', '#ffd54f', '#ff9800', '#c62828']  // 0~3

function MapEventHandler({ onBoundsChange }) {
  useMapEvents({
    moveend: (e) => {
      const b = e.target.getBounds()
      onBoundsChange([b.getWest(), b.getSouth(), b.getEast(), b.getNorth()])
    },
  })
  return null
}

export default function RoadMap() {
  const { showDamage, showBlackIce, bbox, setBbox, selectedDistrict } = useMapStore()
  const [damageData, setDamageData]  = useState([])
  const [blackIceData, setBlackIceData] = useState([])

  useEffect(() => {
    if (showDamage) {
      roadDamageApi.getMapData(bbox)
        .then((res) => setDamageData(res.data.data || []))
        .catch(() => {})
    } else {
      setDamageData([])
    }
  }, [bbox, showDamage])

  useEffect(() => {
    if (showBlackIce) {
      blackIceApi.getMapData(bbox)
        .then((res) => setBlackIceData(res.data.data || []))
        .catch(() => {})
    } else {
      setBlackIceData([])
    }
  }, [bbox, showBlackIce])

  // 법정동 필터: 선택된 district와 일치하는 마커만 표시
  const filteredDamage = selectedDistrict
    ? damageData.filter((f) => f.properties.district === selectedDistrict)
    : damageData

  return (
    <div className="map-wrapper">
      <MapContainer
        center={[36.5, 127.8]}
        zoom={7}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="© OpenStreetMap contributors"
        />
        <MapEventHandler onBoundsChange={setBbox} />

        {filteredDamage.map((f) => (
          <CircleMarker
            key={`d-${f.id}`}
            center={[f.geometry.coordinates[1], f.geometry.coordinates[0]]}
            radius={8}
            fillColor={DAMAGE_COLOR[f.properties.damageType] || '#999'}
            color="white"
            weight={1.5}
            fillOpacity={0.85}
          >
            <Popup>
              <strong>{f.properties.damageType === 'pothole' ? '포트홀' : '균열'}</strong><br />
              신뢰도: {(f.properties.confidence * 100).toFixed(1)}%<br />
              도로명: {f.properties.roadName || '-'}<br />
              행정구역: {f.properties.district || '-'}<br />
              탐지일시: {f.properties.detectedAt?.replace('T', ' ')?.slice(0, 16)}
            </Popup>
          </CircleMarker>
        ))}

        {blackIceData.map((f) => (
          <CircleMarker
            key={`b-${f.id}`}
            center={[f.geometry.coordinates[1], f.geometry.coordinates[0]]}
            radius={12}
            fillColor={BLACKICE_COLOR[f.properties.riskLevel] || '#90a4ae'}
            color="white"
            weight={1.5}
            fillOpacity={0.75}
          >
            <Popup>
              <strong>블랙아이스 {f.properties.riskLabel}</strong><br />
              관측소: {f.properties.stationId}<br />
              기온: {f.properties.temperature}°C<br />
              예측일시: {f.properties.predictedAt?.replace('T', ' ')?.slice(0, 16)}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      <div className="map-legend">
        <div className="legend-title">범례</div>
        <div className="legend-section">도로 파손</div>
        <div className="legend-item"><span style={{background:'#c62828'}} />포트홀</div>
        <div className="legend-item"><span style={{background:'#e65100'}} />균열</div>
        <div className="legend-section" style={{marginTop:8}}>블랙아이스</div>
        {['안전','관심','주의','위험'].map((l, i) => (
          <div key={i} className="legend-item">
            <span style={{background: BLACKICE_COLOR[i]}} />{l}
          </div>
        ))}
      </div>
    </div>
  )
}
