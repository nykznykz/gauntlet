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
  // Prevent aggressive CDN caching for pages that fetch API data
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=0, must-revalidate',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
