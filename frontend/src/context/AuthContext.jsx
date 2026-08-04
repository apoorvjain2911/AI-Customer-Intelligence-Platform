import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import {
  clearAuthSession,
  getCurrentUser,
  getStoredToken,
  getStoredUser,
  loginUser,
  registerUser,
  setAuthSession,
} from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser())
  const [token, setToken] = useState(() => getStoredToken())
  const [loading, setLoading] = useState(Boolean(getStoredToken()))

  const syncSession = (nextToken, nextUser) => {
    setToken(nextToken)
    setUser(nextUser)
    setAuthSession(nextToken, nextUser)
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    clearAuthSession()
  }

  const fetchCurrentUser = async () => {
    const storedToken = getStoredToken()

    if (!storedToken) {
      setLoading(false)
      return null
    }

    setLoading(true)

    try {
      const response = await getCurrentUser()
      const nextUser = response.data
      syncSession(storedToken, nextUser)
      return nextUser
    } catch {
      logout()
      return null
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (getStoredToken()) {
      fetchCurrentUser()
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (payload) => {
    const response = await loginUser(payload)
    const nextToken = response.data.access_token
    const nextUser = response.data.user || null

    if (nextToken) {
      syncSession(nextToken, nextUser)
    }

    if (!nextUser && nextToken) {
      await fetchCurrentUser()
    }

    return response.data
  }

  const register = async (payload) => {
    const response = await registerUser(payload)
    return response.data
  }

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      isAuthenticated: Boolean(token),
      login,
      register,
      logout,
      refreshSession: fetchCurrentUser,
    }),
    [loading, token, user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}