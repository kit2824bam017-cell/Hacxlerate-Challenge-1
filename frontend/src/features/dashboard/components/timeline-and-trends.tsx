import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Calendar,
  TrendingUp,
  FileText,
  Pill,
  Activity,
  Layers,
  Filter,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceArea,
  Legend,
} from 'recharts'
import { TimelineEventItem, ObservationTrend, api } from '@/services/api'
import { toast } from 'sonner'

export function TimelineAndTrends() {
  const [events, setEvents] = useState<TimelineEventItem[]>([])
  const [trends, setTrends] = useState<ObservationTrend[]>([])
  const [activeCategory, setActiveCategory] = useState<string>('all')
  const [selectedTrendIndex, setSelectedTrendIndex] = useState<number>(0)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadTimelineAndTrends()
  }, [])

  const loadTimelineAndTrends = async () => {
    try {
      setIsLoading(true)
      const [tlData, trendData] = await Promise.all([
        api.getTimeline(),
        api.getObservationTrends(),
      ])
      setEvents(tlData.events || [])
      setTrends(trendData || [])
    } catch (err: any) {
      toast.error('Failed to load timeline or trend data.')
    } finally {
      setIsLoading(false)
    }
  }

  const filteredEvents =
    activeCategory === 'all'
      ? events
      : events.filter((e) => e.category.toLowerCase() === activeCategory.toLowerCase())

  const activeTrend = trends[selectedTrendIndex]

  return (
    <div className='space-y-6'>
      {/* Trends Section */}
      <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
        <CardHeader className='flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4'>
          <div>
            <CardTitle className='text-base font-semibold flex items-center gap-2'>
              <TrendingUp className='h-5 w-5 text-teal-600' />
              Longitudinal Biomarker Analysis
            </CardTitle>
            <CardDescription className='text-xs'>
              Historical measurements compared over time using strictly identical units and laboratory intervals.
            </CardDescription>
          </div>
          {trends.length > 0 && (
            <div className='flex items-center gap-2 overflow-x-auto'>
              {trends.map((t, idx) => (
                <Button
                  key={t.test_name}
                  size='sm'
                  variant={selectedTrendIndex === idx ? 'default' : 'outline'}
                  onClick={() => setSelectedTrendIndex(idx)}
                  className={`text-xs h-7 px-2.5 ${selectedTrendIndex === idx ? 'bg-teal-700 hover:bg-teal-800 text-white' : ''}`}
                >
                  {t.test_name}
                </Button>
              ))}
            </div>
          )}
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className='h-64 flex items-center justify-center'>
              <RefreshCw className='h-6 w-6 animate-spin text-teal-600' />
            </div>
          ) : activeTrend ? (
            <div className='space-y-4'>
              <div className='flex items-center justify-between text-xs text-muted-foreground p-3 rounded-lg bg-slate-50 dark:bg-slate-900'>
                <span>
                  Analyzed Biomarker: <strong>{activeTrend.test_name}</strong>
                </span>
                <span>
                  Measurement Unit: <strong>{activeTrend.unit}</strong>
                </span>
                <span>
                  Normal Reference Interval:{' '}
                  <strong>
                    {activeTrend.reference_low ?? '—'} - {activeTrend.reference_high ?? '—'} {activeTrend.unit}
                  </strong>
                </span>
              </div>
              <div className='h-64 w-full'>
                <ResponsiveContainer width='100%' height='100%'>
                  <LineChart data={activeTrend.history} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray='3 3' stroke='#e2e8f0' opacity={0.6} />
                    <XAxis dataKey='date' stroke='#64748b' fontSize={12} />
                    <YAxis
                      domain={[
                        (dataMin: number) => Math.max(0, Math.floor(dataMin * 0.8)),
                        (dataMax: number) => Math.ceil(dataMax * 1.2),
                      ]}
                      stroke='#64748b'
                      fontSize={12}
                    />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload
                          return (
                            <div className='p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-background shadow-md text-xs space-y-1'>
                              <p className='font-semibold'>{data.date}</p>
                              <p className='text-teal-600 font-bold'>
                                Value: {data.value} {data.unit}
                              </p>
                              <p className='text-muted-foreground'>
                                Range: {data.reference_low} - {data.reference_high} {data.unit}
                              </p>
                            </div>
                          )
                        }
                        return null
                      }}
                    />
                    <Legend />
                    <Line
                      type='monotone'
                      dataKey='value'
                      name={`${activeTrend.test_name} (${activeTrend.unit})`}
                      stroke='#0d9488'
                      strokeWidth={2.5}
                      dot={{ r: 5, fill: '#0d9488' }}
                      activeDot={{ r: 7 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          ) : (
            <div className='h-48 flex items-center justify-center text-xs text-muted-foreground'>
              No comparable longitudinal observations recorded yet.
            </div>
          )}
        </CardContent>
      </Card>

      {/* Chronological Timeline Section */}
      <Card className='border-slate-200 dark:border-slate-800 shadow-xs'>
        <CardHeader className='flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4'>
          <div>
            <CardTitle className='text-base font-semibold flex items-center gap-2'>
              <Calendar className='h-5 w-5 text-teal-600' />
              Chronological Health Timeline
            </CardTitle>
            <CardDescription className='text-xs'>
              Unified historical trajectory linking every lab report, prescription, and integration event.
            </CardDescription>
          </div>
          <div className='flex items-center gap-1.5'>
            {['all', 'Diagnostic', 'Medication', 'Integration'].map((cat) => (
              <Button
                key={cat}
                size='sm'
                variant={activeCategory === cat ? 'default' : 'ghost'}
                onClick={() => setActiveCategory(cat)}
                className={`text-xs h-7 capitalize ${activeCategory === cat ? 'bg-slate-800 dark:bg-slate-200 text-white dark:text-slate-900' : ''}`}
              >
                {cat}
              </Button>
            ))}
          </div>
        </CardHeader>
        <CardContent>
          <div className='relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800'>
            {filteredEvents.map((event) => {
              const isDiag = event.category === 'Diagnostic'
              const isMed = event.category === 'Medication'
              const isInt = event.category === 'Integration'
              return (
                <div key={event.id} className='relative group'>
                  {/* Dot */}
                  <div
                    className={`absolute -left-6 top-1 h-3.5 w-3.5 rounded-full border-2 border-background ${
                      isDiag ? 'bg-teal-600' : isMed ? 'bg-blue-600' : 'bg-purple-600'
                    }`}
                  />
                  <div className='p-3.5 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 space-y-1.5'>
                    <div className='flex items-center justify-between gap-2'>
                      <div className='flex items-center gap-2'>
                        <span className='font-semibold text-sm'>{event.title}</span>
                        <Badge variant='outline' className='text-[10px] uppercase tracking-wider'>
                          {event.category}
                        </Badge>
                      </div>
                      <span className='text-xs text-muted-foreground'>
                        {new Date(event.event_date).toLocaleDateString(undefined, {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </span>
                    </div>
                    <p className='text-xs text-slate-700 dark:text-slate-300 leading-relaxed'>
                      {event.description}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
