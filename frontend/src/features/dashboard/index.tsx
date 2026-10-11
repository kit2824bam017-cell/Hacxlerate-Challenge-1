import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { TopNav } from '@/components/layout/top-nav'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { ThemeSwitch } from '@/components/theme-switch'
import {
  FileText,
  Activity,
  Pill,
  Sparkles,
  Calendar,
  ShieldCheck,
  Upload,
  RefreshCw,
  SlidersHorizontal,
} from 'lucide-react'
import { toast } from 'sonner'

import {
  api,
  MedicalDocument,
  ObservationRecord,
  MedicationRecord,
  ABHAStatus,
} from '@/services/api'
import { HealthOverview } from './components/health-overview'
import { DocumentManager } from './components/document-manager'
import { ExtractionReview } from './components/extraction-review'
import { AISummaryViewer } from './components/ai-summary-viewer'
import { TimelineAndTrends } from './components/timeline-and-trends'
import { MedicationHistory } from './components/medication-history'
import { ABHASandbox } from './components/abha-sandbox'

export function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const [documents, setDocuments] = useState<MedicalDocument[]>([])
  const [observations, setObservations] = useState<ObservationRecord[]>([])
  const [medications, setMedications] = useState<MedicationRecord[]>([])
  const [abhaStatus, setAbhaStatus] = useState<ABHAStatus | null>(null)
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadAllData()
  }, [])

  const loadAllData = async () => {
    try {
      setIsLoading(true)
      const [docs, obs, meds, abha] = await Promise.all([
        api.listDocuments(),
        api.getObservations(),
        api.getMedications(),
        api.getABHAStatus(),
      ])
      setDocuments(docs || [])
      setObservations(obs || [])
      setMedications(meds || [])
      setAbhaStatus(abha)
      if (docs && docs.length > 0 && !selectedDocId) {
        setSelectedDocId(docs[0].id)
      }
    } catch (err: any) {
      toast.error('Failed to load patient health records.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectReviewDoc = (docId: string) => {
    setSelectedDocId(docId)
    setActiveTab('review')
  }

  const handleSelectSummaryDoc = (docId: string) => {
    setSelectedDocId(docId)
    setActiveTab('summary')
  }

  const handleDocumentConfirmed = () => {
    loadAllData()
    setActiveTab('overview')
  }

  const pendingReviewCount = documents.filter((d) => d.processing_status === 'awaiting_review').length

  return (
    <>
      {/* Top Header */}
      <Header>
        <div className='flex items-center gap-3 me-auto'>
          <div className='h-8 w-8 rounded-lg bg-teal-600 flex items-center justify-center text-white font-bold text-sm shadow-xs'>
            HC
          </div>
          <div>
            <h1 className='text-sm font-bold tracking-tight text-slate-900 dark:text-slate-100'>
              Personal Health Copilot
            </h1>
            <p className='text-[10px] text-muted-foreground'>Altrix Labs Innovation Challenge</p>
          </div>
        </div>
        <div className='flex items-center space-x-2'>
          <Button
            size='sm'
            variant='outline'
            onClick={loadAllData}
            disabled={isLoading}
            className='h-8 px-2.5 text-xs'
          >
            <RefreshCw className={`h-3.5 w-3.5 mr-1 ${isLoading ? 'animate-spin' : ''}`} /> Sync
          </Button>
          <ThemeSwitch />
          <ProfileDropdown />
        </div>
      </Header>

      {/* Main Workspace */}
      <Main>
        <div className='mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3'>
          <div>
            <h2 className='text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100'>
              Personal Health Portal
            </h2>
            <p className='text-xs text-muted-foreground'>
              Document OCR Intelligence • Bilingual Tamil Summaries • ABDM Ready
            </p>
          </div>
          <div className='flex items-center gap-2'>
            <Button
              size='sm'
              onClick={() => setActiveTab('documents')}
              className='bg-teal-700 hover:bg-teal-800 text-white text-xs h-8'
            >
              <Upload className='mr-1.5 h-3.5 w-3.5' /> Upload Document
            </Button>
          </div>
        </div>

        {/* Workspace Navigation Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className='space-y-4'>
          <div className='w-full overflow-x-auto pb-1'>
            <TabsList className='bg-slate-100 dark:bg-slate-900 p-1 border border-slate-200 dark:border-slate-800 h-9'>
              <TabsTrigger value='overview' onClick={() => setActiveTab('overview')} className='text-xs px-3 cursor-pointer'>
                Overview
              </TabsTrigger>
              <TabsTrigger value='documents' onClick={() => setActiveTab('documents')} className='text-xs px-3 cursor-pointer'>
                Documents ({documents.length})
              </TabsTrigger>
              <TabsTrigger value='review' onClick={() => setActiveTab('review')} className='text-xs px-3 cursor-pointer'>
                Review Extractions
                {pendingReviewCount > 0 && (
                  <Badge className='ml-1.5 bg-amber-500 hover:bg-amber-600 text-white text-[10px] px-1 py-0 h-4'>
                    {pendingReviewCount}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value='summary' onClick={() => setActiveTab('summary')} className='text-xs px-3 flex items-center gap-1 cursor-pointer'>
                <Sparkles className='h-3 w-3 text-teal-600' /> AI Summary
              </TabsTrigger>
              <TabsTrigger value='timeline' onClick={() => setActiveTab('timeline')} className='text-xs px-3 cursor-pointer'>
                Timeline & Trends
              </TabsTrigger>
              <TabsTrigger value='medications' onClick={() => setActiveTab('medications')} className='text-xs px-3 cursor-pointer'>
                Medications ({medications.length})
              </TabsTrigger>
              <TabsTrigger value='abha' onClick={() => setActiveTab('abha')} className='text-xs px-3 cursor-pointer'>
                ABHA Sandbox
              </TabsTrigger>
            </TabsList>
          </div>

          {/* 1. Overview Tab */}
          <TabsContent value='overview'>
            <HealthOverview
              documents={documents}
              observations={observations}
              medications={medications}
              abhaStatus={abhaStatus}
              onNavigateTab={setActiveTab}
              onSelectReviewDoc={handleSelectReviewDoc}
            />
          </TabsContent>

          {/* 2. Documents Management Tab */}
          <TabsContent value='documents'>
            <DocumentManager
              documents={documents}
              onRefresh={loadAllData}
              onSelectReviewDoc={handleSelectReviewDoc}
              onSelectSummaryDoc={handleSelectSummaryDoc}
            />
          </TabsContent>

          {/* 3. Extraction Review Tab */}
          <TabsContent value='review'>
            <ExtractionReview
              documents={documents}
              selectedDocId={selectedDocId}
              onDocumentConfirmed={handleDocumentConfirmed}
            />
          </TabsContent>

          {/* 4. Grounded AI Summary Tab */}
          <TabsContent value='summary'>
            <AISummaryViewer
              documents={documents}
              selectedDocId={selectedDocId}
            />
          </TabsContent>

          {/* 5. Timeline & Trends Tab */}
          <TabsContent value='timeline'>
            <TimelineAndTrends />
          </TabsContent>

          {/* 6. Medications Tab */}
          <TabsContent value='medications'>
            <MedicationHistory />
          </TabsContent>

          {/* 7. ABHA Sandbox Tab */}
          <TabsContent value='abha'>
            <ABHASandbox />
          </TabsContent>
        </Tabs>
      </Main>
    </>
  )
}
