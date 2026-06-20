import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { FiFileText, FiMap, FiHelpCircle, FiEdit3, FiVideo, FiFile, FiCompass, FiMessageCircle, FiArrowRight } from 'react-icons/fi'

const modules = [
  { to: '/resumes', icon: FiFileText, label: 'Resumes', color: 'bg-blue-500', desc: 'Build AI-powered resumes' },
  { to: '/roadmaps', icon: FiMap, label: 'Roadmaps', color: 'bg-green-500', desc: 'Career learning paths' },
  { to: '/doubts', icon: FiHelpCircle, label: 'Doubt Solver', color: 'bg-purple-500', desc: 'AI tutor assistance' },
  { to: '/blogs', icon: FiEdit3, label: 'Blog Writer', color: 'bg-orange-500', desc: 'Generate AI blogs' },
  { to: '/youtube', icon: FiVideo, label: 'YouTube', color: 'bg-red-500', desc: 'Summarize videos' },
  { to: '/pdf-chat', icon: FiFile, label: 'PDF Chat', color: 'bg-teal-500', desc: 'Chat with documents' },
  { to: '/career', icon: FiCompass, label: 'Career', color: 'bg-indigo-500', desc: 'Career guidance' },
  { to: '/question-papers', icon: FiMessageCircle, label: 'Question Papers', color: 'bg-pink-500', desc: 'Generate assessments' },
]

export default function Dashboard() {
  const [stats, setStats] = useState({ resumes: 0, roadmaps: 0, doubts: 0, blogs: 0 })

  useEffect(() => {
    Promise.all([
      api.get('/api/resumes/').catch(() => ({ data: [] })),
      api.get('/api/roadmaps/').catch(() => ({ data: [] })),
      api.get('/api/doubts/').catch(() => ({ data: [] })),
      api.get('/api/blogs/').catch(() => ({ data: [] })),
    ]).then(([resumes, roadmaps, doubts, blogs]) => {
      setStats({
        resumes: resumes.data?.count || resumes.data?.length || 0,
        roadmaps: roadmaps.data?.count || roadmaps.data?.length || 0,
        doubts: doubts.data?.count || doubts.data?.length || 0,
        blogs: blogs.data?.count || blogs.data?.length || 0,
      })
    })
  }, [])

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400">Welcome to StudyGenius AI – your learning companion</p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Resumes', value: stats.resumes, icon: FiFileText, color: 'text-blue-600 bg-blue-100 dark:bg-blue-900/20' },
          { label: 'Roadmaps', value: stats.roadmaps, icon: FiMap, color: 'text-green-600 bg-green-100 dark:bg-green-900/20' },
          { label: 'Doubts Solved', value: stats.doubts, icon: FiHelpCircle, color: 'text-purple-600 bg-purple-100 dark:bg-purple-900/20' },
          { label: 'Blogs', value: stats.blogs, icon: FiEdit3, color: 'text-orange-600 bg-orange-100 dark:bg-orange-900/20' },
        ].map((item, i) => (
          <div key={i} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">{item.label}</p>
                <p className="text-2xl font-bold mt-1">{item.value}</p>
              </div>
              <div className={`p-3 rounded-xl ${item.color}`}><item.icon className="w-6 h-6" /></div>
            </div>
          </div>
        ))}
      </div>
      <h2 className="text-xl font-semibold mt-8">Quick Access</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {modules.map((mod) => (
          <Link key={mod.to} to={mod.to} className="card hover:shadow-md transition-shadow group">
            <div className="flex items-start gap-3">
              <div className={`p-3 rounded-xl ${mod.color} text-white`}><mod.icon className="w-5 h-5" /></div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 dark:text-white">{mod.label}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{mod.desc}</p>
              </div>
              <FiArrowRight className="w-5 h-5 text-gray-300 group-hover:text-primary-600 transition-colors" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
