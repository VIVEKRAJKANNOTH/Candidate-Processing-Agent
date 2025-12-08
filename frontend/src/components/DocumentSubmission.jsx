import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../services/api'

export function DocumentSubmission() {
    const [searchParams] = useSearchParams()
    const candidateId = searchParams.get('candidate_id')

    const [candidateName, setCandidateName] = useState('')
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const [panCard, setPanCard] = useState(null)
    const [aadhaarCard, setAadhaarCard] = useState(null)
    const [submitting, setSubmitting] = useState(false)
    const [submitted, setSubmitted] = useState(false)
    const [submitError, setSubmitError] = useState(null)

    useEffect(() => {
        if (!candidateId) {
            setError('Invalid link. No candidate ID found.')
            setLoading(false)
            return
        }

        const fetchCandidateInfo = async () => {
            try {
                const data = await api.getPublicCandidateInfo(candidateId)
                if (data.error) {
                    setError(data.error)
                } else {
                    setCandidateName(data.name)
                }
            } catch (err) {
                setError('Unable to load your information. Please try again later.')
            } finally {
                setLoading(false)
            }
        }

        fetchCandidateInfo()
    }, [candidateId])

    const handlePanCardChange = (e) => {
        const file = e.target.files[0]
        if (file && file.size > 5 * 1024 * 1024) {
            alert('File size must be less than 5MB')
            return
        }
        setPanCard(file)
    }

    const handleAadhaarChange = (e) => {
        const file = e.target.files[0]
        if (file && file.size > 5 * 1024 * 1024) {
            alert('File size must be less than 5MB')
            return
        }
        setAadhaarCard(file)
    }

    const handleSubmit = async (e) => {
        e.preventDefault()

        if (!panCard || !aadhaarCard) {
            setSubmitError('Please select both documents')
            return
        }

        setSubmitting(true)
        setSubmitError(null)

        try {
            const result = await api.submitDocuments(candidateId, {
                panCard,
                aadhaarCard
            })

            if (result.success) {
                setSubmitted(true)
            } else {
                setSubmitError(result.error || 'Failed to submit documents. Please try again.')
            }
        } catch (err) {
            setSubmitError('Network error. Please check your connection and try again.')
        } finally {
            setSubmitting(false)
        }
    }

    // Loading state
    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 flex items-center justify-center">
                <div className="animate-pulse flex flex-col items-center gap-4">
                    <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-slate-300 text-lg">Loading...</p>
                </div>
            </div>
        )
    }

    // Error state
    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-950 to-slate-900 flex items-center justify-center p-4">
                <div className="bg-slate-800/50 backdrop-blur-xl border border-red-500/30 rounded-2xl p-8 max-w-md text-center">
                    <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </div>
                    <h2 className="text-xl font-semibold text-white mb-2">Error</h2>
                    <p className="text-red-300">{error}</p>
                </div>
            </div>
        )
    }

    // Success state
    if (submitted) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-950 to-slate-900 flex items-center justify-center p-4">
                <div className="bg-slate-800/50 backdrop-blur-xl border border-emerald-500/30 rounded-2xl p-8 max-w-md text-center">
                    <div className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6 animate-bounce">
                        <svg className="w-10 h-10 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-3">Success!</h2>
                    <p className="text-emerald-200 mb-4">Your documents have been submitted successfully.</p>
                    <p className="text-slate-400 text-sm">
                        You will receive a confirmation email shortly. Our team will review your documents and notify you once verification is complete.
                    </p>
                </div>
            </div>
        )
    }

    // Main form
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 flex items-center justify-center p-4">
            <div className="w-full max-w-lg">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl mb-4 shadow-lg shadow-indigo-500/25">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-2">Document Submission</h1>
                    <p className="text-indigo-200">
                        Welcome, <span className="font-semibold text-white">{candidateName}</span>!
                    </p>
                </div>

                {/* Form Card */}
                <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* PAN Card Upload */}
                        <div>
                            <label className="block text-slate-300 font-medium mb-2">
                                PAN Card <span className="text-red-400">*</span>
                            </label>
                            <div className={`relative border-2 border-dashed rounded-xl p-4 transition-all ${panCard
                                    ? 'border-emerald-500/50 bg-emerald-500/5'
                                    : 'border-slate-600 hover:border-indigo-500/50 hover:bg-indigo-500/5'
                                }`}>
                                <input
                                    type="file"
                                    accept="image/*,.pdf"
                                    onChange={handlePanCardChange}
                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                />
                                <div className="flex items-center gap-4">
                                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${panCard ? 'bg-emerald-500/20' : 'bg-slate-700'
                                        }`}>
                                        {panCard ? (
                                            <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            </svg>
                                        ) : (
                                            <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                            </svg>
                                        )}
                                    </div>
                                    <div className="flex-1">
                                        {panCard ? (
                                            <>
                                                <p className="text-emerald-300 font-medium truncate">{panCard.name}</p>
                                                <p className="text-slate-500 text-sm">{(panCard.size / 1024).toFixed(1)} KB</p>
                                            </>
                                        ) : (
                                            <>
                                                <p className="text-slate-300 font-medium">Choose PAN Card</p>
                                                <p className="text-slate-500 text-sm">JPG, PNG, or PDF (max 5MB)</p>
                                            </>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Aadhaar Card Upload */}
                        <div>
                            <label className="block text-slate-300 font-medium mb-2">
                                Aadhaar Card <span className="text-red-400">*</span>
                            </label>
                            <div className={`relative border-2 border-dashed rounded-xl p-4 transition-all ${aadhaarCard
                                    ? 'border-emerald-500/50 bg-emerald-500/5'
                                    : 'border-slate-600 hover:border-indigo-500/50 hover:bg-indigo-500/5'
                                }`}>
                                <input
                                    type="file"
                                    accept="image/*,.pdf"
                                    onChange={handleAadhaarChange}
                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                />
                                <div className="flex items-center gap-4">
                                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${aadhaarCard ? 'bg-emerald-500/20' : 'bg-slate-700'
                                        }`}>
                                        {aadhaarCard ? (
                                            <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            </svg>
                                        ) : (
                                            <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                                            </svg>
                                        )}
                                    </div>
                                    <div className="flex-1">
                                        {aadhaarCard ? (
                                            <>
                                                <p className="text-emerald-300 font-medium truncate">{aadhaarCard.name}</p>
                                                <p className="text-slate-500 text-sm">{(aadhaarCard.size / 1024).toFixed(1)} KB</p>
                                            </>
                                        ) : (
                                            <>
                                                <p className="text-slate-300 font-medium">Choose Aadhaar Card</p>
                                                <p className="text-slate-500 text-sm">JPG, PNG, or PDF (max 5MB)</p>
                                            </>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Error Message */}
                        {submitError && (
                            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                                <p className="text-red-300 text-sm">{submitError}</p>
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={submitting || !panCard || !aadhaarCard}
                            className={`w-full py-4 rounded-xl font-semibold text-lg transition-all duration-300 ${submitting || !panCard || !aadhaarCard
                                    ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                                    : 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/40 hover:scale-[1.02] active:scale-[0.98]'
                                }`}
                        >
                            {submitting ? (
                                <span className="flex items-center justify-center gap-2">
                                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Uploading...
                                </span>
                            ) : (
                                'Submit Documents'
                            )}
                        </button>
                    </form>

                    {/* Footer Note */}
                    <p className="mt-6 text-center text-slate-500 text-sm">
                        Your documents are encrypted and stored securely.
                    </p>
                </div>

                {/* Powered by */}
                <p className="text-center text-slate-600 text-sm mt-6">
                    Powered by <span className="text-indigo-400 font-medium">TraqCheck</span>
                </p>
            </div>
        </div>
    )
}
