import { NavLink } from 'react-router-dom'
import { IS_DEMO } from '../../api/mockData'
import './Sidebar.css'

const MENU = [
  { path: '/',            label: '대시보드',        icon: '📊' },
  { path: '/road-damage', label: '도로 파손 현황',  icon: '🕳️' },
  { path: '/blackice',    label: '블랙아이스 예측', icon: '❄️' },
  { path: '/report',      label: '보고서',          icon: '📄' },
]

const HF_URL = 'https://huggingface.co/spaces/simonahn/ai_porthole_detected'

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="logo-icon">🗺️</span>
        <span className="logo-text">RoadGIS</span>
        {IS_DEMO && <span className="logo-demo">DEMO</span>}
      </div>
      <nav className="sidebar-nav">
        {MENU.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>
      {IS_DEMO && (
        <div className="sidebar-hf">
          <a href={HF_URL} target="_blank" rel="noopener noreferrer" className="hf-link">
            🤗 AI 기능 직접 체험
            <span className="hf-sub">Hugging Face Space</span>
          </a>
        </div>
      )}
    </aside>
  )
}
