import { Metadata } from 'next'
import SignupForm from './SignupForm'

export const metadata: Metadata = {
  title: 'Create account — Operra',
}

export default function SignupPage() {
  return <SignupForm />
}
