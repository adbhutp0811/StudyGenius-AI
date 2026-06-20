import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { FiMail, FiArrowLeft } from 'react-icons/fi'
import toast from 'react-hot-toast'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await api.post('/api/auth/forgot-password/', { email })
      setSent(true)
      toast.success('Reset link sent if email exists')
    } catch { toast.error('Failed to send reset email') } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-accent-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 p-4">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-600 mb-4"><span className="text-2xl font-bold text-white">SG</span></div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Forgot Password</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">{sent ? 'Check your email for reset instructions' : "Enter your email and we'll send you a reset link"}</p>
        </div>
        <div className="card">
          {!sent ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <div className="relative">
                  <FiMail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="input-field pl-10" placeholder="you@example.com" required />
                </div>
              </div>
              <button type="submit" disabled={loading} className="btn-primary w-full py-3">{loading ? 'Sending...' : 'Send Reset Link'}</button>
            </form>
          ) : (
            <div className="text-center py-4">
              <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center mx-auto mb-4">✓</div>
              <p className="text-gray-600 dark:text-gray-400">Password reset instructions have been sent to your email.</p>
            </div>
          )}
          <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
            <Link to="/login" className="flex items-center justify-center gap-1 text-primary-600 hover:text-primary-700"><FiArrowLeft /> Back to Login</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
