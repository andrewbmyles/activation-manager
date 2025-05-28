# Data Structures and Types Reference

## Table of Contents
1. [TypeScript Configuration](#typescript-configuration)
2. [Core Data Types](#core-data-types)
3. [Component Props Types](#component-props-types)
4. [API Types](#api-types)
5. [Form Types](#form-types)
6. [State Types](#state-types)
7. [Utility Types](#utility-types)
8. [Data Validation Schemas](#data-validation-schemas)
9. [Sample Data Structures](#sample-data-structures)

## TypeScript Configuration

### tsconfig.json
```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": [
      "dom",
      "dom.iterable",
      "es6"
    ],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": [
    "src"
  ]
}
```

## Core Data Types

### Audience Types
```typescript
// src/types/audience.ts
export interface Audience {
  id: string;
  name: string;
  description?: string;
  type?: AudienceType;
  subtype?: AudienceSubtype;
  criteria: AudienceCriteria[];
  estimatedSize: number;
  createdAt: Date;
  updatedAt: Date;
  platforms: string[];
  tags?: string[];
  status: AudienceStatus;
  createdBy?: string;
  lastModifiedBy?: string;
}

export type AudienceType = '1st-party' | '3rd-party' | 'clean-room';

export type AudienceSubtype = 
  | 'rampid' 
  | 'uid2' 
  | 'google-pair' 
  | 'yahoo-connect' 
  | 'maid'
  | 'postal-code' 
  | 'prizm-segment' 
  | 'partner-id';

export type AudienceStatus = 'active' | 'inactive' | 'archived' | 'pending';

export interface AudienceCriteria {
  id: string;
  type: CriteriaType;
  field: string;
  operator: CriteriaOperator;
  value: CriteriaValue;
  logicalOperator?: 'AND' | 'OR';
}

export type CriteriaType = 
  | 'demographic' 
  | 'behavioral' 
  | 'geographic' 
  | 'technographic' 
  | 'transactional' 
  | 'engagement' 
  | 'custom';

export type CriteriaOperator = 
  | 'equals' 
  | 'not_equals' 
  | 'contains' 
  | 'not_contains' 
  | 'greater_than' 
  | 'less_than' 
  | 'between' 
  | 'in' 
  | 'not_in' 
  | 'is_null' 
  | 'is_not_null';

export type CriteriaValue = string | number | boolean | Date | (string | number)[];

// Extended criteria for form handling
export interface ExtendedAudienceCriteria extends AudienceCriteria {
  variable?: VariableMetadata;
  errors?: Record<string, string>;
}
```

### Platform Types
```typescript
// src/types/platform.ts
export interface Platform {
  id: string;
  name: string;
  logo: string;
  connected: boolean;
  lastSync?: Date;
  status: PlatformStatus;
  configuration: PlatformConfiguration;
  capabilities: PlatformCapabilities;
  metrics?: PlatformMetrics;
}

export type PlatformStatus = 'connected' | 'disconnected' | 'error' | 'syncing';

export interface PlatformConfiguration {
  apiEndpoint?: string;
  credentials: Record<string, string>;
  settings: Record<string, any>;
  lastUpdated: Date;
}

export interface PlatformCapabilities {
  supportsRealTimeSync: boolean;
  supportsBatchSync: boolean;
  maxAudienceSize: number;
  supportedDataTypes: string[];
  rateLimits: {
    requestsPerMinute: number;
    requestsPerDay: number;
  };
}

export interface PlatformMetrics {
  totalAudiences: number;
  lastSyncDuration: number;
  averageMatchRate: number;
  totalRecordsProcessed: number;
  errorRate: number;
}

// Platform-specific configuration types
export interface MetaConfiguration extends PlatformConfiguration {
  credentials: {
    appId: string;
    appSecret: string;
    accessToken: string;
  };
}

export interface GoogleConfiguration extends PlatformConfiguration {
  credentials: {
    customerId: string;
    developerToken: string;
    managerAccountId: string;
  };
}

export interface LinkedInConfiguration extends PlatformConfiguration {
  credentials: {
    organizationId: string;
    accessToken: string;
  };
}
```

### Variable Metadata Types
```typescript
// src/types/variable.ts
export interface VariableMetadata {
  id: string;
  name: string;
  category: VariableCategory;
  dataType: VariableDataType;
  operators: CriteriaOperator[];
  description?: string;
  examples?: string[];
  hierarchy: number;
  sortOrder: number;
  tooltip?: string;
  validationRules?: ValidationRule[];
  defaultValue?: any;
  isRequired?: boolean;
  isDeprecated?: boolean;
}

export type VariableCategory = 
  | 'Demographics' 
  | 'Behavioral' 
  | 'Geographic' 
  | 'Technographic' 
  | 'Transactional' 
  | 'Engagement' 
  | 'Custom Attributes';

export type VariableDataType = 
  | 'string' 
  | 'number' 
  | 'boolean' 
  | 'date' 
  | 'array' 
  | 'object' 
  | 'enum';

export interface ValidationRule {
  type: 'min' | 'max' | 'pattern' | 'required' | 'custom';
  value?: any;
  message: string;
  validator?: (value: any) => boolean;
}

// Variable option for dropdowns
export interface VariableOption {
  value: string | number;
  label: string;
  description?: string;
  group?: string;
}
```

### Distribution Types
```typescript
// src/types/distribution.ts
export interface Distribution {
  id: string;
  audienceId: string;
  platformId: string;
  status: DistributionStatus;
  startedAt: Date;
  completedAt?: Date;
  recordsProcessed?: number;
  recordsTotal?: number;
  error?: DistributionError;
  configuration: DistributionConfiguration;
  metrics?: DistributionMetrics;
}

export type DistributionStatus = 
  | 'pending' 
  | 'in_progress' 
  | 'completed' 
  | 'failed' 
  | 'cancelled' 
  | 'paused';

export interface DistributionError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: Date;
  retryable: boolean;
}

export interface DistributionConfiguration {
  batchSize: number;
  retryAttempts: number;
  timeout: number;
  skipDuplicates: boolean;
  notifyOnComplete: boolean;
  customMapping?: Record<string, string>;
}

export interface DistributionMetrics {
  processingTime: number;
  matchRate: number;
  throughput: number;
  errorCount: number;
  retryCount: number;
}

// Workflow-related types
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  steps: WorkflowStep[];
  schedule?: WorkflowSchedule;
  status: WorkflowStatus;
  createdAt: Date;
  updatedAt: Date;
  lastRunAt?: Date;
  nextRunAt?: Date;
}

export type WorkflowStatus = 'active' | 'inactive' | 'running' | 'failed';

export interface WorkflowStep {
  id: string;
  type: WorkflowStepType;
  configuration: Record<string, any>;
  order: number;
  dependencies?: string[];
}

export type WorkflowStepType = 
  | 'audience_select' 
  | 'platform_distribute' 
  | 'wait' 
  | 'condition' 
  | 'notification';

export interface WorkflowSchedule {
  type: 'once' | 'recurring';
  startDate: Date;
  endDate?: Date;
  cronExpression?: string;
  timezone: string;
}
```

### Analytics Types
```typescript
// src/types/analytics.ts
export interface AnalyticsData {
  date: string;
  audienceId: string;
  platformId: string;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
  ctr: number;
  cpc: number;
  cpm: number;
  roas: number;
}

export interface DashboardMetrics {
  totalAudiences: number;
  totalReach: number;
  activeDistributions: number;
  totalSpend: number;
  changes: {
    audiences: number;
    reach: number;
    distributions: number;
    spend: number;
  };
}

export interface AudienceAnalytics {
  audienceId: string;
  timeRange: TimeRange;
  demographics: DemographicBreakdown;
  performance: PerformanceMetrics;
  trends: TrendData[];
}

export interface TimeRange {
  start: Date;
  end: Date;
  granularity: 'hour' | 'day' | 'week' | 'month';
}

export interface DemographicBreakdown {
  age: AgeDistribution[];
  gender: GenderDistribution[];
  location: LocationDistribution[];
  interests: InterestDistribution[];
}

export interface AgeDistribution {
  range: string;
  percentage: number;
  count: number;
}

export interface GenderDistribution {
  gender: 'male' | 'female' | 'other' | 'unknown';
  percentage: number;
  count: number;
}

export interface LocationDistribution {
  country: string;
  state?: string;
  city?: string;
  percentage: number;
  count: number;
}

export interface InterestDistribution {
  category: string;
  subcategory?: string;
  affinity: number;
  percentage: number;
}

export interface PerformanceMetrics {
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
  ctr: number;
  cpc: number;
  cpm: number;
  roas: number;
  conversionRate: number;
}

export interface TrendData {
  date: string;
  value: number;
  metric: string;
}
```

## Component Props Types

### Form Component Props
```typescript
// Form-related prop types
export interface FormProps<T = any> {
  initialData?: Partial<T>;
  onSubmit: (data: T) => Promise<void> | void;
  onCancel?: () => void;
  loading?: boolean;
  disabled?: boolean;
  className?: string;
}

export interface FormFieldProps {
  label: string;
  children: React.ReactNode;
  error?: string;
  required?: boolean;
  help?: string;
  className?: string;
}

export interface SelectProps<T = string> {
  value?: T;
  onChange: (value: T) => void;
  options: SelectOption<T>[];
  placeholder?: string;
  disabled?: boolean;
  loading?: boolean;
  searchable?: boolean;
  clearable?: boolean;
  className?: string;
}

export interface SelectOption<T = string> {
  value: T;
  label: string;
  description?: string;
  disabled?: boolean;
  group?: string;
}
```

### Display Component Props
```typescript
// Table component props
export interface DataTableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
  onSort?: (column: keyof T, direction: 'asc' | 'desc') => void;
  pagination?: PaginationConfig;
  selection?: TableSelection<T>;
}

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  render?: (value: any, row: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
  className?: string;
}

export interface PaginationConfig {
  page: number;
  pageSize: number;
  total: number;
  onChange: (page: number, pageSize: number) => void;
}

export interface TableSelection<T> {
  selectedRows: T[];
  onSelectionChange: (rows: T[]) => void;
  selectableRowKeys?: (keyof T)[];
}

// Chart component props
export interface ChartProps {
  data: any[];
  width?: number;
  height?: number;
  margin?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  };
  loading?: boolean;
  empty?: boolean;
  className?: string;
}

export interface LineChartProps extends ChartProps {
  xKey: string;
  yKey: string;
  lineColor?: string;
  showDots?: boolean;
  showGrid?: boolean;
}

export interface BarChartProps extends ChartProps {
  xKey: string;
  yKey: string;
  barColor?: string;
  orientation?: 'horizontal' | 'vertical';
}
```

## API Types

### Request/Response Types
```typescript
// Generic API response wrapper
export interface ApiResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
  errors?: ApiError[];
  pagination?: PaginationInfo;
}

export interface ApiError {
  code: string;
  message: string;
  field?: string;
  details?: Record<string, any>;
}

export interface PaginationInfo {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

// Audience API types
export interface CreateAudienceRequest {
  name: string;
  description?: string;
  type: AudienceType;
  subtype: AudienceSubtype;
  criteria: Omit<AudienceCriteria, 'id'>[];
  tags?: string[];
}

export interface UpdateAudienceRequest extends Partial<CreateAudienceRequest> {
  id: string;
}

export interface AudienceListRequest {
  page?: number;
  pageSize?: number;
  search?: string;
  type?: AudienceType;
  status?: AudienceStatus;
  sortBy?: keyof Audience;
  sortOrder?: 'asc' | 'desc';
}

// Platform API types
export interface ConnectPlatformRequest {
  platformId: string;
  configuration: PlatformConfiguration;
}

export interface SyncPlatformRequest {
  platformId: string;
  audienceIds?: string[];
  force?: boolean;
}

// Distribution API types
export interface CreateDistributionRequest {
  audienceIds: string[];
  platformIds: string[];
  configuration?: Partial<DistributionConfiguration>;
  schedule?: WorkflowSchedule;
}
```

### HTTP Client Types
```typescript
// HTTP client configuration
export interface HttpClientConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
  retries: number;
  retryDelay: number;
}

export interface RequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  url: string;
  data?: any;
  params?: Record<string, any>;
  headers?: Record<string, string>;
  timeout?: number;
}

export interface ResponseData<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
}
```

## Form Types

### React Hook Form Integration
```typescript
// Form data types
export interface AudienceFormData {
  name: string;
  description?: string;
  type: AudienceType;
  subtype: AudienceSubtype;
  criteria: CriteriaFormData[];
  tags: string[];
}

export interface CriteriaFormData {
  variableId: string;
  operator: CriteriaOperator;
  value: CriteriaValue;
  logicalOperator?: 'AND' | 'OR';
}

export interface PlatformConfigFormData {
  name: string;
  credentials: Record<string, string>;
  settings: Record<string, any>;
  notifications: {
    email: boolean;
    webhook: boolean;
  };
}

// Form validation schemas (using Zod)
export const audienceSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  description: z.string().max(500, 'Description too long').optional(),
  type: z.enum(['1st-party', '3rd-party', 'clean-room']),
  subtype: z.string().min(1, 'Subtype is required'),
  criteria: z.array(criteriaSchema).min(1, 'At least one criteria required'),
  tags: z.array(z.string()).optional(),
});

export const criteriaSchema = z.object({
  variableId: z.string().min(1, 'Variable is required'),
  operator: z.enum(['equals', 'not_equals', 'contains', 'greater_than', 'less_than', 'between', 'in']),
  value: z.union([z.string(), z.number(), z.boolean(), z.array(z.union([z.string(), z.number()]))]),
  logicalOperator: z.enum(['AND', 'OR']).optional(),
});

// Form state types
export interface FormState<T> {
  data: T;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  isValid: boolean;
  isDirty: boolean;
}
```

## State Types

### React Query State
```typescript
// Query state types
export interface QueryState<T> {
  data?: T;
  error: Error | null;
  isLoading: boolean;
  isError: boolean;
  isSuccess: boolean;
  isFetching: boolean;
  isRefetching: boolean;
  isStale: boolean;
}

export interface MutationState<T, V> {
  data?: T;
  error: Error | null;
  isLoading: boolean;
  isError: boolean;
  isSuccess: boolean;
  variables?: V;
  reset: () => void;
}

// Custom hook return types
export interface UseAudiencesReturn {
  audiences: Audience[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
  createAudience: (data: CreateAudienceRequest) => Promise<Audience>;
  updateAudience: (data: UpdateAudienceRequest) => Promise<Audience>;
  deleteAudience: (id: string) => Promise<void>;
}

export interface UsePlatformsReturn {
  platforms: Platform[];
  isLoading: boolean;
  error: Error | null;
  connectPlatform: (data: ConnectPlatformRequest) => Promise<Platform>;
  syncPlatform: (data: SyncPlatformRequest) => Promise<void>;
}
```

### Local Component State
```typescript
// Component state interfaces
export interface VariableSelectorState {
  isOpen: boolean;
  search: string;
  expandedCategories: Set<string>;
  selectedVariable?: VariableMetadata;
}

export interface AudienceBuilderState {
  isCreating: boolean;
  selectedAudience?: Audience;
  criteria: ExtendedAudienceCriteria[];
  audienceType: AudienceType;
  audienceSubtype: AudienceSubtype;
  estimatedSize: number;
}

export interface DashboardState {
  dateRange: TimeRange;
  selectedMetrics: string[];
  refreshInterval: number;
  autoRefresh: boolean;
}
```

## Utility Types

### Common Utility Types
```typescript
// Generic utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type PartialExcept<T, K extends keyof T> = Partial<T> & Pick<T, K>;

// Event handler types
export type EventHandler<T = Event> = (event: T) => void;
export type ChangeHandler<T = string> = (value: T) => void;
export type SubmitHandler<T> = (data: T) => Promise<void> | void;

// Async operation types
export type AsyncOperation<T = void> = () => Promise<T>;
export type AsyncCallback<T, R = void> = (data: T) => Promise<R>;

// Filter and sort types
export interface FilterConfig<T> {
  field: keyof T;
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than' | 'in';
  value: any;
}

export interface SortConfig<T> {
  field: keyof T;
  direction: 'asc' | 'desc';
}

// Theme and styling types
export type ColorScheme = 'light' | 'dark' | 'system';
export type Size = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type Variant = 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';

// Navigation types
export interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  badge?: string | number;
  disabled?: boolean;
  children?: NavigationItem[];
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
  current?: boolean;
}
```

## Data Validation Schemas

### Zod Schemas for Runtime Validation
```typescript
import { z } from 'zod';

// Audience validation schemas
export const audienceTypeSchema = z.enum(['1st-party', '3rd-party', 'clean-room']);
export const audienceSubtypeSchema = z.enum([
  'rampid', 'uid2', 'google-pair', 'yahoo-connect', 'maid',
  'postal-code', 'prizm-segment', 'partner-id'
]);

export const audienceCriteriaSchema = z.object({
  id: z.string(),
  type: z.enum(['demographic', 'behavioral', 'geographic', 'technographic', 'transactional', 'engagement', 'custom']),
  field: z.string().min(1),
  operator: z.enum(['equals', 'not_equals', 'contains', 'not_contains', 'greater_than', 'less_than', 'between', 'in', 'not_in']),
  value: z.union([z.string(), z.number(), z.boolean(), z.date(), z.array(z.union([z.string(), z.number()]))]),
  logicalOperator: z.enum(['AND', 'OR']).optional(),
});

export const audienceSchema = z.object({
  id: z.string(),
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
  type: audienceTypeSchema.optional(),
  subtype: audienceSubtypeSchema.optional(),
  criteria: z.array(audienceCriteriaSchema),
  estimatedSize: z.number().min(0),
  createdAt: z.date(),
  updatedAt: z.date(),
  platforms: z.array(z.string()),
  tags: z.array(z.string()).optional(),
  status: z.enum(['active', 'inactive', 'archived', 'pending']),
});

// Platform validation schemas
export const platformConfigurationSchema = z.object({
  apiEndpoint: z.string().url().optional(),
  credentials: z.record(z.string()),
  settings: z.record(z.any()),
  lastUpdated: z.date(),
});

export const platformSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  logo: z.string(),
  connected: z.boolean(),
  lastSync: z.date().optional(),
  status: z.enum(['connected', 'disconnected', 'error', 'syncing']),
  configuration: platformConfigurationSchema,
});

// Variable metadata validation
export const variableMetadataSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  category: z.enum(['Demographics', 'Behavioral', 'Geographic', 'Technographic', 'Transactional', 'Engagement', 'Custom Attributes']),
  dataType: z.enum(['string', 'number', 'boolean', 'date', 'array', 'object', 'enum']),
  operators: z.array(z.string()),
  description: z.string().optional(),
  examples: z.array(z.string()).optional(),
  hierarchy: z.number().min(1),
  sortOrder: z.number().min(0),
  tooltip: z.string().optional(),
});

// Form validation schemas
export const createAudienceRequestSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  description: z.string().max(500, 'Description too long').optional(),
  type: audienceTypeSchema,
  subtype: audienceSubtypeSchema,
  criteria: z.array(audienceCriteriaSchema.omit({ id: true })).min(1, 'At least one criteria required'),
  tags: z.array(z.string()).optional(),
});

// API response validation
export const apiResponseSchema = <T>(dataSchema: z.ZodSchema<T>) => z.object({
  data: dataSchema,
  success: z.boolean(),
  message: z.string().optional(),
  errors: z.array(z.object({
    code: z.string(),
    message: z.string(),
    field: z.string().optional(),
  })).optional(),
});
```

## Sample Data Structures

### Sample Audience Data
```typescript
export const sampleAudiences: Audience[] = [
  {
    id: '1',
    name: 'High-Value Customers',
    description: 'Customers with high lifetime value and frequent purchases',
    type: '1st-party',
    subtype: 'rampid',
    criteria: [
      {
        id: 'c1',
        type: 'transactional',
        field: 'lifetime_value',
        operator: 'greater_than',
        value: 1000,
      },
      {
        id: 'c2',
        type: 'behavioral',
        field: 'purchase_frequency',
        operator: 'greater_than',
        value: 5,
        logicalOperator: 'AND',
      },
    ],
    estimatedSize: 45000,
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-02-01'),
    platforms: ['meta', 'google'],
    tags: ['high-value', 'loyalty'],
    status: 'active',
  },
  // ... more sample audiences
];

export const sampleVariableMetadata: VariableMetadata[] = [
  {
    id: 'age',
    name: 'Age',
    category: 'Demographics',
    dataType: 'number',
    operators: ['equals', 'greater_than', 'less_than', 'between'],
    description: 'Customer age in years',
    examples: ['25', '30-40', '65+'],
    hierarchy: 1,
    sortOrder: 1,
    tooltip: 'Age is calculated based on birth date',
  },
  {
    id: 'income',
    name: 'Household Income',
    category: 'Demographics',
    dataType: 'number',
    operators: ['greater_than', 'less_than', 'between'],
    description: 'Annual household income in USD',
    examples: ['50000', '75000-100000'],
    hierarchy: 1,
    sortOrder: 5,
  },
  // ... more variable metadata
];

export const samplePlatforms: Platform[] = [
  {
    id: 'meta',
    name: 'Meta Ads',
    logo: 'meta',
    connected: true,
    lastSync: new Date('2024-03-01T10:30:00Z'),
    status: 'connected',
    configuration: {
      credentials: {
        appId: 'your_app_id',
        appSecret: 'your_app_secret',
        accessToken: 'your_access_token',
      },
      settings: {
        accountId: 'act_123456789',
        defaultCampaignObjective: 'CONVERSIONS',
      },
      lastUpdated: new Date('2024-02-15'),
    },
    capabilities: {
      supportsRealTimeSync: true,
      supportsBatchSync: true,
      maxAudienceSize: 10000000,
      supportedDataTypes: ['email', 'phone', 'device_id'],
      rateLimits: {
        requestsPerMinute: 200,
        requestsPerDay: 20000,
      },
    },
  },
  // ... more sample platforms
];
```

This comprehensive type system ensures type safety throughout the application and provides clear contracts for all data structures and component interfaces.