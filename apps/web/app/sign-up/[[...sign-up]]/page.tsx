import { SignUp } from "@clerk/nextjs"
import Link from "next/link"

const clerkAppearance = {
  variables: {
    colorPrimary: "#3B82F6",
    colorBackground: "#FFFFFF",
    colorText: "#0F172A",
    colorTextSecondary: "#64748B",
    colorInputBackground: "#FFFFFF",
    colorInputText: "#0F172A",
    borderRadius: "10px",
    fontFamily: "Inter, sans-serif",
    fontSize: "15px",
  },
  elements: {
    rootBox: "w-full",
    card: "shadow-none border-0 rounded-none bg-transparent p-0 gap-6",
    cardBox: "shadow-none border-0 w-full",
    header: "text-left px-0 pb-2",
    headerTitle: "text-2xl font-bold text-[#0F172A] text-left",
    headerSubtitle: "text-[#64748B] text-sm text-left mt-1",
    socialButtonsBlockButton:
      "border border-[#E2E8F0] bg-white text-[#0F172A] hover:bg-[#F1F5F9] rounded-[10px] font-medium h-11 transition-colors",
    socialButtonsBlockButtonText: "font-medium text-[#0F172A]",
    dividerRow: "my-2",
    dividerLine: "bg-[#E2E8F0]",
    dividerText: "text-[#64748B] text-xs px-3",
    formFieldRow: "gap-1.5",
    formFieldLabel: "text-sm font-medium text-[#0F172A]",
    formFieldInput:
      "border border-[#E2E8F0] bg-white rounded-[10px] text-[#0F172A] placeholder:text-[#94A3B8] h-11 px-3 focus:ring-2 focus:ring-[#3B82F6] focus:border-[#3B82F6] transition-colors",
    formButtonPrimary:
      "bg-[#3B82F6] hover:bg-[#2563EB] active:bg-[#1D4ED8] text-white font-semibold rounded-[10px] h-11 transition-colors shadow-none",
    footerAction: "mt-4",
    footerActionText: "text-[#64748B] text-sm",
    footerActionLink: "text-[#3B82F6] hover:text-[#2563EB] font-semibold",
    footer: "hidden",
    identityPreviewText: "text-[#0F172A]",
    identityPreviewEditButton: "text-[#3B82F6]",
    formFieldErrorText: "text-[#EF4444] text-xs mt-1",
    alert: "rounded-[10px] border border-[#FCA5A5] bg-[#FEF2F2]",
    alertText: "text-[#EF4444] text-sm",
    badge: "hidden",
    providerIcon__google: "w-5 h-5",
    socialButtonsBlockButtonArrow: "hidden",
  },
}

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-[#0B1F3A] px-14 py-12">
        <div>
          <span className="text-xl font-bold tracking-widest text-white uppercase">
            Operra
          </span>
        </div>

        <div className="space-y-5">
          <h2 className="text-[2.6rem] font-bold leading-tight text-white">
            Get started.<br />
            One system for<br />
            your entire business.
          </h2>
          <p className="text-[#60A5FA] text-sm font-medium tracking-wide">
            CRM · Leads · Invoicing · Bookings · Analytics
          </p>
        </div>

        <Link
          href="/"
          className="flex items-center gap-1.5 text-sm text-[#60A5FA] hover:text-white transition-colors w-fit"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5M5 12l7-7M5 12l7 7" />
          </svg>
          Back to home
        </Link>
      </div>

      {/* Right panel */}
      <div className="flex w-full lg:w-1/2 flex-col items-center justify-center bg-white px-8 py-12 overflow-hidden">
        <div className="w-full max-w-[400px] overflow-hidden">

          {/* Mobile logo */}
          <div className="mb-8 lg:hidden text-center">
            <span className="text-xl font-bold tracking-widest text-[#0B1F3A] uppercase">
              Operra
            </span>
          </div>

          <SignUp
            appearance={clerkAppearance}
            afterSignUpUrl="/dashboard"
            signInUrl="/sign-in"
          />

          {/* Mobile back link */}
          <div className="mt-6 text-center lg:hidden">
            <Link
              href="/"
              className="inline-flex items-center gap-1.5 text-sm text-[#64748B] hover:text-[#0B1F3A] transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 12H5M5 12l7-7M5 12l7 7" />
              </svg>
              Back to home
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
