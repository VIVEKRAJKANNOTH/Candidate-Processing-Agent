import { useState, useEffect } from 'react'
import { api } from '../services/api'

export function CandidateProfile({ candidateId, onBack }) {
    const [candidate, setCandidate] = useState(null)
    const [loading, setLoading] = useState(true)
    const [requesting, setRequesting] = useState(false)
    const [requestResult, setRequestResult] = useState(null)

    useEffect(() => {
        loadCandidate()
    }, [candidateId])

    const loadCandidate = async () => {
        setLoading(true)
        try {
            const data = await api.getCandidate(candidateId)
            setCandidate(data)
        } catch (error) {
            console.error('Failed to load candidate:', error)
        }
        setLoading(false)
    }

    const handleRequestDocuments = async () => {
        setRequesting(true)
        setRequestResult(null)
        try {
            const result = await api.requestDocuments(candidateId)
            setRequestResult(result)
            await loadCandidate()
        } catch (error) {
            setRequestResult({ success: false, error: error.message })
        }
        setRequesting(false)
    }

    const getDocStatusColor = (status) => {
        switch (status?.toUpperCase()) {
            case 'REQUESTED': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
            case 'SUBMITTED': return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
            case 'VERIFIED': return 'bg-green-500/20 text-green-400 border-green-500/30'
            default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30'
        }
    }

    const getConfidenceColor = (score) => {
        if (score >= 0.8) return 'bg-green-500'
        if (score >= 0.5) return 'bg-yellow-500'
        return 'bg-red-500'
    }

    const getConfidenceText = (score) => {
        if (score >= 0.8) return 'text-green-400'
        if (score >= 0.5) return 'text-yellow-400'
        return 'text-red-400'
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
            </div>
        )
    }

    if (!candidate) {
        return (
            <div className="text-center py-12">
                <p className="text-slate-400">Candidate not found</p>
                <button onClick={onBack} className="mt-4 text-indigo-400 hover:text-indigo-300">
                    ← Back to Dashboard
                </button>
            </div>
        )
    }

    // Safely parse skills
    let skills = []
    try {
        if (candidate.skills) {
            skills = typeof candidate.skills === 'string'
                ? JSON.parse(candidate.skills)
                : candidate.skills
        }
    } catch (e) {
        skills = []
    }

    // Safely parse confidence scores
    let scores = {}
    try {
        if (candidate.confidence_scores) {
            scores = typeof candidate.confidence_scores === 'string'
                ? JSON.parse(candidate.confidence_scores)
                : candidate.confidence_scores
        }
    } catch (e) {
        scores = {}
    }

    // Fields with confidence scores
    const fields = [
        { key: 'name', label: 'Name' },
        { key: 'email', label: 'Email' },
        { key: 'phone', label: 'Phone' },
        { key: 'company', label: 'Company' },
        { key: 'designation', label: 'Designation' },
        { key: 'experience_years', label: 'Experience', format: v => v ? `${v} years` : null },
        { key: 'skills', label: 'Skills', format: () => skills.length > 0 ? skills.join(', ') : null }
    ]

    const isRequested = candidate.document_status === 'REQUESTED'
    const isSubmitted = candidate.document_status === 'SUBMITTED'
    const isVerified = candidate.document_status === 'VERIFIED'

    return (
        <div className="space-y-6">
            {/* Header with Back Button */}
            <div className="flex items-center gap-4">
                <button
                    onClick={onBack}
                    className="text-slate-400 hover:text-white transition-colors"
                >
                    ← Back
                </button>
                <h2 className="text-2xl font-bold">{candidate.name}</h2>
                <span className={`px-2 py-1 rounded text-xs font-medium ${candidate.status === 'PARSED' ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'}`}>
                    {candidate.status}
                </span>
            </div>

            {/* Document Status & Action Card - MOVED TO TOP */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <h3 className="text-lg font-semibold text-slate-300">Document Collection</h3>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getDocStatusColor(candidate.document_status)}`}>
                            {candidate.document_status || 'NOT_REQUESTED'}
                        </span>
                    </div>

                    {/* Action Button */}
                    {isVerified ? (
                        <span className="text-green-400 font-medium">✅ Verified</span>
                    ) : isSubmitted ? (
                        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-colors">
                            🔍 Verify Documents
                        </button>
                    ) : (
                        <button
                            onClick={handleRequestDocuments}
                            disabled={requesting}
                            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2"
                        >
                            {requesting ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                    Sending...
                                </>
                            ) : (
                                <>📧 {isRequested ? 'Resend Request' : 'Request Documents'}</>
                            )}
                        </button>
                    )}
                </div>

                {/* Status Info */}
                {isRequested && (
                    <div className="mt-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
                        <p className="text-yellow-400 text-sm">
                            ✉️ Request sent on {candidate.documents_requested_at ? new Date(candidate.documents_requested_at).toLocaleDateString() : 'recently'} - Waiting for candidate
                        </p>
                    </div>
                )}
                {isSubmitted && (
                    <div className="mt-4 bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                        <p className="text-blue-400 text-sm">📄 Documents submitted - Ready for verification</p>
                    </div>
                )}

                {/* Request Result */}
                {requestResult && (
                    <div className={`mt-4 p-3 rounded-lg ${requestResult.success ? 'bg-green-500/10 border border-green-500/30' : 'bg-red-500/10 border border-red-500/30'}`}>
                        {requestResult.success ? (
                            <p className="text-green-400 text-sm">✅ Request sent to {requestResult.email?.candidate_email || candidate.email}</p>
                        ) : (
                            <p className="text-red-400 text-sm">❌ Failed: {requestResult.error}</p>
                        )}
                    </div>
                )}
            </div>

            {/* Extracted Data with Confidence Scores */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
                <h3 className="text-lg font-semibold text-slate-300 mb-4">Extracted Information</h3>
                <table className="w-full">
                    <thead>
                        <tr className="text-slate-400 text-sm">
                            <th className="text-left pb-2 w-28">Field</th>
                            <th className="text-left pb-2">Value</th>
                            <th className="text-right pb-2 w-28">Confidence</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                        {fields.map(({ key, label, format }) => {
                            const value = format ? format(candidate[key]) : candidate[key]
                            const score = scores[key]
                            return (
                                <tr key={key}>
                                    <td className="py-3 text-slate-400">{label}</td>
                                    <td className="py-3 text-white">{value || '-'}</td>
                                    <td className="py-3 text-right">
                                        {score !== undefined ? (
                                            <div className="flex items-center justify-end gap-2">
                                                <div className="w-16 h-2 bg-slate-600 rounded-full overflow-hidden">
                                                    <div className={`h-full ${getConfidenceColor(score)}`} style={{ width: `${score * 100}%` }}></div>
                                                </div>
                                                <span className={`text-xs font-medium ${getConfidenceText(score)}`}>
                                                    {Math.round(score * 100)}%
                                                </span>
                                            </div>
                                        ) : (
                                            <span className="text-slate-500 text-xs">-</span>
                                        )}
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>

                {/* Skills as Tags */}
                {skills.length > 0 && (
                    <div className="mt-6 pt-6 border-t border-slate-700">
                        <h4 className="text-sm font-medium text-slate-400 mb-3">Skills</h4>
                        <div className="flex flex-wrap gap-2">
                            {skills.map((skill, index) => (
                                <span
                                    key={index}
                                    className="px-3 py-1 bg-indigo-500/20 text-indigo-300 rounded-full text-sm border border-indigo-500/30"
                                >
                                    {skill}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* Metadata */}
                <div className="mt-6 pt-6 border-t border-slate-700 flex justify-between items-center text-sm">
                    <span className="text-slate-500">ID: {candidate.id}</span>
                    <span className="text-slate-500">Created: {candidate.created_at || '-'}</span>
                </div>
            </div>
        </div>
    )
}
