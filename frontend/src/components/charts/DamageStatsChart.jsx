import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = { pothole: '#c62828', crack: '#e65100' }
const LABELS = { pothole: '포트홀', crack: '균열' }

export default function DamageStatsChart({ data }) {
  const chartData = (data || []).map((d) => ({
    name: LABELS[d.type] || d.type,
    value: Number(d.count),
    color: COLORS[d.type] || '#999',
  }))

  return (
    <div style={{ background: 'white', borderRadius: 12, padding: 16, flex: 1, boxShadow: '0 1px 6px rgba(0,0,0,0.08)' }}>
      <h4 style={{ marginBottom: 8, fontSize: 14, color: '#333' }}>도로 파손 유형 분포</h4>
      {chartData.length === 0 ? (
        <p style={{ color: '#aaa', fontSize: 13, textAlign: 'center', paddingTop: 40 }}>데이터 없음</p>
      ) : (
        <ResponsiveContainer width="100%" height={160}>
          <PieChart>
            <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={60} label>
              {chartData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
