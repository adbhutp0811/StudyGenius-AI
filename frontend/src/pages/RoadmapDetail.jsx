import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { FiCheckCircle, FiCircle, FiChevronRight } from 'react-icons/fi'

export default function RoadmapDetail() {
  const { id } = useParams()
  const [roadmap, setRoadmap] = useState(null)
  const [loading, setLoading] = useState(true)
  const [milestones, setMilestones] = useState([])

  useEffect(() => {
    Promise.all([
      api.get(`/api/roadmaps/${id}/`),
      api.get(`/api/roadmaps/milestones/?roadmap=${id}`),
    ]).then(([rm, ms]) => {
      setRoadmap(rm.data)
      setMilestones(ms.data.results || ms.data)
    }).catch(() => toast.error('Failed to load roadmap'))
      .finally(() => setLoading(false))
  }, [id])

  const handleMilestoneComplete = async (milestoneId) => {
    try {
      await api.post(`/api/roadmaps/milestones/${milestoneId}/mark_complete/`)
      const { data } = await api.post(`/api/roadmaps/${id}/update_progress/`)
      setRoadmap(prev => ({ ...prev, progress: data.progress, is_completed: data.is_completed }))
      setMilestones(prev => prev.map(m => m.id === milestoneId ? { ...m, status: 'completed' } : m))
      toast.success('Milestone completed!')
    } catch { toast.error('Failed to update milestone') }
  }

  if (loading) return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>
  if (!roadmap) return <div className="text-center p-8">Roadmap not found</div>

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold">{roadmap.title}</h1>
        <p className="text-gray-500 dark:text-gray-400">{roadmap.career_goal_display} • {roadmap.duration_months} months</p>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Progress</span>
          <span className="text-sm font-medium text-primary-600">{roadmap.progress?.toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
          <div className="bg-primary-600 rounded-full h-3 transition-all duration-500" style={{ width: `${roadmap.progress || 0}%` }} />
        </div>
        {roadmap.is_completed && <p className="text-green-600 font-medium text-sm mt-2">🎉 All milestones completed!</p>}
      </div>

      <div className="space-y-3">
        <h2 className="text-xl font-semibold">Milestones</h2>
        {milestones.map((milestone, index) => (
          <div key={milestone.id} className={`card flex items-start gap-4 ${milestone.status === 'completed' ? 'opacity-75' : ''}`}>
            <button onClick={() => milestone.status !== 'completed' && handleMilestoneComplete(milestone.id)} className="mt-1">
              {milestone.status === 'completed'
                ? <FiCheckCircle className="w-6 h-6 text-green-500" />
                : <FiCircle className="w-6 h-6 text-gray-300 dark:text-gray-600" />}
            </button>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">#{index + 1}</span>
                <h3 className={`font-semibold ${milestone.status === 'completed' ? 'line-through text-gray-400' : ''}`}>{milestone.title}</h3>
                <span className={`badge ${milestone.status === 'completed' ? 'badge-success' : milestone.status === 'in_progress' ? 'badge-primary' : 'badge-warning'}`}>
                  {milestone.status.replace('_', ' ')}
                </span>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{milestone.description}</p>
              <p className="text-xs text-gray-400 mt-1">Duration: {milestone.duration_days} days</p>
              {milestone.resources?.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {milestone.resources.map((r, i) => (
                    <span key={i} className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">{r.title || r}</span>
                  ))}
                </div>
              )}
            </div>
            <FiChevronRight className="w-5 h-5 text-gray-300" />
          </div>
        ))}
      </div>
    </div>
  )
}
