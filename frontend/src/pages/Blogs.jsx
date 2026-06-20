import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { FiPlus, FiEdit3, FiTrash2, FiZap } from 'react-icons/fi'

export default function Blogs() {
  const [blogs, setBlogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [showGenerator, setShowGenerator] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [keywords, setKeywords] = useState('')
  const [tone, setTone] = useState('professional')
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/api/blogs/').then(({ data }) => setBlogs(data.results || data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleGenerate = async (e) => {
    e.preventDefault()
    setGenerating(true)
    try {
      const { data } = await api.post('/api/blogs/generate/', {
        keywords: keywords.split(',').map(k => k.trim()).filter(Boolean),
        tone,
      })
      setBlogs(prev => [data, ...prev])
      setShowGenerator(false)
      toast.success('Blog generated!')
      navigate(`/blogs/${data.id}`)
    } catch { toast.error('Generation failed') } finally { setGenerating(false) }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this blog?')) return
    try {
      await api.delete(`/api/blogs/${id}/`)
      setBlogs(prev => prev.filter(b => b.id !== id))
      toast.success('Blog deleted')
    } catch { toast.error('Failed to delete') }
  }

  if (loading) return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">AI Blog Writer</h1>
          <p className="text-gray-500 dark:text-gray-400">Generate and manage blog articles</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowGenerator(!showGenerator)} className="btn-secondary flex items-center gap-2"><FiZap /> Generate</button>
          <Link to="/blogs/new" className="btn-primary flex items-center gap-2"><FiPlus /> New Blog</Link>
        </div>
      </div>

      {showGenerator && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Generate Blog with AI</h2>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Keywords (comma-separated)</label>
              <input value={keywords} onChange={(e) => setKeywords(e.target.value)} className="input-field" placeholder="AI, machine learning, future" required />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Tone</label>
              <select value={tone} onChange={(e) => setTone(e.target.value)} className="input-field">
                <option value="professional">Professional</option>
                <option value="conversational">Conversational</option>
                <option value="academic">Academic</option>
                <option value="creative">Creative</option>
                <option value="technical">Technical</option>
              </select>
            </div>
            <button type="submit" disabled={generating} className="btn-primary">{generating ? 'Generating...' : 'Generate Blog'}</button>
          </form>
        </div>
      )}

      {blogs.length === 0 ? (
        <div className="card text-center py-12">
          <FiEdit3 className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-600 dark:text-gray-400">No blogs yet</h3>
          <p className="text-gray-400 dark:text-gray-500 mt-1">Generate your first blog article</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {blogs.map((blog) => (
            <div key={blog.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-2">
                <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/20"><FiEdit3 className="w-5 h-5 text-orange-600" /></div>
                <button onClick={() => handleDelete(blog.id)} className="p-1 hover:bg-red-100 dark:hover:bg-red-900/20 rounded text-red-500"><FiTrash2 className="w-4 h-4" /></button>
              </div>
              <Link to={`/blogs/${blog.id}`}>
                <h3 className="font-semibold text-gray-900 dark:text-white hover:text-primary-600">{blog.title}</h3>
              </Link>
              <p className="text-sm text-gray-500 mt-1 line-clamp-2">{blog.excerpt}</p>
              <div className="flex items-center gap-2 mt-3">
                <span className={`badge ${blog.status === 'published' ? 'badge-success' : 'badge-warning'}`}>{blog.status}</span>
                <span className="text-xs text-gray-400">{blog.reading_time} min read</span>
                <span className="text-xs text-gray-400">{blog.word_count} words</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
