import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Sparkles,
  Languages,
  AlertTriangle,
  HelpCircle,
  ShieldCheck,
  FileText,
  RefreshCw,
  Info,
} from 'lucide-react'
import { MedicalDocument, DocumentSummary, api } from '@/services/api'
import { toast } from 'sonner'

interface AISummaryViewerProps {
  documents: MedicalDocument[]
  selectedDocId: string | null
}

export function AISummaryViewer({ documents, selectedDocId }: AISummaryViewerProps) {
  const [currentDocId, setCurrentDocId] = useState<string>(
    selectedDocId || documents[0]?.id || ''
  )
  const [summary, setSummary] = useState<DocumentSummary | null>(null)
  const [language, setLanguage] = useState<'en' | 'ta'>('en')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (selectedDocId) {
      setCurrentDocId(selectedDocId)
    }
  }, [selectedDocId])

  useEffect(() => {
    if (currentDocId) {
      loadSummary(currentDocId, language)
    }
  }, [currentDocId, language])

  const loadSummary = async (docId: string, lang: 'en' | 'ta') => {
    try {
      setIsLoading(true)
      const data = await api.getSummary(docId, lang)
      setSummary(data)
    } catch (err: any) {
      toast.error('Failed to load AI summary for this document.')
      setSummary(null)
    } finally {
      setIsLoading(false)
    }
  }

  const handleTranslate = async (targetLang: 'en' | 'ta') => {
    setLanguage(targetLang)
  }

  const currentDoc = documents.find((d) => d.id === currentDocId)

  return (
    <div className='space-y-6'>
      {/* Header and Controls */}
      <div className='flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-card shadow-xs'>
        <div>
          <h2 className='text-base font-bold flex items-center gap-2'>
            <Sparkles className='h-5 w-5 text-teal-600' />
            Evidence-Grounded AI Health Summary
          </h2>
          <p className='text-xs text-muted-foreground mt-0.5'>
            Plain-language explanations strictly grounded in your uploaded medical report.
          </p>
        </div>
        <div className='flex flex-wrap items-center gap-3'>
          {/* Document Select */}
          <select
            value={currentDocId}
            onChange={(e) => setCurrentDocId(e.target.value)}
            className='text-xs rounded-md border border-slate-200 dark:border-slate-800 bg-background px-3 py-1.5 focus:outline-hidden max-w-xs'
          >
            {documents.map((d) => (
              <option key={d.id} value={d.id}>
                {d.original_filename}
              </option>
            ))}
          </select>

          {/* Bilingual Language Selector */}
          <div className='inline-flex rounded-md shadow-xs p-0.5 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800'>
            <Button
              size='sm'
              variant={language === 'en' ? 'default' : 'ghost'}
              onClick={() => handleTranslate('en')}
              className={`text-xs h-7 px-3 ${language === 'en' ? 'bg-teal-700 hover:bg-teal-800 text-white' : ''}`}
            >
              English
            </Button>
            <Button
              size='sm'
              variant={language === 'ta' ? 'default' : 'ghost'}
              onClick={() => handleTranslate('ta')}
              className={`text-xs h-7 px-3 ${language === 'ta' ? 'bg-teal-700 hover:bg-teal-800 text-white' : ''}`}
            >
              தமிழ் (Tamil)
            </Button>
          </div>
        </div>
      </div>

      {isLoading ? (
        <Card className='p-12 text-center'>
          <RefreshCw className='h-8 w-8 animate-spin mx-auto text-teal-600 mb-3' />
          <p className='text-sm text-muted-foreground'>
            {language === 'ta'
              ? 'சரவம் AI மூலம் தமிழ் மொழிபெயர்ப்பு பெறப்படுகிறது...'
              : 'Synthesizing evidence-grounded summary...'}
          </p>
        </Card>
      ) : !summary ? (
        <Card className='p-12 text-center'>
          <p className='text-sm text-muted-foreground'>
            No AI summary generated for this document yet. Please complete extraction review.
          </p>
        </Card>
      ) : (
        <div className='space-y-6'>
          {/* Overview Card */}
          <Card className='border-slate-200 dark:border-slate-800 shadow-xs bg-slate-50/50 dark:bg-slate-900/40'>
            <CardHeader className='pb-2'>
              <div className='flex items-center justify-between'>
                <CardTitle className='text-sm font-semibold text-teal-800 dark:text-teal-300 flex items-center gap-2'>
                  <FileText className='h-4 w-4' />
                  {language === 'ta' ? 'ஆவண கண்ணோட்டம்' : 'Document Overview'}
                </CardTitle>
                <Badge variant='outline' className='text-[10px] bg-background'>
                  {language === 'ta' ? 'தமிழ் மொழிபெயர்ப்பு' : 'English Original'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className='text-sm leading-relaxed text-slate-800 dark:text-slate-200 font-medium'>
                {summary.overview}
              </p>
            </CardContent>
          </Card>

          {/* Key Findings */}
          <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
            <CardHeader className='pb-3'>
              <CardTitle className='text-base font-semibold'>
                {language === 'ta' ? 'முக்கிய மருத்துவ கண்டுபிடிப்புகள்' : 'Important Findings'}
              </CardTitle>
              <CardDescription className='text-xs'>
                {language === 'ta'
                  ? 'உங்கள் ஆய்வக அறிக்கையில் உள்ள துல்லியமான அளவீடுகள்'
                  : 'Grounded directly in the explicit readings printed in the source document'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className='space-y-2.5'>
                {summary.key_findings.map((kf, i) => (
                  <li key={i} className='flex items-start gap-2.5 text-sm'>
                    <div className='h-2 w-2 rounded-full bg-teal-600 mt-2 shrink-0' />
                    <span className='leading-relaxed text-slate-800 dark:text-slate-200'>{kf}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Abnormal Laboratory Flags Explanation */}
          {summary.abnormal_explanations.length > 0 && (
            <Card className='border-amber-200 dark:border-amber-900/50 bg-amber-50/30 dark:bg-amber-950/20 shadow-xs'>
              <CardHeader className='pb-3'>
                <div className='flex items-center gap-2'>
                  <AlertTriangle className='h-5 w-5 text-amber-600 dark:text-amber-400' />
                  <CardTitle className='text-base font-semibold text-amber-900 dark:text-amber-200'>
                    {language === 'ta' ? 'இயல்பு வரம்பிற்கு வெளியே உள்ள அளவீடுகள்' : 'Reported Values Outside Reference Range'}
                  </CardTitle>
                </div>
                <CardDescription className='text-xs text-amber-700 dark:text-amber-300'>
                  {language === 'ta'
                    ? 'ஆய்வக வரம்புகளுடன் ஒப்பிட்ட எளிய விளக்கம் (நோய் கண்டறிதல் அல்ல)'
                    : 'Contextual educational explanations based strictly on the reporting laboratory’s reference interval'}
                </CardDescription>
              </CardHeader>
              <CardContent className='space-y-3.5'>
                {summary.abnormal_explanations.map((item, idx) => (
                  <div
                    key={idx}
                    className='p-3.5 rounded-lg border border-amber-200/80 dark:border-amber-800/80 bg-background/80 shadow-2xs space-y-1.5'
                  >
                    <div className='flex flex-wrap items-center justify-between gap-2'>
                      <span className='font-semibold text-sm'>{item.test_name}</span>
                      <div className='flex items-center gap-2'>
                        <span className='text-sm font-bold text-red-600 dark:text-red-400'>{item.value}</span>
                        <Badge variant='outline' className='text-[10px] bg-red-50 text-red-700 border-red-300 dark:bg-red-950/40 dark:text-red-400 dark:border-red-800'>
                          {item.status}
                        </Badge>
                      </div>
                    </div>
                    <p className='text-xs text-muted-foreground'>
                      {language === 'ta' ? 'இயல்பு வரம்பு:' : 'Laboratory Reference Range:'} {item.reference}
                    </p>
                    <p className='text-xs text-slate-700 dark:text-slate-300 leading-relaxed pt-1'>
                      {item.plain_explanation}
                    </p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Clinician Questions */}
          <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
            <CardHeader className='pb-3'>
              <div className='flex items-center gap-2'>
                <HelpCircle className='h-5 w-5 text-teal-600' />
                <CardTitle className='text-base font-semibold'>
                  {language === 'ta' ? 'மருத்துவரிடம் கேட்க வேண்டிய கேள்விகள்' : 'Questions to Discuss with Your Doctor'}
                </CardTitle>
              </div>
              <CardDescription className='text-xs'>
                {language === 'ta'
                  ? 'உங்கள் அடுத்த மருத்துவ ஆலோசனையின் போது கேட்கக்கூடிய வினாக்கள்'
                  : 'Tailored questions to help you prepare for an informed healthcare consultation'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className='space-y-2'>
                {summary.questions_for_doctor.map((q, idx) => (
                  <li
                    key={idx}
                    className='p-2.5 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 text-sm flex items-start gap-2.5'
                  >
                    <span className='font-bold text-teal-700 dark:text-teal-400'>{idx + 1}.</span>
                    <span className='leading-relaxed text-slate-800 dark:text-slate-200'>{q}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Mandatory Healthcare Safety Disclaimer */}
          <div className='p-4 rounded-xl border border-teal-200 dark:border-teal-900 bg-teal-50/40 dark:bg-teal-950/20 text-teal-900 dark:text-teal-200 space-y-1.5'>
            <div className='flex items-center gap-2'>
              <ShieldCheck className='h-4 w-4 text-teal-700 shrink-0' />
              <h5 className='text-xs font-bold uppercase tracking-wider'>
                {language === 'ta' ? 'மருத்துவ பாதுகாப்பு அறிக்கை' : 'Healthcare Safety & Limitations'}
              </h5>
            </div>
            <p className='text-xs leading-relaxed'>{summary.safety_disclaimer}</p>
            {summary.limitations && (
              <p className='text-xs text-teal-800 dark:text-teal-300 pt-1'>
                <strong>{language === 'ta' ? 'வரம்புகள்:' : 'Scope & Limitations:'}</strong> {summary.limitations}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
