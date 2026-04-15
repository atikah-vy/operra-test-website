import type { Metadata } from "next"
import { ClerkProvider } from "@clerk/nextjs"
import "@operra/ui/styles.css"
import "./globals.css"

export const metadata: Metadata = {
  title: "Operra — One System. Total Control.",
  description:
    "Operra brings your entire business operation into one intelligent platform — CRM, leads, invoicing, bookings, and analytics, unified from day one."
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <head>
          <link rel="preconnect" href="https://fonts.googleapis.com" />
          <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
          <link
            href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
            rel="stylesheet"
          />
        </head>
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}
