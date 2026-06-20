import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import Resumes from './pages/Resumes'
import ResumeBuilder from './pages/ResumeBuilder'
import Roadmaps from './pages/Roadmaps'
import RoadmapDetail from './pages/RoadmapDetail'
import DoubtSolver from './pages/DoubtSolver'
import Blogs from './pages/Blogs'
import BlogEditor from './pages/BlogEditor'
import YouTube from './pages/YouTube'
import PDFChat from './pages/PDFChat'
import Career from './pages/Career'
import Assessment from './pages/Assessment'
import QuestionPapers from './pages/QuestionPapers'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>
  return user ? children : <Navigate to="/login" />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="profile" element={<Profile />} />
        <Route path="resumes" element={<Resumes />} />
        <Route path="resumes/new" element={<ResumeBuilder />} />
        <Route path="resumes/:id" element={<ResumeBuilder />} />
        <Route path="roadmaps" element={<Roadmaps />} />
        <Route path="roadmaps/:id" element={<RoadmapDetail />} />
        <Route path="doubts" element={<DoubtSolver />} />
        <Route path="blogs" element={<Blogs />} />
        <Route path="blogs/new" element={<BlogEditor />} />
        <Route path="blogs/:id" element={<BlogEditor />} />
        <Route path="youtube" element={<YouTube />} />
        <Route path="pdf-chat" element={<PDFChat />} />
        <Route path="career" element={<Career />} />
        <Route path="career/assessment/:id" element={<Assessment />} />
        <Route path="question-papers" element={<QuestionPapers />} />
      </Route>
    </Routes>
  )
}
