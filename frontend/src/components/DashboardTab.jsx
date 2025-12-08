import { useState, useEffect } from 'react'
import { api } from '../services/api'
import { CandidateModal } from './CandidateModal'

export function DashboardTab() {
    const [candidates, setCandidates] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [selectedCandidate, setSelectedCandidate] = useState(null)
    const [modalLoading, setModalLoading] = useState(false)

    useEffect(() => {
        fetchCandidates()
    }, [])

    const fetchCandidates = async () => {
        try {
            const data = await api.getCandidates()
            setCandidates(data)
        } catch (err) {
            setError('Failed to load candidates')
        } finally {
            setLoading(false)
        }
    }

    const openCandidateModal = async (id) => {
        setModalLoading(true)
        try {
            const data = await api.getCandidate(id)
            setSelectedCandidate(data)
        } catch (err) {
            setError('Failed to load candidate details')
        } finally {
            setModalLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="text-center py-12">
                <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                <p className="text-slate-400 mt-4">Loading candidates...</p>
            </div>
        )
    }

    if (error) {
        return <div className="bg-red-900/30 border border-red-700 rounded-xl p-4 text-red-300">{error}</div>
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">All Candidates</h2>
                <span className="text-slate-400 text-sm">{candidates.length} total</span>
            </div>

            {candidates.length === 0 ? (
                <div className="text-center py-12 text-slate-400">
                    No candidates yet. Upload a resume to get started.
                </div>
            ) : (
                <div className="bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-slate-700/50">
                            <tr>
                                <th className="text-left py-3 px-4 text-slate-300 font-medium">ID</th>
                                <th className="text-left py-3 px-4 text-slate-300 font-medium">Name</th>
                                <th className="text-left py-3 px-4 text-slate-300 font-medium">Email</th>
                                <th className="text-left py-3 px-4 text-slate-300 font-medium">Company</th>
                                <th className="text-left py-3 px-4 text-slate-300 font-medium">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700">
                            {candidates.map(c => (
                                <tr
                                    key={c.id}
                                    onClick={() => openCandidateModal(c.id)}
                                    className="hover:bg-slate-700/30 transition-colors cursor-pointer"
                                >
                                    <td className="py-3 px-4 text-slate-500 font-mono text-sm">{c.id.slice(0, 8)}</td>
                                    <td className="py-3 px-4 text-white">{c.name}</td>
                                    <td className="py-3 px-4 text-slate-300">{c.email}</td>
                                    <td className="py-3 px-4 text-slate-300">{c.company}</td>
                                    <td className="py-3 px-4">
                                        <span className={`px-2 py-1 rounded text-xs font-medium ${c.status === 'PARSED' ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'
                                            }`}>
                                            {c.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {modalLoading && (
                <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
                    <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                </div>
            )}

            <CandidateModal
                candidate={selectedCandidate}
                onClose={() => setSelectedCandidate(null)}
            />
        </div>
    )
}
