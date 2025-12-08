// Use environment variable for API URL, or empty string for relative paths in production
export const API_BASE = import.meta.env.VITE_API_URL || ''

export const api = {
    async uploadResume(file) {
        const formData = new FormData()
        formData.append('resume', file)
        const response = await fetch(`${API_BASE}/candidates/upload`, {
            method: 'POST',
            body: formData
        })
        return response.json()
    },

    async getCandidates() {
        const response = await fetch(`${API_BASE}/candidates`)
        return response.json()
    },

    async getCandidate(id) {
        const response = await fetch(`${API_BASE}/candidates/${id}`)
        return response.json()
    },

    async requestDocuments(candidateId) {
        const response = await fetch(`${API_BASE}/candidates/${candidateId}/request-documents`, {
            method: 'POST'
        })
        return response.json()
    },

    async getPublicCandidateInfo(id) {
        const response = await fetch(`${API_BASE}/api/candidates/${id}/public`)
        return response.json()
    },

    async submitDocuments(candidateId, files) {
        const formData = new FormData()
        formData.append('pan_card', files.panCard)
        formData.append('aadhaar_card', files.aadhaarCard)
        const response = await fetch(`${API_BASE}/candidates/${candidateId}/submit-documents`, {
            method: 'POST',
            body: formData
        })
        return response.json()
    }
}

