import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import type { Lang } from '../i18n/strings'
import { t } from '../i18n/strings'

export default function WorkerDetail({ lang }: { lang: Lang }) {
  const { id } = useParams()
  const [worker, setWorker] = useState<any>(null)
  const [certs, setCerts] = useState<any[]>([])
  const [careerPath, setCareerPath] = useState<any>(null)
  const [loadingPath, setLoadingPath] = useState(false)

  useEffect(() => {
    if (!id) return
    fetch(`/api/v1/workers/${id}`).then(r => r.json()).then(setWorker)
    fetch(`/api/v1/workers/${id}/certifications`).then(r => r.json()).then(setCerts)
  }, [id])

  const getCareerPath = async () => {
    setLoadingPath(true)
    const res = await fetch(`/api/v1/ai/career-path?worker_id=${id}`, { method: 'POST' })
    const data = await res.json()
    setCareerPath(data)
    setLoadingPath(false)
  }

  if (!worker) return <div className="empty">{t(lang, 'loading')}</div>

  return (
    <div>
      <h1 className="page-title">👷 {worker.name}</h1>
      <div className="kpi-grid">
        {[
          ['Trade', worker.trade],
          ['City', `${worker.city}, ${worker.state}`],
          ['English', worker.english_level],
          ['Experience', `${worker.experience_years}y`],
          ['Status', worker.status],
          ['Score', worker.english_score ?? '—'],
        ].map(([l, v]) => (
          <div className="kpi-card" key={String(l)}><div className="label">{l}</div><div className="value" style={{ fontSize: '1.1rem' }}>{v}</div></div>
        ))}
      </div>

      <div className="card">
        <h3>Certificaciones</h3>
        {certs.length === 0 ? <p className="empty">Sin certificaciones</p> : (
          <table>
            <thead><tr><th>ID</th><th>Certification</th><th>Status</th><th>Score</th><th>Exam Date</th></tr></thead>
            <tbody>{certs.map(c => <tr key={c.id}><td>{c.certification_id}</td><td>—</td><td>{c.status}</td><td>{c.score ?? '—'}</td><td>{c.exam_date ?? '—'}</td></tr>)}</tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h3>🤖 {t(lang, 'careerPath')}</h3>
        {!careerPath && <button className="btn btn-primary" onClick={getCareerPath} disabled={loadingPath}>{loadingPath ? t(lang, 'loading') : t(lang, 'careerPath')}</button>}
        {careerPath && (
          <div>
            {careerPath.paths?.map((p: any, i: number) => (
              <div key={i} style={{ marginBottom: '1rem', padding: '1rem', background: '#f8f9fb', borderRadius: 8 }}>
                <strong>{p.name}</strong> ({p.authority})<br />
                <span style={{ color: '#666', fontSize: '0.85rem' }}>US: {p.us_equivalent} | {p.timeline_months}mo | ${p.expected_salary_usd_min?.toLocaleString()}-${p.expected_salary_usd_max?.toLocaleString()}/yr</span><br />
                <span style={{ color: '#1a7a4a', fontSize: '0.85rem' }}>Placement: {p.placement_probability_pct}%</span>
                <ul style={{ marginTop: '0.5rem', paddingLeft: '1.2rem', fontSize: '0.85rem' }}>
                  {p.steps?.map((s: string, j: number) => <li key={j}>{s}</li>)}
                </ul>
              </div>
            ))}
            {careerPath.recommendation && <p style={{ color: '#666', fontStyle: 'italic', marginTop: '0.5rem' }}>{careerPath.recommendation}</p>}
          </div>
        )}
      </div>
    </div>
  )
}
