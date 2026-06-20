import { useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { FiLock } from 'react-icons/fi'
import toast from 'react-hot-toast'

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const [form, setForm] = useState({ password: '', password2: '' })
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password !== form.password2) { toast.error('Passwords do not match'); return }
    setLoading(true)
    try {
      await api.post('/api/auth/reset-password/', { token: searchParams.get('token'), ...form })
      toast.success('Password reset successful')
      navigate('/login')
    } catch { toast.error('Failed to reset password') } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-accent-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 p-4">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-600 mb-4"><span className="text-2xl font-bold text-white">SG</span></div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Reset Password</h1>
        </div>
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">New Password</label>
              <div className="relative"><FiLock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" /><input type="password" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})} className="input-field pl-10" required /></div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Confirm Password</label>
              <div className="relative"><FiLock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" /><input type="password" value={form.password2} onChange={(e) => setForm({...form, password2: e.target.value})} className="input-field pl-10" required /></div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full py-3">{loading ? 'Resetting...' : 'Reset Password'}</button>
          </form>
        </div>
      </div>
    </div>
  )
}
