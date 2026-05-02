import { useEffect, useState } from 'react'
import type { Lang } from '../i18n/strings'
import { t } from '../i18n/strings'

interface Employer {
  id: number; company_name: string; country: string; state_province: string
  city: string; industry: string; contact_email: string; nearshoring_partner: boolean; verified: boolean
}

export default function Employers({ lang }: { lang: Lang }) {
  const [employers, setEmployers] = useState<Employer[]>([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ company_name: '', country: 'us', state_province: '', city: '', industry: 'manufacturing', contact_name: '', contact_email: '', contact_phone: '', nearshoring_partner: true })

  useEffect(() => {
    fetch('/api/v1/employers').then(r => r.json()).then(setEmployers).catch(() => {})
  }, [])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    const res = await fetch('/api/v1/employers', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) })
    const emp = await res.json()
    setEmployers(prev => [...prev, emp])
    setShowForm(false)
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 className="page-title" style={{ margin: 0 }}>🏢 {t(lang, 'employers')}</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>{t(lang, 'registerEmployer')}</button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '1rem' }}>
          <h3>{t(lang, 'registerEmployer')}</h3>
          <form onSubmit={submit}>
            <div className="form-grid">
              <div><label>Company Name</label><input required value={form.company_name} onChange={e => setForm({...form, company_name: e.target.value})} /></div>
              <div><label>Country</label><select value={form.country} onChange={e => setForm({...form, country: e.target.value})}><option value="us">🇺🇸 USA</option><option value="canada">🇨🇦 Canada</option></select></div>
              <div><label>State/Province</label><input value={form.state_province} onChange={e => setForm({...form, state_province: e.target.value})} /></div>
              <div><label>City</label><input value={form.city} onChange={e => setForm({...form, city: e.target.value})} /></div>
              <div><label>Industry</label>
                <select value={form.industry} onChange={e => setForm({...form, industry: e.target.value})}>
                  {['manufacturing','automotive','aerospace','electronics','logistics'].map(i => <option key={i} value={i}>{i}</option>)}
                </select>
              </div>
              <div><label>Contact Email</label><input type="email" value={form.contact_email} onChange={e => setForm({...form, contact_email: e.target.value})} /></div>
            </div>
            <button type="submit" className="btn btn-primary">{t(lang, 'save')}</button>
          </form>
        </div>
      )}

      <table>
        <thead><tr><th>Company</th><th>Country</th><th>City</th><th>Industry</th><th>Nearshoring</th><th>Verified</th></tr></thead>
        <tbody>
          {employers.map(e => (
            <tr key={e.id}>
              <td><strong>{e.company_name}</strong></td>
              <td>{e.country === 'us' ? '🇺🇸 USA' : '🇨🇦 Canada'}</td>
              <td>{e.city}, {e.state_province}</td>
              <td>{e.industry}</td>
              <td>{e.nearshoring_partner ? <span className="badge badge-green">Yes</span> : '—'}</td>
              <td>{e.verified ? <span className="badge badge-blue">✓</span> : '—'}</td>
            </tr>
          ))}
          {employers.length === 0 && <tr><td colSpan={6} className="empty">{t(lang, 'noData')}</td></tr>}
        </tbody>
      </table>
    </div>
  )
}
