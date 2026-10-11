import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  ShieldCheck,
  Activity,
  Link,
  Unlink,
  CheckCircle2,
  AlertTriangle,
  Info,
  Server,
  KeyRound,
  RefreshCw,
} from 'lucide-react'
import { ABHAStatus, api } from '@/services/api'
import { toast } from 'sonner'

export function ABHASandbox() {
  const [status, setStatus] = useState<ABHAStatus | null>(null)
  const [abhaInput, setAbhaInput] = useState('MOCK-ABHA-0001')
  const [otpInput, setOtpInput] = useState('123456')
  const [step, setStep] = useState<'initial' | 'otp'>('initial')
  const [transactionId, setTransactionId] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadStatus()
  }, [])

  const loadStatus = async () => {
    try {
      setIsLoading(true)
      const data = await api.getABHAStatus()
      setStatus(data)
    } catch (err: any) {
      toast.error('Failed to load ABHA connection status.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleInitiateLink = async () => {
    if (!abhaInput.trim()) {
      toast.error('Please enter a mock ABHA identifier.')
      return
    }
    try {
      setIsLoading(true)
      const res = await api.linkABHA(abhaInput.trim())
      setTransactionId(res.transaction_id)
      setStep('otp')
      toast.info(res.message || 'Simulated OTP dispatched. Enter 123456 to verify.')
    } catch (err: any) {
      toast.error(err.message || 'Failed to initiate mock ABHA link.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerifyOtp = async () => {
    try {
      setIsLoading(true)
      const res = await api.verifyABHA(transactionId, otpInput.trim())
      if (res.success) {
        toast.success('Mock ABHA account verified and connected!')
        setStep('initial')
        loadStatus()
      } else {
        toast.error(res.message || 'Verification failed. Use OTP 123456 for demo.')
      }
    } catch (err: any) {
      toast.error(err.message || 'OTP verification failed.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRevoke = async () => {
    if (!confirm('Disconnect this mock ABHA account?')) return
    try {
      setIsLoading(true)
      await api.revokeABHA()
      toast.success('Mock ABHA link disconnected.')
      loadStatus()
    } catch (err: any) {
      toast.error(err.message || 'Failed to revoke link.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className='space-y-6'>
      {/* Explicit Simulation Warning Alert */}
      <div className='p-4 rounded-xl border border-purple-200 dark:border-purple-900 bg-purple-50/50 dark:bg-purple-950/20 text-purple-900 dark:text-purple-200 space-y-1.5'>
        <div className='flex items-center gap-2'>
          <Info className='h-4 w-4 text-purple-700 shrink-0' />
          <h4 className='text-xs font-bold uppercase tracking-wider'>
            Demonstration Mode: Visibly Simulated Sandbox Architecture
          </h4>
        </div>
        <p className='text-xs leading-relaxed'>
          This connection demonstrates the citizen-facing ABHA linking workflow using transparent mock identifiers
          (e.g., <strong>MOCK-ABHA-0001</strong>). No real 14-digit national identity records or government OTP portals
          are scraped or falsely claimed.
        </p>
      </div>

      {/* Main Connection Status Card */}
      <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
        <CardHeader>
          <div className='flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3'>
            <div>
              <CardTitle className='text-base font-semibold flex items-center gap-2'>
                <Activity className='h-5 w-5 text-purple-600' />
                ABDM / ABHA Linkage Status
              </CardTitle>
              <CardDescription className='text-xs'>
                Ayushman Bharat Digital Mission interoperability interface.
              </CardDescription>
            </div>
            <div className='flex items-center gap-2'>
              <Badge variant='outline' className='bg-background text-xs'>
                Provider: {status?.provider_mode || 'mock'}
              </Badge>
              <Badge
                variant='outline'
                className={
                  status?.is_linked
                    ? 'bg-teal-50 text-teal-700 border-teal-300 dark:bg-teal-950 dark:text-teal-300 text-xs'
                    : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 text-xs'
                }
              >
                {status?.is_linked ? 'Linked (Simulated)' : 'Not Linked'}
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className='space-y-6'>
          {status?.is_linked ? (
            <div className='p-4 rounded-xl border border-teal-200 dark:border-teal-900 bg-teal-50/30 dark:bg-teal-950/20 space-y-4'>
              <div className='flex flex-col sm:flex-row sm:items-center justify-between gap-3'>
                <div className='flex items-center gap-3'>
                  <div className='p-2.5 rounded-lg bg-teal-600 text-white'>
                    <CheckCircle2 className='h-5 w-5' />
                  </div>
                  <div>
                    <h5 className='text-sm font-semibold text-teal-900 dark:text-teal-200'>
                      Linked Mock ABHA ID: {status.external_reference}
                    </h5>
                    <p className='text-xs text-muted-foreground'>
                      Environment: {status.environment} • Verification: {status.verification_method}
                    </p>
                  </div>
                </div>
                <Button
                  size='sm'
                  variant='outline'
                  onClick={handleRevoke}
                  disabled={isLoading}
                  className='text-xs text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/30 border-red-200'
                >
                  <Unlink className='mr-1.5 h-3.5 w-3.5' /> Disconnect Link
                </Button>
              </div>
              <p className='text-xs text-slate-600 dark:text-slate-400'>
                Verified on {status.verified_at ? new Date(status.verified_at).toLocaleString() : 'Recent'}.
                All extracted observations and prescriptions are indexed against your internal patient UUID and mapped to
                FHIR R4 resources.
              </p>
            </div>
          ) : step === 'initial' ? (
            <div className='max-w-md space-y-4'>
              <div className='space-y-1.5'>
                <label className='text-xs font-semibold'>Mock ABHA Identifier</label>
                <Input
                  value={abhaInput}
                  onChange={(e) => setAbhaInput(e.target.value)}
                  placeholder='MOCK-ABHA-0001'
                  className='text-xs h-9'
                />
                <p className='text-[11px] text-muted-foreground'>
                  Use synthetic identifiers like <code>MOCK-ABHA-0001</code> for test verification.
                </p>
              </div>
              <Button
                size='sm'
                onClick={handleInitiateLink}
                disabled={isLoading}
                className='bg-teal-700 hover:bg-teal-800 text-white text-xs h-8'
              >
                <Link className='mr-1.5 h-3.5 w-3.5' /> Link Mock ABHA
              </Button>
            </div>
          ) : (
            <div className='max-w-md space-y-4 p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50'>
              <div className='space-y-1.5'>
                <div className='flex items-center gap-2'>
                  <KeyRound className='h-4 w-4 text-teal-600' />
                  <label className='text-xs font-semibold'>Enter Simulated OTP</label>
                </div>
                <Input
                  value={otpInput}
                  onChange={(e) => setOtpInput(e.target.value)}
                  placeholder='123456'
                  className='text-xs h-9 tracking-widest font-mono'
                />
                <p className='text-[11px] text-teal-700 dark:text-teal-400 font-medium'>
                  Mock OTP dispatched. Enter <strong>123456</strong> to complete simulated verification.
                </p>
              </div>
              <div className='flex items-center gap-2'>
                <Button
                  size='sm'
                  onClick={handleVerifyOtp}
                  disabled={isLoading}
                  className='bg-teal-700 hover:bg-teal-800 text-white text-xs h-8'
                >
                  Confirm & Link
                </Button>
                <Button
                  size='sm'
                  variant='ghost'
                  onClick={() => setStep('initial')}
                  className='text-xs h-8'
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Roadmap to Genuine ABDM Gateway Sandbox */}
      <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
        <CardHeader>
          <CardTitle className='text-sm font-semibold flex items-center gap-2'>
            <Server className='h-4 w-4 text-teal-600' />
            Path to Official ABDM Sandbox Integration
          </CardTitle>
          <CardDescription className='text-xs'>
            Technical implementation readiness across ABDM milestones.
          </CardDescription>
        </CardHeader>
        <CardContent className='space-y-3 text-xs'>
          <div className='grid gap-3 sm:grid-cols-3'>
            <div className='p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 space-y-1'>
              <Badge variant='outline' className='text-[10px] bg-background'>
                Milestone M1
              </Badge>
              <p className='font-semibold'>ABHA Creation & Linking</p>
              <p className='text-muted-foreground text-[11px] leading-relaxed'>
                Pluggable <code>LiveABDMProvider</code> adapter ready for NHA OTP generation and X-Token session management.
              </p>
            </div>
            <div className='p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 space-y-1'>
              <Badge variant='outline' className='text-[10px] bg-background'>
                Milestone M2
              </Badge>
              <p className='font-semibold'>Consent Manager Flow</p>
              <p className='text-muted-foreground text-[11px] leading-relaxed'>
                Database schema includes <code>consent_records</code> with purpose, scope, and auto-expiry timestamps.
              </p>
            </div>
            <div className='p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 space-y-1'>
              <Badge variant='outline' className='text-[10px] bg-background'>
                Milestone M3
              </Badge>
              <p className='font-semibold'>FHIR R4 Data Transfer</p>
              <p className='text-muted-foreground text-[11px] leading-relaxed'>
                Extracted records stored as standard <code>DiagnosticReport</code>, <code>Observation</code>, and <code>MedicationRequest</code>.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
