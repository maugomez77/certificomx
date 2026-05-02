import { useNavigate } from 'react-router-dom'
import type { Lang } from '../i18n/strings'
import { t } from '../i18n/strings'

export default function Landing({ lang }: { lang: Lang }) {
  const nav = useNavigate()
  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #1a1f36 0%, #2d3561 100%)', color: '#fff', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2rem', textAlign: 'center' }}>
      <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🏆</div>
      <h1 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '1rem', maxWidth: 600 }}>{t(lang, 'heroTitle')}</h1>
      <p style={{ fontSize: '1.1rem', color: '#aab', maxWidth: 500, marginBottom: '2.5rem' }}>{t(lang, 'heroSubtitle')}</p>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '3rem' }}>
        <button className="btn btn-primary" style={{ fontSize: '1rem', padding: '0.8rem 2rem' }} onClick={() => nav('/app/workers')}>{t(lang, 'ctaWorker')}</button>
        <button className="btn" style={{ fontSize: '1rem', padding: '0.8rem 2rem', background: 'rgba(255,255,255,0.1)', color: '#fff', border: '1px solid rgba(255,255,255,0.3)' }} onClick={() => nav('/app/employers')}>{t(lang, 'ctaEmployer')}</button>
      </div>
      <div style={{ display: 'flex', gap: '3rem' }}>
        {[['500+', t(lang, 'stat1')], ['50+', t(lang, 'stat2')], ['78%', t(lang, 'stat3')]].map(([val, label]) => (
          <div key={label}>
            <div style={{ fontSize: '2rem', fontWeight: 700, color: '#7c8cff' }}>{val}</div>
            <div style={{ fontSize: '0.85rem', color: '#889' }}>{label}</div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: '3rem', display: 'flex', gap: '1.5rem', fontSize: '2rem' }}>
        {['🔧', '⚡', '🚗', '🔩', '📱', '📦', '🏭'].map(icon => (
          <span key={icon} style={{ opacity: 0.7 }}>{icon}</span>
        ))}
      </div>
    </div>
  )
}
