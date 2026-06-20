import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { FiPlus, FiFileText, FiTrash2, FiEdit2, FiBarChart2 } from 'react-icons/fi'

export default function Resumes() {
  const [resumes, setResumes] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/api/resumes/').then(({ data }) => setResumes(data.results || data))
      .catch(() => toast.error('Failed to load resumes'))
      .finally(() => setLoading(false))
  }, [])

  const handleDelete = async (id) => {
    if (!confirm('Delete this resume?')) return
    try {
      await api.delete(`/api/resumes/${id}/`)
      setResumes(resumes.filter(r => r.id !== id))
      toast.success('Resume deleted')
    } catch { toast.error('Failed to delete') }
  }

  const handleAnalyze = async (id) => {
    try {
      const { data } = await api.post(`/api/resumes/${id}/analyze_score/`)
      toast.success(`Score: ${data.score}/100`)
    } catch { toast.error('Analysis failed') }
  }

  if (loading) return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">AI Resume Builder</h1>
          <p className="text-gray-500 dark:text-gray-400">Create professional resumes with AI</p>
        </div>
        <Link to="/resumes/new" className="btn-primary flex items-center gap-2"><FiPlus /> New Resume</Link>
      </div>
      {resumes.length === 0 ? (
        <div className="card text-center py-12">
          <FiFileText className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-600 dark:text-gray-400">No resumes yet</h3>
          <p className="text-gray-400 dark:text-gray-500 mt-1">Create your first AI-powered resume</p>
          <Link to="/resumes/new" className="btn-primary inline-flex items-center gap-2 mt-4"><FiPlus /> Create Resume</Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {resumes.map((resume) => (
            <div key={resume.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="p-2 rounded-lg bg-primary-100 dark:bg-primary-900/20"><FiFileText className="w-5 h-5 text-primary-600" /></div>
                <div className="flex gap-1">
                  <button onClick={() => navigate(`/resumes/${resume.id}`)} className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"><FiEdit2 className="w-4 h-4" /></button>
                  <button onClick={() => handleAnalyze(resume.id)} className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"><FiBarChart2 className="w-4 h-4" /></button>
                  <button onClick={() => handleDelete(resume.id)} className="p-1.5 hover:bg-red-100 dark:hover:bg-red-900/20 rounded text-red-500"><FiTrash2 className="w-4 h-4" /></button>
                </div>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white">{resume.title}</h3>
              <p className="text-sm text-gray-500">{resume.full_name}</p>
              <div className="flex items-center gap-2 mt-2">
                <span className={`badge ${resume.is_complete ? 'badge-success' : 'badge-warning'}`}>{resume.is_complete ? 'Complete' : 'Draft'}</span>
                {resume.ats_score > 0 && <span className="badge-primary">Score: {resume.ats_score}</span>}
              </div>
              <p className="text-xs text-gray-400 mt-2">Updated: {new Date(resume.updated_at).toLocaleDateString()}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
