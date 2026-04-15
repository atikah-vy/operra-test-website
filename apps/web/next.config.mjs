/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@operra/ui", "@operra/config"],
  experimental: {
    optimizePackageImports: ["lucide-react"]
  }
}

export default nextConfig
