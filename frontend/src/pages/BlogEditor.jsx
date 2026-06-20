import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { FiSave, FiSend, FiZap, FiDownload, FiCheckCircle } from 'react-icons/fi'

export default function BlogEditor() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [blog, setBlog] = useState({ title: '', content: '', excerpt: '', keywords: [], status: 'draft' })
  const [loading, setLoading] = useState(id ? true : false)
  const [saving, setSaving] = useState(false)
  const [keywordInput, setKeywordInput] = useState('')

  useEffect(() => {
    if (id) {
      api.get(`/api/blogs/${id}/`).then(({ data }) => setBlog(data))
        .catch(() => toast.error('Failed to load blog'))
        .finally(() => setLoading(false))
    }
  }, [id])

  const handleSave = async () => {
    setSaving(true)
    try {
      if (id) {
        await api.patch(`/api/blogs/${id}/`, blog)
        toast.success('Blog saved')
      } else {
        const { data } = await api.post('/api/blogs/', blog)
        navigate(`/blogs/${data.id}`, { replace: true })
        toast.success('Blog created')
      }
    } catch { toast.error('Failed to save') } finally { setSaving(false) }
  }

  const handlePublish = async () => {
    if (!id) return
    try {
      await api.post(`/api/blogs/${id}/publish/`)
      setBlog(prev => ({ ...prev, status: 'published' }))
      toast.success('Blog published!')
    } catch { toast.error('Failed to publish') }
  }

  const handleGrammarCheck = async () => {
    if (!id) return
    try {
      const { data } = await api.post(`/api/blogs/${id}/grammar_check/`)
      if (data.corrected_content) setBlog(prev => ({ ...prev, content: data.corrected_content }))
      toast.success(`Grammar score: ${data.score || 'checked'}`)
    } catch { toast.error('Grammar check failed') }
  }

  const handleExport = async (format) => {
    if (!id) return
    try {
      const response = await api.get(`/api/blogs/${id}/export/?export_format=${format}`, { responseType: 'blob' })
      const ext = format === 'markdown' ? 'md' : format
      const safeName = blog.title.replace(/[\\/*?:"<>|]/g, '_').replace(/\s+/g, '_')
      const url = window.URL.createObjectURL(response.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `${safeName || 'blog'}.${ext}`
      document.body.appendChild(a)
      a.click()
      a.remove()
      setTimeout(() => window.URL.revokeObjectURL(url), 1000)
      toast.success(`Exported as ${format}`)
    } catch { toast.error('Export failed') }
  }

  const addKeyword = () => {
    if (keywordInput.trim() && !blog.keywords.includes(keywordInput.trim())) {
      setBlog(prev => ({ ...prev, keywords: [...prev.keywords, keywordInput.trim()] }))
      setKeywordInput('')
    }
  }

  if (loading) return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{id ? 'Edit Blog' : 'New Blog'}</h1>
        <div className="flex gap-2 flex-wrap">
          {id && <button onClick={handleGrammarCheck} className="btn-secondary flex items-center gap-1 text-sm"><FiCheckCircle /> Grammar</button>}
          {id && <button onClick={() => handleExport('markdown')} className="btn-secondary flex items-center gap-1 text-sm"><FiDownload /> MD</button>}
          {id && <button onClick={() => handleExport('html')} className="btn-secondary flex items-center gap-1 text-sm"><FiDownload /> HTML</button>}
          {id && <button onClick={() => handleExport('pdf')} className="btn-secondary flex items-center gap-1 text-sm"><FiDownload /> PDF</button>}
          {id && blog.status !== 'published' && <button onClick={handlePublish} className="btn-primary flex items-center gap-1 text-sm"><FiSend /> Publish</button>}
          <button onClick={handleSave} disabled={saving} className="btn-primary flex items-center gap-1"><FiSave /> {saving ? 'Saving...' : 'Save'}</button>
        </div>
      </div>

      <div className="card space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Title</label>
          <input value={blog.title} onChange={(e) => setBlog({...blog, title: e.target.value})} className="input-field text-lg font-semibold" placeholder="Blog title..." />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Content (Markdown)</label>
          <textarea value={blog.content} onChange={(e) => setBlog({...blog, content: e.target.value})} className="input-field font-mono text-sm" rows="20" placeholder="Write your blog content here..." />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Excerpt</label>
          <textarea value={blog.excerpt} onChange={(e) => setBlog({...blog, excerpt: e.target.value})} className="input-field" rows="2" placeholder="Brief summary..." />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Keywords</label>
          <div className="flex gap-2">
            <input value={keywordInput} onChange={(e) => setKeywordInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addKeyword())} className="input-field flex-1" placeholder="Add keyword..." />
            <button onClick={addKeyword} type="button" className="btn-secondary">Add</button>
          </div>
          <div className="flex flex-wrap gap-2 mt-2">
            {blog.keywords.map((kw, i) => (
              <span key={i} className="badge-primary flex items-center gap-1">
                {kw}
                <button onClick={() => setBlog(prev => ({ ...prev, keywords: prev.keywords.filter((_, j) => j !== i) }))} className="text-xs ml-1">&times;</button>
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
