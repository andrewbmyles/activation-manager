# Activation Manager

A modern audience management and distribution platform built with React and TypeScript for enterprise marketing operations.

## 🚀 Features

### Audience Management
- **Advanced Audience Builder**: Create segments with 50+ variables across 7 categories
- **Audience Type Classification**: 1st Party, 3rd Party, and Clean Room data sources
- **Data Source Integration**: RampID, UID2.0, Google PAIR, Yahoo! Connect, MAID, and more
- **Real-time Size Estimation**: Dynamic audience size calculations

### Platform Integration
- **Multi-Platform Support**: Meta, Google Ads, LinkedIn, TikTok, Netflix, The Trade Desk
- **Connection Management**: Platform status monitoring and health checks
- **Configuration Interface**: Platform-specific setup and credential management

### Distribution Workflows
- **Automated Distribution**: Schedule and manage audience deployments
- **Workflow Builder**: Visual workflow creation with approval chains
- **Error Handling**: Robust retry mechanisms and failure recovery
- **Performance Monitoring**: Real-time distribution tracking

### Analytics & Reporting
- **Custom Dashboards**: Drag-and-drop dashboard builder
- **Performance Metrics**: Audience analytics and platform ROI analysis
- **Automated Reports**: Scheduled reporting with multiple export formats
- **Data Visualization**: Interactive charts and trend analysis

## 🛠 Tech Stack

- **Frontend**: React 18+ with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **Routing**: React Router v6
- **State Management**: React Query (TanStack Query)
- **Forms**: React Hook Form with validation
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React
- **Build**: Create React App with optimizations

## 📦 Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd activation-manager
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm start
   ```
   Opens at [http://localhost:3000](http://localhost:3000)

4. **Build for production**:
   ```bash
   npm run build
   ```

## 📁 Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── Layout.tsx       # Main application layout
│   ├── VariableSelector.tsx  # Advanced variable selection
│   └── PlatformLogo.tsx      # Platform logo components
├── pages/               # Main page components
│   ├── Dashboard.tsx    # Analytics dashboard
│   ├── AudienceBuilder.tsx   # Audience creation interface
│   ├── PlatformManagement.tsx # Platform configuration
│   └── DistributionCenter.tsx # Distribution workflows
├── data/                # Data layer
│   ├── variableMetadata.ts   # 50+ targeting variables
│   ├── platformLogos.tsx     # Platform SVG assets
│   └── sampleData.ts         # Mock data for demo
├── types/               # TypeScript definitions
└── utils/               # Helper functions
```

## 🎯 Key Components

### Variable Metadata System
- 50+ targeting variables across Demographics, Behavioral, Geographic, Technographic, Transactional, Engagement, and Custom Attributes
- Hierarchical organization with search and filtering
- Dynamic operator and value inputs based on data types

### Audience Type System
- **1st Party**: RampID, UID2.0, Google PAIR, Yahoo! Connect, MAID
- **3rd Party**: Postal Code, PRIZM Segment  
- **Clean Room**: PartnerID

### Platform Integration
- Dynamic logo rendering for 6 major platforms
- Status monitoring and connection health
- Platform-specific configuration forms

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Vercel auto-detects React configuration
3. Deploy with default settings

### Other Platforms
- **Netlify**: Use `npm run build` and deploy `build/` folder
- **GitHub Pages**: Follow Create React App deployment guide
- **AWS S3**: Static hosting with CloudFront CDN

## 📊 Performance

- **Bundle Size**: ~220KB gzipped
- **Load Time**: <2 seconds on 3G
- **Variables**: 50+ with real-time search
- **Responsive**: Mobile-first design

## 🔧 Development

### Available Scripts
- `npm start` - Development server
- `npm run build` - Production build  
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Code Style
- TypeScript strict mode enabled
- ESLint with React hooks rules
- Prettier for code formatting
- Tailwind CSS for styling

## 📝 Documentation

- [Release Notes](./RELEASE-NOTES.md) - Version history and changes
- [Update Protocol](./UPDATE-PROTOCOL.md) - Development workflow
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Platform-specific deployment
- [GitHub Setup](./GITHUB-SETUP.md) - Repository creation guide

## 🤝 Contributing

This is a private project. All development follows the established [Update Protocol](./UPDATE-PROTOCOL.md).

## 📄 License

Private and proprietary. All rights reserved.

---

**Built with ❤️ using Claude Code**  
*Enterprise-grade audience management for modern marketing teams*