import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { CAREER_GOALS } from '../utils/constants'
import { FiMap, FiPlus, FiTrendingUp, FiClock } from 'react-icons/fi'

export default function Roadmaps() {
  const [roadmaps, setRoadmaps] = useState([])
  const [loading, setLoading] = useState(true)
  const [showGenerator, setShowGenerator] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [form, setForm] = useState({ career_goal: 'web_development', duration_months: 6, skill_level: 'beginner' })
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/api/roadmaps/').then(({ data }) => setRoadmaps(data.results || data))
      .catch(() => toast.error('Failed to load roadmaps'))
      .finally(() => setLoading(false))
  }, [])

  const handleGenerate = async (e) => {
    e.preventDefault()
    setGenerating(true)
    try {
      const { data } = await api.post('/api/roadmaps/generate/', form)
      setRoadmaps(prev => [data, ...prev])
      setShowGenerator(false)
      toast.success('Roadmap generated!')
      navigate(`/roadmaps/${data.id}`)
    } catch { toast.error('Generation failed') } finally { setGenerating(false) }
  }

  if (loading) return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">AI Roadmap Generator</h1>
          <p className="text-gray-500 dark:text-gray-400">Personalized learning roadmaps</p>
        </div>
        <button onClick={() => setShowGenerator(!showGenerator)} className="btn-primary flex items-center gap-2"><FiPlus /> New Roadmap</button>
      </div>

      {showGenerator && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Generate Learning Roadmap</h2>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Career Goal</label>
              <select value={form.career_goal} onChange={(e) => setForm({...form, career_goal: e.target.value})} className="input-field">
                {CAREER_GOALS.map(g => <option key={g.value} value={g.value}>{g.icon} {g.label}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Duration (months)</label>
                <input type="number" min={1} max={24} value={form.duration_months} onChange={(e) => setForm({...form, duration_months: parseInt(e.target.value)})} className="input-field" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Skill Level</label>
                <select value={form.skill_level} onChange={(e) => setForm({...form, skill_level: e.target.value})} className="input-field">
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
            </div>
            <button type="submit" disabled={generating} className="btn-primary">{generating ? 'Generating...' : 'Generate Roadmap'}</button>
          </form>
        </div>
      )}

      {roadmaps.length === 0 && !showGenerator ? (
        <div className="card text-center py-12">
          <FiMap className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-600 dark:text-gray-400">No roadmaps yet</h3>
          <p className="text-gray-400 dark:text-gray-500 mt-1">Generate your first learning roadmap</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {roadmaps.map((rm) => (
            <div key={rm.id} onClick={() => navigate(`/roadmaps/${rm.id}`)} className="card hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-start gap-3 mb-3">
                <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900/20"><FiMap className="w-5 h-5 text-green-600" /></div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">{rm.title}</h3>
                  <p className="text-sm text-gray-500">{rm.career_goal_display}</p>
                </div>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span className="flex items-center gap-1"><FiTrendingUp className="w-4 h-4" /> {rm.progress?.toFixed(0)}%</span>
                <span className="flex items-center gap-1"><FiClock className="w-4 h-4" /> {rm.duration_months}mo</span>
              </div>
              <div className="mt-3 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div className="bg-primary-600 rounded-full h-2 transition-all" style={{ width: `${rm.progress || 0}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
