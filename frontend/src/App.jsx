import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import RoadDamagePage from './pages/RoadDamagePage'
import BlackIcePage from './pages/BlackIcePage'
import ReportPage from './pages/ReportPage'
import Sidebar from './components/common/Sidebar'
import Header from './components/common/Header'
import ErrorBoundary from './components/common/ErrorBoundary'
import ToastContainer from './components/common/Toast'
import './App.css'

// BASE_URL은 dev에서 '/', 프로덕션(GitHub Pages)에서 '/ai_porthole_detected/'
const basename = import.meta.env.BASE_URL.replace(/\/$/, '') || '/'

function PrivateLayout({ children }) {
  const token = useAuthStore((s) => s.token)
  if (!token) return <Navigate to="/login" replace />
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Header />
        <div className="app-content">
          <ErrorBoundary>{children}</ErrorBoundary>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter basename={basename}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/"             element={<PrivateLayout><DashboardPage /></PrivateLayout>} />
        <Route path="/road-damage"  element={<PrivateLayout><RoadDamagePage /></PrivateLayout>} />
        <Route path="/blackice"     element={<PrivateLayout><BlackIcePage /></PrivateLayout>} />
        <Route path="/report"       element={<PrivateLayout><ReportPage /></PrivateLayout>} />
        <Route path="*"             element={<Navigate to="/" replace />} />
      </Routes>
      <ToastContainer />
    </BrowserRouter>
  )
}
