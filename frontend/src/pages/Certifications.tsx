import { useEffect, useState } from 'react'
import type { Lang } from '../i18n/strings'
import { t } from '../i18n/strings'
import { TRADE_ICONS } from '../App'

interface Cert {
  id: number; name: string; code: string; trade: string; authority: string
  level: string; duration_hours: number; cost_mxn: number; us_equivalent: string; active: boolean
}

const LEVEL_BADGE: Record<string, string> = { basic: 'badge-green', intermediate: 'badge-yellow', advanced: 'badge-blue' }

export default function Certifications({ lang }: { lang: Lang }) {
  const [certs, setCerts] = useState<Cert[]>([])
  const [trade, setTrade] = useState('')

  useEffect(() => {
    const params = trade ? `?trade=${trade}` : ''
    fetch(`/api/v1/certifications${params}`).then(r => r.json()).then(setCerts).catch(() => {})
  }, [trade])

  return (
    <div>
      <h1 className="page-title">🎓 {t(lang, 'certifications')}</h1>
      <div style={{ marginBottom: '1rem' }}>
        <select value={trade} onChange={e => setTrade(e.target.value)} style={{ width: 200, marginBottom: 0 }}>
          <option value="">All trades</option>
          {['welding','electrical','automotive','plumbing','electronics','logistics','manufacturing'].map(tr => (
            <option key={tr} value={tr}>{TRADE_ICONS[tr]} {tr}</option>
          ))}
        </select>
      </div>
      <table>
        <thead>
          <tr><th>Code</th><th>Name</th><th>{t(lang, 'trade')}</th><th>{t(lang, 'authority')}</th><th>{t(lang, 'certLevel')}</th><th>{t(lang, 'hours')}</th><th>{t(lang, 'cost')}</th><th>{t(lang, 'usEquivalent')}</th></tr>
        </thead>
        <tbody>
          {certs.map(c => (
            <tr key={c.id}>
              <td><code>{c.code}</code></td>
              <td>{c.name}</td>
              <td>{TRADE_ICONS[c.trade]} {c.trade}</td>
              <td>{c.authority}</td>
              <td><span className={`badge ${LEVEL_BADGE[c.level] ?? 'badge-gray'}`}>{c.level}</span></td>
              <td>{c.duration_hours}h</td>
              <td>${c.cost_mxn?.toLocaleString()} MXN</td>
              <td style={{ fontSize: '0.8rem', color: '#666' }}>{c.us_equivalent}</td>
            </tr>
          ))}
          {certs.length === 0 && <tr><td colSpan={8} className="empty">{t(lang, 'noData')}</td></tr>}
        </tbody>
      </table>
    </div>
  )
}
