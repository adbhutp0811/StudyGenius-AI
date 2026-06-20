import { useState, useEffect } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'
import { FiMessageCircle, FiPlus, FiDownload, FiTrash2, FiEye } from 'react-icons/fi'
import { DIFFICULTY_LEVELS } from '../utils/constants'

export default function QuestionPapers() {
  const [papers, setPapers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showGenerator, setShowGenerator] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [selectedPaper, setSelectedPaper] = useState(null)
  const [form, setForm] = useState({
    subject: '', syllabus: '', difficulty: 'medium',
    num_mcq: 5, num_short_answer: 5, num_long_answer: 3,
    time_duration_minutes: 60,
  })

  useEffect(() => {
    api.get('/api/question-papers/papers/').then(({ data }) => setPapers(data.results || data))
      .catch(() => {}).finally(() => setLoading(false))
  }, [])

  const handleGenerate = async (e) => {
    e.preventDefault()
    setGenerating(true)
    try {
      const { data } = await api.post('/api/question-papers/papers/generate/', form)
      setPapers(prev => [data, ...prev])
      setSelectedPaper(data)
      setShowGenerator(false)
      toast.success('Question paper generated!')
    } catch { toast.error('Generation failed') } finally { setGenerating(false) }
  }

  const handleExportPDF = async (id) => {
    try {
      const response = await api.get(`/api/question-papers/papers/${id}/export_pdf/`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const a = document.createElement('a'); a.href = url; a.download = 'question-paper.pdf'
      a.click(); window.URL.revokeObjectURL(url)
      toast.success('PDF exported')
    } catch { toast.error('Export failed') }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this paper?')) return
    try {
      await api.delete(`/api/question-papers/papers/${id}/`)
      setPapers(prev => prev.filter(p => p.id !== id))
      if (selectedPaper?.id === id) setSelectedPaper(null)
      toast.success('Deleted')
    } catch { toast.error('Failed to delete') }
  }

  const groupedByDifficulty = (questions = []) => ({
    mcq: questions.filter(q => q.type === 'mcq'),
    short: questions.filter(q => q.type === 'short_answer'),
    long: questions.filter(q => q.type === 'long_answer'),
  })

  if (loading) return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>

  return (
    <div className="flex gap-6 h-[calc(100vh-8rem)] animate-fade-in">
      <div className="w-80 shrink-0 space-y-4 overflow-y-auto">
        <button onClick={() => setShowGenerator(!showGenerator)} className="w-full btn-primary flex items-center gap-2 justify-center"><FiPlus /> Generate Paper</button>

        {showGenerator && (
          <div className="card p-4">
            <h3 className="font-semibold mb-3">Generate Question Paper</h3>
            <form onSubmit={handleGenerate} className="space-y-3">
              <input value={form.subject} onChange={(e) => setForm({...form, subject: e.target.value})} className="input-field text-sm" placeholder="Subject" required />
              <textarea value={form.syllabus} onChange={(e) => setForm({...form, syllabus: e.target.value})} className="input-field text-sm" rows="2" placeholder="Syllabus (optional)" />
              <select value={form.difficulty} onChange={(e) => setForm({...form, difficulty: e.target.value})} className="input-field text-sm">
                {DIFFICULTY_LEVELS.map(d => <option key={d.value} value={d.value}>{d.label}</option>)}
              </select>
              <div className="grid grid-cols-2 gap-2">
                <div><label className="text-xs">MCQs</label><input type="number" min={0} value={form.num_mcq} onChange={(e) => setForm({...form, num_mcq: parseInt(e.target.value) || 0})} className="input-field text-sm" /></div>
                <div><label className="text-xs">Short</label><input type="number" min={0} value={form.num_short_answer} onChange={(e) => setForm({...form, num_short_answer: parseInt(e.target.value) || 0})} className="input-field text-sm" /></div>
                <div><label className="text-xs">Long</label><input type="number" min={0} value={form.num_long_answer} onChange={(e) => setForm({...form, num_long_answer: parseInt(e.target.value) || 0})} className="input-field text-sm" /></div>
                <div><label className="text-xs">Minutes</label><input type="number" value={form.time_duration_minutes} onChange={(e) => setForm({...form, time_duration_minutes: parseInt(e.target.value) || 60})} className="input-field text-sm" /></div>
              </div>
              <button type="submit" disabled={generating} className="btn-primary w-full text-sm">{generating ? 'Generating...' : 'Generate'}</button>
            </form>
          </div>
        )}

        <h3 className="text-xs font-semibold text-gray-500 uppercase px-1">Saved Papers</h3>
        {papers.map((p) => (
          <div key={p.id} className={`card p-3 cursor-pointer hover:shadow transition-shadow ${selectedPaper?.id === p.id ? 'ring-2 ring-primary-500' : ''}`} onClick={() => setSelectedPaper(p)}>
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{p.title}</p>
                <p className="text-xs text-gray-400">{p.subject_name} • {p.difficulty}</p>
                <p className="text-xs text-gray-400">{p.total_questions} questions • {p.total_marks} marks</p>
              </div>
              <div className="flex gap-1">
                <button onClick={(e) => { e.stopPropagation(); handleExportPDF(p.id) }} className="p-1 text-gray-400 hover:text-primary-600"><FiDownload className="w-3.5 h-3.5" /></button>
                <button onClick={(e) => { e.stopPropagation(); handleDelete(p.id) }} className="p-1 text-gray-400 hover:text-red-500"><FiTrash2 className="w-3.5 h-3.5" /></button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex-1 card overflow-y-auto">
        {selectedPaper ? (
          <div className="space-y-6">
            <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
              <h2 className="text-xl font-bold">{selectedPaper.title}</h2>
              <p className="text-sm text-gray-500">
                {selectedPaper.subject_name} • {selectedPaper.difficulty} • 
                Duration: {selectedPaper.time_duration_minutes} mins • 
                Total: {selectedPaper.total_marks} marks
              </p>
            </div>
            {(() => {
              const grouped = groupedByDifficulty(selectedPaper.questions)
              return (
                <>
                  {grouped.mcq.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-primary-600 mb-3">Section A: Multiple Choice Questions ({grouped.mcq.length} × 1 mark)</h3>
                      {grouped.mcq.map((q, i) => (
                        <div key={q.id || i} className="mb-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                          <p className="font-medium text-sm">{i + 1}. {q.question}</p>
                          <div className="ml-4 mt-2 space-y-1">
                            {(q.options || []).map((opt, oi) => <p key={oi} className="text-sm text-gray-600 dark:text-gray-400">{String.fromCharCode(65 + oi)}. {opt}</p>)}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  {grouped.short.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-primary-600 mb-3">Section B: Short Answer Questions ({grouped.short.length} × 2 marks)</h3>
                      {grouped.short.map((q, i) => (
                        <div key={q.id || i} className="mb-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                          <p className="font-medium text-sm">{i + 1}. {q.question}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  {grouped.long.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-primary-600 mb-3">Section C: Long Answer Questions ({grouped.long.length} × 5 marks)</h3>
                      {grouped.long.map((q, i) => (
                        <div key={q.id || i} className="mb-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                          <p className="font-medium text-sm">{i + 1}. {q.question}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )
            })()}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
            <FiMessageCircle className="w-16 h-16 mb-4" />
            <p>Generate or select a question paper</p>
          </div>
        )}
      </div>
    </div>
  )
}
