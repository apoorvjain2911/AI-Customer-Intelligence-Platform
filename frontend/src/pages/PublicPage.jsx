import { useMemo, useState } from 'react'
import { ArrowRight, Building2, ShieldCheck, Sparkles, UserPlus, Users } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const modeConfig = {
  landing: {
    eyebrow: 'Enterprise CRM',
    title: 'AI Customer Intelligence Platform',
    subtitle:
      'Turn your churn system into a real CRM with authentication, customer management, explainability, AI copilot workflows, and model operations built in.',
    primaryCta: { label: 'Sign in', to: '/login' },
    secondaryCta: { label: 'Create account', to: '/register' },
  },
  login: {
    eyebrow: 'Welcome back',
    title: 'Sign in to your workspace',
    subtitle: 'Access customer analytics, AI copilot tools, model operations, and admin workflows with your JWT session.',
  },
  register: {
    eyebrow: 'Start here',
    title: 'Create your CRM account',
    subtitle: 'Register a sales manager or customer success user and immediately begin managing customers and predictions.',
  },
}

const initialFormState = {
  name: '',
  email: '',
  password: '',
}

export default function PublicPage({ mode = 'landing' }) {
  const { login, register, isAuthenticated, loading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState(initialFormState)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const config = modeConfig[mode] || modeConfig.landing

  const destination = useMemo(() => {
    const from = location.state?.from?.pathname || '/dashboard'
    return from
  }, [location.state])

  if (loading) {
    return (
      <section className="glass-card mx-auto mt-12 max-w-3xl p-8 text-center">
        <p className="text-sm font-medium text-slate-500">Restoring your session...</p>
      </section>
    )
  }

  if (isAuthenticated && mode !== 'landing') {
    navigate(destination, { replace: true })
  }

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      if (mode === 'login') {
        await login({ email: form.email, password: form.password })
      } else if (mode === 'register') {
        await register({ name: form.name, email: form.email, password: form.password })
        await login({ email: form.email, password: form.password })
      }

      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to complete the request.')
    } finally {
      setSubmitting(false)
    }
  }

  if (mode === 'landing') {
    return (
      <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
        <section className="space-y-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700">
            <Sparkles className="h-4 w-4" />
            Salesforce-like customer intelligence, built on top of your churn system
          </div>

          <div className="space-y-4">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-400">{config.eyebrow}</p>
            <h1 className="title-display max-w-3xl text-4xl font-bold tracking-tight text-slate-950 sm:text-5xl lg:text-6xl">{config.title}</h1>
            <p className="max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">{config.subtitle}</p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Link to={config.primaryCta.to} className="inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-200 transition hover:bg-blue-700">
              {config.primaryCta.label}
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link to={config.secondaryCta.to} className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700">
              {config.secondaryCta.label}
            </Link>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {[
              ['CRM-ready', Building2],
              ['Protected routes', ShieldCheck],
              ['AI copilot', Sparkles],
              ['Multi-role access', Users],
            ].map(([label, Icon]) => (
              <div key={label} className="glass-card flex items-center gap-3 px-4 py-4">
                <span className="rounded-2xl bg-blue-50 p-3 text-blue-600">
                  <Icon className="h-5 w-5" />
                </span>
                <p className="text-sm font-semibold text-slate-700">{label}</p>
              </div>
            ))}
          </div>
        </section>

        <aside className="glass-card space-y-5 p-6 shadow-soft">
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">What’s inside</p>
            <h2 className="title-display text-2xl font-bold text-slate-950">Complete enterprise CRM controls</h2>
          </div>

          <ul className="space-y-3 text-sm text-slate-600">
            <li className="rounded-2xl border border-slate-200 bg-white px-4 py-3">Authentication, JWT session persistence, and role-based routing</li>
            <li className="rounded-2xl border border-slate-200 bg-white px-4 py-3">Customer lifecycle management, CLV, segmentation, and explainability</li>
            <li className="rounded-2xl border border-slate-200 bg-white px-4 py-3">Copilot workflows for retention, executive summaries, and sales actions</li>
            <li className="rounded-2xl border border-slate-200 bg-white px-4 py-3">Admin panel, model status, retraining, and report management</li>
          </ul>
        </aside>
      </div>
    )
  }

  return (
    <section className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[1fr_0.9fr] lg:items-center">
      <div className="space-y-5">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-400">{config.eyebrow}</p>
        <h1 className="title-display text-4xl font-bold tracking-tight text-slate-950 sm:text-5xl">{config.title}</h1>
        <p className="max-w-xl text-base leading-7 text-slate-600">{config.subtitle}</p>

        {error ? (
          <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-4 text-sm font-medium text-rose-700">{error}</div>
        ) : null}

        <form onSubmit={handleSubmit} className="glass-card space-y-4 p-6 shadow-soft">
          {mode === 'register' ? (
            <label className="block space-y-2">
              <span className="text-sm font-semibold text-slate-700">Name</span>
              <input
                name="name"
                value={form.name}
                onChange={handleChange}
                type="text"
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-400"
                placeholder="Alex Morgan"
                required
              />
            </label>
          ) : null}

          <label className="block space-y-2">
            <span className="text-sm font-semibold text-slate-700">Email</span>
            <input
              name="email"
              value={form.email}
              onChange={handleChange}
              type="email"
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-400"
              placeholder="you@example.com"
              required
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-semibold text-slate-700">Password</span>
            <input
              name="password"
              value={form.password}
              onChange={handleChange}
              type="password"
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-400"
              placeholder="••••••••"
              required
            />
          </label>

          <button
            type="submit"
            disabled={submitting}
            className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-200 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? 'Processing...' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>

          <p className="text-center text-sm text-slate-500">
            {mode === 'login' ? (
              <>
                Need an account? <Link to="/register" className="font-semibold text-blue-700">Register</Link>
              </>
            ) : (
              <>
                Already have an account? <Link to="/login" className="font-semibold text-blue-700">Sign in</Link>
              </>
            )}
          </p>
        </form>
      </div>

      <aside className="glass-card space-y-4 p-6 shadow-soft">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Enterprise-ready</p>
        <h2 className="title-display text-2xl font-bold text-slate-950">What you get after signing in</h2>
        <div className="space-y-3 text-sm text-slate-600">
          <div className="rounded-2xl border border-slate-200 bg-white px-4 py-4">Live dashboard, customers, predictions, and model analytics.</div>
          <div className="rounded-2xl border border-slate-200 bg-white px-4 py-4">AI Copilot, SHAP explanations, segmentation, CLV, reports, and admin controls.</div>
          <div className="rounded-2xl border border-slate-200 bg-white px-4 py-4">Session persistence with JWT and automatic protected-route handling.</div>
        </div>
      </aside>
    </section>
  )
}