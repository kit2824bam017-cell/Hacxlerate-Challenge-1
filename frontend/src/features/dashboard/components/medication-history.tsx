import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Pill, CheckCircle, Clock, AlertCircle, RefreshCw, Info } from 'lucide-react'
import { MedicationRecord, api } from '@/services/api'
import { toast } from 'sonner'

export function MedicationHistory() {
  const [medications, setMedications] = useState<MedicationRecord[]>([])
  const [filter, setFilter] = useState<'all' | 'active' | 'prescribed'>('all')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadMedications()
  }, [])

  const loadMedications = async () => {
    try {
      setIsLoading(true)
      const data = await api.getMedications()
      setMedications(data || [])
    } catch (err: any) {
      toast.error('Failed to load medication history.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleStatus = async (medId: string, currentStatus: string) => {
    const nextStatus = currentStatus === 'active' ? 'prescribed' : 'active'
    try {
      await api.updateMedicationStatus(medId, nextStatus)
      toast.success(
        nextStatus === 'active'
          ? 'Medication marked as actively taken.'
          : 'Medication marked as prescribed / historical.'
      )
      loadMedications()
    } catch (err: any) {
      toast.error(err.message || 'Status update failed.')
    }
  }

  const filtered =
    filter === 'all'
      ? medications
      : medications.filter((m) => m.medication_status === filter)

  const activeCount = medications.filter((m) => m.medication_status === 'active').length

  return (
    <div className='space-y-6'>
      {/* Informational Guidance Banner */}
      <div className='p-4 rounded-xl border border-blue-200 dark:border-blue-900 bg-blue-50/40 dark:bg-blue-950/20 text-blue-900 dark:text-blue-200 space-y-1.5'>
        <div className='flex items-center gap-2'>
          <Info className='h-4 w-4 text-blue-700 shrink-0' />
          <h4 className='text-xs font-bold uppercase tracking-wider'>
            Active Intake Verification vs Prescribed Record
          </h4>
        </div>
        <p className='text-xs leading-relaxed'>
          Older prescriptions are not assumed to remain active automatically. You can explicitly confirm which
          prescribed drugs you currently take versus historical courses.
        </p>
      </div>

      <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
        <CardHeader className='flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4'>
          <div>
            <CardTitle className='text-base font-semibold flex items-center gap-2'>
              <Pill className='h-5 w-5 text-blue-600' />
              Medication History & Regimen
            </CardTitle>
            <CardDescription className='text-xs'>
              {medications.length} medications extracted from doctor prescriptions ({activeCount} confirmed active).
            </CardDescription>
          </div>
          <div className='flex items-center gap-2'>
            <div className='inline-flex rounded-md shadow-xs p-0.5 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs'>
              <Button
                size='sm'
                variant={filter === 'all' ? 'default' : 'ghost'}
                onClick={() => setFilter('all')}
                className={`text-xs h-7 px-3 ${filter === 'all' ? 'bg-slate-800 dark:bg-slate-200 text-white dark:text-slate-900' : ''}`}
              >
                All ({medications.length})
              </Button>
              <Button
                size='sm'
                variant={filter === 'active' ? 'default' : 'ghost'}
                onClick={() => setFilter('active')}
                className={`text-xs h-7 px-3 ${filter === 'active' ? 'bg-teal-700 hover:bg-teal-800 text-white' : ''}`}
              >
                Active ({activeCount})
              </Button>
              <Button
                size='sm'
                variant={filter === 'prescribed' ? 'default' : 'ghost'}
                onClick={() => setFilter('prescribed')}
                className={`text-xs h-7 px-3 ${filter === 'prescribed' ? 'bg-slate-800 dark:bg-slate-200 text-white dark:text-slate-900' : ''}`}
              >
                Historical ({medications.length - activeCount})
              </Button>
            </div>
            <Button size='sm' variant='outline' onClick={loadMedications} className='h-8 px-2.5'>
              <RefreshCw className='h-3.5 w-3.5' />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className='h-48 flex items-center justify-center'>
              <RefreshCw className='h-6 w-6 animate-spin text-teal-600' />
            </div>
          ) : filtered.length === 0 ? (
            <div className='text-center py-12 text-xs text-muted-foreground'>
              No medications matching selected filter.
            </div>
          ) : (
            <div className='overflow-x-auto'>
              <table className='w-full text-left text-sm'>
                <thead>
                  <tr className='border-b border-slate-100 dark:border-slate-800 text-xs font-semibold text-muted-foreground'>
                    <th className='pb-3'>Medication & Salt</th>
                    <th className='pb-3'>Dose Directions</th>
                    <th className='pb-3'>Frequency & Route</th>
                    <th className='pb-3'>Prescription Date</th>
                    <th className='pb-3'>Status</th>
                    <th className='pb-3 text-right'>Action</th>
                  </tr>
                </thead>
                <tbody className='divide-y divide-slate-100 dark:divide-slate-800'>
                  {filtered.map((med) => {
                    const isActive = med.medication_status === 'active'
                    return (
                      <tr key={med.id} className='hover:bg-slate-50/50 dark:hover:bg-slate-900/50'>
                        <td className='py-3.5'>
                          <div>
                            <span className='font-semibold text-slate-800 dark:text-slate-200 block'>
                              {med.medication_name}{' '}
                              {med.strength && (
                                <span className='text-xs text-muted-foreground font-normal'>
                                  ({med.strength})
                                </span>
                              )}
                            </span>
                            {med.generic_name && (
                              <span className='text-xs text-muted-foreground block'>
                                Active Salt: {med.generic_name}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className='py-3.5 text-xs text-slate-700 dark:text-slate-300'>
                          {med.dose_instructions || '—'}
                          {med.duration && (
                            <span className='block text-muted-foreground text-[11px]'>
                              Duration: {med.duration}
                            </span>
                          )}
                        </td>
                        <td className='py-3.5 text-xs text-muted-foreground'>
                          {med.frequency || 'Once daily'} • {med.route || 'oral'}
                        </td>
                        <td className='py-3.5 text-xs text-muted-foreground'>
                          {med.prescription_date || '—'}
                        </td>
                        <td className='py-3.5'>
                          <Badge
                            variant='outline'
                            className={
                              isActive
                                ? 'bg-teal-50 text-teal-700 border-teal-300 dark:bg-teal-950/40 dark:text-teal-400 dark:border-teal-800 text-xs'
                                : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 text-xs'
                            }
                          >
                            {isActive ? 'Confirmed Active' : 'Prescribed'}
                          </Badge>
                        </td>
                        <td className='py-3.5 text-right'>
                          <Button
                            size='sm'
                            variant={isActive ? 'outline' : 'default'}
                            onClick={() => handleToggleStatus(med.id, med.medication_status)}
                            className={`text-xs h-7 px-2.5 ${!isActive ? 'bg-teal-700 hover:bg-teal-800 text-white' : ''}`}
                          >
                            {isActive ? 'Mark Inactive' : 'Confirm Active'}
                          </Button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
