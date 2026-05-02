import { useEffect, useState } from 'react'
import type { Lang } from '../i18n/strings'
import { t } from '../i18n/strings'
import { TRADE_ICONS } from '../App'

interface DashboardData {
  total_workers: number
  active_workers: number
  placed_this_month: number
  active_jobs: number
  total_employers: number
  total_applications: number
  placement_rate: number
  top_trades: { trade: string; count: number }[]
}

export default function Dashboard({ lang }: { lang: Lang }) {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetch('/api/v1/dashboard')
      .then(r => r.json())
      .then(setData)
      .catch(() => setError(true))
  }, [])

  if (error) return <div className="empty">{t(lang, 'error')}</div>
  if (!data) return <div className="empty">{t(lang, 'loading')}</div>

  const maxCount = Math.max(...(data.top_trades?.map(t => t.count) ?? [1]), 1)

  return (
    <div>
      <h1 className="page-title">📊 {t(lang, 'dashboard')}</h1>
      <div className="kpi-grid">
        {[
          [t(lang, 'totalWorkers'), data.total_workers, '👷'],
          [t(lang, 'activeWorkers'), data.active_workers, '🔍'],
          [t(lang, 'placedWorkers'), data.placed_this_month, '✅'],
          [t(lang, 'activeJobs'), data.active_jobs, '💼'],
          [t(lang, 'totalEmployers'), data.total_employers, '🏢'],
          [t(lang, 'totalApplications'), data.total_applications, '📋'],
          [t(lang, 'placementRate'), `${data.placement_rate}%`, '📈'],
        ].map(([label, value, icon]) => (
          <div className="kpi-card" key={String(label)}>
            <div className="label">{icon} {label}</div>
            <div className="value">{value}</div>
          </div>
        ))}
      </div>

      {data.top_trades?.length > 0 && (
        <div className="card">
          <h3>{t(lang, 'topTrades')}</h3>
          {data.top_trades.map(({ trade, count }) => (
            <div key={trade} style={{ marginBottom: '0.7rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.2rem' }}>
                <span>{TRADE_ICONS[trade] ?? '🔨'} {trade}</span>
                <span style={{ color: '#888' }}>{count} workers</span>
              </div>
              <div className="bar-container">
                <div className="bar-fill" style={{ width: `${(count / maxCount) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
