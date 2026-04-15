"use client"

import { Button } from "@operra/ui/button"

export default function DashboardError({
  error,
  reset
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center rounded-lg border border-red-200 bg-red-50 p-6 text-center">
      <h2 className="text-lg font-semibold text-red-700">Something went wrong</h2>
      <p className="mt-1 max-w-md text-sm text-red-600">{error.message}</p>
      <Button onClick={reset} variant="outline" className="mt-4">
        Try again
      </Button>
    </div>
  )
}
