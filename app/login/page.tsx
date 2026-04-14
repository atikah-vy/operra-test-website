import { Metadata } from 'next'
import LoginForm from './LoginForm'

export const metadata: Metadata = {
  title: 'Sign in — Operra',
}

export default function LoginPage() {
  return (
    <div className="auth-page">
      <LoginForm />
    </div>
  )
}
