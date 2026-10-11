import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  CheckCircle,
  FileText,
  AlertTriangle,
  Pill,
  Save,
  Check,
  Eye,
  Info,
  RefreshCw,
} from 'lucide-react'
import { MedicalDocument, ExtractionResult, CandidateObservation, CandidateMedication, api } from '@/services/api'
import { toast } from 'sonner'

interface ExtractionReviewProps {
  documents: MedicalDocument[]
  selectedDocId: string | null
  onDocumentConfirmed: () => void
}

export function ExtractionReview({
  documents,
  selectedDocId,
  onDocumentConfirmed,
}: ExtractionReviewProps) {
  const [currentDocId, setCurrentDocId] = useState<string>(
    selectedDocId || documents[0]?.id || ''
  )
  const [extraction, setExtraction] = useState<ExtractionResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [observations, setObservations] = useState<CandidateObservation[]>([])
  const [medications, setMedications] = useState<CandidateMedication[]>([])
  const [activeMedicationNames, setActiveMedicationNames] = useState<string[]>([])
  const [showRawOcr, setShowRawOcr] = useState(false)

  useEffect(() => {
    if (selectedDocId) {
      setCurrentDocId(selectedDocId)
    }
  }, [selectedDocId])

  useEffect(() => {
    if (currentDocId) {
      loadExtraction(currentDocId)
    }
  }, [currentDocId])

  const loadExtraction = async (docId: string) => {
    try {
      setIsLoading(true)
      const data = await api.getExtraction(docId)
      setExtraction(data)
      setObservations(data.structured_candidate_data.observations || [])
      setMedications(data.structured_candidate_data.medications || [])
      // Default all candidate medications to active initially
      setActiveMedicationNames(
        (data.structured_candidate_data.medications || []).map((m) => m.medication_name)
      )
    } catch (err: any) {
      toast.error('Failed to load extraction data for document.')
      setExtraction(null)
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpdateObservation = (index: number, field: keyof CandidateObservation, value: any) => {
    const updated = [...observations]
    updated[index] = { ...updated[index], [field]: value }
    setObservations(updated)
  }

  const handleUpdateMedication = (index: number, field: keyof CandidateMedication, value: any) => {
    const updated = [...medications]
    updated[index] = { ...updated[index], [field]: value }
    setMedications(updated)
  }

  const toggleActiveMed = (mname: string) => {
    if (activeMedicationNames.includes(mname)) {
      setActiveMedicationNames(activeMedicationNames.filter((name) => name !== mname))
    } else {
      setActiveMedicationNames([...activeMedicationNames, mname])
    }
  }

  const handleSaveDraft = async () => {
    if (!currentDocId || !extraction) return
    try {
      setIsSaving(true)
      const updatedCandidate = {
        ...extraction.structured_candidate_data,
        observations,
        medications,
      }
      await api.updateExtraction(currentDocId, updatedCandidate, 'in_review')
      toast.success('Extraction corrections saved as draft.')
    } catch (err: any) {
      toast.error(err.message || 'Failed to save changes.')
    } finally {
      setIsSaving(false)
    }
  }

  const handleConfirmAndPromote = async () => {
    if (!currentDocId || !extraction) return
    try {
      setIsSaving(true)
      // 1. Save any in-progress edits first
      const updatedCandidate = {
        ...extraction.structured_candidate_data,
        observations,
        medications,
      }
      await api.updateExtraction(currentDocId, updatedCandidate, 'approved')

      // 2. Promote candidate records into confirmed observations & medications
      await api.confirmExtraction(currentDocId, {
        confirm_all: true,
        active_medications: activeMedicationNames,
      })

      toast.success('Medical data confirmed! Added to longitudinal timeline and medications.')
      onDocumentConfirmed()
    } catch (err: any) {
      toast.error(err.message || 'Confirmation failed.')
    } finally {
      setIsSaving(false)
    }
  }

  const currentDoc = documents.find((d) => d.id === currentDocId)

  return (
    <div className='space-y-6'>
      {/* Header and Document Picker */}
      <div className='flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-card shadow-xs'>
        <div>
          <h2 className='text-base font-bold flex items-center gap-2'>
            <FileText className='h-5 w-5 text-teal-600' />
            Extraction Verification & Human-in-the-Loop Review
          </h2>
          <p className='text-xs text-muted-foreground mt-0.5'>
            Inspect candidate OCR extractions. Review or correct values before confirming into health records.
          </p>
        </div>
        <div className='flex items-center gap-3'>
          <label className='text-xs font-medium text-muted-foreground'>Document:</label>
          <select
            value={currentDocId}
            onChange={(e) => setCurrentDocId(e.target.value)}
            className='text-xs rounded-md border border-slate-200 dark:border-slate-800 bg-background px-3 py-1.5 focus:outline-hidden max-w-xs'
          >
            {documents.map((d) => (
              <option key={d.id} value={d.id}>
                {d.original_filename} ({d.processing_status})
              </option>
            ))}
          </select>
        </div>
      </div>

      {isLoading ? (
        <Card className='p-12 text-center'>
          <RefreshCw className='h-8 w-8 animate-spin mx-auto text-teal-600 mb-3' />
          <p className='text-sm text-muted-foreground'>Loading candidate extraction data...</p>
        </Card>
      ) : !extraction ? (
        <Card className='p-12 text-center'>
          <p className='text-sm text-muted-foreground'>No extraction record found for this document.</p>
        </Card>
      ) : (
        <div className='space-y-6'>
          {/* Status Bar */}
          <div className='flex flex-wrap items-center justify-between gap-4 p-3.5 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs'>
            <div className='flex items-center gap-3'>
              <Badge variant='outline' className='bg-background'>
                Provider: {extraction.extraction_provider}
              </Badge>
              <Badge
                variant='outline'
                className={
                  extraction.review_status === 'approved'
                    ? 'bg-teal-50 text-teal-700 border-teal-200 dark:bg-teal-950 dark:text-teal-300'
                    : 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950 dark:text-amber-300'
                }
              >
                Status: {extraction.review_status}
              </Badge>
              <span className='text-muted-foreground'>
                Provider: {extraction.structured_candidate_data.healthcare_provider || 'Not specified'}
              </span>
            </div>
            <Button
              size='sm'
              variant='outline'
              onClick={() => setShowRawOcr(!showRawOcr)}
              className='text-xs h-7'
            >
              <Eye className='mr-1.5 h-3.5 w-3.5' />
              {showRawOcr ? 'Hide Raw OCR' : 'Inspect Raw OCR'}
            </Button>
          </div>

          {/* Raw OCR Collapsible */}
          {showRawOcr && (
            <Card className='border-slate-200 dark:border-slate-800 bg-slate-950 text-slate-100 font-mono text-xs'>
              <CardHeader className='pb-2'>
                <CardTitle className='text-xs text-slate-400'>Raw OCR Text Source</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className='whitespace-pre-wrap leading-relaxed max-h-60 overflow-y-auto'>
                  {extraction.raw_ocr_text || 'No raw OCR captured.'}
                </pre>
              </CardContent>
            </Card>
          )}

          {/* Candidate Laboratory Observations */}
          {observations.length > 0 && (
            <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
              <CardHeader className='pb-3'>
                <div className='flex items-center justify-between'>
                  <div>
                    <CardTitle className='text-base font-semibold'>Extracted Laboratory Observations</CardTitle>
                    <CardDescription className='text-xs'>
                      Verify test names, measured values, units, and laboratory reference intervals.
                    </CardDescription>
                  </div>
                  <Badge variant='secondary' className='text-xs'>
                    {observations.length} Biomarkers
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className='overflow-x-auto'>
                  <table className='w-full text-left text-xs'>
                    <thead>
                      <tr className='border-b border-slate-200 dark:border-slate-800 font-semibold text-muted-foreground'>
                        <th className='pb-2.5 w-1/4'>Test Name</th>
                        <th className='pb-2.5 w-1/6'>Value</th>
                        <th className='pb-2.5 w-1/6'>Unit</th>
                        <th className='pb-2.5 w-1/4'>Reference Interval</th>
                        <th className='pb-2.5 w-1/8'>Flag</th>
                        <th className='pb-2.5 w-1/8'>Confidence</th>
                      </tr>
                    </thead>
                    <tbody className='divide-y divide-slate-100 dark:divide-slate-800'>
                      {observations.map((obs, idx) => (
                        <tr key={idx} className='hover:bg-slate-50/50 dark:hover:bg-slate-900/50'>
                          <td className='py-2.5 pr-2'>
                            <Input
                              value={obs.test_name}
                              onChange={(e) => handleUpdateObservation(idx, 'test_name', e.target.value)}
                              className='h-8 text-xs font-medium'
                            />
                          </td>
                          <td className='py-2.5 pr-2'>
                            <Input
                              type='number'
                              step='any'
                              value={obs.value_numeric ?? ''}
                              onChange={(e) =>
                                handleUpdateObservation(
                                  idx,
                                  'value_numeric',
                                  e.target.value ? parseFloat(e.target.value) : null
                                )
                              }
                              className='h-8 text-xs font-bold text-teal-700 dark:text-teal-300'
                            />
                          </td>
                          <td className='py-2.5 pr-2'>
                            <Input
                              value={obs.unit ?? ''}
                              onChange={(e) => handleUpdateObservation(idx, 'unit', e.target.value)}
                              className='h-8 text-xs'
                            />
                          </td>
                          <td className='py-2.5 pr-2'>
                            <div className='flex items-center gap-1'>
                              <Input
                                placeholder='Low'
                                type='number'
                                step='any'
                                value={obs.reference_low ?? ''}
                                onChange={(e) =>
                                  handleUpdateObservation(
                                    idx,
                                    'reference_low',
                                    e.target.value ? parseFloat(e.target.value) : null
                                  )
                                }
                                className='h-8 text-xs w-18'
                              />
                              <span className='text-muted-foreground'>-</span>
                              <Input
                                placeholder='High'
                                type='number'
                                step='any'
                                value={obs.reference_high ?? ''}
                                onChange={(e) =>
                                  handleUpdateObservation(
                                    idx,
                                    'reference_high',
                                    e.target.value ? parseFloat(e.target.value) : null
                                  )
                                }
                                className='h-8 text-xs w-18'
                              />
                            </div>
                          </td>
                          <td className='py-2.5 pr-2'>
                            <select
                              value={obs.source_abnormal_flag || ''}
                              onChange={(e) =>
                                handleUpdateObservation(idx, 'source_abnormal_flag', e.target.value || null)
                              }
                              className='h-8 text-xs rounded-md border border-slate-200 dark:border-slate-800 bg-background px-2'
                            >
                              <option value=''>NORMAL</option>
                              <option value='H'>H (High)</option>
                              <option value='L'>L (Low)</option>
                              <option value='CRITICAL'>CRITICAL</option>
                            </select>
                          </td>
                          <td className='py-2.5'>
                            <Badge variant='outline' className='text-[10px] bg-slate-50 dark:bg-slate-900'>
                              {obs.confidence}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Candidate Prescribed Medications */}
          {medications.length > 0 && (
            <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
              <CardHeader className='pb-3'>
                <div className='flex items-center justify-between'>
                  <div>
                    <CardTitle className='text-base font-semibold'>Extracted Prescriptions & Medications</CardTitle>
                    <CardDescription className='text-xs'>
                      Review medicine brand, strength, and schedule. Check the box if you currently take this medication.
                    </CardDescription>
                  </div>
                  <Badge variant='secondary' className='text-xs'>
                    {medications.length} Medications
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className='overflow-x-auto'>
                  <table className='w-full text-left text-xs'>
                    <thead>
                      <tr className='border-b border-slate-200 dark:border-slate-800 font-semibold text-muted-foreground'>
                        <th className='pb-2.5 w-1/4'>Medication & Strength</th>
                        <th className='pb-2.5 w-1/4'>Dose Instructions</th>
                        <th className='pb-2.5 w-1/6'>Frequency</th>
                        <th className='pb-2.5 w-1/6'>Duration</th>
                        <th className='pb-2.5 text-center'>Currently Taking</th>
                      </tr>
                    </thead>
                    <tbody className='divide-y divide-slate-100 dark:divide-slate-800'>
                      {medications.map((med, idx) => {
                        const isActive = activeMedicationNames.includes(med.medication_name)
                        return (
                          <tr key={idx} className='hover:bg-slate-50/50 dark:hover:bg-slate-900/50'>
                            <td className='py-2.5 pr-2'>
                              <div className='space-y-1'>
                                <Input
                                  value={med.medication_name}
                                  onChange={(e) => handleUpdateMedication(idx, 'medication_name', e.target.value)}
                                  className='h-8 text-xs font-semibold'
                                />
                                <Input
                                  placeholder='Salt/Strength (e.g. 500 mg)'
                                  value={med.strength ?? ''}
                                  onChange={(e) => handleUpdateMedication(idx, 'strength', e.target.value)}
                                  className='h-7 text-[11px] text-muted-foreground'
                                />
                              </div>
                            </td>
                            <td className='py-2.5 pr-2'>
                              <Input
                                value={med.dose_instructions ?? ''}
                                onChange={(e) => handleUpdateMedication(idx, 'dose_instructions', e.target.value)}
                                className='h-8 text-xs'
                              />
                            </td>
                            <td className='py-2.5 pr-2'>
                              <Input
                                value={med.frequency ?? ''}
                                onChange={(e) => handleUpdateMedication(idx, 'frequency', e.target.value)}
                                className='h-8 text-xs'
                              />
                            </td>
                            <td className='py-2.5 pr-2'>
                              <Input
                                value={med.duration ?? ''}
                                onChange={(e) => handleUpdateMedication(idx, 'duration', e.target.value)}
                                className='h-8 text-xs'
                              />
                            </td>
                            <td className='py-2.5 text-center'>
                              <Button
                                size='sm'
                                variant={isActive ? 'default' : 'outline'}
                                onClick={() => toggleActiveMed(med.medication_name)}
                                className={`text-xs h-7 px-2.5 ${isActive ? 'bg-teal-600 hover:bg-teal-700 text-white' : 'text-slate-600'}`}
                              >
                                {isActive ? 'Active' : 'Prescribed'}
                              </Button>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Action Bar */}
          <div className='flex items-center justify-between p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-card shadow-xs'>
            <div className='flex items-center gap-2 text-xs text-muted-foreground'>
              <Info className='h-4 w-4 text-teal-600' />
              <span>Confirmed records will be securely archived and plotted on your health timeline.</span>
            </div>
            <div className='flex items-center gap-3'>
              <Button size='sm' variant='outline' onClick={handleSaveDraft} disabled={isSaving}>
                <Save className='mr-1.5 h-3.5 w-3.5' /> Save Draft
              </Button>
              <Button
                size='sm'
                onClick={handleConfirmAndPromote}
                disabled={isSaving}
                className='bg-teal-700 hover:bg-teal-800 text-white'
              >
                <Check className='mr-1.5 h-3.5 w-3.5' /> Confirm & Save Records
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
