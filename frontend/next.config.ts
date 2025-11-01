import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    domains: [],
  },
  // Force new build ID to clear Railway CDN cache
  generateBuildId: async () => {
    return `build-${Date.now()}`;
  },
};

export default nextConfig;
