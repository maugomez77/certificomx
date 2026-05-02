import { useState } from 'react'
import { Routes, Route, NavLink, Navigate } from 'react-router-dom'
import type { Lang } from './i18n/strings'
import { t } from './i18n/strings'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import Workers from './pages/Workers'
import WorkerDetail from './pages/WorkerDetail'
import Jobs from './pages/Jobs'
import Certifications from './pages/Certifications'
import Employers from './pages/Employers'
import MarketIntel from './pages/MarketIntel'
import EnglishAssess from './pages/EnglishAssess'

const TRADE_ICONS: Record<string, string> = {
  welding: '🔧', electrical: '⚡', automotive: '🚗',
  plumbing: '🔩', electronics: '📱', logistics: '📦', manufacturing: '🏭',
}

export { TRADE_ICONS }

export default function App() {
  const [lang, setLang] = useState<Lang>('es')

  return (
    <>
      <button className="lang-toggle" onClick={() => setLang(l => l === 'es' ? 'en' : 'es')}>
        {lang === 'es' ? '🇺🇸 EN' : '🇲🇽 ES'}
      </button>
      <Routes>
        <Route path="/" element={<Landing lang={lang} />} />
        <Route path="/app/*" element={
          <div className="layout">
            <nav className="sidebar">
              <div className="sidebar-logo">📋 CertificoMX</div>
              <div className="sidebar-section">Principal</div>
              <NavLink to="/app/dashboard">{t(lang, 'dashboard')}</NavLink>
              <div className="sidebar-section">Talento</div>
              <NavLink to="/app/workers">{t(lang, 'workers')}</NavLink>
              <NavLink to="/app/certifications">{t(lang, 'certifications')}</NavLink>
              <NavLink to="/app/assess">{t(lang, 'englishAssess')}</NavLink>
              <div className="sidebar-section">Empleos</div>
              <NavLink to="/app/jobs">{t(lang, 'jobs')}</NavLink>
              <NavLink to="/app/employers">{t(lang, 'employers')}</NavLink>
              <div className="sidebar-section">Inteligencia</div>
              <NavLink to="/app/market">{t(lang, 'marketIntel')}</NavLink>
            </nav>
            <main className="main">
              <Routes>
                <Route index element={<Navigate to="dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard lang={lang} />} />
                <Route path="workers" element={<Workers lang={lang} />} />
                <Route path="workers/:id" element={<WorkerDetail lang={lang} />} />
                <Route path="jobs" element={<Jobs lang={lang} />} />
                <Route path="certifications" element={<Certifications lang={lang} />} />
                <Route path="employers" element={<Employers lang={lang} />} />
                <Route path="market" element={<MarketIntel lang={lang} />} />
                <Route path="assess" element={<EnglishAssess lang={lang} />} />
              </Routes>
            </main>
          </div>
        } />
      </Routes>
    </>
  )
}
