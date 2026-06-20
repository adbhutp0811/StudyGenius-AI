import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { FiCheckCircle, FiClock, FiBarChart2 } from 'react-icons/fi'

export default function Assessment() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [assessment, setAssessment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [answers, setAnswers] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [currentQ, setCurrentQ] = useState(0)

  useEffect(() => {
    api.get(`/api/career/assessments/${id}/`).then(({ data }) => {
      setAssessment(data)
      setAnswers(data.answers || {})
    }).catch(() => toast.error('Assessment not found'))
      .finally(() => setLoading(false))
  }, [id])

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }))
    api.post(`/api/career/assessments/${id}/submit_answer/`, { question_id: questionId, answer })
      .catch(() => {})
  }

  const handleComplete = async () => {
    setSubmitting(true)
    try {
      const { data } = await api.post(`/api/career/assessments/${id}/complete/`)
      setAssessment(data.assessment)
      toast.success(`Assessment complete! Score: ${data.assessment.overall_score}%`)
      navigate('/career')
    } catch { toast.error('Failed to complete assessment') } finally { setSubmitting(false) }
  }

  if (loading) return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>
  if (!assessment) return <div className="text-center p-8">Assessment not found</div>
  if (assessment.is_completed) {
    return (
      <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
        <div className="card text-center py-12">
          <FiCheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold">{assessment.title}</h1>
          <div className="text-5xl font-bold text-primary-600 my-4">{assessment.overall_score}%</div>
          <p className="text-gray-500">Overall Score</p>
          {assessment.recommendations?.length > 0 && (
            <div className="mt-6 text-left">
              <h3 className="font-semibold mb-2">Recommendations</h3>
              <ul className="list-disc list-inside space-y-1">
                {assessment.recommendations.map((rec, i) => <li key={i} className="text-sm">{rec}</li>)}
              </ul>
            </div>
          )}
        </div>
      </div>
    )
  }

  const questions = assessment.questions || []
  const progress = ((Object.keys(answers).length) / Math.max(questions.length, 1)) * 100

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{assessment.title}</h1>
          <p className="text-gray-500 text-sm">{Object.keys(answers).length} of {questions.length} answered</p>
        </div>
        <button onClick={handleComplete} disabled={submitting} className="btn-primary">
          {submitting ? 'Submitting...' : 'Complete Assessment'}
        </button>
      </div>

      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div className="bg-primary-600 rounded-full h-2 transition-all" style={{ width: `${progress}%` }} />
      </div>

      {questions.map((q, qIndex) => (
        <div key={q.id} className={`card ${qIndex === currentQ ? 'ring-2 ring-primary-500' : ''}`} onClick={() => setCurrentQ(qIndex)}>
          <div className="flex items-start gap-3">
            <span className="text-sm font-bold text-primary-600 mt-0.5">Q{qIndex + 1}.</span>
            <div className="flex-1">
              <p className="font-medium mb-3">{q.question}</p>
              <div className="space-y-2">
                {(q.options || []).map((opt, oIndex) => (
                  <label key={oIndex} className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${answers[q.id] === opt ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'}`}>
                    <input type="radio" name={q.id} value={opt} checked={answers[q.id] === opt} onChange={() => handleAnswer(q.id, opt)} className="text-primary-600" />
                    <span className="text-sm">{opt}</span>
                  </label>
                ))}
              </div>
              <span className={`badge mt-2 ${q.difficulty === 'easy' ? 'badge-success' : q.difficulty === 'hard' ? 'badge-danger' : 'badge-warning'}`}>{q.difficulty}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
