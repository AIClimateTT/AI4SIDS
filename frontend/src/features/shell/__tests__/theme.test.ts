import { describe, it, expect, beforeEach } from 'vitest'
import { getStoredTheme, setTheme, toggleTheme, initTheme } from '../theme'

beforeEach(() => {
  localStorage.clear()
  document.documentElement.classList.remove('dark')
})

describe('theme helpers', () => {
  it('defaults to light when nothing stored', () => {
    expect(getStoredTheme()).toBe('light')
  })

  it('setTheme persists and applies the dark class', () => {
    setTheme('dark')
    expect(localStorage.getItem('ai4sids_theme')).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('setTheme light removes the dark class', () => {
    setTheme('dark')
    setTheme('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('toggleTheme flips and returns the new value', () => {
    setTheme('light')
    expect(toggleTheme()).toBe('dark')
    expect(getStoredTheme()).toBe('dark')
  })

  it('initTheme applies the stored theme', () => {
    localStorage.setItem('ai4sids_theme', 'dark')
    expect(initTheme()).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})
