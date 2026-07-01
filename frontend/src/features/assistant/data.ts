export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
  bullets?: string[]
  time: string
}

export const INITIAL_TRANSCRIPT: ChatMessage[] = [
  {
    id: 'm1',
    role: 'user',
    text: 'What should local authorities do if heavy rainfall is forecast for the next 24 hours?',
    time: '10:31 AM',
  },
  {
    id: 'm2',
    role: 'assistant',
    text: 'Based on the current forecast and risk assessment, here are the recommended actions:',
    bullets: [
      'Monitor rainfall and river levels closely',
      'Inspect and clear drainage systems',
      'Ensure shelters are prepared and supplies are stocked',
      'Alert vulnerable communities and review evacuation plans',
      'Coordinate with ODPM and regional corporations',
    ],
    time: '10:31 AM',
  },
]

export const SUGGESTED_PROMPTS: string[] = [
  'Which areas are most at risk right now?',
  'Summarise the latest flood watch',
  'What supplies should shelters stock?',
]
