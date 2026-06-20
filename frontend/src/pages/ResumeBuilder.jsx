import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { FiSave, FiSend, FiZap, FiDownload } from 'react-icons/fi'

export default function ResumeBuilder() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(id ? true : false)
  const [saving, setSaving] = useState(false)
  const [resume, setResume] = useState({
    title: 'My Resume', full_name: '', email: '', phone: '', address: '',
    linkedin: '', github: '', portfolio: '', professional_summary: '',
    skills: [], experience: [], education: [], certifications: [],
    projects: [], languages: [],
  })

  useEffect(() => {
    if (id) {
      api.get(`/api/resumes/${id}/`).then(({ data }) => setResume(data))
        .catch(() => toast.error('Failed to load resume'))
        .finally(() => setLoading(false))
    }
  }, [id])

  const handleSave = async () => {
    setSaving(true)
    try {
      if (id) {
        await api.patch(`/api/resumes/${id}/`, resume)
        toast.success('Resume updated')
      } else {
        const { data } = await api.post('/api/resumes/', resume)
        navigate(`/resumes/${data.id}`, { replace: true })
        toast.success('Resume created')
      }
    } catch { toast.error('Failed to save') } finally { setSaving(false) }
  }

  const handleGenerateSummary = async () => {
    if (!id) { toast.error('Save resume first'); return }
    try {
      const { data } = await api.post(`/api/resumes/${id}/generate_summary/`)
      setResume(prev => ({ ...prev, professional_summary: data.professional_summary }))
      toast.success('Summary generated')
    } catch { toast.error('Generation failed') }
  }

  const handleSuggestSkills = async () => {
    if (!id) { toast.error('Save resume first'); return }
    try {
      const { data } = await api.post(`/api/resumes/${id}/suggest_skills/`)
      const newSkills = [...new Set([...resume.skills, ...data.suggested_skills])]
      setResume(prev => ({ ...prev, skills: newSkills }))
      toast.success('Skills suggested')
    } catch { toast.error('Failed to suggest skills') }
  }

  const handleExportPDF = async () => {
    if (!id) return
    try {
      const response = await api.get(`/api/resumes/${id}/export_pdf/`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const a = document.createElement('a'); a.href = url; a.download = `${resume.full_name || 'Resume'}.pdf`
      a.click(); window.URL.revokeObjectURL(url)
      toast.success('PDF downloaded')
    } catch { toast.error('Export failed') }
  }

  const addItem = (field, item) => setResume(prev => ({ ...prev, [field]: [...prev[field], item] }))
  const removeItem = (field, index) => setResume(prev => ({ ...prev, [field]: prev[field].filter((_, i) => i !== index) }))

  if (loading) return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Resume Builder</h1>
        <div className="flex gap-2">
          <button onClick={handleExportPDF} className="btn-secondary flex items-center gap-1"><FiDownload /> PDF</button>
          <button onClick={handleSave} disabled={saving} className="btn-primary flex items-center gap-1"><FiSave /> {saving ? 'Saving...' : 'Save'}</button>
        </div>
      </div>

      <div className="card space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Resume Title</label><input value={resume.title} onChange={(e) => setResume({...resume, title: e.target.value})} className="input-field" /></div>
          <div><label className="block text-sm font-medium mb-1">Full Name</label><input value={resume.full_name} onChange={(e) => setResume({...resume, full_name: e.target.value})} className="input-field" /></div>
          <div><label className="block text-sm font-medium mb-1">Email</label><input type="email" value={resume.email} onChange={(e) => setResume({...resume, email: e.target.value})} className="input-field" /></div>
          <div><label className="block text-sm font-medium mb-1">Phone</label><input value={resume.phone} onChange={(e) => setResume({...resume, phone: e.target.value})} className="input-field" /></div>
          <div className="md:col-span-2"><label className="block text-sm font-medium mb-1">Address</label><input value={resume.address} onChange={(e) => setResume({...resume, address: e.target.value})} className="input-field" /></div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium">Professional Summary</label>
            <button onClick={handleGenerateSummary} className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"><FiZap /> Generate with AI</button>
          </div>
          <textarea value={resume.professional_summary} onChange={(e) => setResume({...resume, professional_summary: e.target.value})} className="input-field" rows="4" />
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium">Skills</label>
            <button onClick={handleSuggestSkills} className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"><FiZap /> Suggest Skills</button>
          </div>
          <input value={resume.skills.join(', ')} onChange={(e) => setResume({...resume, skills: e.target.value.split(',').map(s => s.trim()).filter(Boolean)})} className="input-field" placeholder="Python, JavaScript, React, ..." />
          <div className="flex flex-wrap gap-2 mt-2">
            {resume.skills.map((skill, i) => <span key={i} className="badge-primary">{skill}</span>)}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Experience</label>
          {resume.experience.map((exp, i) => (
            <div key={i} className="flex items-center gap-2 mb-2 p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span className="flex-1 text-sm">{exp.title} at {exp.company}</span>
              <button onClick={() => removeItem('experience', i)} className="text-red-500 text-sm">Remove</button>
            </div>
          ))}
          <button onClick={() => {
            const title = prompt('Job Title:'); const company = prompt('Company:')
            if (title && company) addItem('experience', { title, company, dates: '', description: '' })
          }} className="text-sm text-primary-600 hover:text-primary-700">+ Add Experience</button>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Education</label>
          {resume.education.map((edu, i) => (
            <div key={i} className="flex items-center gap-2 mb-2 p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span className="flex-1 text-sm">{edu.degree} at {edu.institution}</span>
              <button onClick={() => removeItem('education', i)} className="text-red-500 text-sm">Remove</button>
            </div>
          ))}
          <button onClick={() => {
            const degree = prompt('Degree:'); const institution = prompt('Institution:')
            if (degree && institution) addItem('education', { degree, institution, year: '' })
          }} className="text-sm text-primary-600 hover:text-primary-700">+ Add Education</button>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Projects</label>
          {resume.projects.map((proj, i) => (
            <div key={i} className="flex items-center gap-2 mb-2 p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span className="flex-1 text-sm">{proj.name}</span>
              <button onClick={() => removeItem('projects', i)} className="text-red-500 text-sm">Remove</button>
            </div>
          ))}
          <button onClick={() => {
            const name = prompt('Project Name:')
            if (name) addItem('projects', { name, description: '', technologies: [] })
          }} className="text-sm text-primary-600 hover:text-primary-700">+ Add Project</button>
        </div>
      </div>
    </div>
  )
}
