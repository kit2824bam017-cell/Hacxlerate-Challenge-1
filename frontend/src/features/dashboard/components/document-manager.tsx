import React, { useState, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Upload,
  FileText,
  CheckCircle2,
  AlertCircle,
  Clock,
  Eye,
  Trash2,
  Sparkles,
  RefreshCw,
  FileUp,
} from 'lucide-react'
import { MedicalDocument, api } from '@/services/api'
import { toast } from 'sonner'

interface DocumentManagerProps {
  documents: MedicalDocument[]
  onRefresh: () => void
  onSelectReviewDoc: (docId: string) => void
  onSelectSummaryDoc: (docId: string) => void
}

export function DocumentManager({
  documents,
  onRefresh,
  onSelectReviewDoc,
  onSelectSummaryDoc,
}: DocumentManagerProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [selectedTypeFilter, setSelectedTypeFilter] = useState<string>('all')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await uploadFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await uploadFile(e.target.files[0])
    }
  }

  const uploadFile = async (file: File) => {
    const validExtensions = ['pdf', 'jpg', 'jpeg', 'png']
    const fileExt = file.name.split('.').pop()?.toLowerCase() || ''
    if (!validExtensions.includes(fileExt)) {
      toast.error('Unsupported file format. Please upload PDF, JPG, JPEG, or PNG.')
      return
    }

    if (file.size > 15 * 1024 * 1024) {
      toast.error('File size exceeds the 15MB limit.')
      return
    }

    try {
      setIsUploading(true)
      toast.info(`Uploading and processing '${file.name}' with Sarvam OCR...`)
      const res = await api.uploadDocument(file)
      toast.success(`'${file.name}' processed successfully! Awaiting your review.`)
      onRefresh()
      // Automatically prompt to review the newly uploaded document
      onSelectReviewDoc(res.id)
    } catch (err: any) {
      toast.error(err.message || 'Upload failed')
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleDelete = async (docId: string, filename: string) => {
    if (!confirm(`Are you sure you want to delete ${filename}?`)) return
    try {
      await api.deleteDocument(docId)
      toast.success(`Document deleted.`)
      onRefresh()
    } catch (err: any) {
      toast.error(err.message || 'Delete failed')
    }
  }

  const filteredDocs =
    selectedTypeFilter === 'all'
      ? documents
      : documents.filter((d) => d.document_type === selectedTypeFilter)

  return (
    <div className='space-y-6'>
      {/* Upload Zone */}
      <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
        <CardHeader>
          <CardTitle className='text-base font-semibold'>Upload Medical Documents</CardTitle>
          <CardDescription className='text-xs'>
            Upload prescriptions, blood/urine laboratory reports, and discharge summaries for OCR extraction.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
              isDragging
                ? 'border-teal-500 bg-teal-50/50 dark:bg-teal-950/20'
                : 'border-slate-300 dark:border-slate-700 hover:border-teal-400 hover:bg-slate-50/50 dark:hover:bg-slate-900/50'
            }`}
          >
            <input
              type='file'
              ref={fileInputRef}
              onChange={handleFileChange}
              accept='.pdf,.jpg,.jpeg,.png'
              className='hidden'
            />
            <div className='flex flex-col items-center justify-center space-y-3'>
              <div className='p-3.5 rounded-full bg-teal-100 dark:bg-teal-950 text-teal-700 dark:text-teal-300'>
                {isUploading ? (
                  <RefreshCw className='h-6 w-6 animate-spin' />
                ) : (
                  <FileUp className='h-6 w-6' />
                )}
              </div>
              <div className='space-y-1'>
                <p className='text-sm font-semibold text-slate-800 dark:text-slate-200'>
                  {isUploading ? 'Extracting Medical Records with OCR...' : 'Click to upload or drag & drop'}
                </p>
                <p className='text-xs text-muted-foreground'>
                  Supported Formats: PDF, JPG, JPEG, PNG (Max: 15MB)
                </p>
              </div>
              <div className='flex items-center gap-2 pt-1'>
                <Badge variant='outline' className='text-[11px] text-teal-800 dark:text-teal-300 bg-teal-50 dark:bg-teal-950/40 border-teal-200 dark:border-teal-800'>
                  Prescriptions
                </Badge>
                <Badge variant='outline' className='text-[11px] text-teal-800 dark:text-teal-300 bg-teal-50 dark:bg-teal-950/40 border-teal-200 dark:border-teal-800'>
                  Blood & Urine Lab Reports
                </Badge>
                <Badge variant='outline' className='text-[11px] text-teal-800 dark:text-teal-300 bg-teal-50 dark:bg-teal-950/40 border-teal-200 dark:border-teal-800'>
                  Discharge Summaries
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Document Library Table */}
      <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
        <CardHeader className='flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3'>
          <div>
            <CardTitle className='text-base font-semibold'>Medical Document Repository</CardTitle>
            <CardDescription className='text-xs'>
              {documents.length} records securely archived in private patient storage.
            </CardDescription>
          </div>
          <div className='flex items-center gap-2'>
            <select
              value={selectedTypeFilter}
              onChange={(e) => setSelectedTypeFilter(e.target.value)}
              className='text-xs rounded-md border border-slate-200 dark:border-slate-800 bg-background px-2.5 py-1.5 focus:outline-hidden'
            >
              <option value='all'>All Document Types</option>
              <option value='lab_report'>Laboratory Reports</option>
              <option value='prescription'>Prescriptions</option>
              <option value='discharge_summary'>Discharge Summaries</option>
              <option value='other'>Other</option>
            </select>
            <Button size='sm' variant='outline' onClick={onRefresh} className='h-8 px-2.5'>
              <RefreshCw className='h-3.5 w-3.5' />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className='overflow-x-auto'>
            <table className='w-full text-left text-sm'>
              <thead>
                <tr className='border-b border-slate-100 dark:border-slate-800 text-xs font-semibold text-muted-foreground'>
                  <th className='pb-3'>Document</th>
                  <th className='pb-3'>Type</th>
                  <th className='pb-3'>Report Date</th>
                  <th className='pb-3'>Processing Status</th>
                  <th className='pb-3 text-right'>Actions</th>
                </tr>
              </thead>
              <tbody className='divide-y divide-slate-100 dark:divide-slate-800'>
                {filteredDocs.map((doc) => {
                  const isAwaiting = doc.processing_status === 'awaiting_review'
                  const isDone = doc.processing_status === 'completed'
                  return (
                    <tr key={doc.id} className='hover:bg-slate-50/50 dark:hover:bg-slate-900/50'>
                      <td className='py-3.5'>
                        <div className='flex items-center gap-2.5'>
                          <FileText className='h-4 w-4 text-teal-600 shrink-0' />
                          <div>
                            <span className='font-medium text-slate-800 dark:text-slate-200 block truncate max-w-xs'>
                              {doc.original_filename}
                            </span>
                            <span className='text-xs text-muted-foreground'>
                              {((doc.file_size_bytes || 0) / 1024).toFixed(1)} KB
                            </span>
                          </div>
                        </div>
                      </td>
                      <td className='py-3.5'>
                        <Badge variant='outline' className='text-xs font-normal capitalize'>
                          {doc.document_type.replace('_', ' ')}
                        </Badge>
                      </td>
                      <td className='py-3.5 text-xs text-muted-foreground'>
                        {doc.document_date || '—'}
                      </td>
                      <td className='py-3.5'>
                        {isAwaiting ? (
                          <Badge variant='outline' className='bg-amber-50 text-amber-700 border-amber-300 dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-800 text-xs flex items-center gap-1 w-fit'>
                            <Clock className='h-3 w-3' /> Awaiting Review
                          </Badge>
                        ) : isDone ? (
                          <Badge variant='outline' className='bg-teal-50 text-teal-700 border-teal-300 dark:bg-teal-950/40 dark:text-teal-400 dark:border-teal-800 text-xs flex items-center gap-1 w-fit'>
                            <CheckCircle2 className='h-3 w-3' /> Completed
                          </Badge>
                        ) : (
                          <Badge variant='outline' className='text-xs'>
                            {doc.processing_status}
                          </Badge>
                        )}
                      </td>
                      <td className='py-3.5 text-right'>
                        <div className='flex items-center justify-end gap-1.5'>
                          {isAwaiting && (
                            <Button
                              size='sm'
                              variant='default'
                              className='bg-amber-600 hover:bg-amber-700 text-white text-xs h-7 px-2'
                              onClick={() => onSelectReviewDoc(doc.id)}
                            >
                              Review Data
                            </Button>
                          )}
                          <Button
                            size='sm'
                            variant='outline'
                            className='text-xs h-7 px-2 text-teal-700 dark:text-teal-300'
                            onClick={() => onSelectSummaryDoc(doc.id)}
                          >
                            <Sparkles className='h-3 w-3 mr-1' /> Summary
                          </Button>
                          <Button
                            size='sm'
                            variant='ghost'
                            className='text-xs h-7 px-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30'
                            onClick={() => handleDelete(doc.id, doc.original_filename)}
                          >
                            <Trash2 className='h-3.5 w-3.5' />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
