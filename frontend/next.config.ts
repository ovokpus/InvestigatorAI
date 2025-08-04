import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // App Router is enabled by default in Next.js 15
  
  // Enable standalone output for Docker optimization
  output: 'standalone',
  
  // Configure for production deployment
  trailingSlash: false,
};

export default nextConfig;
