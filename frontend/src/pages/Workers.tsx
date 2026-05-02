import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { Lang } from '../i18n/strings'
import { t } from '../i18n/strings'
import { TRADE_ICONS } from '../App'

interface Worker {
  id: number; name: string; phone: string; trade: string; city: string
  state: string; english_level: string; experience_years: number; status: string
}

const STATUS_BADGE: Record<string, string> = {
  seeking: 'badge-yellow', certified: 'badge-blue', placed: 'badge-green', inactive: 'badge-gray',
}

export default function Workers({ lang }: { lang: Lang }) {
  const [workers, setWorkers] = useState<Worker[]>([])
  const [trade, setTrade] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', phone: '', trade: 'welding', city: '', state: '', experience_years: 0, english_level: 'none' })
  const nav = useNavigate()

  const load = () => {
    const params = trade ? `?trade=${trade}` : ''
    fetch(`/api/v1/workers${params}`).then(r => r.json()).then(setWorkers).catch(() => {})
  }

  useEffect(() => { load() }, [trade])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    await fetch('/api/v1/workers', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) })
    setShowForm(false)
    load()
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 className="page-title" style={{ margin: 0 }}>👷 {t(lang, 'workers')}</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>{t(lang, 'registerWorker')}</button>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <select value={trade} onChange={e => setTrade(e.target.value)} style={{ width: 200, marginBottom: 0 }}>
          <option value="">All trades</option>
          {['welding','electrical','automotive','plumbing','electronics','logistics','manufacturing'].map(t => (
            <option key={t} value={t}>{TRADE_ICONS[t]} {t}</option>
          ))}
        </select>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '1rem' }}>
          <h3>{t(lang, 'registerWorker')}</h3>
          <form onSubmit={submit}>
            <div className="form-grid">
              <div><label>{t(lang, 'name')}</label><input required value={form.name} onChange={e => setForm({...form, name: e.target.value})} /></div>
              <div><label>{t(lang, 'phone')}</label><input required value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} /></div>
              <div><label>{t(lang, 'trade')}</label>
                <select value={form.trade} onChange={e => setForm({...form, trade: e.target.value})}>
                  {['welding','electrical','automotive','plumbing','electronics','logistics','manufacturing'].map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div><label>{t(lang, 'englishLevel')}</label>
                <select value={form.english_level} onChange={e => setForm({...form, english_level: e.target.value})}>
                  {['none','basic','intermediate','advanced'].map(l => <option key={l} value={l}>{l}</option>)}
                </select>
              </div>
              <div><label>{t(lang, 'city')}</label><input value={form.city} onChange={e => setForm({...form, city: e.target.value})} /></div>
              <div><label>{t(lang, 'state')}</label><input value={form.state} onChange={e => setForm({...form, state: e.target.value})} /></div>
            </div>
            <button type="submit" className="btn btn-primary">{t(lang, 'save')}</button>
          </form>
        </div>
      )}

      <table>
        <thead><tr><th>ID</th><th>{t(lang, 'name')}</th><th>{t(lang, 'trade')}</th><th>{t(lang, 'city')}</th><th>{t(lang, 'englishLevel')}</th><th>{t(lang, 'experience')}</th><th>{t(lang, 'status')}</th><th></th></tr></thead>
        <tbody>
          {workers.map(w => (
            <tr key={w.id}>
              <td>{w.id}</td>
              <td><strong>{w.name}</strong></td>
              <td>{TRADE_ICONS[w.trade]} {w.trade}</td>
              <td>{w.city}</td>
              <td>{w.english_level}</td>
              <td>{w.experience_years}y</td>
              <td><span className={`badge ${STATUS_BADGE[w.status] ?? 'badge-gray'}`}>{w.status}</span></td>
              <td><button className="btn btn-sm btn-primary" onClick={() => nav(`/app/workers/${w.id}`)}>{t(lang, 'viewDetail')}</button></td>
            </tr>
          ))}
          {workers.length === 0 && <tr><td colSpan={8} className="empty">{t(lang, 'noData')}</td></tr>}
        </tbody>
      </table>
    </div>
  )
}
