const API_BASE = 'http://localhost:5000'

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
    }
}
