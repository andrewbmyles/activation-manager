# Activation Manager - Technical Architecture

## Table of Contents
1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Core Architecture Patterns](#core-architecture-patterns)
5. [Data Flow](#data-flow)
6. [Component Hierarchy](#component-hierarchy)
7. [State Management](#state-management)
8. [Routing Strategy](#routing-strategy)
9. [Performance Considerations](#performance-considerations)
10. [Security Implementation](#security-implementation)

## System Overview

The Activation Manager is a single-page application (SPA) built with React and TypeScript, designed for enterprise audience management and distribution across advertising platforms.

### Core Modules
- **Audience Management**: Create, edit, and organize audience segments
- **Platform Integration**: Connect and manage advertising platforms
- **Distribution Workflows**: Automate audience deployment
- **Analytics Dashboard**: Performance monitoring and reporting

### Architecture Principles
- **Component-Based**: Modular, reusable UI components
- **Type Safety**: Full TypeScript implementation
- **Responsive Design**: Mobile-first approach
- **Performance Optimized**: Code splitting and lazy loading
- **Accessibility**: WCAG 2.1 compliance

## Technology Stack

### Frontend Framework
```typescript
// Core Dependencies
"react": "^19.1.0"               // UI library
"react-dom": "^19.1.0"           // DOM rendering
"typescript": "^4.9.5"           // Type safety
```

### State Management
```typescript
"@tanstack/react-query": "^5.76.2"  // Server state management
// Built-in React hooks for local state
```

### Styling Framework
```typescript
"tailwindcss": "^3.4.17"        // Utility-first CSS
"autoprefixer": "^10.4.21"      // CSS vendor prefixes
"postcss": "^8.5.3"             // CSS processing
```

### Routing & Navigation
```typescript
"react-router-dom": "^7.6.0"    // Client-side routing
```

### Form Management
```typescript
"react-hook-form": "^7.56.4"    // Form state and validation
```

### Data Visualization
```typescript
"recharts": "^2.15.3"           // Chart components
```

### Utilities
```typescript
"clsx": "^2.1.1"                // Conditional class names
"lucide-react": "^0.511.0"      // Icon library
```

## Project Structure

```
src/
├── components/               # Reusable UI components
│   ├── Layout.tsx           # Main application shell
│   ├── VariableSelector.tsx # Advanced dropdown component
│   ├── PlatformLogo.tsx     # SVG logo renderer
│   ├── AudienceIcon.tsx     # Dynamic audience icons
│   ├── OperatorSelector.tsx # Criteria operator selection
│   ├── ValueInput.tsx       # Dynamic value input component
│   └── ErrorBoundary.tsx    # Error handling boundary
├── pages/                   # Route-level components
│   ├── Dashboard.tsx        # Main dashboard view
│   ├── AudienceBuilder.tsx  # Audience creation/editing
│   ├── PlatformManagement.tsx # Platform configuration
│   ├── PlatformConfig.tsx   # Individual platform setup
│   ├── DistributionCenter.tsx # Distribution workflows
│   └── Analytics.tsx        # Reporting dashboard
├── data/                    # Static data and metadata
│   ├── variableMetadata.ts  # 50+ targeting variables
│   ├── platformLogos.tsx    # SVG platform logos
│   └── sampleData.ts        # Mock data for development
├── types/                   # TypeScript type definitions
│   └── index.ts            # Shared interfaces
├── hooks/                   # Custom React hooks
├── utils/                   # Utility functions
│   └── debugHelper.ts      # Development utilities
└── api/                    # API integration layer
```

## Core Architecture Patterns

### 1. Component Composition Pattern
```typescript
// Layout as container component
export function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <main className="lg:pl-64">
        <Header />
        <div className="px-6 py-8">
          <Outlet /> {/* React Router outlet */}
        </div>
      </main>
    </div>
  );
}
```

### 2. Compound Component Pattern
```typescript
// VariableSelector with internal state management
export function VariableSelector({ value, onChange }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  
  return (
    <div className="relative">
      <Trigger onClick={() => setIsOpen(!isOpen)} />
      {isOpen && (
        <Dropdown>
          <SearchInput value={search} onChange={setSearch} />
          <CategoryList />
          <VariableList />
        </Dropdown>
      )}
    </div>
  );
}
```

### 3. Provider Pattern
```typescript
// React Query client provider
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <Router>
          <Routes>
            {/* Route definitions */}
          </Routes>
        </Router>
      </ErrorBoundary>
    </QueryClientProvider>
  );
}
```

### 4. Hook Pattern
```typescript
// Custom hook for audience operations
export function useAudiences() {
  return useQuery({
    queryKey: ['audiences'],
    queryFn: fetchAudiences,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

## Data Flow

### 1. Server State Flow
```
API → React Query → Component → UI Update
```

### 2. Form State Flow
```
User Input → React Hook Form → Validation → State Update → UI Feedback
```

### 3. Navigation Flow
```
User Action → React Router → Route Change → Component Mount → Data Fetch
```

### 4. Audience Creation Flow
```
Form Input → Validation → Criteria Building → Size Estimation → API Call → Cache Update
```

## Component Hierarchy

### Page-Level Components
```
App
├── Layout
│   ├── Sidebar
│   │   ├── Navigation Items
│   │   └── User Profile
│   ├── Header
│   │   ├── Title
│   │   └── User Menu
│   └── Main Content
│       └── [Page Component]
```

### Audience Builder Hierarchy
```
AudienceBuilder
├── Form Container
│   ├── Basic Info Section
│   │   ├── Name Input
│   │   ├── Description Input
│   │   ├── Type Selector
│   │   └── Subtype Selector
│   ├── Criteria Section
│   │   ├── Criteria List
│   │   │   └── Criteria Item
│   │   │       ├── VariableSelector
│   │   │       ├── OperatorSelector
│   │   │       └── ValueInput
│   │   └── Add Criteria Button
│   ├── Size Estimation
│   └── Form Actions
└── Audience List View
    └── Audience Cards
```

### Dashboard Hierarchy
```
Dashboard
├── Stats Section
│   └── Metric Cards
├── Recent Audiences Section
│   ├── Audience List
│   │   └── Audience Item
│   │       ├── AudienceIcon
│   │       ├── Details
│   │       └── Platform Badges
│   └── View All Link
└── Platform Status Section
    ├── Platform List
    │   └── Platform Item
    │       ├── PlatformLogo
    │       ├── Status Info
    │       └── Connection Status
    └── Manage Link
```

## State Management

### Server State (React Query)
```typescript
// Audience data fetching
const { data: audiences, isLoading, error } = useQuery({
  queryKey: ['audiences'],
  queryFn: async () => {
    const response = await fetch('/api/audiences');
    return response.json();
  },
  staleTime: 5 * 60 * 1000,
});

// Audience creation mutation
const createAudience = useMutation({
  mutationFn: async (audienceData) => {
    const response = await fetch('/api/audiences', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(audienceData),
    });
    return response.json();
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['audiences'] });
  },
});
```

### Local State (React Hooks)
```typescript
// Component state management
function AudienceBuilder() {
  const [isCreating, setIsCreating] = useState(false);
  const [criteria, setCriteria] = useState<AudienceCriteria[]>([]);
  const [audienceType, setAudienceType] = useState<AudienceType>('1st-party');
  
  // Form state (React Hook Form)
  const { register, handleSubmit, setValue, reset } = useForm();
  
  // Derived state
  const estimatedSize = useMemo(() => 
    calculateAudienceSize(criteria), [criteria]
  );
}
```

### State Persistence
```typescript
// URL state for filters and navigation
const [searchParams, setSearchParams] = useSearchParams();

// Local storage for user preferences
const [theme, setTheme] = useLocalStorage('theme', 'light');
```

## Routing Strategy

### Route Structure
```typescript
const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: "dashboard", element: <Dashboard /> },
      { path: "audiences", element: <AudienceBuilder /> },
      { path: "platforms", element: <PlatformManagement /> },
      { path: "platforms/:platformId", element: <PlatformConfig /> },
      { path: "distribution", element: <DistributionCenter /> },
      { path: "analytics", element: <Analytics /> },
    ],
  },
]);
```

### Navigation Implementation
```typescript
// Programmatic navigation
const navigate = useNavigate();

const handlePlatformClick = (platformId: string) => {
  navigate(`/platforms/${platformId}`);
};

// Link navigation
<Link to="/audiences" className="nav-link">
  Audiences
</Link>
```

## Performance Considerations

### Code Splitting
```typescript
// Lazy loading for route components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const AudienceBuilder = lazy(() => import('./pages/AudienceBuilder'));

// Suspense wrapper
<Suspense fallback={<LoadingSpinner />}>
  <Routes>
    {/* Route definitions */}
  </Routes>
</Suspense>
```

### Memoization
```typescript
// Component memoization
const AudienceCard = memo(({ audience }: { audience: Audience }) => {
  return (
    <div className="audience-card">
      {/* Component content */}
    </div>
  );
});

// Value memoization
const expensiveCalculation = useMemo(() => {
  return calculateComplexMetrics(data);
}, [data]);

// Callback memoization
const handleCriteriaChange = useCallback((id: string, updates: any) => {
  setCriteria(prev => prev.map(c => 
    c.id === id ? { ...c, ...updates } : c
  ));
}, []);
```

### Virtualization (for large lists)
```typescript
// Virtual scrolling for variable selector
import { FixedSizeList as List } from 'react-window';

const VirtualizedVariableList = ({ variables }: Props) => {
  return (
    <List
      height={300}
      itemCount={variables.length}
      itemSize={60}
      itemData={variables}
    >
      {VariableItem}
    </List>
  );
};
```

## Security Implementation

### Input Sanitization
```typescript
// Form validation with React Hook Form
const schema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
  criteria: z.array(criteriaSchema),
});

// XSS prevention
const sanitizeInput = (input: string) => {
  return DOMPurify.sanitize(input);
};
```

### Environment Variables
```typescript
// .env configuration
REACT_APP_API_BASE_URL=https://api.example.com
REACT_APP_ENVIRONMENT=production

// Usage in code
const apiBaseUrl = process.env.REACT_APP_API_BASE_URL;
```

### Error Boundaries
```typescript
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

### Content Security Policy
```html
<!-- In public/index.html -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self' 'unsafe-inline';">
```

This technical architecture provides the foundation for building the Activation Manager. The next documents will cover specific implementation details for each component and system.