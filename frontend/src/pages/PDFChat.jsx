import { useState, useEffect, useRef } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'
import { FiUpload, FiFile, FiSend, FiTrash2, FiSearch, FiPlus } from 'react-icons/fi'

export default function PDFChat() {
  const [documents, setDocuments] = useState([])
  const [sessions, setSessions] = useState([])
  const [activeSession, setActiveSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [selectedDocs, setSelectedDocs] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    Promise.all([
      api.get('/api/pdfchat/documents/').then(({ data }) => setDocuments(data.results || data)).catch(() => {}),
      api.get('/api/pdfchat/sessions/').then(({ data }) => setSessions(data.results || data)).catch(() => {}),
    ])
  }, [])

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file || file.type !== 'application/pdf') { toast.error('Please select a PDF file'); return }
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', file.name.replace('.pdf', ''))
    try {
      const { data } = await api.post('/api/pdfchat/documents/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setDocuments(prev => [data, ...prev])
      toast.success('PDF uploaded and processed')
    } catch { toast.error('Upload failed') } finally { setUploading(false) }
  }

  const loadSession = async (sessionId) => {
    setLoading(true)
    try {
      const { data } = await api.get(`/api/pdfchat/sessions/${sessionId}/`)
      setActiveSession(data)
      setMessages(data.messages || [])
    } catch { toast.error('Failed to load session') } finally { setLoading(false) }
  }

  const handleAsk = async (e) => {
    e.preventDefault()
    if (!question.trim()) return
    if (!activeSession && selectedDocs.length === 0) { toast.error('Select PDFs or start a session'); return }
    setLoading(true)
    const q = question
    setQuestion('')
    try {
      const { data } = await api.post('/api/pdfchat/sessions/ask/', {
        session_id: activeSession?.id || '',
        document_ids: selectedDocs,
        question: q,
      })
      setActiveSession(data.session)
      setMessages(data.session.messages || [])
      setSessions(prev => {
        const exists = prev.find(s => s.id === data.session.id)
        return exists ? prev : [data.session, ...prev]
      })
      if (selectedDocs.length > 0) setSelectedDocs([])
    } catch { toast.error('Failed to get answer') } finally { setLoading(false) }
  }

  const handleDeleteDoc = async (id) => {
    try {
      await api.delete(`/api/pdfchat/documents/${id}/`)
      setDocuments(prev => prev.filter(d => d.id !== id))
      toast.success('Document deleted')
    } catch { toast.error('Failed to delete') }
  }

  const toggleDoc = (id) => {
    setSelectedDocs(prev => prev.includes(id) ? prev.filter(d => d !== id) : [...prev, id])
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4 animate-fade-in">
      <div className="w-72 shrink-0 space-y-2 overflow-y-auto">
        <div className="card p-3">
          <label className="btn-primary flex items-center gap-2 justify-center cursor-pointer text-sm">
            <FiUpload /> {uploading ? 'Uploading...' : 'Upload PDF'}
            <input type="file" accept=".pdf" onChange={handleUpload} className="hidden" disabled={uploading} />
          </label>
        </div>
        {documents.length > 0 && (
          <div className="card p-3">
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Documents</h3>
            {documents.map((doc) => (
              <div key={doc.id} className="flex items-center gap-2 py-1.5">
                <input type="checkbox" checked={selectedDocs.includes(doc.id)} onChange={() => toggleDoc(doc.id)} className="rounded" />
                <FiFile className="w-4 h-4 text-gray-400 shrink-0" />
                <span className="text-sm truncate flex-1">{doc.title}</span>
                <button onClick={() => handleDeleteDoc(doc.id)} className="text-gray-400 hover:text-red-500"><FiTrash2 className="w-3 h-3" /></button>
              </div>
            ))}
          </div>
        )}
        <div className="card p-3">
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Chat Sessions</h3>
          <button onClick={() => { setActiveSession(null); setMessages([]) }} className="w-full flex items-center gap-2 text-sm text-primary-600 mb-2"><FiPlus /> New Chat</button>
          {sessions.map((s) => (
            <div key={s.id} className={`p-2 rounded-lg cursor-pointer text-sm hover:bg-gray-100 dark:hover:bg-gray-700 ${activeSession?.id === s.id ? 'bg-primary-50 dark:bg-primary-900/20' : ''}`} onClick={() => loadSession(s.id)}>
              <p className="truncate font-medium">{s.title}</p>
              <p className="text-xs text-gray-400">{s.document_count} docs</p>
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col card">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {loading && messages.length === 0 ? (
            <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
              <FiFile className="w-16 h-16 mb-4" />
              <p>Upload PDFs and ask questions about their content</p>
              {selectedDocs.length > 0 && <p className="text-sm text-primary-600 mt-2">{selectedDocs.length} document(s) selected</p>}
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100 dark:bg-gray-700'}`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  {msg.relevant_sections?.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600">
                      <p className="text-xs font-semibold mb-1">Relevant sections:</p>
                      {msg.relevant_sections.map((sec, i) => <p key={i} className="text-xs opacity-70">• {sec}</p>)}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleAsk} className="flex gap-2">
          <input value={question} onChange={(e) => setQuestion(e.target.value)} className="input-field flex-1" placeholder="Ask about your PDFs..." required />
          <button type="submit" disabled={loading} className="btn-primary px-4"><FiSend className="w-5 h-5" /></button>
        </form>
      </div>
    </div>
  )
}
