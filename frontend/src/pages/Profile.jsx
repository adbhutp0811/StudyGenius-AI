import { useState, useEffect } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'
import { FiUser, FiMail, FiPhone, FiBook, FiSave } from 'react-icons/fi'

export default function Profile() {
  const [profile, setProfile] = useState({ full_name: '', phone: '', bio: '', education: '', skills: [] })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.get('/api/auth/profile/').then(({ data }) => {
      setProfile({ full_name: data.full_name || '', phone: data.phone || '', bio: data.bio || '', education: data.education || '', skills: data.skills || [] })
    }).catch(() => toast.error('Failed to load profile')).finally(() => setLoading(false))
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.patch('/api/auth/profile/', profile)
      toast.success('Profile updated')
    } catch { toast.error('Failed to update') } finally { setSaving(false) }
  }

  if (loading) return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Profile Settings</h1>
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-20 h-20 rounded-full bg-primary-600 text-white flex items-center justify-center text-2xl font-bold">
              {profile.full_name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <div><h2 className="text-xl font-semibold">{profile.full_name || 'Your Name'}</h2><p className="text-gray-500 text-sm">Manage your profile information</p></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Full Name</label>
              <div className="relative"><FiUser className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" /><input value={profile.full_name} onChange={(e) => setProfile({...profile, full_name: e.target.value})} className="input-field pl-10" /></div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Phone</label>
              <div className="relative"><FiPhone className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" /><input value={profile.phone} onChange={(e) => setProfile({...profile, phone: e.target.value})} className="input-field pl-10" /></div>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Education</label>
            <div className="relative"><FiBook className="absolute left-3 top-3 text-gray-400" /><input value={profile.education} onChange={(e) => setProfile({...profile, education: e.target.value})} className="input-field pl-10" placeholder="e.g., B.Tech Computer Science" /></div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Bio</label>
            <textarea value={profile.bio} onChange={(e) => setProfile({...profile, bio: e.target.value})} className="input-field" rows="3" placeholder="Tell us about yourself" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Skills (comma separated)</label>
            <input value={profile.skills.join(', ')} onChange={(e) => setProfile({...profile, skills: e.target.value.split(',').map(s => s.trim()).filter(Boolean)})} className="input-field" placeholder="Python, JavaScript, React" />
            <div className="flex flex-wrap gap-2 mt-2">
              {profile.skills.map((skill, i) => <span key={i} className="badge-primary">{skill}</span>)}
            </div>
          </div>
          <button type="submit" disabled={saving} className="btn-primary flex items-center gap-2"><FiSave /> {saving ? 'Saving...' : 'Save Changes'}</button>
        </form>
      </div>
    </div>
  )
}
