import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import { UploadTab } from './components/UploadTab'
import { DashboardTab } from './components/DashboardTab'
import { CandidateProfile } from './components/CandidateProfile'
import { DocumentSubmission } from './components/DocumentSubmission'
import './App.css'

function HRDashboard() {
  const [activeTab, setActiveTab] = useState('upload')
  const [selectedCandidateId, setSelectedCandidateId] = useState(null)

  const handleSelectCandidate = (candidateId) => {
    setSelectedCandidateId(candidateId)
  }

  const handleBackToDashboard = () => {
    setSelectedCandidateId(null)
  }

  // If a candidate is selected, show their profile
  if (selectedCandidateId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <h1 className="text-3xl font-bold text-center mb-2">TraqCheck</h1>
          <p className="text-slate-400 text-center mb-8">AI-Powered Candidate Processor</p>

          <CandidateProfile
            candidateId={selectedCandidateId}
            onBack={handleBackToDashboard}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-3xl font-bold text-center mb-2">TraqCheck</h1>
        <p className="text-slate-400 text-center mb-8">AI-Powered Candidate Processor</p>

        <div className="flex justify-center gap-2 mb-8">
          {['upload', 'dashboard'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-2 rounded-lg font-medium transition-all ${activeTab === tab
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
            >
              {tab === 'upload' ? 'Upload' : 'Dashboard'}
            </button>
          ))}
        </div>

        {activeTab === 'upload' ? (
          <UploadTab />
        ) : (
          <DashboardTab onSelectCandidate={handleSelectCandidate} />
        )}
      </div>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HRDashboard />} />
      <Route path="/submit-docs" element={<DocumentSubmission />} />
    </Routes>
  )
}

export default App
