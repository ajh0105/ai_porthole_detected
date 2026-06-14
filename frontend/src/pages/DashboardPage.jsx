import { useEffect, useState } from 'react'
import { roadDamageApi } from '../api/roadDamageApi'
import { blackIceApi } from '../api/blackIceApi'
import { useMapStore } from '../store/mapStore'
import RoadMap from '../components/map/RoadMap'
import RegionFilter from '../components/map/RegionFilter'
import WeatherPanel from '../components/map/WeatherPanel'
import DamageStatsChart from '../components/charts/DamageStatsChart'
import RiskLevelChart from '../components/charts/RiskLevelChart'
import './DashboardPage.css'

export default function DashboardPage() {
  const [damageStats, setDamageStats] = useState(null)
  const [iceStats, setIceStats] = useState(null)
  const { showDamage, showBlackIce, setShowDamage, setShowBlackIce } = useMapStore()

  useEffect(() => {
    roadDamageApi.getStats().then((r) => setDamageStats(r.data.data)).catch(() => {})
    blackIceApi.getStats().then((r) => setIceStats(r.data.data)).catch(() => {})
  }, [])

  const cards = [
    { label: '전체 도로 파손', value: damageStats?.totalCount ?? '-', color: '#1565c0', icon: '🕳️' },
    { label: '포트홀', value: damageStats?.potholeCount ?? '-', color: '#c62828', icon: '⚠️' },
    { label: '균열', value: damageStats?.crackCount ?? '-', color: '#e65100', icon: '💢' },
    { label: '블랙아이스 예측', value: iceStats?.totalCount ?? '-', color: '#37474f', icon: '❄️' },
  ]

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>대시보드</h2>
        <div className="layer-toggles">
          <label className="toggle">
            <input type="checkbox" checked={showDamage} onChange={(e) => setShowDamage(e.target.checked)} />
            <span>도로 파손 레이어</span>
          </label>
          <label className="toggle">
            <input type="checkbox" checked={showBlackIce} onChange={(e) => setShowBlackIce(e.target.checked)} />
            <span>블랙아이스 레이어</span>
          </label>
        </div>
      </div>

      <RegionFilter />

      <div className="stat-cards">
        {cards.map((c) => (
          <div key={c.label} className="stat-card" style={{ borderLeft: `4px solid ${c.color}` }}>
            <span className="stat-icon">{c.icon}</span>
            <div>
              <div className="stat-value">{typeof c.value === 'number' ? c.value.toLocaleString() : c.value}</div>
              <div className="stat-label">{c.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-body">
        <div className="map-panel">
          <RoadMap />
        </div>
        <div className="chart-panel">
          <WeatherPanel />
          <DamageStatsChart data={damageStats?.byType || []} />
          <RiskLevelChart data={iceStats?.byRiskLevel || []} />
        </div>
      </div>
    </div>
  )
}
