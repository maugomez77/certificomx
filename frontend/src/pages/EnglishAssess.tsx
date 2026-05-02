import { useState } from 'react'
import type { Lang } from '../i18n/strings'
import { t } from '../i18n/strings'

const QUESTIONS = [
  { question: "Tell me about your work experience in your trade.", placeholder: "I have worked as a welder for..." },
  { question: "What safety measures do you follow at work?", placeholder: "I always wear protective equipment..." },
  { question: "Describe a challenging project you completed.", placeholder: "Once I had to..." },
  { question: "Why do you want to work in the United States?", placeholder: "I want to work in the US because..." },
  { question: "What are your strengths as a skilled worker?", placeholder: "My main strengths are..." },
]

const LEVEL_COLOR: Record<string, string> = { none: '#c0392b', basic: '#e67e22', intermediate: '#2980b9', advanced: '#1a7a4a' }

export default function EnglishAssess({ lang }: { lang: Lang }) {
  const [answers, setAnswers] = useState<string[]>(Array(5).fill(''))
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [started, setStarted] = useState(false)

  const submit = async () => {
    setLoading(true)
    const qa = QUESTIONS.map((q, i) => ({ question: q.question, answer: answers[i] }))
    const res = await fetch('/api/v1/ai/english-assess', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(qa)
    })
    const data = await res.json()
    setResult(data)
    setLoading(false)
  }

  if (result) {
    return (
      <div>
        <h1 className="page-title">🗣 {t(lang, 'englishAssess')}</h1>
        <div className="kpi-grid">
          <div className="kpi-card">
            <div className="label">{t(lang, 'yourScore')}</div>
            <div className="value" style={{ color: LEVEL_COLOR[result.level] }}>{result.total_score}/100</div>
          </div>
          <div className="kpi-card">
            <div className="label">{t(lang, 'yourLevel')}</div>
            <div className="value" style={{ fontSize: '1.2rem', color: LEVEL_COLOR[result.level] }}>{result.level?.toUpperCase()}</div>
          </div>
        </div>
        <div className="card">
          <h3>{t(lang, 'feedback')}</h3>
          <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>{result.feedback_es}</p>
          {result.strengths?.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <strong>{t(lang, 'strengths')}:</strong>
              <ul style={{ paddingLeft: '1.2rem', marginTop: '0.5rem' }}>
                {result.strengths.map((s: string, i: number) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
          {result.areas_to_improve?.length > 0 && (
            <div>
              <strong>{t(lang, 'improve')}:</strong>
              <ul style={{ paddingLeft: '1.2rem', marginTop: '0.5rem' }}>
                {result.areas_to_improve.map((a: string, i: number) => <li key={i}>{a}</li>)}
              </ul>
            </div>
          )}
        </div>
        <button className="btn btn-primary" onClick={() => { setResult(null); setStarted(false); setAnswers(Array(5).fill('')) }}>Try Again</button>
      </div>
    )
  }

  return (
    <div>
      <h1 className="page-title">🗣 {t(lang, 'englishAssess')}</h1>
      {!started ? (
        <div className="card" style={{ maxWidth: 500 }}>
          <h3>English Level Assessment</h3>
          <p style={{ color: '#666', marginBottom: '1.5rem', lineHeight: 1.6 }}>
            Answer 5 questions in English to evaluate your level. This helps match you with jobs that fit your communication skills.
          </p>
          <button className="btn btn-primary" onClick={() => setStarted(true)}>{t(lang, 'startAssessment')}</button>
        </div>
      ) : (
        <div>
          {QUESTIONS.map((q, i) => (
            <div className="card" key={i}>
              <h3>Question {i + 1}</h3>
              <p style={{ marginBottom: '1rem', fontWeight: 500 }}>{q.question}</p>
              <textarea
                rows={3}
                placeholder={q.placeholder}
                value={answers[i]}
                onChange={e => { const a = [...answers]; a[i] = e.target.value; setAnswers(a) }}
                style={{ width: '100%' }}
              />
            </div>
          ))}
          <button className="btn btn-primary" onClick={submit} disabled={loading || answers.some(a => !a.trim())}>
            {loading ? t(lang, 'loading') : t(lang, 'submitAnswers')}
          </button>
        </div>
      )}
    </div>
  )
}
