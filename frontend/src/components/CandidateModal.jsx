export function CandidateModal({ candidate, onClose }) {
    if (!candidate) return null

    const fields = [
        { key: 'name', label: 'Name' },
        { key: 'email', label: 'Email' },
        { key: 'phone', label: 'Phone' },
        { key: 'company', label: 'Company' },
        { key: 'designation', label: 'Designation' },
        { key: 'experience_years', label: 'Experience', format: v => `${v} years` },
        { key: 'skills', label: 'Skills', format: v => (v || []).join(', ') }
    ]

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

    const scores = candidate.confidence_scores || {}

    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={onClose}>
            <div className="bg-slate-800 rounded-2xl max-w-lg w-full max-h-[90vh] overflow-auto border border-slate-700" onClick={e => e.stopPropagation()}>
                <div className="flex justify-between items-center p-5 border-b border-slate-700">
                    <h2 className="text-xl font-semibold">Candidate Details</h2>
                    <button onClick={onClose} className="text-slate-400 hover:text-white text-2xl">&times;</button>
                </div>

                <div className="p-5">
                    <table className="w-full">
                        <thead>
                            <tr className="text-slate-400 text-sm">
                                <th className="text-left pb-2 w-28">Field</th>
                                <th className="text-left pb-2">Value</th>
                                <th className="text-right pb-2 w-24">Confidence</th>
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

                    <div className="mt-4 pt-4 border-t border-slate-700 flex justify-between items-center text-sm">
                        <span className={`px-2 py-1 rounded ${candidate.status === 'PARSED' ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'
                            }`}>
                            {candidate.status}
                        </span>
                        <span className="text-slate-500">{candidate.created_at}</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
