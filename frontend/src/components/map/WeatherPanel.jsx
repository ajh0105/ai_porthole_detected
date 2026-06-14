import { useEffect, useState } from 'react'
import { blackIceApi } from '../../api/blackIceApi'
import { useMapStore } from '../../store/mapStore'
import './WeatherPanel.css'

const RISK_COLOR = ['#90a4ae', '#ffd54f', '#ff9800', '#c62828']
const RISK_BG    = ['#eceff1', '#fffde7', '#fff3e0', '#ffebee']

export default function WeatherPanel() {
  const { selectedRegion } = useMapStore()
  const [weather, setWeather] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!selectedRegion) {
      setWeather(null)
      return
    }
    setLoading(true)
    blackIceApi
      .getRegionWeather(selectedRegion.lat, selectedRegion.lng)
      .then((r) => setWeather(r.data.data))
      .catch(() => setWeather(null))
      .finally(() => setLoading(false))
  }, [selectedRegion])

  if (!selectedRegion) return null

  const risk = weather?.riskLevel ?? null
  const panelStyle = risk !== null
    ? { borderLeft: `4px solid ${RISK_COLOR[risk]}`, background: RISK_BG[risk] }
    : {}

  return (
    <div className="weather-panel" style={panelStyle}>
      <div className="weather-panel-header">
        <span className="weather-icon">🌡️</span>
        <div>
          <div className="weather-region-name">{selectedRegion.region}</div>
          <div className="weather-station-name">관측소: {selectedRegion.stationName}</div>
        </div>
        {risk !== null && (
          <span
            className="weather-risk-badge"
            style={{ background: RISK_COLOR[risk], color: risk === 1 ? '#795548' : '#fff' }}
          >
            블랙아이스 {weather.riskLabel}
          </span>
        )}
      </div>

      {loading && <div className="weather-loading">로딩 중...</div>}

      {!loading && weather && !weather.message && (
        <div className="weather-grid">
          <WeatherItem icon="🌡️" label="기온" value={`${weather.temperature}°C`} />
          <WeatherItem icon="💧" label="습도" value={`${weather.humidity}%`} />
          <WeatherItem icon="🌧️" label="강수량" value={`${weather.precipitation ?? 0}mm`} />
          <WeatherItem icon="💨" label="풍속" value={`${weather.windSpeed}m/s`} />
        </div>
      )}

      {!loading && weather?.message && (
        <div className="weather-empty">{weather.message}</div>
      )}

      {!loading && weather && !weather.message && (
        <div className="weather-updated">
          예측시각: {weather.predictedAt?.replace('T', ' ')?.slice(0, 16)}
        </div>
      )}
    </div>
  )
}

function WeatherItem({ icon, label, value }) {
  return (
    <div className="weather-item">
      <span className="weather-item-icon">{icon}</span>
      <span className="weather-item-label">{label}</span>
      <span className="weather-item-value">{value}</span>
    </div>
  )
}
