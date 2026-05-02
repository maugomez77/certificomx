import { useEffect, useState } from 'react'
import type { Lang } from '../i18n/strings'
import { t } from '../i18n/strings'
import { TRADE_ICONS } from '../App'

interface Job {
  id: number; title: string; trade: string; employer_id: number
  salary_usd_min: number; salary_usd_max: number; location_type: string
  required_english_level: string; visa_sponsored: boolean; positions_available: number; status: string
}

export default function Jobs({ lang }: { lang: Lang }) {
  const [jobs, setJobs] = useState<Job[]>([])
  const [trade, setTrade] = useState('')

  useEffect(() => {
    const params = trade ? `?trade=${trade}` : ''
    fetch(`/api/v1/jobs${params}`).then(r => r.json()).then(setJobs).catch(() => {})
  }, [trade])

  return (
    <div>
      <h1 className="page-title">💼 {t(lang, 'jobs')}</h1>
      <div style={{ marginBottom: '1rem' }}>
        <select value={trade} onChange={e => setTrade(e.target.value)} style={{ width: 200, marginBottom: 0 }}>
          <option value="">All trades</option>
          {['welding','electrical','automotive','plumbing','electronics','logistics','manufacturing'].map(tr => (
            <option key={tr} value={tr}>{TRADE_ICONS[tr]} {tr}</option>
          ))}
        </select>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
        {jobs.map(job => (
          <div className="card" key={job.id}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '1.2rem' }}>{TRADE_ICONS[job.trade]}</span>
              {job.visa_sponsored && <span className="badge badge-green">{t(lang, 'visa')}</span>}
            </div>
            <h3 style={{ marginBottom: '0.5rem' }}>{job.title}</h3>
            <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '0.75rem' }}>
              <div>💰 ${job.salary_usd_min?.toLocaleString()}-${job.salary_usd_max?.toLocaleString()}/yr</div>
              <div>📍 {job.location_type.replace('_', ' ')}</div>
              <div>🗣 English: {job.required_english_level}</div>
              <div>👥 {job.positions_available} position(s)</div>
            </div>
            <button className="btn btn-primary btn-sm">{t(lang, 'applyJob')}</button>
          </div>
        ))}
        {jobs.length === 0 && <div className="empty">{t(lang, 'noData')}</div>}
      </div>
    </div>
  )
}
