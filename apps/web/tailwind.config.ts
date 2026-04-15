import type { Config } from "tailwindcss"
import { baseConfig } from "@operra/tailwind-config"

const config: Config = {
  ...baseConfig,
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "../../packages/ui/src/**/*.{ts,tsx}"
  ]
}

export default config
