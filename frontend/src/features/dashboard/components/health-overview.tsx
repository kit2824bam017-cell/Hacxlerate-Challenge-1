import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  FileText,
  AlertTriangle,
  Pill,
  ShieldCheck,
  Upload,
  ArrowRight,
  TrendingUp,
  Activity,
  CheckCircle2,
} from 'lucide-react'
import { MedicalDocument, ObservationRecord, MedicationRecord, ABHAStatus } from '@/services/api'

interface HealthOverviewProps {
  documents: MedicalDocument[]
  observations: ObservationRecord[]
  medications: MedicationRecord[]
  abhaStatus: ABHAStatus | null
  onNavigateTab: (tab: string) => void
  onSelectReviewDoc: (docId: string) => void
}

export function HealthOverview({
  documents,
  observations,
  medications,
  abhaStatus,
  onNavigateTab,
  onSelectReviewDoc,
}: HealthOverviewProps) {
  const pendingReviewDocs = documents.filter((d) => d.processing_status === 'awaiting_review')
  const completedDocs = documents.filter((d) => d.processing_status === 'completed')
  const activeMeds = medications.filter((m) => m.medication_status === 'active')
  const abnormalObservations = observations.filter(
    (o) => o.source_abnormal_flag && ['H', 'L', 'CRITICAL'].includes(o.source_abnormal_flag)
  )

  return (
    <div className='space-y-6'>
      {/* Informational Assistant Banner */}
      <div className='flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-teal-50 dark:bg-teal-950/30 border border-teal-200 dark:border-teal-800 text-teal-900 dark:text-teal-200'>
        <div className='flex items-center gap-3'>
          <div className='p-2 rounded-lg bg-teal-600 text-white'>
            <ShieldCheck className='h-5 w-5' />
          </div>
          <div>
            <h4 className='font-semibold text-sm'>Informational Personal Health Copilot</h4>
            <p className='text-xs text-teal-700 dark:text-teal-300'>
              Patient Profile: <strong>Ananya Sharma</strong> (38/F) • Blood Group: <strong>B+</strong> • Mode: Verified Grounded Informatics
            </p>
          </div>
        </div>
        <div className='flex items-center gap-2'>
          <Badge variant='outline' className='bg-white/80 dark:bg-teal-900 border-teal-300 dark:border-teal-700 text-teal-800 dark:text-teal-200'>
            {abhaStatus?.is_linked ? `Linked: ${abhaStatus.external_reference}` : 'ABHA Ready'}
          </Badge>
          <Button size='sm' onClick={() => onNavigateTab('documents')} className='bg-teal-700 hover:bg-teal-800 text-white'>
            <Upload className='mr-1.5 h-3.5 w-3.5' /> Upload Document
          </Button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
        <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
          <CardHeader className='flex flex-row items-center justify-between pb-2'>
            <CardTitle className='text-sm font-medium text-muted-foreground'>Total Documents</CardTitle>
            <FileText className='h-4 w-4 text-teal-600' />
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold'>{documents.length}</div>
            <p className='text-xs text-muted-foreground mt-1'>
              {completedDocs.length} confirmed • {documents.length - completedDocs.length} processing
            </p>
          </CardContent>
        </Card>

        <Card className={`border-slate-200 dark:border-slate-800 shadow-xs ${pendingReviewDocs.length > 0 ? 'border-amber-400 dark:border-amber-600 bg-amber-50/20' : ''}`}>
          <CardHeader className='flex flex-row items-center justify-between pb-2'>
            <CardTitle className='text-sm font-medium text-muted-foreground'>Awaiting Review</CardTitle>
            <AlertTriangle className={`h-4 w-4 ${pendingReviewDocs.length > 0 ? 'text-amber-600' : 'text-slate-400'}`} />
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold text-amber-700 dark:text-amber-400'>{pendingReviewDocs.length}</div>
            <p className='text-xs text-muted-foreground mt-1'>
              {pendingReviewDocs.length > 0 ? 'Needs patient validation' : 'All extractions verified'}
            </p>
          </CardContent>
        </Card>

        <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
          <CardHeader className='flex flex-row items-center justify-between pb-2'>
            <CardTitle className='text-sm font-medium text-muted-foreground'>Active Medications</CardTitle>
            <Pill className='h-4 w-4 text-blue-600' />
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold text-blue-700 dark:text-blue-400'>{activeMeds.length}</div>
            <p className='text-xs text-muted-foreground mt-1'>
              {medications.length} total prescribed in records
            </p>
          </CardContent>
        </Card>

        <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
          <CardHeader className='flex flex-row items-center justify-between pb-2'>
            <CardTitle className='text-sm font-medium text-muted-foreground'>ABHA Status</CardTitle>
            <Activity className='h-4 w-4 text-purple-600' />
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold text-purple-700 dark:text-purple-400'>
              {abhaStatus?.is_linked ? 'Connected' : 'Unlinked'}
            </div>
            <p className='text-xs text-muted-foreground mt-1'>
              {abhaStatus?.is_linked ? 'Simulated Sandbox Linked' : 'Ready for Mock Verification'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Grid: Pending Reviews & Abnormal Observations */}
      <div className='grid gap-6 md:grid-cols-2'>
        {/* Pending Reviews or Recent Uploads */}
        <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
          <CardHeader>
            <div className='flex items-center justify-between'>
              <div>
                <CardTitle className='text-base font-semibold'>Recent Uploads & Extraction</CardTitle>
                <CardDescription className='text-xs'>Medical reports processed by Sarvam OCR</CardDescription>
              </div>
              <Button variant='ghost' size='sm' onClick={() => onNavigateTab('documents')}>
                View All <ArrowRight className='ml-1 h-3.5 w-3.5' />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className='space-y-3'>
              {documents.slice(0, 4).map((doc) => (
                <div
                  key={doc.id}
                  className='flex items-center justify-between p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-100/50 transition-colors'
                >
                  <div className='flex items-center gap-3 overflow-hidden'>
                    <div className='p-2 rounded-md bg-teal-100 dark:bg-teal-950 text-teal-700 dark:text-teal-300 shrink-0'>
                      <FileText className='h-4 w-4' />
                    </div>
                    <div className='truncate'>
                      <p className='text-sm font-medium truncate'>{doc.original_filename}</p>
                      <p className='text-xs text-muted-foreground'>
                        {doc.document_type.replace('_', ' ').toUpperCase()} • {doc.document_date || 'Recent'}
                      </p>
                    </div>
                  </div>
                  <div className='flex items-center gap-2 shrink-0'>
                    {doc.processing_status === 'awaiting_review' ? (
                      <Button
                        size='sm'
                        variant='default'
                        className='bg-amber-600 hover:bg-amber-700 text-white text-xs h-7 px-2.5'
                        onClick={() => {
                          onSelectReviewDoc(doc.id)
                          onNavigateTab('review')
                        }}
                      >
                        Review
                      </Button>
                    ) : (
                      <Badge
                        variant='outline'
                        className={
                          doc.processing_status === 'completed'
                            ? 'text-teal-700 bg-teal-50 border-teal-200 dark:bg-teal-950/40 dark:text-teal-300 dark:border-teal-800 text-xs'
                            : 'text-slate-600 bg-slate-100 text-xs'
                        }
                      >
                        {doc.processing_status}
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Noteworthy Laboratory Values */}
        <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
          <CardHeader>
            <div className='flex items-center justify-between'>
              <div>
                <CardTitle className='text-base font-semibold'>Reported Laboratory Highlights</CardTitle>
                <CardDescription className='text-xs'>Values compared against laboratory reference intervals</CardDescription>
              </div>
              <Button variant='ghost' size='sm' onClick={() => onNavigateTab('timeline')}>
                Trends <TrendingUp className='ml-1 h-3.5 w-3.5' />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className='space-y-3'>
              {observations.slice(0, 5).map((obs) => {
                const isAbnormal = obs.source_abnormal_flag && ['H', 'L', 'CRITICAL'].includes(obs.source_abnormal_flag)
                return (
                  <div
                    key={obs.id}
                    className='flex items-center justify-between p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50'
                  >
                    <div>
                      <div className='flex items-center gap-2'>
                        <span className='text-sm font-medium'>{obs.display_name}</span>
                        {isAbnormal && (
                          <Badge variant='outline' className='bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-400 dark:border-red-800 text-[10px] px-1.5 py-0'>
                            {obs.source_abnormal_flag === 'H' ? 'Above Range' : 'Below Range'}
                          </Badge>
                        )}
                      </div>
                      <p className='text-xs text-muted-foreground mt-0.5'>
                        Ref Interval: {obs.reference_low ?? '—'} - {obs.reference_high ?? '—'} {obs.unit}
                      </p>
                    </div>
                    <div className='text-right'>
                      <span className={`text-sm font-bold ${isAbnormal ? 'text-red-600 dark:text-red-400' : 'text-slate-800 dark:text-slate-200'}`}>
                        {obs.value_numeric} <span className='text-xs font-normal text-muted-foreground'>{obs.unit}</span>
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
