import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { FiCompass, FiTrendingUp, FiDollarSign, FiClipboard, FiStar, FiBookOpen } from 'react-icons/fi'

export default function Career() {
  const [assessments, setAssessments] = useState([])
  const [recommendation, setRecommendation] = useState(null)
  const [trends, setTrends] = useState([])
  const [salaries, setSalaries] = useState([])
  const [loading, setLoading] = useState(true)
  const [showNewAssessment, setShowNewAssessment] = useState(false)
  const [category, setCategory] = useState('technology')
  const [skillLevel, setSkillLevel] = useState('beginner')
  const [creating, setCreating] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([
      api.get('/api/career/assessments/').catch(() => ({ data: [] })),
      api.get('/api/career/recommendations/latest/').catch(() => ({ data: null })),
      api.get('/api/career/trends/').catch(() => ({ data: [] })),
      api.get('/api/career/salaries/').catch(() => ({ data: [] })),
    ]).then(([assessmentsRes, recRes, trendsRes, salariesRes]) => {
      setAssessments(assessmentsRes.data.results || assessmentsRes.data || [])
      setRecommendation(recRes.data)
      setTrends(trendsRes.data.results || trendsRes.data || [])
      setSalaries(salariesRes.data.results || salariesRes.data || [])
    }).finally(() => setLoading(false))
  }, [])

  const handleStartAssessment = async (e) => {
    e.preventDefault()
    setCreating(true)
    try {
      const { data } = await api.post('/api/career/assessments/start/', { category, skill_level: skillLevel })
      setAssessments(prev => [data, ...prev])
      setShowNewAssessment(false)
      navigate(`/career/assessment/${data.id}`)
    } catch { toast.error('Failed to start assessment') } finally { setCreating(false) }
  }

  if (loading) return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">AI Career Guidance</h1>
          <p className="text-gray-500 dark:text-gray-400">Assess your skills and find the right career path</p>
        </div>
        <button onClick={() => setShowNewAssessment(!showNewAssessment)} className="btn-primary flex items-center gap-2"><FiClipboard /> Start Assessment</button>
      </div>

      {showNewAssessment && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Start Skill Assessment</h2>
          <form onSubmit={handleStartAssessment} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Category</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)} className="input-field">
                <option value="technology">Technology</option>
                <option value="healthcare">Healthcare</option>
                <option value="finance">Finance</option>
                <option value="education">Education</option>
                <option value="business">Business</option>
                <option value="science">Science</option>
                <option value="engineering">Engineering</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Skill Level</label>
              <select value={skillLevel} onChange={(e) => setSkillLevel(e.target.value)} className="input-field">
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
            <button type="submit" disabled={creating} className="btn-primary">{creating ? 'Creating...' : 'Start Assessment'}</button>
          </form>
        </div>
      )}

      {recommendation && (
        <div className="card border-l-4 border-primary-500">
          <h2 className="text-lg font-semibold flex items-center gap-2"><FiStar className="text-primary-600" /> Career Recommendation</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">{recommendation.summary}</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            {recommendation.career_options?.slice(0, 3).map((opt, i) => (
              <div key={i} className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <h3 className="font-semibold">{opt.title}</h3>
                <p className="text-sm text-gray-500">Match: {opt.match_percentage}%</p>
                <p className="text-xs text-gray-400 mt-1">{opt.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2"><FiTrendingUp /> Industry Trends</h2>
          <div className="space-y-3">
            {trends.slice(0, 5).map((trend, i) => (
              <div key={i} className="card p-4">
                <h3 className="font-medium text-sm">{trend.title}</h3>
                <p className="text-xs text-gray-500 mt-1">{trend.industry}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{trend.description}</p>
              </div>
            ))}
            {trends.length === 0 && <p className="text-sm text-gray-400">No trends loaded</p>}
          </div>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2"><FiDollarSign /> Salary Insights</h2>
          <div className="space-y-3">
            {salaries.slice(0, 5).map((sal, i) => (
              <div key={i} className="card p-4">
                <h3 className="font-medium text-sm">{sal.role}</h3>
                <p className="text-xs text-gray-500">{sal.industry} • {sal.experience_level}</p>
                <p className="text-lg font-bold text-primary-600 mt-1">{sal.salary_range}</p>
              </div>
            ))}
            {salaries.length === 0 && <p className="text-sm text-gray-400">No salary data loaded</p>}
          </div>
        </div>
      </div>

      {assessments.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2"><FiBookOpen /> Your Assessments</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {assessments.map((a) => (
              <div key={a.id} onClick={() => navigate(`/career/assessment/${a.id}`)} className="card cursor-pointer hover:shadow-md">
                <h3 className="font-medium">{a.title}</h3>
                <p className="text-sm text-gray-500">{a.category}</p>
                {a.is_completed ? (
                  <div className="mt-2"><span className="badge-success">Score: {a.overall_score}%</span></div>
                ) : (
                  <span className="badge-warning mt-2 inline-block">In Progress</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
