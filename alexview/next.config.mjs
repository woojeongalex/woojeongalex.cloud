/** @type {import('next').NextConfig} */
const nextConfig = {
  compress: false,
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
}

export default nextConfig
