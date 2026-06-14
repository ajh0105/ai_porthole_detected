import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const COLORS = ['#90a4ae', '#ffd54f', '#ff9800', '#c62828']
const LABELS = ['안전', '관심', '주의', '위험']

export default function RiskLevelChart({ data }) {
  const chartData = LABELS.map((label, i) => {
    const found = (data || []).find((d) => Number(d.level) === i)
    return { name: label, value: found ? Number(found.count) : 0, color: COLORS[i] }
  })

  return (
    <div style={{ background: 'white', borderRadius: 12, padding: 16, flex: 1, boxShadow: '0 1px 6px rgba(0,0,0,0.08)' }}>
      <h4 style={{ marginBottom: 8, fontSize: 14, color: '#333' }}>블랙아이스 위험도 분포</h4>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="value" name="건수" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
