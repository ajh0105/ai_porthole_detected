import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={styles.container}>
          <div style={styles.box}>
            <div style={styles.icon}>⚠️</div>
            <h2 style={styles.title}>화면을 불러오는 중 오류가 발생했습니다</h2>
            <p style={styles.message}>{this.state.error?.message}</p>
            <button style={styles.btn} onClick={() => this.setState({ hasError: false, error: null })}>
              다시 시도
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

const styles = {
  container: { display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' },
  box: { textAlign: 'center', padding: '40px', background: 'white', borderRadius: '14px', maxWidth: '480px', boxShadow: '0 2px 16px rgba(0,0,0,0.1)' },
  icon: { fontSize: '48px', marginBottom: '16px' },
  title: { fontSize: '18px', fontWeight: '700', marginBottom: '8px', color: '#333' },
  message: { fontSize: '13px', color: '#888', marginBottom: '24px' },
  btn: { padding: '10px 24px', background: '#1565c0', color: 'white', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', cursor: 'pointer' },
}
