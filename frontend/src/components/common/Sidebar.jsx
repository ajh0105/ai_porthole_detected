import { NavLink } from 'react-router-dom'
import './Sidebar.css'

const MENU = [
  { path: '/',            label: '대시보드',        icon: '📊' },
  { path: '/road-damage', label: '도로 파손 현황',  icon: '🕳️' },
  { path: '/blackice',    label: '블랙아이스 예측', icon: '❄️' },
  { path: '/report',      label: '보고서',          icon: '📄' },
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="logo-icon">🗺️</span>
        <span className="logo-text">RoadGIS</span>
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
    </aside>
  )
}
