import { NavLink } from 'react-router-dom'
import { useState } from 'react'
import { FiGrid, FiFileText, FiMap, FiHelpCircle, FiEdit3, FiVideo, FiFile, FiCompass, FiMessageCircle, FiMenu, FiX } from 'react-icons/fi'

const navItems = [
  { to: '/', icon: FiGrid, label: 'Dashboard' },
  { to: '/resumes', icon: FiFileText, label: 'Resumes' },
  { to: '/roadmaps', icon: FiMap, label: 'Roadmaps' },
  { to: '/doubts', icon: FiHelpCircle, label: 'Doubt Solver' },
  { to: '/blogs', icon: FiEdit3, label: 'Blogs' },
  { to: '/youtube', icon: FiVideo, label: 'YouTube' },
  { to: '/pdf-chat', icon: FiFile, label: 'PDF Chat' },
  { to: '/career', icon: FiCompass, label: 'Career' },
  { to: '/question-papers', icon: FiMessageCircle, label: 'Question Papers' },
]

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button onClick={() => setIsOpen(true)} className="fixed top-3 left-3 z-50 p-2 bg-white dark:bg-gray-800 rounded-lg shadow md:hidden"><FiMenu className="w-5 h-5" /></button>
      <aside className={`fixed md:static inset-y-0 left-0 z-40 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 transition-transform duration-200`}>
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center"><span className="text-white font-bold text-sm">SG</span></div>
            <span className="font-bold text-lg text-gray-800 dark:text-white">StudyGenius</span>
          </div>
          <button onClick={() => setIsOpen(false)} className="md:hidden p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"><FiX className="w-5 h-5" /></button>
        </div>
        <nav className="p-3 space-y-1">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === '/'} onClick={() => setIsOpen(false)}
              className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'}`}>
              <item.icon className="w-5 h-5" /> {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      {isOpen && <div onClick={() => setIsOpen(false)} className="fixed inset-0 bg-black/50 z-30 md:hidden" />}
    </>
  )
}
