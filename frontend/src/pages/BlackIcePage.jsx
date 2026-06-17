import { useState, useEffect, useCallback } from 'react'
import { blackIceApi } from '../api/blackIceApi'
import { IS_DEMO } from '../api/mockData'
import './DataPage.css'
import './BlackIcePage.css'

const RISK_STYLE = [
  { label: '안전', color: '#607d8b', bg: '#eceff1' },
  { label: '관심', color: '#f9a825', bg: '#fffde7' },
  { label: '주의', color: '#e65100', bg: '#fff3e0' },
  { label: '위험', color: '#c62828', bg: '#ffebee' },
]

const STATION_NAME = { '108': '서울', '119': '수원', '133': '대전', '143': '대구', '156': '광주', '159': '부산' }

const HF_URL = 'https://huggingface.co/spaces/ajh0105/road-damage-ai'

export default function BlackIcePage() {
  const [data, setData] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [riskLevel, setRiskLevel] = useState('')
  const [predicting, setPredicting] = useState(false)
  const [loading, setLoading] = useState(false)

  const [currentWeather, setCurrentWeather] = useState([])
  const [weatherLoading, setWeatherLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchCurrentWeather = useCallback(() => {
    setWeatherLoading(true)
    blackIceApi.getCurrentWeather()
      .then((r) => {
        setCurrentWeather(r.data.data || [])
        setLastUpdated(new Date())
      })
      .catch(() => {})
      .finally(() => setWeatherLoading(false))
  }, [])

  const fetchList = useCallback(() => {
    setLoading(true)
    const params = { page, size: 20, ...(riskLevel !== '' ? { riskLevel } : {}) }
    blackIceApi.getList(params)
      .then((res) => { setData(res.data.data.content); setTotal(res.data.data.totalElements) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [page, riskLevel])

  useEffect(() => { fetchCurrentWeather() }, [fetchCurrentWeather])
  useEffect(() => { fetchList() }, [fetchList])

  const handlePredict = async () => {
    if (IS_DEMO) {
      alert('데모 모드에서는 실시간 기상 API 연동이 지원되지 않습니다.\n\nXGBoost + LightGBM 앙상블 예측 기능은 Hugging Face Space에서 체험해보세요:\n' + HF_URL)
      return
    }
    setPredicting(true)
    try {
      await blackIceApi.predict()
      alert('블랙아이스 예측 완료')
      fetchList()
      fetchCurrentWeather()
    } catch {
      alert('예측 실패. AI 서버 연결을 확인하세요.')
    } finally {
      setPredicting(false)
    }
  }

  const totalPages = Math.ceil(total / 20)

  return (
    <div className="data-page">
      <div className="page-header">
        <h2>블랙아이스 위험 예측</h2>
        <div className="page-actions">
          {IS_DEMO && (
            <a className="btn-hf" href={HF_URL} target="_blank" rel="noopener noreferrer">
              🤗 AI 예측 체험 (Hugging Face)
            </a>
          )}
          <button className="btn-primary" onClick={handlePredict} disabled={predicting}>
            {predicting ? '예측 중...' : '최신 기상 데이터로 예측 실행'}
          </button>
        </div>
      </div>

      <div className="current-weather-section">
        <div className="current-weather-header">
          <span className="section-title">관측소별 현재 기상 현황</span>
          <button
            className="refresh-btn"
            onClick={fetchCurrentWeather}
            disabled={weatherLoading}
            title="새로고침"
          >
            {weatherLoading ? '로딩...' : '↻ 새로고침'}
          </button>
          {lastUpdated && (
            <span className="last-updated">
              갱신: {lastUpdated.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </span>
          )}
        </div>

        {currentWeather.length === 0 && !weatherLoading ? (
          <div className="weather-empty-msg">
            예측 데이터가 없습니다. 상단 버튼으로 예측을 실행하세요.
          </div>
        ) : (
          <div className="station-cards">
            {currentWeather.map((w) => {
              const style = RISK_STYLE[w.riskLevel] || RISK_STYLE[0]
              return (
                <div
                  key={w.stationId}
                  className="station-card"
                  style={{ borderTop: `4px solid ${style.color}`, background: style.bg }}
                >
                  <div className="station-card-title">
                    {STATION_NAME[w.stationId] || w.stationId}
                    <span className="risk-badge" style={{ background: style.color }}>
                      {w.riskLabel}
                    </span>
                  </div>
                  <div className="station-metrics">
                    <Metric icon="🌡️" label="기온" value={`${w.temperature?.toFixed(1)}°C`} />
                    <Metric icon="💧" label="습도" value={`${w.humidity?.toFixed(0)}%`} />
                    <Metric icon="🌧️" label="강수" value={`${w.precipitation?.toFixed(1) ?? 0}mm`} />
                    <Metric icon="💨" label="풍속" value={`${w.windSpeed?.toFixed(1)}m/s`} />
                  </div>
                  <div className="station-card-time">
                    {w.predictedAt?.replace('T', ' ')?.slice(0, 16)}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      <div className="filter-bar" style={{ marginTop: 16 }}>
        <select value={riskLevel} onChange={(e) => { setRiskLevel(e.target.value); setPage(0) }}>
          <option value="">전체 위험도</option>
          <option value="0">0 - 안전</option>
          <option value="1">1 - 관심</option>
          <option value="2">2 - 주의</option>
          <option value="3">3 - 위험</option>
        </select>
        <span className="total-count">예측 이력 총 {total.toLocaleString()}건</span>
      </div>

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th><th>관측소</th><th>위험도</th><th>기온(°C)</th>
              <th>습도(%)</th><th>강수량(mm)</th><th>풍속(m/s)</th><th>예측일시</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={8} className="loading-cell">로딩 중...</td></tr>
            ) : data.length === 0 ? (
              <tr><td colSpan={8} className="empty-cell">데이터가 없습니다.</td></tr>
            ) : data.map((row) => {
              const style = RISK_STYLE[row.riskLevel] || RISK_STYLE[0]
              return (
                <tr key={row.id}>
                  <td>{row.id}</td>
                  <td>{STATION_NAME[row.stationId] || row.stationId}</td>
                  <td>
                    <span className="badge" style={{ background: style.color }}>
                      L{row.riskLevel} {style.label}
                    </span>
                  </td>
                  <td>{row.temperature?.toFixed(1) ?? '-'}</td>
                  <td>{row.humidity?.toFixed(1) ?? '-'}</td>
                  <td>{row.precipitation?.toFixed(1) ?? '-'}</td>
                  <td>{row.windSpeed?.toFixed(1) ?? '-'}</td>
                  <td>{row.predictedAt?.replace('T', ' ')?.slice(0, 16)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <button onClick={() => setPage(0)} disabled={page === 0}>처음</button>
        <button onClick={() => setPage(p => p - 1)} disabled={page === 0}>이전</button>
        <span>{page + 1} / {totalPages || 1}</span>
        <button onClick={() => setPage(p => p + 1)} disabled={page >= totalPages - 1}>다음</button>
        <button onClick={() => setPage(totalPages - 1)} disabled={page >= totalPages - 1}>끝</button>
      </div>
    </div>
  )
}

function Metric({ icon, label, value }) {
  return (
    <div className="metric">
      <span className="metric-icon">{icon}</span>
      <span className="metric-label">{label}</span>
      <span className="metric-value">{value}</span>
    </div>
  )
}
