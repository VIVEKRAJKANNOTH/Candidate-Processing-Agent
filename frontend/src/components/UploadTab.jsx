import { useState, useRef } from 'react'
import { api } from '../services/api'

const ALLOWED_TYPES = ['.pdf', '.docx', '.txt']

export function UploadTab() {
    const [file, setFile] = useState(null)
    const [isDragging, setIsDragging] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)
    const fileInputRef = useRef(null)

    const handleFile = (f) => {
        if (!f) return
        const ext = '.' + f.name.split('.').pop().toLowerCase()
        if (!ALLOWED_TYPES.includes(ext)) {
            setError('Invalid file type. Please upload PDF, DOCX, or TXT.')
            return
        }
        setFile(f)
        setError(null)
        setResult(null)
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setIsDragging(false)
        handleFile(e.dataTransfer.files[0])
    }

    const formatSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B'
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    }

    const processResume = async () => {
        if (!file) return
        setIsLoading(true)
        setError(null)

        try {
            const data = await api.uploadResume(file)
            if (data.success) {
                setResult(data.data)
            } else {
                setError(data.error || 'Failed to parse resume')
            }
        } catch (err) {
            setError('Connection error: ' + err.message)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="max-w-2xl mx-auto">
            <div
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${isDragging ? 'border-indigo-500 bg-indigo-500/10' : 'border-slate-600 hover:border-indigo-500'
                    }`}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept=".pdf,.docx,.txt"
                    onChange={(e) => handleFile(e.target.files[0])}
                />
                {!file ? (
                    <>
                        <svg className="w-16 h-16 mx-auto mb-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <p className="text-slate-300 text-lg mb-2">Drag & drop your resume here</p>
                        <p className="text-slate-500 text-sm">or click to browse</p>
                        <p className="text-slate-600 text-xs mt-4">Supports: PDF, DOCX, TXT</p>
                    </>
                ) : (
                    <>
                        <svg className="w-12 h-12 mx-auto mb-3 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p className="text-white font-medium">{file.name}</p>
                        <p className="text-slate-400 text-sm">{formatSize(file.size)}</p>
                    </>
                )}
            </div>

            <button
                onClick={processResume}
                disabled={!file || isLoading}
                className={`w-full mt-6 py-4 rounded-xl font-semibold text-lg transition-all duration-300 ${file && !isLoading
                        ? 'bg-indigo-600 hover:bg-indigo-700 text-white cursor-pointer'
                        : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    }`}
            >
                {isLoading ? 'Processing...' : 'Process Resume'}
            </button>

            {isLoading && (
                <div className="mt-8 text-center">
                    <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                    <p className="text-slate-300 mt-4">Parsing resume with AI...</p>
                </div>
            )}

            {result && (
                <div className="mt-8 bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
                    <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                        <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                        </svg>
                        Extracted Data
                    </h2>
                    <table className="w-full">
                        <tbody className="divide-y divide-slate-700">
                            {[
                                ['Name', result.name],
                                ['Email', result.email],
                                ['Company', result.company],
                                ['Status', result.validation_status]
                            ].map(([label, value]) => (
                                <tr key={label}>
                                    <td className="py-3 text-slate-400 w-32">{label}</td>
                                    <td className="py-3 text-white font-medium">{value || '-'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    <p className={`mt-4 text-sm ${result.is_update ? 'text-yellow-400' : 'text-green-400'}`}>
                        {result.is_update ? '⟳ Candidate updated' : '✓ New candidate saved'}
                    </p>
                </div>
            )}

            {error && (
                <div className="mt-8 bg-red-900/30 border border-red-700 rounded-xl p-4 text-red-300">
                    {error}
                </div>
            )}
        </div>
    )
}
