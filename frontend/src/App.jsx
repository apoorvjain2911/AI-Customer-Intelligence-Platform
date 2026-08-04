import { Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Dashboard from './pages/Dashboard'
import History from './pages/History'
import ModulePage from './pages/ModulePage'
import PublicPage from './pages/PublicPage'
import ProtectedRoute from './components/ProtectedRoute'

function Layout({ children }) {
  return (
    <div className="min-h-screen text-slate-900">
      <Navbar />
      <main className="mx-auto w-full max-w-7xl px-4 pb-12 pt-6 sm:px-6 lg:px-8">{children}</main>
      <Footer />
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <PublicPage mode="landing" />
        }
      />
      <Route path="/login" element={<PublicPage mode="login" />} />
      <Route path="/register" element={<PublicPage mode="register" />} />
      <Route
        path="/*"
        element={
          <Layout>
            <Routes>
              <Route path="dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="analytics" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="history" element={<ProtectedRoute><History /></ProtectedRoute>} />
              <Route path="customers" element={<ProtectedRoute><ModulePage mode="customers" /></ProtectedRoute>} />
              <Route path="customers/new" element={<ProtectedRoute><ModulePage mode="customers" /></ProtectedRoute>} />
              <Route path="customers/:customerId" element={<ProtectedRoute><ModulePage mode="customers" /></ProtectedRoute>} />
              <Route path="predictions" element={<ProtectedRoute><ModulePage mode="predictions" /></ProtectedRoute>} />
              <Route path="segments" element={<ProtectedRoute><ModulePage mode="segments" /></ProtectedRoute>} />
              <Route path="clv" element={<ProtectedRoute><ModulePage mode="clv" /></ProtectedRoute>} />
              <Route path="xai" element={<ProtectedRoute><ModulePage mode="xai" /></ProtectedRoute>} />
              <Route path="copilot" element={<ProtectedRoute><ModulePage mode="copilot" /></ProtectedRoute>} />
              <Route path="reports" element={<ProtectedRoute><ModulePage mode="reports" /></ProtectedRoute>} />
              <Route path="admin" element={<ProtectedRoute roles={["admin"]}><ModulePage mode="admin" /></ProtectedRoute>} />
              <Route path="profile" element={<ProtectedRoute><ModulePage mode="profile" /></ProtectedRoute>} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Layout>
        }
      />
    </Routes>
  )
}
