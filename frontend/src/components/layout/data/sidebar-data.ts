import {
  LayoutDashboard,
  FileText,
  CheckSquare,
  Sparkles,
  Calendar,
  Pill,
  Activity,
  ShieldCheck,
  User,
  Settings,
  HeartPulse,
} from 'lucide-react'
import { type SidebarData } from '../types'

export const sidebarData: SidebarData = {
  user: {
    name: 'Ananya Sharma',
    email: 'ananya.sharma@example.internal',
    avatar: '',
  },
  teams: [
    {
      name: 'Personal Health Copilot',
      logo: HeartPulse,
      plan: 'Altrix Labs Prototype',
    },
  ],
  navGroups: [
    {
      title: 'Clinical Care Portal',
      items: [
        {
          title: 'Health Dashboard',
          url: '/',
          icon: LayoutDashboard,
        },
        {
          title: 'Medical Documents',
          url: '/',
          icon: FileText,
        },
        {
          title: 'Extraction Review',
          url: '/',
          icon: CheckSquare,
        },
        {
          title: 'Bilingual Summaries',
          url: '/',
          icon: Sparkles,
        },
        {
          title: 'Timeline & Trends',
          url: '/',
          icon: Calendar,
        },
        {
          title: 'Medication Regimen',
          url: '/',
          icon: Pill,
        },
        {
          title: 'ABDM / ABHA Sandbox',
          url: '/',
          icon: Activity,
        },
      ],
    },
    {
      title: 'Standards & Security',
      items: [
        {
          title: 'FHIR R4 Schema',
          url: '/',
          icon: ShieldCheck,
        },
        {
          title: 'Patient Profile',
          url: '/',
          icon: User,
        },
      ],
    },
  ],
}
