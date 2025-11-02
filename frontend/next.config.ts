import type { NextConfig } from "next";
import type { Configuration } from 'webpack';

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
  // Force all chunks to have unique hashes to bust Railway CDN cache
  webpack: (config: Configuration, { isServer }) => {
    if (!isServer && config.output) {
      const timestamp = Date.now();
      config.output.filename = `static/chunks/[name]-${timestamp}.js`;
      config.output.chunkFilename = `static/chunks/[name]-${timestamp}.js`;
    }
    return config;
  },
};

export default nextConfig;
