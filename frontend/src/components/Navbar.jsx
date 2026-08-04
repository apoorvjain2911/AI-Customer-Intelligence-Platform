import { ActivitySquare, LogOut, UserCircle2 } from 'lucide-react'
import { NavLink, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const navLinkClass = ({ isActive }) =>
  [
    'rounded-full px-4 py-2 text-sm font-medium transition-all duration-200',
    isActive ? 'bg-blue-600 text-white shadow-lg shadow-blue-200' : 'text-slate-600 hover:bg-blue-50 hover:text-blue-700',
  ].join(' ')

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()

  return (
    <header className="sticky top-0 z-50 border-b border-white/60 bg-white/75 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-200">
            <ActivitySquare className="h-6 w-6" />
          </span>
          <div>
            <p className="title-display text-lg font-bold text-slate-950 sm:text-xl">AI Customer Intelligence</p>
            <p className="text-xs font-medium uppercase tracking-[0.24em] text-slate-400">Enterprise CRM</p>
          </div>
        </Link>

        <nav className="flex flex-wrap items-center justify-end gap-2">
          <NavLink to="/dashboard" className={navLinkClass}>
            Dashboard
          </NavLink>
          <NavLink to="/customers" className={navLinkClass}>
            Customers
          </NavLink>
          <NavLink to="/copilot" className={navLinkClass}>
            Copilot
          </NavLink>
          <NavLink to="/admin" className={navLinkClass}>
            Admin
          </NavLink>
          <NavLink to="/history" className={navLinkClass}>
            History
          </NavLink>
          {isAuthenticated ? (
            <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5">
              <UserCircle2 className="h-4 w-4 text-slate-500" />
              <span className="text-sm font-medium text-slate-700">{user?.name || user?.email || 'User'}</span>
              <button type="button" onClick={logout} className="inline-flex items-center gap-1 rounded-full bg-slate-950 px-3 py-1.5 text-xs font-semibold text-white">
                <LogOut className="h-3.5 w-3.5" />
                Logout
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <NavLink to="/login" className={navLinkClass}>Login</NavLink>
              <NavLink to="/register" className={navLinkClass}>Register</NavLink>
            </div>
          )}
        </nav>
      </div>
    </header>
  )
}
