import { create } from 'zustand'
import { useEffect } from 'react'

// Zustand 토스트 스토어
export const useToastStore = create((set) => ({
  toasts: [],
  show: (message, type = 'info') => {
    const id = Date.now()
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }))
    setTimeout(() => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })), 3500)
  },
}))

const TYPE_COLOR = { info: '#1565c0', success: '#2e7d32', error: '#c62828', warning: '#e65100' }

export default function ToastContainer() {
  const toasts = useToastStore((s) => s.toasts)
  return (
    <div style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 9999, display: 'flex', flexDirection: 'column', gap: 8 }}>
      {toasts.map((t) => (
        <div key={t.id} style={{
          background: TYPE_COLOR[t.type] || '#333',
          color: 'white',
          padding: '12px 20px',
          borderRadius: 10,
          fontSize: 14,
          fontWeight: 500,
          boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
          animation: 'slideIn 0.25s ease',
          maxWidth: 360,
        }}>
          {t.message}
        </div>
      ))}
      <style>{`@keyframes slideIn { from { transform: translateX(40px); opacity: 0; } to { transform: none; opacity: 1; } }`}</style>
    </div>
  )
}
