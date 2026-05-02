import { useEffect, useState } from 'react'
import type { Lang } from '../i18n/strings'
import { t } from '../i18n/strings'
import { TRADE_ICONS } from '../App'

const DEMAND_COLOR: Record<string, string> = { high: '#1a7a4a', medium: '#a07800', low: '#c0392b' }

export default function MarketIntel({ lang }: { lang: Lang }) {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/v1/ai/market-intel')
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="empty">🔍 {t(lang, 'fetchingData')}</div>
  if (!data || data.error) return <div className="empty">{t(lang, 'error')}</div>

  const maxSalary = Math.max(...(data.top_trades?.map((t: any) => t.avg_salary_usd ?? 0) ?? [1]), 1)

  return (
    <div>
      <h1 className="page-title">📡 {t(lang, 'marketIntel')}</h1>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <div className="card">
          <h3>{t(lang, 'topTrades')}</h3>
          {data.top_trades?.map((item: any) => (
            <div key={item.trade} style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.2rem' }}>
                <span>{TRADE_ICONS[item.trade] ?? '🔨'} {item.trade}</span>
                <span style={{ color: DEMAND_COLOR[item.demand] ?? '#666' }}>{item.demand} demand</span>
              </div>
              <div className="bar-container">
                <div className="bar-fill" style={{ width: `${((item.avg_salary_usd ?? 0) / maxSalary) * 100}%`, background: DEMAND_COLOR[item.demand] ?? '#7c8cff' }} />
              </div>
              <div style={{ fontSize: '0.75rem', color: '#888' }}>${item.avg_salary_usd?.toLocaleString()}/yr</div>
            </div>
          ))}
        </div>

        <div>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <h3>🔑 {t(lang, 'keyCerts')}</h3>
            <ul style={{ paddingLeft: '1.2rem', fontSize: '0.9rem' }}>
              {data.key_certifications?.map((c: string, i: number) => <li key={i} style={{ marginBottom: '0.3rem' }}>{c}</li>)}
            </ul>
          </div>
          <div className="card">
            <h3>🏙 {t(lang, 'bestCities')}</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {data.best_cities?.map((c: string) => (
                <span key={c} className="badge badge-blue">{c}</span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {data.outlook && (
        <div className="card">
          <h3>🔮 {t(lang, 'outlook')}</h3>
          <p style={{ color: '#444', lineHeight: 1.6 }}>{data.outlook}</p>
        </div>
      )}
    </div>
  )
}
