import api from '../api/axiosInstance'
import './ReportPage.css'

export default function ReportPage() {
  const download = async (type) => {
    try {
      const res = await api.get(`/report/${type}`, { responseType: 'blob' })
      const ext  = type === 'excel' ? 'xlsx' : 'pdf'
      const url  = URL.createObjectURL(res.data)
      const a    = document.createElement('a')
      a.href     = url
      a.download = `road_report.${ext}`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      alert('보고서 생성에 실패했습니다.')
    }
  }

  return (
    <div className="report-page">
      <h2>보고서 생성</h2>
      <p className="report-desc">
        현재 도로 파손 및 블랙아이스 위험도 데이터를 기반으로 보고서를 생성합니다.
      </p>
      <div className="report-cards">
        <div className="report-card">
          <div className="report-icon">📊</div>
          <h3>Excel 보고서</h3>
          <p>도로 파손 및 블랙아이스 데이터를 Excel 형식으로 다운로드합니다.</p>
          <button className="btn-download" onClick={() => download('excel')}>
            Excel 다운로드 (.xlsx)
          </button>
        </div>
        <div className="report-card">
          <div className="report-icon">📄</div>
          <h3>PDF 보고서</h3>
          <p>요약 통계와 최근 탐지 목록이 포함된 PDF 보고서를 다운로드합니다.</p>
          <button className="btn-download" onClick={() => download('pdf')}>
            PDF 다운로드 (.pdf)
          </button>
        </div>
      </div>
    </div>
  )
}
