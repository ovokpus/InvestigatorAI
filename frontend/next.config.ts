import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // App Router is enabled by default in Next.js 15
  
  // Optimize for Vercel deployment
  trailingSlash: false,
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  
  // Enable experimental features for better performance
  experimental: {
    optimizePackageImports: ['@/components', '@/utils'],
  },
};

export default nextConfig;
