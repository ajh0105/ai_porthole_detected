import { useAuthStore } from '../../store/authStore'
import './Header.css'

export default function Header() {
  const { username, logout } = useAuthStore()

  return (
    <header className="header">
      <div className="header-title">GIS 기반 도로 안전 관제 플랫폼</div>
      <div className="header-right">
        <span className="header-user">{username}</span>
        <button className="logout-btn" onClick={logout}>로그아웃</button>
      </div>
    </header>
  )
}
