/** Next.js config for Docker deployment */
module.exports = {
  reactStrictMode: true,
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.BACKEND_URL 
          ? `${process.env.BACKEND_URL}/api/:path*`
          : 'http://localhost:8000/api/:path*',
      },
      {
        source: '/ws/:path*',
        destination: process.env.BACKEND_URL 
          ? `${process.env.BACKEND_URL}/ws/:path*`
          : 'http://localhost:8000/ws/:path*',
      },
    ];
  },
}
