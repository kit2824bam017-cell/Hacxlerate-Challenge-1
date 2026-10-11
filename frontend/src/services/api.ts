// API Client for AI-Powered Personal Health Copilot
const BASE_URL = '/api/v1'

export interface PatientProfile {
  id: string
  user_id: string
  full_name: string
  date_of_birth: string | null
  gender: string | null
  blood_group: string | null
  contact_phone: string | null
  email: string | null
  emergency_contact: string | null
  preferred_language: string
  created_at: string
  updated_at: string
}

export interface MedicalDocument {
  id: string
  patient_id: string
  storage_path: string
  original_filename: string
  mime_type: string
  file_size_bytes: number | null
  document_type: 'lab_report' | 'prescription' | 'discharge_summary' | 'other'
  document_date: string | null
  processing_status: 'uploaded' | 'queued' | 'processing' | 'awaiting_review' | 'completed' | 'failed'
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface CandidateObservation {
  id?: string
  test_name: string
  value_numeric?: number | null
  value_text?: string | null
  unit?: string | null
  reference_low?: number | null
  reference_high?: number | null
  source_abnormal_flag?: string | null
  confidence: string
  validation_status: string
  source_text?: string | null
}

export interface CandidateMedication {
  id?: string
  medication_name: string
  generic_name?: string | null
  strength?: string | null
  dose_instructions?: string | null
  route?: string | null
  frequency?: string | null
  duration?: string | null
  prescription_date?: string | null
  confidence: string
  validation_status: string
  source_text?: string | null
}

export interface ExtractionResult {
  id: string
  document_id: string
  raw_ocr_text?: string | null
  structured_candidate_data: {
    document_type: string
    document_date?: string | null
    healthcare_provider?: string | null
    practitioner_name?: string | null
    observations: CandidateObservation[]
    medications: CandidateMedication[]
    unreadable_segments: string[]
  }
  extraction_provider: string
  provider_model?: string | null
  validation_status: string
  review_status: string
  created_at: string
  updated_at: string
}

export interface AbnormalExplanation {
  test_name: string
  value: string
  reference: string
  status: string
  plain_explanation: string
}

export interface DocumentSummary {
  id: string
  document_id: string
  language: string
  overview: string
  key_findings: string[]
  abnormal_explanations: AbnormalExplanation[]
  questions_for_doctor: string[]
  limitations?: string | null
  safety_disclaimer: string
  created_at: string
}

export interface ObservationRecord {
  id: string
  patient_id: string
  document_id?: string | null
  display_name: string
  value_numeric?: number | null
  value_text?: string | null
  unit?: string | null
  reference_low?: number | null
  reference_high?: number | null
  source_abnormal_flag?: string | null
  effective_at?: string | null
  validation_status: string
  created_at: string
}

export interface TrendPoint {
  date: string
  value: number
  unit: string
  reference_low?: number | null
  reference_high?: number | null
  source_document_id?: string | null
}

export interface ObservationTrend {
  test_name: string
  unit: string
  reference_low?: number | null
  reference_high?: number | null
  history: TrendPoint[]
}

export interface MedicationRecord {
  id: string
  patient_id: string
  document_id?: string | null
  medication_name: string
  generic_name?: string | null
  strength?: string | null
  dose_instructions?: string | null
  route?: string | null
  frequency?: string | null
  duration?: string | null
  prescription_date?: string | null
  medication_status: 'prescribed' | 'active' | 'discontinued' | 'completed'
  review_status: string
  created_at: string
}

export interface TimelineEventItem {
  id: string
  event_type: string
  title: string
  description: string
  event_date: string
  category: string
  source_document_id?: string | null
  badge_color?: string
  metadata: Record<string, any>
}

export interface ABHAStatus {
  patient_id: string
  provider_mode: string
  environment: string
  is_linked: boolean
  external_reference?: string | null
  verification_method?: string | null
  verified_at?: string | null
  simulated_disclaimer: string
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(errorBody.detail || `HTTP Error ${res.status}`)
  }
  return res.json()
}

export const api = {
  // Auth
  loginDemo: () => request<{ access_token: string; patient_id: string; full_name: string }>('/auth/demo-login', { method: 'POST' }),

  // Patient
  getPatient: () => request<PatientProfile>('/patient/me'),
  updatePatient: (data: Partial<PatientProfile>) =>
    request<PatientProfile>('/patient/me', { method: 'PATCH', body: JSON.stringify(data) }),

  // Documents
  listDocuments: (params?: { doc_type?: string; status?: string }) => {
    const query = new URLSearchParams()
    if (params?.doc_type) query.append('doc_type', params.doc_type)
    if (params?.status) query.append('status', params.status)
    const qStr = query.toString() ? `?${query.toString()}` : ''
    return request<MedicalDocument[]>(`/documents${qStr}`)
  },
  getDocument: (id: string) => request<MedicalDocument>(`/documents/${id}`),
  uploadDocument: async (file: File): Promise<MedicalDocument> => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${BASE_URL}/documents`, {
      method: 'POST',
      body: formData,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || 'Upload failed')
    }
    return res.json()
  },
  getDocumentStatus: (id: string) => request<{ id: string; processing_status: string; error_message?: string }>(`/documents/${id}/status`),
  deleteDocument: (id: string) => request<{ status: string }>(`/documents/${id}`, { method: 'DELETE' }),

  // Extraction Review
  getExtraction: (documentId: string) => request<ExtractionResult>(`/documents/${documentId}/extraction`),
  updateExtraction: (documentId: string, candidateData: any, reviewStatus?: string) =>
    request<ExtractionResult>(`/documents/${documentId}/extraction`, {
      method: 'PATCH',
      body: JSON.stringify({ structured_candidate_data: candidateData, review_status: reviewStatus || 'in_review' }),
    }),
  confirmExtraction: (documentId: string, payload: { confirm_all: boolean; active_medications: string[] }) =>
    request<{ status: string; message: string }>(`/documents/${documentId}/confirm`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // AI Summaries & Translation
  getSummary: (documentId: string, lang = 'en') =>
    request<DocumentSummary>(`/documents/${documentId}/summary?lang=${lang}`),
  translateSummary: (documentId: string, targetLanguage = 'ta') =>
    request<DocumentSummary>(`/documents/${documentId}/summary/translate`, {
      method: 'POST',
      body: JSON.stringify({ target_language: targetLanguage }),
    }),

  // Observations & Trends
  getObservations: (testName?: string) => {
    const q = testName ? `?test_name=${encodeURIComponent(testName)}` : ''
    return request<ObservationRecord[]>(`/observations${q}`)
  },
  getObservationTrends: () => request<ObservationTrend[]>('/observations/trends'),

  // Medications
  getMedications: (status?: string) => {
    const q = status ? `?status=${status}` : ''
    return request<MedicationRecord[]>(`/medications${q}`)
  },
  updateMedicationStatus: (id: string, status: string) =>
    request<MedicationRecord>(`/medications/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ medication_status: status }),
    }),

  // Timeline
  getTimeline: (category?: string) => {
    const q = category ? `?category=${category}` : ''
    return request<{ patient_id: string; events: TimelineEventItem[]; total_count: number }>(`/timeline${q}`)
  },

  // ABHA
  getABHAStatus: () => request<ABHAStatus>('/abha/status'),
  linkABHA: (identifier: string) =>
    request<{ status: string; transaction_id: string; message: string }>('/abha/link', {
      method: 'POST',
      body: JSON.stringify({ abha_identifier: identifier }),
    }),
  verifyABHA: (transactionId: string, otp: string) =>
    request<{ success: boolean; message: string }>('/abha/verify', {
      method: 'POST',
      body: JSON.stringify({ transaction_id: transactionId, otp }),
    }),
  revokeABHA: () => request<{ success: boolean; message: string }>('/abha/revoke', { method: 'POST' }),
}
