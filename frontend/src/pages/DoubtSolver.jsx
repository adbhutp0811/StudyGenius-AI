import { useState, useEffect, useRef } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'
import { SUBJECTS } from '../utils/constants'
import { FiSend, FiBookmark, FiBookOpen, FiCode, FiImage, FiTrash2, FiPlus } from 'react-icons/fi'

export default function DoubtSolver() {
  const [sessions, setSessions] = useState([])
  const [activeSession, setActiveSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [subject, setSubject] = useState('programming')
  const [codeSnippet, setCodeSnippet] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingSessions, setLoadingSessions] = useState(true)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    api.get('/api/doubts/').then(({ data }) => setSessions(data.results || data))
      .catch(() => {})
      .finally(() => setLoadingSessions(false))
  }, [])

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const loadSession = async (sessionId) => {
    setLoading(true)
    try {
      const { data } = await api.get(`/api/doubts/${sessionId}/`)
      setActiveSession(data)
      setMessages(data.messages || [])
    } catch { toast.error('Failed to load session') } finally { setLoading(false) }
  }

  const handleAsk = async (e) => {
    e.preventDefault()
    if (!question.trim()) return
    setLoading(true)
    const userMsg = question
    setQuestion('')
    try {
      const { data } = await api.post('/api/doubts/ask/', {
        session_id: activeSession?.id || '',
        subject,
        question: userMsg,
        code_snippet: codeSnippet,
      })
      setActiveSession(data.session)
      setMessages(data.session.messages || [])
      setSessions(prev => {
        const exists = prev.find(s => s.id === data.session.id)
        if (exists) return prev
        return [data.session, ...prev]
      })
    } catch { toast.error('Failed to get answer') } finally { setLoading(false) }
  }

  const handleNewChat = () => {
    setActiveSession(null)
    setMessages([])
    setQuestion('')
    setCodeSnippet('')
  }

  const handleBookmark = async (messageId) => {
    if (!activeSession) return
    try {
      await api.post(`/api/doubts/${activeSession.id}/bookmark/`, { message_id: messageId })
      toast.success('Bookmark toggled')
    } catch { toast.error('Failed to bookmark') }
  }

  const handleDeleteSession = async (sessionId) => {
    if (!confirm('Delete this chat session?')) return
    try {
      await api.delete(`/api/doubts/${sessionId}/`)
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      if (activeSession?.id === sessionId) { setActiveSession(null); setMessages([]) }
      toast.success('Session deleted')
    } catch { toast.error('Failed to delete') }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4 animate-fade-in">
      <div className="w-72 shrink-0 space-y-2 overflow-y-auto">
        <button onClick={handleNewChat} className="w-full btn-primary flex items-center gap-2 justify-center mb-4"><FiPlus /> New Chat</button>
        {loadingSessions ? (
          <div className="animate-pulse space-y-2">{[...Array(3)].map((_, i) => <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded-lg" />)}</div>
        ) : (
          sessions.map((s) => (
            <div key={s.id} className={`card p-3 cursor-pointer hover:shadow transition-shadow ${activeSession?.id === s.id ? 'ring-2 ring-primary-500' : ''}`} onClick={() => loadSession(s.id)}>
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium truncate">{s.title}</p>
                <button onClick={(e) => { e.stopPropagation(); handleDeleteSession(s.id) }} className="text-gray-400 hover:text-red-500"><FiTrash2 className="w-3.5 h-3.5" /></button>
              </div>
              <p className="text-xs text-gray-400 mt-1">{s.subject} • {s.message_count || 0} messages</p>
            </div>
          ))
        )}
      </div>

      <div className="flex-1 flex flex-col card">
        <div className="flex items-center gap-3 mb-4 border-b border-gray-200 dark:border-gray-700 pb-3">
          <select value={subject} onChange={(e) => setSubject(e.target.value)} className="input-field w-auto text-sm">
            {SUBJECTS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
          <span className="text-xs text-gray-400">{activeSession ? `Chat: ${activeSession.title}` : 'New Chat'}</span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {loading && messages.length === 0 ? (
            <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
              <FiBookOpen className="w-16 h-16 mb-4" />
              <p>Ask any question and get AI-powered answers</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100 dark:bg-gray-700'}`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  {msg.code_snippet && (
                    <pre className="mt-2 p-3 bg-gray-800 text-green-400 rounded-lg text-xs overflow-x-auto"><code>{msg.code_snippet}</code></pre>
                  )}
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs opacity-70">{new Date(msg.created_at).toLocaleTimeString()}</span>
                    {msg.role === 'assistant' && (
                      <button onClick={() => handleBookmark(msg.id)} className={`text-xs ${msg.is_bookmarked ? 'text-yellow-400' : 'opacity-50 hover:opacity-100'}`}>
                        <FiBookmark className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleAsk} className="space-y-2">
          <div className="flex gap-2">
            <input value={codeSnippet} onChange={(e) => setCodeSnippet(e.target.value)} className="input-field w-1/4 text-xs" placeholder="Code (optional)" />
            <input value={question} onChange={(e) => setQuestion(e.target.value)} className="input-field flex-1" placeholder="Type your question..." required />
            <button type="submit" disabled={loading} className="btn-primary px-4"><FiSend className="w-5 h-5" /></button>
          </div>
        </form>
      </div>
    </div>
  )
}
