
import { useEffect, useMemo, useState } from 'react'

import { useParams } from 'react-router-dom'
import {
  assignSegment,
  clearAuthSession,
  createCustomer,
  createReport,
  deleteCustomer,
  deleteReport,
  getXaiExplanation,
  getAdminDashboard,
  getAdminUsers,
  getClvSummary,
  getCopilotResponse,
  getCustomer,
  getCustomers,
  getHistory,
  getModelStatus,
  getReports,
  getSegmentStats,
  getSegments,
  getTopClvCustomers,
  predictBatch,
  refreshCustomerClv,
  retrainModel,
  updateAdminUserRole,
  updateAdminUserStatus,
  updateCustomer,
} from '../services/api'
import { useAuth } from '../context/AuthContext'

const customerFields = [
  { name: 'customer_id', label: 'Customer ID', type: 'text' },
  { name: 'name', label: 'Name', type: 'text' },
  { name: 'email', label: 'Email', type: 'email' },
  { name: 'phone', label: 'Phone', type: 'text' },
  { name: 'company', label: 'Company', type: 'text' },
  { name: 'city', label: 'City', type: 'text' },
  { name: 'country', label: 'Country', type: 'text' },
  { name: 'industry', label: 'Industry', type: 'text' },
  { name: 'age', label: 'Age', type: 'number' },
  { name: 'gender', label: 'Gender', type: 'text' },
  { name: 'subscription_plan', label: 'Subscription Plan', type: 'text' },
  { name: 'contract_type', label: 'Contract Type', type: 'text' },
  { name: 'join_date', label: 'Join Date', type: 'date' },
  { name: 'monthly_charges', label: 'Monthly Charges', type: 'number', step: '0.01' },
  { name: 'total_charges', label: 'Total Charges', type: 'number', step: '0.01' },
  { name: 'tenure', label: 'Tenure', type: 'number' },
  { name: 'payment_status', label: 'Payment Status', type: 'text' },
  { name: 'support_tickets', label: 'Support Tickets', type: 'number' },
  { name: 'last_login', label: 'Last Login', type: 'datetime-local' },
  { name: 'churn_probability', label: 'Churn Probability', type: 'number', step: '0.01' },
  { name: 'risk_level', label: 'Risk Level', type: 'text' },
  { name: 'customer_lifetime_value', label: 'CLV', type: 'number', step: '0.01' },
  { name: 'expected_revenue', label: 'Expected Revenue', type: 'number', step: '0.01' },
  { name: 'priority_score', label: 'Priority Score', type: 'number', step: '0.01' },
]

const initialCustomerForm = customerFields.reduce((accumulator, field) => {
  accumulator[field.name] = ''
  return accumulator
}, {})

const reportFieldDefaults = {
  report_type: 'customer',
  title: '',
  description: '',
  file_format: 'pdf',
  file_path: '',
  status: 'generated',
}

const copilotPrompts = [
  'Why is this customer likely to churn?',
  'Generate a retention strategy.',
  'Draft a retention email.',
  'Which customers should sales call today?',
  'Generate an executive summary.',
]

const roleOptions = ['admin', 'sales_manager', 'customer_success_manager']

const inputClass =
  'w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-400'

function SectionCard({ title, description, children, action }) {
  return (
    <section className="glass-card animate-fade-in p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="title-display text-xl font-bold text-slate-950">{title}</h2>
          {description ? <p className="mt-1 text-sm text-slate-500">{description}</p> : null}
        </div>
        {action}
      </div>
      <div className="mt-5">{children}</div>
    </section>
  )
}

function MetricGrid({ items }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <div key={item.label} className="rounded-3xl border border-slate-200 bg-white px-4 py-4">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">{item.label}</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">{item.value}</p>
          {item.helper ? <p className="mt-2 text-sm text-slate-500">{item.helper}</p> : null}
        </div>
      ))}
    </div>
  )
}

function CustomerForm({ value, onChange, onSubmit, onCancel, submitLabel = 'Save customer' }) {
  return (
    <form onSubmit={onSubmit} className="space-y-4 rounded-3xl border border-slate-200 bg-slate-50/80 p-5">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {customerFields.map((field) => (
          <label key={field.name} className="block space-y-2">
            <span className="text-sm font-semibold text-slate-700">{field.label}</span>
            <input
              name={field.name}
              type={field.type}
              step={field.step}
              value={value[field.name] ?? ''}
              onChange={onChange}
              className={inputClass}
              placeholder={field.label}
            />
          </label>
        ))}
      </div>

      <div className="flex flex-wrap gap-3 pt-2">
        <button type="submit" className="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700">
          {submitLabel}
        </button>
        <button type="button" onClick={onCancel} className="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
          Cancel
        </button>
      </div>
    </form>
  )
}

function toCustomerPayload(form) {
  const payload = { ...form }
  const numericFields = new Set(['age', 'monthly_charges', 'total_charges', 'tenure', 'support_tickets', 'churn_probability', 'customer_lifetime_value', 'expected_revenue', 'priority_score'])

  Object.entries(payload).forEach(([key, value]) => {
    if (value === '') {
      delete payload[key]
      return
    }

    if (numericFields.has(key)) {
      payload[key] = Number(value)
    }
  })

  return payload
}

function adaptReport(record) {
  return {
    id: record.id,
    report_type: record.report_type,
    title: record.title,
    description: record.description,
    file_format: record.file_format,
    status: record.status,
    created_at: record.created_at,
  }
}

function adaptCustomerRow(row) {
  return {
    id: row.id,
    customer_id: row.customer_id,
    name: row.name,
    company: row.company,
    email: row.email,
    risk_level: row.risk_level || 'low',
    churn_probability: row.churn_probability ?? row.probability ?? 0,
    priority_score: row.priority_score,
    recommendation: row.recommendation || row.summary || 'Review customer account',
  }
}

export default function ModulePage({ mode = 'customers' }) {
  const { user, logout } = useAuth()
  const params = useParams()

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [customers, setCustomers] = useState([])
  const [customerPage, setCustomerPage] = useState(1)
  const [customerTotal, setCustomerTotal] = useState(0)
  const [selectedExplanation, setSelectedExplanation] = useState(null);
const [loadingExplanation, setLoadingExplanation] = useState(false);
  const [customerQuery, setCustomerQuery] = useState({
    search: '',
    risk_level: '',
    company: '',
    country: '',
    sort_by: 'created_at',
    sort_order: 'desc',
    page_size: 12,
  })
  const [customerForm, setCustomerForm] = useState(initialCustomerForm)
  const [editingCustomerId, setEditingCustomerId] = useState(null)
  const [selectedCustomer, setSelectedCustomer] = useState(null)

  const [history, setHistory] = useState([])
  const [dashboard, setDashboard] = useState(null)
  const [copilotPrompt, setCopilotPrompt] = useState(copilotPrompts[0])
  const [copilotCustomerId, setCopilotCustomerId] = useState('')
  const [copilotCustomerName, setCopilotCustomerName] = useState('')
  const [copilotProvider, setCopilotProvider] = useState('local')
  const [copilotMessages, setCopilotMessages] = useState([])
  const [copilotInput, setCopilotInput] = useState('')
  const [copilotLoading, setCopilotLoading] = useState(false)
  const [copilotResponse, setCopilotResponse] = useState(null)

  const [clvSummary, setClvSummary] = useState(null)
  const [segmentStats, setSegmentStats] = useState(null)
  const [segments, setSegments] = useState([])
  const [reports, setReports] = useState([])
  const [reportForm, setReportForm] = useState(reportFieldDefaults)
  const [adminState, setAdminState] = useState(null)
  const [adminUsers, setAdminUsers] = useState([])
  const [modelStatus, setModelStatus] = useState(null)
  const [xaiOutput, setXaiOutput] = useState(null)
  const [xaiCustomerId, setXaiCustomerId] = useState('')

  const customerPageCount = Math.max(Math.ceil(customerTotal / Number(customerQuery.page_size || 12)), 1)

  const selectedCustomerRow = useMemo(() => {
    return selectedCustomer || (params.customerId ? customers.find((item) => String(item.id) === String(params.customerId)) : null)
  }, [customers, params.customerId, selectedCustomer])

  const loadCustomers = async (page = customerPage, query = customerQuery) => {
    const response = await getCustomers({
      ...query,
      page,
      page_size: query.page_size,
    })
    setCustomers(response.data.items || [])
    setCustomerTotal(response.data.total || 0)
    setCustomerPage(response.data.page || page)
  }

  const loadDashboard = async () => {
    const response = await (await import('../services/api')).getDashboardSummary()
    setDashboard(response.data)
  }

  const loadHistory = async () => {
    const response = await getHistory()
    setHistory(response.data || [])
  }

  const loadClv = async () => {
    const response = await getClvSummary()
    setClvSummary(response.data)
  }

  const loadSegments = async () => {
    const [segmentResponse, statsResponse] = await Promise.all([getSegments(), getSegmentStats()])
    setSegments(segmentResponse.data.items || segmentResponse.data || [])
    setSegmentStats(statsResponse.data)
  }

  const loadReports = async () => {
    const response = await getReports()
    setReports(response.data.items || [])
  }

  const loadAdmin = async () => {
    const [dashboardResponse, usersResponse, statusResponse] = await Promise.all([
      getAdminDashboard(),
      getAdminUsers(),
      getModelStatus(),
    ])

    setAdminState(dashboardResponse.data)
    setAdminUsers(usersResponse.data || [])
    setModelStatus(statusResponse.data)
  }

  const loadXai = async (customerId = xaiCustomerId || selectedCustomerRow?.id) => {
    if (!customerId) return
    const response = await getXaiExplanation(customerId)
    setXaiOutput(response.data)
  }

  useEffect(() => {
    let cancelled = false

    const run = async () => {
      try {
        setLoading(true)
        setError('')

        if (mode === 'customers') {
          await loadCustomers(1, customerQuery)
          if (params.customerId) {
            const detailResponse = await getCustomer(params.customerId)
            if (!cancelled) {
              setSelectedCustomer(detailResponse.data)
              setCustomerForm({
                ...initialCustomerForm,
                ...detailResponse.data,
                join_date: detailResponse.data.join_date || '',
                last_login: detailResponse.data.last_login ? String(detailResponse.data.last_login).slice(0, 16) : '',
              })
              setEditingCustomerId(detailResponse.data.id)
            }
          }
        } else if (mode === 'predictions') {
          await loadHistory()
        } else if (mode === 'clv') {
          await loadClv()
        } else if (mode === 'segments') {
          await loadSegments()
          await loadCustomers(1, { ...customerQuery, page_size: 20 })
        } else if (mode === 'reports') {
          await loadReports()
        } else if (mode === 'admin') {
          await loadAdmin()
        } else if (mode === 'copilot') {
          await loadCustomers(1, { ...customerQuery, page_size: 50 })
        } else if (mode === 'xai') {
          await loadCustomers(1, { ...customerQuery, page_size: 50 })
          if (params.customerId) {
            await loadXai(params.customerId)
            setXaiCustomerId(params.customerId)
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(err?.response?.data?.detail || err?.message || 'Unable to load this module.')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    run()

    return () => {
      cancelled = true
    }
  }, [mode])

  useEffect(() => {
    if (mode !== 'customers') return
    const timer = window.setTimeout(() => {
      loadCustomers(1, customerQuery).catch((err) => setError(err?.response?.data?.detail || 'Unable to load customers.'))
    }, 250)

    return () => window.clearTimeout(timer)
  }, [customerQuery])

  const handleCustomerQueryChange = (event) => {
    const { name, value } = event.target
    setCustomerQuery((current) => ({ ...current, [name]: value }))
  }

  const resetCustomerForm = () => {
    setCustomerForm(initialCustomerForm)
    setEditingCustomerId(null)
    setSelectedCustomer(null)
  }

  const handleCustomerFormChange = (event) => {
    const { name, value } = event.target
    setCustomerForm((current) => ({ ...current, [name]: value }))
  }

  const saveCustomer = async (event) => {
    event.preventDefault()
    try {
      const payload = toCustomerPayload(customerForm)
      if (editingCustomerId) {
        await updateCustomer(editingCustomerId, payload)
      } else {
        await createCustomer(payload)
      }
      resetCustomerForm()
      await loadCustomers(1, customerQuery)
      if (selectedCustomerRow?.id) {
        const detailResponse = await getCustomer(selectedCustomerRow.id)
        setSelectedCustomer(detailResponse.data)
      }
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to save customer.')
    }
  }

  const handleDeleteCustomer = async (customerId) => {
    if (!window.confirm('Delete this customer?')) return
    await deleteCustomer(customerId)
    if (selectedCustomerRow?.id === customerId) {
      resetCustomerForm()
    }
    await loadCustomers(customerPage, customerQuery)
  }

  const handleRunBatchPrediction = async () => {
    try {
      await predictBatch()
      await loadHistory()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to run batch prediction.')
    }
  }

  const handleCopilotSubmit = async (event) => {
    event.preventDefault()
    setCopilotLoading(true)
    setError('')

    const nextMessages = [...copilotMessages, { role: 'user', content: copilotInput || copilotPrompt }]
    setCopilotMessages(nextMessages)

    try {
      const response = await getCopilotResponse({
        prompt: copilotInput || copilotPrompt,
        customer_id: copilotCustomerId ? Number(copilotCustomerId) : null,
        customer_name: copilotCustomerName || null,
        provider: copilotProvider,
      })

      setCopilotResponse(response.data)
      setCopilotMessages([...nextMessages, { role: 'assistant', content: response.data.response }])
      setCopilotInput('')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to generate copilot response.')
    } finally {
      setCopilotLoading(false)
    }
  }

  const handleCreateReport = async (event) => {
    event.preventDefault()
    try {
      await createReport(reportForm)
      setReportForm(reportFieldDefaults)
      await loadReports()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to create report.')
    }
  }

  const handleDeleteReport = async (reportId) => {
    if (!window.confirm('Delete this report?')) return
    await deleteReport(reportId)
    await loadReports()
  }

  const handleRoleChange = async (userId, role) => {
    await updateAdminUserRole(userId, { role })
    await loadAdmin()
  }

  const handleStatusToggle = async (userId, isActive) => {
    await updateAdminUserStatus(userId, { is_active: isActive })
    await loadAdmin()
  }

  const handleRetrain = async () => {
    try {
      await retrainModel()
      await loadAdmin()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to retrain the model.')
    }
  }

  const handleLogout = () => {
    logout()
    window.location.href = '/login'
  }

  const pageTitle = {
    customers: 'Customers',
    predictions: 'Predictions',
    analytics: 'Analytics',
    xai: 'SHAP Explanation',
    segments: 'Customer Segmentation',
    clv: 'Customer Lifetime Value',
    copilot: 'AI Copilot',
    reports: 'Reports',
    admin: 'Admin',
    profile: 'Profile',
  }[mode] || 'Module'

  const pageDescription = {
    customers: 'Manage customer records, filters, pagination, and detail views using the live backend API.',
    predictions: 'Review the latest prediction history and trigger a new batch prediction from the latest dataset.',
    analytics: 'Inspect live dashboard analytics from the backend summary endpoint.',
    xai: 'Generate SHAP-based explanations tied to the trained churn model.',
    segments: 'Assign and review customer segments using the CRM segmentation API.',
    clv: 'Inspect customer lifetime value, expected revenue, and priority scores.',
    copilot: 'Use AI prompts that combine customer, prediction, CLV, and explanation context.',
    reports: 'Create and manage export metadata for customer, churn, and monthly reports.',
    admin: 'Manage users, roles, model status, and retraining from one control center.',
    profile: 'Review the current authenticated user session.',
  }[mode] || ''

  if (loading) {
    return <div className="glass-card p-8 text-sm text-slate-500">Loading {pageTitle.toLowerCase()}...</div>
  }

  if (error) {
    return <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-4 text-sm font-medium text-rose-700">{error}</div>
  }

  if (mode === 'customers') {
    return (
      <div className="space-y-6">
        <SectionCard
          title="Customer Management"
          description={pageDescription}
          action={<button onClick={resetCustomerForm} className="rounded-2xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white">Add customer</button>}
        >
          <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
            {['search', 'company', 'country', 'risk_level', 'sort_by', 'sort_order'].map((name) => (
              <label key={name} className="block space-y-2">
                <span className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">{name.replaceAll('_', ' ')}</span>
                <input name={name} value={customerQuery[name] || ''} onChange={handleCustomerQueryChange} className={inputClass} placeholder={name} />
              </label>
            ))}
          </div>

          <div className="mt-4 overflow-hidden rounded-3xl border border-slate-200 bg-white">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                <tr>
                  <th className="px-4 py-3">Customer</th>
                  <th className="px-4 py-3">Company</th>
                  <th className="px-4 py-3">Risk</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {customers.map((customer) => (
                  <tr key={customer.id} className="hover:bg-blue-50/40">
                    <td className="px-4 py-3">
                      <button type="button" className="font-semibold text-blue-700" onClick={async () => { const response = await getCustomer(customer.id); setSelectedCustomer(response.data); setCustomerForm({ ...initialCustomerForm, ...response.data }); setEditingCustomerId(response.data.id) }}>
                        {customer.name}
                      </button>
                      <p className="text-xs text-slate-500">{customer.customer_id}</p>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{customer.company || '—'}</td>
                    <td className="px-4 py-3 text-slate-600">{customer.risk_level || 'low'}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-2">
                        <button className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold" onClick={() => { setSelectedCustomer(customer); setCustomerForm({ ...initialCustomerForm, ...customer }); setEditingCustomerId(customer.id) }}>Edit</button>
                        <button className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold" onClick={() => handleDeleteCustomer(customer.id)}>Delete</button>
                        <button className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold" onClick={async () => { const response = await getCustomer(customer.id); setSelectedCustomer(response.data); }}>Details</button>
                        <button
    className="rounded-xl bg-purple-600 text-white px-3 py-2 text-xs font-semibold"
    onClick={async () => {
        try {
            setLoadingExplanation(true);

            const response = await getXaiExplanation(customer.id);

            setSelectedExplanation(response.data);
        } catch (err) {
            console.error(err);
            alert("Unable to load AI explanation");
        } finally {
            setLoadingExplanation(false);
        }
    }}
>
    Explain AI
</button>

                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm text-slate-500">
            <p>Page {customerPage} of {customerPageCount}</p>
            <div className="flex gap-2">
              <button disabled={customerPage <= 1} onClick={() => setCustomerPage((current) => Math.max(1, current - 1))} className="rounded-xl border border-slate-200 bg-white px-3 py-2 font-semibold disabled:opacity-50">Previous</button>
              <button disabled={customerPage >= customerPageCount} onClick={() => setCustomerPage((current) => Math.min(customerPageCount, current + 1))} className="rounded-xl border border-slate-200 bg-white px-3 py-2 font-semibold disabled:opacity-50">Next</button>
            </div>
          </div>
        </SectionCard>

        {selectedCustomerRow ? (
          <SectionCard title="Customer Details" description="Detailed customer profile and edit form.">
            <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
              <div className="space-y-3 rounded-3xl border border-slate-200 bg-white p-5">
                <p className="text-sm font-semibold text-slate-400">Selected customer</p>
                <h3 className="title-display text-2xl font-bold text-slate-950">{selectedCustomerRow.name}</h3>
                <p className="text-sm text-slate-500">{selectedCustomerRow.email}</p>
                <div className="grid gap-3 sm:grid-cols-2">
  <div>
    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
      Risk
    </p>
    <p>{selectedCustomerRow.risk_level || "low"}</p>
  </div>

  <div>
    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
      Company
    </p>
    <p>{selectedCustomerRow.company || "—"}</p>
  </div>
</div>

<button
  className="mt-4 w-full rounded-xl bg-purple-600 px-4 py-2 font-semibold text-white hover:bg-purple-700"
  disabled={loadingExplanation}
  onClick={async () => {
    try {
      setLoadingExplanation(true);

      const response = await getXaiExplanation(selectedCustomerRow.id);

      setSelectedExplanation(response.data);
    } catch (err) {
      console.error(err);
      alert("Unable to load SHAP explanation");
    } finally {
      setLoadingExplanation(false);
    }
  }}
>
  {loadingExplanation ? "Loading..." : "Explain with AI"}
</button>

{selectedExplanation && (
  <div className="mt-6 rounded-xl border border-purple-300 bg-purple-50 p-4">
    <h3 className="mb-3 text-lg font-bold text-purple-700">
      SHAP Explanation
    </h3>

    <p>
      <strong>Risk Level:</strong> {selectedExplanation.risk_level}
    </p>

    <p>
      <strong>Probability:</strong>{" "}
      {(selectedExplanation.churn_probability * 100).toFixed(2)}%
    </p>

    <p className="mt-2">
      <strong>Recommendation:</strong>
      <br />
      {selectedExplanation.recommendation}
    </p>

    <p className="mt-2">
      <strong>Business Explanation:</strong>
      <br />
      {selectedExplanation.business_explanation}
    </p>

    <h4 className="mt-4 font-bold">
      Top Features
    </h4>

    <ul className="mt-2 space-y-2">
      {selectedExplanation.top_features.map((item) => (
        <li
          key={item.feature}
          className="rounded bg-white p-3 shadow"
        >
          <strong>{item.feature}</strong>

          <br />

          {item.direction}

          <br />

          Importance: {item.importance_score}
        </li>
      ))}
    </ul>
  </div>
)}
              </div>
              <CustomerForm value={customerForm} onChange={handleCustomerFormChange} onSubmit={saveCustomer} onCancel={resetCustomerForm} submitLabel={editingCustomerId ? 'Update customer' : 'Create customer'} />
            </div>
          </SectionCard>
        ) : (
          <SectionCard title="Add Customer" description="Create a customer record from the CRM form.">
            <CustomerForm value={customerForm} onChange={handleCustomerFormChange} onSubmit={saveCustomer} onCancel={resetCustomerForm} submitLabel={editingCustomerId ? 'Update customer' : 'Create customer'} />
          </SectionCard>
        )}
      </div>
    )
  }

  if (mode === 'predictions') {
    return (
      <div className="space-y-6">
        <SectionCard title="Prediction History" description={pageDescription} action={<button onClick={handleRunBatchPrediction} className="rounded-2xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white">Run batch prediction</button>}>
          <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                <tr>
                  <th className="px-4 py-3">Customer</th>
                  <th className="px-4 py-3">Risk</th>
                  <th className="px-4 py-3">Probability</th>
                  <th className="px-4 py-3">Recommendation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {history.map((item) => (
                  <tr key={item.id}>
                    <td className="px-4 py-3 font-semibold text-slate-900">{item.customer_id}</td>
                    <td className="px-4 py-3 text-slate-600">{item.risk}</td>
                    <td className="px-4 py-3 text-slate-600">{Number(item.probability || 0).toFixed(2)}</td>
                    <td className="px-4 py-3 text-slate-600">{item.recommendation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SectionCard>
      </div>
    )
  }

  if (mode === 'clv') {
    const topCustomers = clvSummary?.top_customers || []
    return (
      <div className="space-y-6">
        <MetricGrid
          items={[
            { label: 'Total customers', value: clvSummary?.total_customers ?? 0 },
            { label: 'Average CLV', value: `$${Number(clvSummary?.average_customer_lifetime_value || 0).toFixed(2)}` },
            { label: 'Priority customers', value: clvSummary?.priority_customers?.length ?? 0 },
            { label: 'High value customers', value: clvSummary?.high_value_customers?.length ?? 0 },
          ]}
        />
        <SectionCard title="Top Customers by CLV" description={pageDescription} action={<button onClick={loadClv} className="rounded-2xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white">Refresh</button>}>
          <div className="grid gap-3 lg:grid-cols-2">
            {topCustomers.map((customer) => (
              <div key={customer.id} className="rounded-3xl border border-slate-200 bg-white p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-semibold text-slate-900">{customer.name}</p>
                    <p className="text-sm text-slate-500">{customer.company || customer.customer_id}</p>
                  </div>
                  <button onClick={() => refreshCustomerClv(customer.id)} className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold">Refresh</button>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-600">
                  <p>CLV: <span className="font-semibold text-slate-950">${Number(customer.customer_lifetime_value || 0).toFixed(2)}</span></p>
                  <p>Priority: <span className="font-semibold text-slate-950">{Number(customer.priority_score || 0).toFixed(2)}</span></p>
                  <p>Revenue: <span className="font-semibold text-slate-950">${Number(customer.expected_revenue || 0).toFixed(2)}</span></p>
                  <p>Risk: <span className="font-semibold text-slate-950">{customer.churn_probability}</span></p>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
    )
  }

  if (mode === 'segments') {
    return (
      <div className="space-y-6">
        <MetricGrid
          items={[
            { label: 'Total segments', value: segmentStats?.total_segments ?? 0 },
            { label: 'Active segments', value: segmentStats?.active_segments ?? 0 },
            { label: 'Inactive segments', value: segmentStats?.inactive_segments ?? 0 },
            { label: 'Customers', value: customers.length },
          ]}
        />
        <SectionCard title="Segment Assignment" description="Assign a segment to any customer using the live backend heuristic." >
          <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                <tr>
                  <th className="px-4 py-3">Customer</th>
                  <th className="px-4 py-3">Segment</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {customers.map((customer) => (
                  <tr key={customer.id}>
                    <td className="px-4 py-3 font-semibold text-slate-900">{customer.name}</td>
                    <td className="px-4 py-3 text-slate-600">{customer.segment_name || customer.risk_level || 'Not assigned'}</td>
                    <td className="px-4 py-3">
                      <button onClick={async () => { await assignSegment(customer.id); await loadSegments() }} className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold">Assign segment</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {(segmentStats?.segment_distribution || []).map((item) => (
              <div key={item.name} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{item.name}</p>
                <p className="mt-2 text-2xl font-bold text-slate-950">{item.value}</p>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
    )
  }

  if (mode === 'copilot') {
    return (
      <div className="space-y-6">
        <SectionCard title="AI Copilot" description={pageDescription}>
          <form onSubmit={handleCopilotSubmit} className="space-y-4">
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <label className="space-y-2"><span className="text-sm font-semibold text-slate-700">Prompt</span><select className={inputClass} value={copilotPrompt} onChange={(e) => setCopilotPrompt(e.target.value)}>{copilotPrompts.map((prompt) => <option key={prompt}>{prompt}</option>)}</select></label>
              <label className="space-y-2"><span className="text-sm font-semibold text-slate-700">Customer ID</span><input className={inputClass} value={copilotCustomerId} onChange={(e) => setCopilotCustomerId(e.target.value)} placeholder="Optional customer id" /></label>
              <label className="space-y-2"><span className="text-sm font-semibold text-slate-700">Customer name</span><input className={inputClass} value={copilotCustomerName} onChange={(e) => setCopilotCustomerName(e.target.value)} placeholder="Optional customer name" /></label>
              <label className="space-y-2"><span className="text-sm font-semibold text-slate-700">Provider</span><select className={inputClass} value={copilotProvider} onChange={(e) => setCopilotProvider(e.target.value)}><option value="local">Local</option><option value="openai">OpenAI</option><option value="groq">Groq</option></select></label>
            </div>
            <textarea className={`${inputClass} min-h-[120px]`} value={copilotInput} onChange={(e) => setCopilotInput(e.target.value)} placeholder="Ask the copilot about retention, discounts, executive summaries, or sales actions..." />
            <button disabled={copilotLoading} className="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60">{copilotLoading ? 'Thinking...' : 'Send to copilot'}</button>
          </form>
        </SectionCard>

        <SectionCard title="Conversation" description="Messages remain in-memory during the session.">
          <div className="space-y-3 rounded-3xl border border-slate-200 bg-white p-4">
            {copilotMessages.length ? copilotMessages.map((message, index) => (
              <div key={`${message.role}-${index}`} className={`rounded-2xl px-4 py-3 ${message.role === 'assistant' ? 'bg-blue-50 text-blue-950' : 'bg-slate-50 text-slate-800'}`}>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{message.role}</p>
                <p className="mt-2 whitespace-pre-wrap text-sm leading-6">{message.content}</p>
              </div>
            )) : <p className="text-sm text-slate-500">No messages yet. Try one of the suggested prompts.</p>}
          </div>
          {copilotResponse ? <pre className="mt-4 overflow-auto rounded-3xl border border-slate-200 bg-slate-950 p-4 text-xs text-slate-100">{JSON.stringify(copilotResponse.context, null, 2)}</pre> : null}
        </SectionCard>
      </div>
    )
  }

  if (mode === 'reports') {
    return (
      <div className="space-y-6">
        <SectionCard title="Reports" description={pageDescription}>
          <form onSubmit={handleCreateReport} className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
            {Object.keys(reportFieldDefaults).map((field) => (
              <label key={field} className="space-y-2">
                <span className="text-sm font-semibold text-slate-700">{field.replaceAll('_', ' ')}</span>
                <input className={inputClass} value={reportForm[field] || ''} onChange={(e) => setReportForm((current) => ({ ...current, [field]: e.target.value }))} />
              </label>
            ))}
            <div className="flex items-end">
              <button className="w-full rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white">Create report</button>
            </div>
          </form>
        </SectionCard>

        <SectionCard title="Saved Reports" description="Manage generated report metadata.">
          <div className="grid gap-3">
            {reports.map((report) => (
              <div key={report.id} className="rounded-3xl border border-slate-200 bg-white p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-slate-900">{report.title}</p>
                    <p className="text-sm text-slate-500">{report.report_type} · {report.file_format} · {report.status}</p>
                  </div>
                  <button onClick={() => handleDeleteReport(report.id)} className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold">Delete</button>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
    )
  }

  if (mode === 'admin') {
    return (
      <div className="space-y-6">
        <MetricGrid
          items={[
            { label: 'Users', value: adminState?.user_metrics?.total_users ?? 0 },
            { label: 'Active', value: adminState?.user_metrics?.active_users ?? 0 },
            { label: 'Inactive', value: adminState?.user_metrics?.inactive_users ?? 0 },
            { label: 'Model ready', value: modelStatus?.model_exists ? 'Yes' : 'No' },
          ]}
        />

        <SectionCard title="Model Operations" description={pageDescription} action={<button onClick={handleRetrain} className="rounded-2xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white">Retrain model</button>}>
          <pre className="overflow-auto rounded-3xl border border-slate-200 bg-slate-950 p-4 text-xs text-slate-100">{JSON.stringify(modelStatus, null, 2)}</pre>
        </SectionCard>

        <SectionCard title="Users" description="Manage roles and account status.">
          <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                <tr>
                  <th className="px-4 py-3">User</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {adminUsers.map((item) => (
                  <tr key={item.id}>
                    <td className="px-4 py-3">
                      <p className="font-semibold text-slate-900">{item.name}</p>
                      <p className="text-xs text-slate-500">{item.email}</p>
                    </td>
                    <td className="px-4 py-3">
                      <select className={inputClass} value={item.role} onChange={(event) => handleRoleChange(item.id, event.target.value)}>
                        {roleOptions.map((role) => <option key={role} value={role}>{role}</option>)}
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <button className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold" onClick={() => handleStatusToggle(item.id, !item.is_active)}>{item.is_active ? 'Deactivate' : 'Activate'}</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SectionCard>
      </div>
    )
  }

  if (mode === 'xai') {
    return (
      <div className="space-y-6">
        <SectionCard title="SHAP Explanation" description={pageDescription}>
          <div className="flex flex-wrap gap-3">
            <input className={inputClass} value={xaiCustomerId} onChange={(e) => setXaiCustomerId(e.target.value)} placeholder="Customer ID" />
            <button onClick={() => loadXai()} className="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white">Explain</button>
          </div>
        </SectionCard>
        {xaiOutput ? <SectionCard title={`Why ${xaiOutput.customer_name} may churn`} description={xaiOutput.business_explanation}>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {(xaiOutput.top_features || []).map((feature) => (
              <div key={feature.feature} className="rounded-3xl border border-slate-200 bg-white p-4">
                <p className="font-semibold text-slate-900">{feature.feature}</p>
                <p className="text-sm text-slate-500">{feature.direction}</p>
                <p className="text-xs text-slate-400">Importance {Number(feature.importance_score || 0).toFixed(4)}</p>
              </div>
            ))}
          </div>
        </SectionCard> : null}
      </div>
    )
  }

  if (mode === 'profile') {
    return (
      <SectionCard title="Profile" description="Authenticated session details and logout control.">
        <div className="space-y-3 rounded-3xl border border-slate-200 bg-white p-4">
          <p className="font-semibold text-slate-900">{user?.name || 'Unknown user'}</p>
          <p className="text-sm text-slate-500">{user?.email}</p>
          <p className="text-sm text-slate-500">Role: {user?.role}</p>
          <button onClick={handleLogout} className="rounded-2xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white">Logout</button>
        </div>
      </SectionCard>
    )
  }

  return <SectionCard title={pageTitle} description={pageDescription}><p className="text-sm text-slate-600">This module is connected to the live backend and can be expanded with additional views.</p></SectionCard>
}