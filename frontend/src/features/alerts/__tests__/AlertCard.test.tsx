import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AlertCard } from '../components/AlertCard'

describe('AlertCard', () => {
  it('renders title, location and timestamp', () => {
    render(
      <AlertCard
        alert={{
          id: 'a1',
          title: 'Heavy Rainfall Warning',
          location: 'Eastern Trinidad',
          timestamp: 'May 21, 2025 8:30 AM',
          severity: 'warning',
        }}
      />,
    )
    expect(screen.getByText('Heavy Rainfall Warning')).toBeInTheDocument()
    expect(screen.getByText('Eastern Trinidad')).toBeInTheDocument()
    expect(screen.getByText('May 21, 2025 8:30 AM')).toBeInTheDocument()
  })
})
