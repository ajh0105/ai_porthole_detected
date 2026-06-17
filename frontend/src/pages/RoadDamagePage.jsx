import { useState, useEffect, useRef } from 'react'
import { roadDamageApi } from '../api/roadDamageApi'
import { IS_DEMO } from '../api/mockData'
import './DataPage.css'

const DAMAGE_BADGE = { pothole: { label: '포트홀', color: '#c62828' }, crack: { label: '균열', color: '#e65100' } }

const HF_URL = 'https://huggingface.co/spaces/ajh0105/road-damage-ai'

export default function RoadDamagePage() {
  const [data, setData] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [filter, setFilter] = useState({ damageType: '', district: '' })
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const fileRef = useRef()

  const fetchData = () => {
    setLoading(true)
    const params = { page, size: 20, ...Object.fromEntries(Object.entries(filter).filter(([,v]) => v)) }
    roadDamageApi.getList(params)
      .then((res) => { setData(res.data.data.content); setTotal(res.data.data.totalElements) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchData() }, [page, filter])

  const handleUpload = async (e) => {
    const files = Array.from(e.target.files)
    if (!files.length) return
    if (IS_DEMO) {
      alert('데모 모드에서는 실제 AI 탐지가 지원되지 않습니다.\n\nYOLOv11 탐지 기능은 Hugging Face Space에서 직접 체험해보세요:\n' + HF_URL)
      e.target.value = ''
      return
    }
    setUploading(true)
    try {
      await roadDamageApi.upload(files)
      alert('AI 탐지 파이프라인 실행 완료')
      fetchData()
    } catch {
      alert('업로드 실패')
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  const handleDelete = async (id) => {
    if (IS_DEMO) {
      alert('데모 모드에서는 삭제가 지원되지 않습니다.')
      return
    }
    if (!confirm('삭제하시겠습니까?')) return
    await roadDamageApi.delete(id)
    fetchData()
  }

  const totalPages = Math.ceil(total / 20)

  return (
    <div className="data-page">
      <div className="page-header">
        <h2>도로 파손 현황</h2>
        <div className="page-actions">
          {IS_DEMO && (
            <a className="btn-hf" href={HF_URL} target="_blank" rel="noopener noreferrer">
              🤗 AI 탐지 체험 (Hugging Face)
            </a>
          )}
          <input
            ref={fileRef}
            type="file"
            multiple
            accept="image/*,video/*"
            style={{ display: 'none' }}
            onChange={handleUpload}
          />
          <button className="btn-primary" onClick={() => fileRef.current.click()} disabled={uploading}>
            {uploading ? '처리 중...' : '영상/이미지 업로드'}
          </button>
        </div>
      </div>

      <div className="filter-bar">
        <select value={filter.damageType} onChange={(e) => setFilter(f => ({ ...f, damageType: e.target.value }))}>
          <option value="">전체 유형</option>
          <option value="pothole">포트홀</option>
          <option value="crack">균열</option>
        </select>
        <input
          type="text"
          placeholder="행정구역 검색"
          value={filter.district}
          onChange={(e) => setFilter(f => ({ ...f, district: e.target.value }))}
        />
        <span className="total-count">총 {total.toLocaleString()}건</span>
      </div>

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th><th>유형</th><th>신뢰도</th><th>위도</th><th>경도</th>
              <th>도로명</th><th>행정구역</th><th>탐지일시</th><th>삭제</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={9} className="loading-cell">로딩 중...</td></tr>
            ) : data.length === 0 ? (
              <tr><td colSpan={9} className="empty-cell">데이터가 없습니다.</td></tr>
            ) : data.map((row) => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td>
                  <span className="badge" style={{ background: DAMAGE_BADGE[row.damageType]?.color }}>
                    {DAMAGE_BADGE[row.damageType]?.label || row.damageType}
                  </span>
                </td>
                <td>{(row.confidence * 100).toFixed(1)}%</td>
                <td>{row.latitude?.toFixed(5)}</td>
                <td>{row.longitude?.toFixed(5)}</td>
                <td>{row.roadName || '-'}</td>
                <td>{row.district || '-'}</td>
                <td>{row.detectedAt?.replace('T', ' ')?.slice(0, 16)}</td>
                <td>
                  <button className="btn-delete" onClick={() => handleDelete(row.id)}>삭제</button>
                </td>
              </tr>
            ))}
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
