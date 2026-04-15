"use client"

import * as React from "react"
import { Button } from "./button"

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: (error: Error, reset: () => void) => React.ReactNode
}

interface ErrorBoundaryState {
  error: Error | null
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error("ErrorBoundary:", error, info)
  }

  reset = () => this.setState({ error: null })

  render() {
    if (this.state.error) {
      if (this.props.fallback) return this.props.fallback(this.state.error, this.reset)
      return (
        <div className="flex flex-col items-center justify-center rounded-lg border border-red-200 bg-red-50 p-6 text-center">
          <h3 className="text-base font-semibold text-red-700">Something went wrong</h3>
          <p className="mt-1 text-sm text-red-600">{this.state.error.message}</p>
          <Button onClick={this.reset} variant="outline" size="sm" className="mt-4">
            Try again
          </Button>
        </div>
      )
    }
    return this.props.children
  }
}
