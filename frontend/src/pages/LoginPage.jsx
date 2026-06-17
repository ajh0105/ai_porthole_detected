import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { IS_DEMO } from '../api/mockData'
import api from '../api/axiosInstance'
import './LoginPage.css'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const setAuth = useAuthStore((s) => s.setAuth)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // 데모 모드: admin/admin1234 로 바로 로그인
    if (IS_DEMO) {
      if (username === 'admin' && password === 'admin1234') {
        setAuth('demo-token', username)
        navigate('/')
      } else {
        setError('데모 계정: admin / admin1234')
      }
      setLoading(false)
      return
    }

    try {
      const res = await api.post('/auth/login', { username, password })
      const { accessToken } = res.data.data
      setAuth(accessToken, username)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.message || '로그인에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">🗺️</div>
        <h1 className="login-title">RoadGIS</h1>
        <p className="login-subtitle">도로 안전 관제 플랫폼</p>

        {IS_DEMO && (
          <div className="demo-notice">
            <span className="demo-badge">DEMO</span>
            <span>포트폴리오 시연용 — 샘플 데이터로 동작합니다</span>
            <br />
            <small>계정: <strong>admin</strong> / <strong>admin1234</strong></small>
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>아이디</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={IS_DEMO ? 'admin' : '아이디 입력'}
              required
            />
          </div>
          <div className="form-group">
            <label>비밀번호</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>
          {error && <p className="login-error">{error}</p>}
          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? '로그인 중...' : '로그인'}
          </button>
        </form>
      </div>
    </div>
  )
}
