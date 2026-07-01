import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ComingSoonPage } from '../ComingSoonPage'

describe('ComingSoonPage', () => {
  it('shows the title and a coming-soon note', () => {
    render(<ComingSoonPage title="Settings" />)
    expect(screen.getByText('Settings')).toBeInTheDocument()
    expect(screen.getByText(/coming soon/i)).toBeInTheDocument()
  })
})
