import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import type { AuthUser, Role } from './types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const TOKEN_KEY = 'ai4sids_token'

interface AuthContextValue {
  token: string | null
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  hasRole: (...roles: Role[]) => boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(() => !!localStorage.getItem(TOKEN_KEY))

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
    setIsLoading(false)
  }, [])

  const fetchMe = useCallback(
    async (activeToken: string) => {
      setIsLoading(true)
      try {
        const res = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${activeToken}` },
        })
        if (res.status === 401) {
          logout()
          return
        }
        if (!res.ok) throw new Error(`Failed to load user: ${res.status}`)
        setUser((await res.json()) as AuthUser)
      } finally {
        setIsLoading(false)
      }
    },
    [logout],
  )

  useEffect(() => {
    if (token) void fetchMe(token)
  }, [token, fetchMe])

  const login = useCallback(async (email: string, password: string) => {
    const body = new URLSearchParams({ username: email, password })
    const res = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail ?? 'Invalid email or password')
    }

    const { access_token } = await res.json()
    localStorage.setItem(TOKEN_KEY, access_token)
    setToken(access_token)
  }, [])

  const refreshUser = useCallback(async () => {
    if (token) await fetchMe(token)
  }, [token, fetchMe])

  const hasRole = useCallback(
    (...roles: Role[]) => {
      if (!user) return false
      return user.role === 'super_admin' || roles.includes(user.role)
    },
    [user],
  )

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isAuthenticated: !!token,
        isLoading,
        hasRole,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
