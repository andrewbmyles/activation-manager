# Deployment and Build Guide

## Table of Contents
1. [Build Process Overview](#build-process-overview)
2. [Development Environment](#development-environment)
3. [Production Build](#production-build)
4. [Environment Configuration](#environment-configuration)
5. [Deployment Platforms](#deployment-platforms)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Performance Optimization](#performance-optimization)
8. [Monitoring and Analytics](#monitoring-and-analytics)
9. [Security Configuration](#security-configuration)
10. [Troubleshooting](#troubleshooting)

## Build Process Overview

The Activation Manager uses Create React App (CRA) as the build system, providing optimized production builds with minimal configuration.

### Build Architecture
```
Source Code → TypeScript Compilation → Bundle Optimization → Static Assets → Deployment
```

### Key Features
- **TypeScript Compilation**: Full type checking and transpilation
- **Code Splitting**: Automatic route-based and component-based splitting
- **Bundle Optimization**: Minification, tree shaking, and compression
- **Asset Optimization**: Image compression and font optimization
- **Cache Optimization**: Long-term caching with content hashing

## Development Environment

### Prerequisites
```bash
# Node.js version
node --version  # v18.0.0 or higher
npm --version   # v9.0.0 or higher

# Alternative: yarn
yarn --version  # v1.22.0 or higher
```

### Development Setup
```bash
# Clone repository
git clone https://github.com/andrewbmyles/activation-manager.git
cd activation-manager

# Install dependencies
npm install

# Start development server
npm start

# Development server will run on:
# Local:            http://localhost:3000
# On Your Network:  http://192.168.x.x:3000
```

### Development Scripts
```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "test:coverage": "react-scripts test --coverage --watchAll=false",
    "test:ci": "CI=true react-scripts test --coverage --watchAll=false",
    "eject": "react-scripts eject",
    "lint": "eslint src --ext .ts,.tsx --fix",
    "type-check": "tsc --noEmit",
    "analyze": "npm run build && npx serve -s build"
  }
}
```

### Development Configuration
```typescript
// src/config/development.ts
export const developmentConfig = {
  API_BASE_URL: 'http://localhost:3001/api',
  MOCK_API: true,
  DEBUG_MODE: true,
  LOG_LEVEL: 'debug',
  HOT_RELOAD: true,
  SOURCE_MAPS: true,
};
```

## Production Build

### Build Command
```bash
# Create production build
npm run build

# Build output
Creating an optimized production build...
Compiled successfully.

File sizes after gzip:
  220.01 kB  build/static/js/main.[hash].js
  5.16 kB    build/static/css/main.[hash].css
  1.79 kB    build/static/js/[hash].chunk.js

The build folder is ready to be deployed.
```

### Build Output Structure
```
build/
├── static/
│   ├── css/
│   │   ├── main.[hash].css
│   │   └── main.[hash].css.map
│   ├── js/
│   │   ├── main.[hash].js
│   │   ├── main.[hash].js.map
│   │   ├── [chunk].[hash].chunk.js
│   │   └── runtime-main.[hash].js
│   └── media/
│       ├── logo.[hash].svg
│       └── headshot.[hash].jpg
├── index.html
├── manifest.json
├── robots.txt
└── favicon.ico
```

### Build Analysis
```bash
# Bundle analyzer
npm install -g webpack-bundle-analyzer
npx webpack-bundle-analyzer build/static/js/*.js

# Alternative: source-map-explorer
npm install -g source-map-explorer
npx source-map-explorer 'build/static/js/*.js'
```

### Build Optimization
```javascript
// public/index.html optimizations
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#2563eb" />
  <meta name="description" content="Activation Manager - Audience Distribution Platform" />
  
  <!-- Preload critical resources -->
  <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin />
  
  <!-- DNS prefetch for external domains -->
  <link rel="dns-prefetch" href="//fonts.googleapis.com" />
  
  <!-- Critical CSS inlined -->
  <style>
    /* Critical above-the-fold styles */
    body { margin: 0; font-family: Inter, sans-serif; }
    .loading { display: flex; align-items: center; justify-content: center; height: 100vh; }
  </style>
  
  <title>Activation Manager</title>
</head>
<body>
  <noscript>You need to enable JavaScript to run this app.</noscript>
  <div id="root">
    <div class="loading">Loading...</div>
  </div>
</body>
</html>
```

## Environment Configuration

### Environment Variables
```bash
# .env.production
REACT_APP_ENV=production
REACT_APP_API_BASE_URL=https://api.activationmanager.com
REACT_APP_SENTRY_DSN=your_sentry_dsn
REACT_APP_GOOGLE_ANALYTICS_ID=GA_TRACKING_ID
REACT_APP_VERSION=$npm_package_version
GENERATE_SOURCEMAP=false

# .env.staging
REACT_APP_ENV=staging
REACT_APP_API_BASE_URL=https://api-staging.activationmanager.com
REACT_APP_SENTRY_DSN=your_staging_sentry_dsn
GENERATE_SOURCEMAP=true

# .env.development (default)
REACT_APP_ENV=development
REACT_APP_API_BASE_URL=http://localhost:3001/api
REACT_APP_MOCK_API=true
GENERATE_SOURCEMAP=true
```

### Configuration Management
```typescript
// src/config/index.ts
interface AppConfig {
  env: 'development' | 'staging' | 'production';
  apiBaseUrl: string;
  mockApi: boolean;
  version: string;
  sentryDsn?: string;
  googleAnalyticsId?: string;
}

export const config: AppConfig = {
  env: (process.env.REACT_APP_ENV as any) || 'development',
  apiBaseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:3001/api',
  mockApi: process.env.REACT_APP_MOCK_API === 'true',
  version: process.env.REACT_APP_VERSION || '1.0.0',
  sentryDsn: process.env.REACT_APP_SENTRY_DSN,
  googleAnalyticsId: process.env.REACT_APP_GOOGLE_ANALYTICS_ID,
};

// Environment-specific configurations
export const isDevelopment = config.env === 'development';
export const isProduction = config.env === 'production';
export const isStaging = config.env === 'staging';
```

## Deployment Platforms

### Vercel Deployment (Recommended)

#### Setup
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

#### vercel.json Configuration
```json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

#### Environment Variables in Vercel
```bash
# Set environment variables
vercel env add REACT_APP_API_BASE_URL production
vercel env add REACT_APP_SENTRY_DSN production

# List environment variables
vercel env ls
```

### Netlify Deployment

#### netlify.toml Configuration
```toml
[build]
  publish = "build"
  command = "npm run build"

[build.environment]
  NODE_VERSION = "18"
  NPM_VERSION = "9"

[[redirects]]
  from = "/api/*"
  to = "https://api.activationmanager.com/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

### AWS S3 + CloudFront Deployment

#### Build and Deploy Script
```bash
#!/bin/bash
# deploy-aws.sh

# Build the application
npm run build

# Sync to S3 bucket
aws s3 sync build/ s3://activation-manager-prod \
  --delete \
  --cache-control "public, max-age=31536000" \
  --exclude "*.html" \
  --exclude "service-worker.js"

# Upload HTML files with no-cache
aws s3 sync build/ s3://activation-manager-prod \
  --cache-control "no-cache" \
  --include "*.html" \
  --include "service-worker.js"

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"

echo "Deployment complete!"
```

#### CloudFront Configuration
```json
{
  "Origins": [
    {
      "Id": "S3-activation-manager",
      "DomainName": "activation-manager-prod.s3.amazonaws.com",
      "S3OriginConfig": {
        "OriginAccessIdentity": "origin-access-identity/cloudfront/YOUR_OAI_ID"
      }
    }
  ],
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-activation-manager",
    "ViewerProtocolPolicy": "redirect-to-https",
    "Compress": true,
    "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
  },
  "CustomErrorResponses": [
    {
      "ErrorCode": 404,
      "ResponseCode": 200,
      "ResponsePagePath": "/index.html"
    }
  ]
}
```

### GitHub Pages Deployment

#### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
      
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Build
      run: npm run build
      env:
        REACT_APP_API_BASE_URL: ${{ secrets.API_BASE_URL }}
        
    - name: Deploy
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./build
```

## CI/CD Pipeline

### GitHub Actions Complete Workflow
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Type check
      run: npm run type-check
      
    - name: Lint
      run: npm run lint
      
    - name: Test
      run: npm run test:ci
      
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      
  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Build
      run: npm run build
      env:
        REACT_APP_ENV: production
        REACT_APP_API_BASE_URL: ${{ secrets.API_BASE_URL }}
        
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: build-files
        path: build/
        
  deploy-staging:
    if: github.ref == 'refs/heads/develop'
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - name: Deploy to staging
      run: |
        # Deploy to staging environment
        echo "Deploying to staging..."
        
  deploy-production:
    if: github.ref == 'refs/heads/main'
    needs: build
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - name: Deploy to production
      run: |
        # Deploy to production environment
        echo "Deploying to production..."
```

### Quality Gates
```yaml
# Quality gate configuration
quality_gates:
  - name: "Test Coverage"
    threshold: 80
    metric: "coverage"
    
  - name: "TypeScript Errors"
    threshold: 0
    metric: "typescript_errors"
    
  - name: "ESLint Errors"
    threshold: 0
    metric: "eslint_errors"
    
  - name: "Bundle Size"
    threshold: 250
    metric: "bundle_size_kb"
```

## Performance Optimization

### Build Optimization
```typescript
// webpack.config.js (if ejected)
const path = require('path');

module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true,
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
};
```

### Code Splitting Implementation
```typescript
// Lazy loading for routes
const Dashboard = lazy(() => import('./pages/Dashboard'));
const AudienceBuilder = lazy(() => import('./pages/AudienceBuilder'));
const PlatformManagement = lazy(() => import('./pages/PlatformManagement'));

// Preloading for better UX
const preloadAudienceBuilder = () => {
  import('./pages/AudienceBuilder');
};

// Component-level code splitting
const HeavyComponent = lazy(() => import('./components/HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/audiences" element={<AudienceBuilder />} />
        <Route path="/platforms" element={<PlatformManagement />} />
      </Routes>
    </Suspense>
  );
}
```

### Asset Optimization
```typescript
// Image optimization
const OptimizedImage = ({ src, alt, ...props }) => {
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      decoding="async"
      {...props}
    />
  );
};

// Font optimization
// In public/index.html
<link
  rel="preload"
  href="/fonts/inter-var.woff2"
  as="font"
  type="font/woff2"
  crossOrigin=""
/>
```

## Monitoring and Analytics

### Error Monitoring with Sentry
```typescript
// src/lib/sentry.ts
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  environment: process.env.REACT_APP_ENV,
  integrations: [
    new BrowserTracing(),
  ],
  tracesSampleRate: 0.1,
  beforeSend(event) {
    // Filter out development errors
    if (process.env.NODE_ENV === 'development') {
      return null;
    }
    return event;
  },
});

// Error boundary with Sentry
export const SentryErrorBoundary = Sentry.withErrorBoundary(App, {
  fallback: ErrorFallback,
  beforeCapture: (scope) => {
    scope.setTag('errorBoundary', true);
  },
});
```

### Analytics Implementation
```typescript
// src/lib/analytics.ts
import { config } from '../config';

class Analytics {
  private initialized = false;

  init() {
    if (this.initialized || !config.googleAnalyticsId) return;
    
    // Load Google Analytics
    const script = document.createElement('script');
    script.src = `https://www.googletagmanager.com/gtag/js?id=${config.googleAnalyticsId}`;
    document.head.appendChild(script);
    
    window.gtag = function() {
      (window as any).dataLayer = (window as any).dataLayer || [];
      (window as any).dataLayer.push(arguments);
    };
    
    window.gtag('js', new Date());
    window.gtag('config', config.googleAnalyticsId);
    
    this.initialized = true;
  }
  
  track(event: string, properties?: Record<string, any>) {
    if (!this.initialized) return;
    
    window.gtag('event', event, properties);
  }
}

export const analytics = new Analytics();
```

### Performance Monitoring
```typescript
// src/lib/performance.ts
export function measurePerformance() {
  // Web Vitals
  import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
    getCLS(console.log);
    getFID(console.log);
    getFCP(console.log);
    getLCP(console.log);
    getTTFB(console.log);
  });
  
  // Custom performance marks
  performance.mark('app-start');
  
  window.addEventListener('load', () => {
    performance.mark('app-loaded');
    performance.measure('app-load-time', 'app-start', 'app-loaded');
    
    const measure = performance.getEntriesByName('app-load-time')[0];
    console.log('App load time:', measure.duration);
  });
}
```

## Security Configuration

### Content Security Policy
```html
<!-- In public/index.html -->
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://www.googletagmanager.com;
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  font-src 'self' https://fonts.gstatic.com;
  img-src 'self' data: https:;
  connect-src 'self' https://api.activationmanager.com;
">
```

### Security Headers
```typescript
// For server-side frameworks
export const securityHeaders = {
  'X-DNS-Prefetch-Control': 'off',
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
};
```

## Troubleshooting

### Common Build Issues

#### TypeScript Errors
```bash
# Clear TypeScript cache
rm -rf node_modules/.cache
npm run type-check

# Fix import issues
# Ensure all imports use correct paths
# Check tsconfig.json paths configuration
```

#### Memory Issues
```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build

# Alternative: use .env
NODE_OPTIONS=--max-old-space-size=4096
```

#### Bundle Size Issues
```bash
# Analyze bundle
npx webpack-bundle-analyzer build/static/js/*.js

# Common fixes:
# 1. Implement code splitting
# 2. Remove unused dependencies
# 3. Use dynamic imports for large libraries
```

### Deployment Issues

#### Vercel Deployment Failures
```bash
# Check build logs
vercel logs

# Common fixes:
# 1. Check environment variables
# 2. Verify build command in vercel.json
# 3. Check Node.js version compatibility
```

#### Routing Issues (SPA)
```nginx
# Nginx configuration for SPA
location / {
  try_files $uri $uri/ /index.html;
}
```

### Performance Issues
```typescript
// Bundle analysis
import('webpack-bundle-analyzer').then(({ BundleAnalyzerPlugin }) => {
  // Analyze what's in your bundle
});

// Runtime performance monitoring
const observer = new PerformanceObserver((list) => {
  list.getEntries().forEach((entry) => {
    console.log(`${entry.name}: ${entry.duration}ms`);
  });
});

observer.observe({ entryTypes: ['measure', 'navigation'] });
```

This comprehensive deployment guide covers all aspects of building, configuring, and deploying the Activation Manager application across different platforms and environments.