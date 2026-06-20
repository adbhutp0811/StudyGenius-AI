import { useState, useEffect } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'
import { FiVideo, FiLink, FiTrash2, FiFileText, FiList } from 'react-icons/fi'

export default function YouTube() {
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(true)
  const [url, setUrl] = useState('')
  const [summarizing, setSummarizing] = useState(false)
  const [selectedVideo, setSelectedVideo] = useState(null)

  useEffect(() => {
    api.get('/api/youtube/').then(({ data }) => setVideos(data.results || data))
      .catch(() => {}).finally(() => setLoading(false))
  }, [])

  const handleSummarize = async (e) => {
    e.preventDefault()
    if (!url.trim()) return
    setSummarizing(true)
    try {
      const { data } = await api.post('/api/youtube/summarize/', { url })
      setVideos(prev => [data, ...prev])
      setSelectedVideo(data)
      setUrl('')
      toast.success('Video summarized!')
    } catch { toast.error('Failed to summarize') } finally { setSummarizing(false) }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this summary?')) return
    try {
      await api.delete(`/api/youtube/${id}/`)
      setVideos(prev => prev.filter(v => v.id !== id))
      if (selectedVideo?.id === id) setSelectedVideo(null)
      toast.success('Deleted')
    } catch { toast.error('Failed to delete') }
  }

  if (loading) return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>

  return (
    <div className="flex gap-6 h-[calc(100vh-8rem)] animate-fade-in">
      <div className="w-80 shrink-0 space-y-4 overflow-y-auto">
        <form onSubmit={handleSummarize} className="card">
          <h2 className="font-semibold mb-2">Summarize Video</h2>
          <div className="flex gap-2">
            <input value={url} onChange={(e) => setUrl(e.target.value)} className="input-field flex-1" placeholder="YouTube URL..." required />
            <button type="submit" disabled={summarizing} className="btn-primary">{summarizing ? '...' : 'Go'}</button>
          </div>
        </form>
        {videos.map((v) => (
          <div key={v.id} className={`card p-3 cursor-pointer hover:shadow transition-shadow ${selectedVideo?.id === v.id ? 'ring-2 ring-primary-500' : ''}`} onClick={() => setSelectedVideo(v)}>
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{v.title}</p>
                <p className="text-xs text-gray-400 truncate">{v.channel_name}</p>
                <p className="text-xs text-gray-400 mt-1">{new Date(v.created_at).toLocaleDateString()}</p>
              </div>
              <button onClick={(e) => { e.stopPropagation(); handleDelete(v.id) }} className="text-gray-400 hover:text-red-500 ml-2"><FiTrash2 className="w-3.5 h-3.5" /></button>
            </div>
          </div>
        ))}
      </div>

      <div className="flex-1 card overflow-y-auto">
        {selectedVideo ? (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold">{selectedVideo.title}</h2>
              <p className="text-sm text-gray-500">{selectedVideo.channel_name}</p>
            </div>
            {selectedVideo.thumbnail_url && (
              <img src={selectedVideo.thumbnail_url} alt={selectedVideo.title} className="w-full rounded-xl max-h-80 object-cover" />
            )}
            <div>
              <h3 className="flex items-center gap-2 text-lg font-semibold mb-2"><FiFileText /> Summary</h3>
              <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{selectedVideo.summary}</p>
            </div>
            {selectedVideo.key_points?.length > 0 && (
              <div>
                <h3 className="flex items-center gap-2 text-lg font-semibold mb-2"><FiList /> Key Points</h3>
                <ul className="list-disc list-inside space-y-1">
                  {selectedVideo.key_points.map((point, i) => <li key={i} className="text-sm text-gray-600 dark:text-gray-400">{point}</li>)}
                </ul>
              </div>
            )}
            {selectedVideo.notes && (
              <div>
                <h3 className="flex items-center gap-2 text-lg font-semibold mb-2"><FiFileText /> Notes</h3>
                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap text-sm">{selectedVideo.notes}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
            <FiVideo className="w-16 h-16 mb-4" />
            <p>Paste a YouTube URL to get started</p>
          </div>
        )}
      </div>
    </div>
  )
}
