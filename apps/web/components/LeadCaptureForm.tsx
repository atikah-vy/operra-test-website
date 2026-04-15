'use client'

import { useState } from 'react'

interface FormState {
  status: 'idle' | 'submitting' | 'success' | 'error'
  message?: string
}

export default function LeadCaptureForm() {
  const [state, setState] = useState<FormState>({ status: 'idle' })

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setState({ status: 'submitting' })
    const data = Object.fromEntries(new FormData(e.currentTarget).entries())

    try {
      const res = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(data)
      })

      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error((body as { error?: string }).error ?? 'Submission failed')
      }

      setState({ status: 'success', message: 'Thanks — we’ll be in touch shortly.' })
      e.currentTarget.reset()
    } catch (err) {
      setState({
        status: 'error',
        message: err instanceof Error ? err.message : 'Something went wrong.'
      })
    }
  }

  return (
    <form
      onSubmit={onSubmit}
      style={{
        display: 'grid',
        gap: '0.75rem',
        maxWidth: 480,
        margin: '0 auto',
        textAlign: 'left'
      }}
    >
      <input
        name="firstName"
        placeholder="First name"
        required
        style={inputStyle}
      />
      <input
        name="email"
        type="email"
        placeholder="Work email"
        required
        style={inputStyle}
      />
      <input
        name="company"
        placeholder="Company (optional)"
        style={inputStyle}
      />
      <textarea
        name="message"
        placeholder="What are you hoping to solve?"
        rows={3}
        style={{ ...inputStyle, resize: 'vertical' as const }}
      />
      <input type="hidden" name="source" value="marketing-site" />
      <button
        type="submit"
        className="btn btn-primary btn-lg"
        disabled={state.status === 'submitting'}
      >
        {state.status === 'submitting' ? 'Sending…' : 'Request a Demo →'}
      </button>
      {state.message ? (
        <p
          style={{
            fontSize: '0.85rem',
            color: state.status === 'error' ? 'var(--danger)' : 'var(--success)',
            marginTop: '0.25rem'
          }}
        >
          {state.message}
        </p>
      ) : null}
    </form>
  )
}

const inputStyle: React.CSSProperties = {
  padding: '0.75rem 1rem',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius)',
  fontSize: '0.95rem',
  fontFamily: 'inherit',
  background: 'var(--bg-card)',
  color: 'var(--text-primary)',
  width: '100%'
}
