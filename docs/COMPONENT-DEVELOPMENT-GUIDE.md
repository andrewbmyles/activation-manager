# Component Development Guide

## Table of Contents
1. [Component Architecture](#component-architecture)
2. [Core Components](#core-components)
3. [Custom Hooks](#custom-hooks)
4. [Form Components](#form-components)
5. [Data Display Components](#data-display-components)
6. [Layout Components](#layout-components)
7. [Testing Strategies](#testing-strategies)
8. [Performance Optimization](#performance-optimization)

## Component Architecture

### Component Design Principles
- **Single Responsibility**: Each component has one clear purpose
- **Composability**: Components can be combined to create complex UIs
- **Reusability**: Components are designed for multiple use cases
- **Type Safety**: Full TypeScript support with proper interfaces
- **Accessibility**: ARIA labels and keyboard navigation

### Component Structure Template
```typescript
import React, { useState, useCallback, memo } from 'react';
import { clsx } from 'clsx';

interface ComponentProps {
  // Required props
  value: string;
  onChange: (value: string) => void;
  
  // Optional props with defaults
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  
  // Event handlers
  onFocus?: () => void;
  onBlur?: () => void;
}

export const Component = memo(({
  value,
  onChange,
  placeholder = 'Enter value...',
  disabled = false,
  className,
  onFocus,
  onBlur,
}: ComponentProps) => {
  // Local state
  const [isFocused, setIsFocused] = useState(false);
  
  // Event handlers
  const handleFocus = useCallback(() => {
    setIsFocused(true);
    onFocus?.();
  }, [onFocus]);
  
  const handleBlur = useCallback(() => {
    setIsFocused(false);
    onBlur?.();
  }, [onBlur]);
  
  // Render
  return (
    <div className={clsx(
      'component-base-styles',
      isFocused && 'focused-styles',
      disabled && 'disabled-styles',
      className
    )}>
      {/* Component content */}
    </div>
  );
});

Component.displayName = 'Component';
```

## Core Components

### 1. VariableSelector Component

**Purpose**: Advanced dropdown for selecting targeting variables with search and categorization.

```typescript
// interfaces/VariableSelector.ts
interface VariableSelectorProps {
  value?: string;
  onChange: (variableId: string, variable: VariableMetadata) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

interface VariableMetadata {
  id: string;
  name: string;
  category: string;
  dataType: 'string' | 'number' | 'boolean' | 'date' | 'array';
  operators: string[];
  description?: string;
  examples?: string[];
  hierarchy: number;
  sortOrder: number;
  tooltip?: string;
}
```

**Implementation Structure**:
```typescript
export function VariableSelector({ value, onChange, placeholder, className }: Props) {
  // State management
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  
  // Refs for DOM interaction
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  
  // Data processing
  const filteredVariables = useMemo(() => 
    filterVariablesBySearch(variableMetadata, search), [search]
  );
  
  const groupedVariables = useMemo(() => 
    groupVariablesByCategory(filteredVariables), [filteredVariables]
  );
  
  // Event handlers
  const handleClickOutside = useCallback((event: MouseEvent) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
      setIsOpen(false);
    }
  }, []);
  
  const handleVariableSelect = useCallback((variable: VariableMetadata) => {
    onChange(variable.id, variable);
    setIsOpen(false);
    setSearch('');
  }, [onChange]);
  
  // Effects
  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [handleClickOutside]);
  
  return (
    <div ref={dropdownRef} className={clsx("relative", className)}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="variable-selector-trigger"
      >
        <span>{selectedVariable?.name || placeholder}</span>
        <ChevronDown className={clsx("transform transition-transform", isOpen && "rotate-180")} />
      </button>
      
      {/* Dropdown Panel */}
      {isOpen && (
        <div className="variable-selector-dropdown">
          {/* Search Input */}
          <div className="search-container">
            <Search className="search-icon" />
            <input
              ref={inputRef}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search variables..."
              className="search-input"
            />
          </div>
          
          {/* Categories and Variables */}
          <div className="variables-list">
            {Object.entries(groupedVariables).map(([category, variables]) => (
              <CategorySection
                key={category}
                category={category}
                variables={variables}
                isExpanded={expandedCategories.has(category)}
                onToggle={() => toggleCategory(category)}
                onVariableSelect={handleVariableSelect}
                selectedValue={value}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

### 2. PlatformLogo Component

**Purpose**: Render SVG logos for different advertising platforms.

```typescript
interface PlatformLogoProps {
  platform: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function PlatformLogo({ platform, className, size = 'md' }: PlatformLogoProps) {
  const LogoComponent = platformLogos[platform];
  
  if (!LogoComponent) {
    return (
      <div className={clsx('platform-logo-fallback', sizeClasses[size], className)}>
        {platform.charAt(0).toUpperCase()}
      </div>
    );
  }
  
  return (
    <LogoComponent 
      className={clsx('platform-logo', sizeClasses[size], className)}
      aria-label={`${platform} logo`}
    />
  );
}

// Platform logos definition
export const platformLogos: Record<string, React.ComponentType<{ className?: string }>> = {
  'meta': ({ className }) => (
    <svg viewBox="0 0 24 24" className={className}>
      {/* Meta logo SVG paths */}
    </svg>
  ),
  'google': ({ className }) => (
    <svg viewBox="0 0 24 24" className={className}>
      {/* Google logo SVG paths */}
    </svg>
  ),
  // ... other platform logos
};
```

### 3. AudienceIcon Component

**Purpose**: Generate dynamic icons based on audience names.

```typescript
interface AudienceIconProps {
  audienceName: string;
  className?: string;
}

export function AudienceIcon({ audienceName, className }: AudienceIconProps) {
  const icon = useMemo(() => {
    const name = audienceName.toLowerCase();
    
    // Icon mapping logic
    if (name.includes('high-value') || name.includes('premium')) {
      return Star;
    }
    if (name.includes('tech') || name.includes('enthusiast')) {
      return Zap;
    }
    if (name.includes('cart') || name.includes('abandon')) {
      return ShoppingCart;
    }
    if (name.includes('millennial') || name.includes('urban')) {
      return Users;
    }
    if (name.includes('frequent') || name.includes('purchaser')) {
      return TrendingUp;
    }
    
    return Users; // Default icon
  }, [audienceName]);
  
  const Icon = icon;
  return <Icon className={className} />;
}
```

## Custom Hooks

### 1. useAudiences Hook

```typescript
export function useAudiences() {
  return useQuery({
    queryKey: ['audiences'],
    queryFn: async (): Promise<Audience[]> => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      return sampleAudiences;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000,   // 10 minutes
  });
}

export function useCreateAudience() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (audienceData: CreateAudienceData): Promise<Audience> => {
      // API call to create audience
      const response = await fetch('/api/audiences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(audienceData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to create audience');
      }
      
      return response.json();
    },
    onSuccess: (newAudience) => {
      // Update cache
      queryClient.setQueryData(['audiences'], (old: Audience[] = []) => 
        [...old, newAudience]
      );
      
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['audience-stats'] });
    },
    onError: (error) => {
      console.error('Failed to create audience:', error);
      // Handle error (show toast, etc.)
    },
  });
}
```

### 2. useLocalStorage Hook

```typescript
export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });
  
  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);
  
  return [storedValue, setValue] as const;
}
```

## Form Components

### 1. Form Architecture with React Hook Form

```typescript
// Form schema definition with Zod
const audienceSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  description: z.string().max(500, 'Description too long').optional(),
  type: z.enum(['1st-party', '3rd-party', 'clean-room']),
  subtype: z.string(),
});

type AudienceFormData = z.infer<typeof audienceSchema>;

// Form component
export function AudienceForm({ onSubmit, initialData }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    setValue,
    reset,
  } = useForm<AudienceFormData>({
    resolver: zodResolver(audienceSchema),
    defaultValues: initialData,
  });
  
  const audienceType = watch('type');
  
  // Reset subtype when type changes
  useEffect(() => {
    if (audienceType) {
      const defaultSubtype = audienceSubtypeOptions[audienceType][0]?.value;
      setValue('subtype', defaultSubtype);
    }
  }, [audienceType, setValue]);
  
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Name field */}
      <FormField
        label="Audience Name"
        error={errors.name?.message}
        required
      >
        <input
          {...register('name')}
          className={clsx('input-field', errors.name && 'input-error')}
          placeholder="e.g., High-Value Customers"
        />
      </FormField>
      
      {/* Description field */}
      <FormField
        label="Description"
        error={errors.description?.message}
      >
        <textarea
          {...register('description')}
          className="input-field"
          rows={3}
          placeholder="Describe this audience segment..."
        />
      </FormField>
      
      {/* Type selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          label="Audience Type"
          error={errors.type?.message}
          required
        >
          <select {...register('type')} className="input-field">
            {audienceTypeOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </FormField>
        
        <FormField
          label="Data Source"
          error={errors.subtype?.message}
          required
        >
          <select {...register('subtype')} className="input-field">
            {audienceSubtypeOptions[audienceType]?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            )) || []}
          </select>
        </FormField>
      </div>
      
      {/* Submit button */}
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={isSubmitting}
          className="btn-primary"
        >
          {isSubmitting ? 'Saving...' : 'Save Audience'}
        </button>
        <button
          type="button"
          onClick={() => reset()}
          className="btn-secondary"
        >
          Reset
        </button>
      </div>
    </form>
  );
}
```

### 2. FormField Component

```typescript
interface FormFieldProps {
  label: string;
  children: React.ReactNode;
  error?: string;
  required?: boolean;
  help?: string;
  className?: string;
}

export function FormField({
  label,
  children,
  error,
  required,
  help,
  className,
}: FormFieldProps) {
  const id = useId();
  
  return (
    <div className={clsx('form-field', className)}>
      <label
        htmlFor={id}
        className={clsx(
          'block text-sm font-medium mb-2',
          error ? 'text-red-700' : 'text-gray-700'
        )}
      >
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {React.cloneElement(children as React.ReactElement, { id })}
      
      {help && !error && (
        <p className="text-sm text-gray-500 mt-1">{help}</p>
      )}
      
      {error && (
        <p className="text-sm text-red-600 mt-1" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
```

## Data Display Components

### 1. DataTable Component

```typescript
interface Column<T> {
  key: keyof T;
  label: string;
  render?: (value: any, row: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
}

export function DataTable<T extends { id: string }>({
  data,
  columns,
  loading,
  emptyMessage = 'No data available',
  onRowClick,
}: DataTableProps<T>) {
  const [sortConfig, setSortConfig] = useState<{
    key: keyof T;
    direction: 'asc' | 'desc';
  } | null>(null);
  
  const sortedData = useMemo(() => {
    if (!sortConfig) return data;
    
    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortConfig]);
  
  const handleSort = (key: keyof T) => {
    setSortConfig(current => {
      if (current?.key === key) {
        return {
          key,
          direction: current.direction === 'asc' ? 'desc' : 'asc',
        };
      }
      return { key, direction: 'asc' };
    });
  };
  
  if (loading) {
    return <TableSkeleton columns={columns.length} rows={5} />;
  }
  
  if (data.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        {emptyMessage}
      </div>
    );
  }
  
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column) => (
              <th
                key={String(column.key)}
                className={clsx(
                  'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                  column.sortable && 'cursor-pointer hover:bg-gray-100'
                )}
                style={{ width: column.width }}
                onClick={() => column.sortable && handleSort(column.key)}
              >
                <div className="flex items-center gap-1">
                  {column.label}
                  {column.sortable && (
                    <ArrowUpDown className="w-4 h-4" />
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sortedData.map((row) => (
            <tr
              key={row.id}
              className={clsx(
                'hover:bg-gray-50 transition-colors',
                onRowClick && 'cursor-pointer'
              )}
              onClick={() => onRowClick?.(row)}
            >
              {columns.map((column) => (
                <td
                  key={String(column.key)}
                  className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                >
                  {column.render
                    ? column.render(row[column.key], row)
                    : String(row[column.key])
                  }
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### 2. MetricCard Component

```typescript
interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  color?: 'primary' | 'green' | 'purple' | 'orange' | 'red';
  loading?: boolean;
}

export function MetricCard({
  title,
  value,
  change,
  icon: Icon,
  color = 'primary',
  loading,
}: MetricCardProps) {
  if (loading) {
    return <MetricCardSkeleton />;
  }
  
  const isPositive = change !== undefined && change > 0;
  const isNegative = change !== undefined && change < 0;
  
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <div className="flex items-start justify-between mb-4">
        <div className={clsx(
          'p-3 rounded-lg',
          colorVariants[color]
        )}>
          <Icon size={24} />
        </div>
        
        {change !== undefined && (
          <div className={clsx(
            'flex items-center gap-1 text-sm font-medium',
            isPositive && 'text-green-600',
            isNegative && 'text-red-600',
            change === 0 && 'text-gray-500'
          )}>
            {isPositive && <ArrowUp size={16} />}
            {isNegative && <ArrowDown size={16} />}
            {change === 0 && <Minus size={16} />}
            {Math.abs(change)}%
          </div>
        )}
      </div>
      
      <div>
        <p className="text-sm text-gray-600 mb-1">{title}</p>
        <p className="text-2xl font-semibold text-gray-900">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
      </div>
    </div>
  );
}

const colorVariants = {
  primary: 'bg-blue-100 text-blue-600',
  green: 'bg-green-100 text-green-600',
  purple: 'bg-purple-100 text-purple-600',
  orange: 'bg-orange-100 text-orange-600',
  red: 'bg-red-100 text-red-600',
};
```

## Layout Components

### 1. Layout Component

```typescript
export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <div className="absolute inset-0 bg-gray-600 opacity-75" />
        </div>
      )}
      
      {/* Sidebar */}
      <div className={clsx(
        'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        <Sidebar onNavigate={() => setSidebarOpen(false)} />
      </div>
      
      {/* Main content */}
      <div className="lg:pl-64">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main className="px-6 py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
```

### 2. Sidebar Component

```typescript
interface SidebarProps {
  onNavigate?: () => void;
}

export function Sidebar({ onNavigate }: SidebarProps) {
  const location = useLocation();
  
  const navigationItems = [
    { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
    { name: 'Audiences', href: '/audiences', icon: Users },
    { name: 'Platforms', href: '/platforms', icon: Zap },
    { name: 'Distribution', href: '/distribution', icon: Send },
    { name: 'Analytics', href: '/analytics', icon: TrendingUp },
  ];
  
  return (
    <div className="flex flex-col h-full">
      {/* Logo and branding */}
      <div className="flex items-center gap-3 p-6 border-b border-gray-200">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <Target className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-gray-800">Activation Manager</h1>
          <p className="text-xs text-gray-500">Audience Distribution Platform</p>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigationItems.map((item) => {
          const isActive = location.pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              to={item.href}
              onClick={onNavigate}
              className={clsx(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <Icon size={20} />
              {item.name}
            </Link>
          );
        })}
      </nav>
      
      {/* User profile */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3">
          <img
            src="/headshot.jpg"
            alt="Andrew Myles"
            className="w-10 h-10 rounded-full"
          />
          <div>
            <p className="text-sm font-medium text-gray-900">Andrew Myles</p>
            <p className="text-xs text-gray-500">Marketing Director</p>
          </div>
        </div>
      </div>
    </div>
  );
}
```

## Testing Strategies

### 1. Unit Testing with Jest and React Testing Library

```typescript
// __tests__/components/VariableSelector.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { VariableSelector } from '../VariableSelector';
import { variableMetadata } from '../../data/variableMetadata';

describe('VariableSelector', () => {
  const mockOnChange = jest.fn();
  
  beforeEach(() => {
    mockOnChange.mockClear();
  });
  
  it('renders with placeholder text', () => {
    render(
      <VariableSelector 
        onChange={mockOnChange} 
        placeholder="Select variable"
      />
    );
    
    expect(screen.getByText('Select variable')).toBeInTheDocument();
  });
  
  it('opens dropdown when clicked', async () => {
    const user = userEvent.setup();
    
    render(<VariableSelector onChange={mockOnChange} />);
    
    const trigger = screen.getByRole('button');
    await user.click(trigger);
    
    expect(screen.getByPlaceholderText('Search variables...')).toBeInTheDocument();
  });
  
  it('filters variables based on search input', async () => {
    const user = userEvent.setup();
    
    render(<VariableSelector onChange={mockOnChange} />);
    
    // Open dropdown
    await user.click(screen.getByRole('button'));
    
    // Search for specific variable
    const searchInput = screen.getByPlaceholderText('Search variables...');
    await user.type(searchInput, 'age');
    
    // Check that age-related variables are shown
    expect(screen.getByText('Age')).toBeInTheDocument();
  });
  
  it('calls onChange when variable is selected', async () => {
    const user = userEvent.setup();
    
    render(<VariableSelector onChange={mockOnChange} />);
    
    // Open dropdown and select first variable
    await user.click(screen.getByRole('button'));
    
    const firstVariable = variableMetadata[0];
    await user.click(screen.getByText(firstVariable.name));
    
    expect(mockOnChange).toHaveBeenCalledWith(firstVariable.id, firstVariable);
  });
});
```

### 2. Integration Testing

```typescript
// __tests__/pages/AudienceBuilder.integration.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { AudienceBuilder } from '../pages/AudienceBuilder';

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('AudienceBuilder Integration', () => {
  it('allows creating a complete audience', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(<AudienceBuilder />);
    
    // Click create audience
    await user.click(screen.getByText('Create Audience'));
    
    // Fill in basic information
    await user.type(screen.getByLabelText('Audience Name'), 'Test Audience');
    await user.type(screen.getByLabelText('Description'), 'Test description');
    
    // Select audience type
    await user.selectOptions(screen.getByLabelText('Audience Type'), '1st-party');
    await user.selectOptions(screen.getByLabelText('Data Source'), 'rampid');
    
    // Add criteria
    await user.click(screen.getByText('Add Criteria'));
    
    // Select variable, operator, and value
    await user.click(screen.getByText('Select variable'));
    await user.click(screen.getByText('Age'));
    
    await user.selectOptions(screen.getByLabelText('Operator'), 'greater_than');
    await user.type(screen.getByLabelText('Value'), '25');
    
    // Submit form
    await user.click(screen.getByText('Save Audience'));
    
    // Verify success
    await waitFor(() => {
      expect(screen.getByText('Test Audience')).toBeInTheDocument();
    });
  });
});
```

## Performance Optimization

### 1. Memoization Strategies

```typescript
// Memoize expensive calculations
const ExpensiveComponent = memo(({ data }: { data: ComplexData[] }) => {
  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      computedValue: expensiveCalculation(item),
    }));
  }, [data]);
  
  return (
    <div>
      {processedData.map(item => (
        <div key={item.id}>{item.computedValue}</div>
      ))}
    </div>
  );
});

// Memoize callbacks
const ParentComponent = () => {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');
  
  const handleClick = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);
  
  const handleNameChange = useCallback((newName: string) => {
    setName(newName);
  }, []);
  
  return (
    <div>
      <ChildComponent onClick={handleClick} />
      <AnotherChild onNameChange={handleNameChange} />
    </div>
  );
};
```

### 2. Code Splitting and Lazy Loading

```typescript
// Route-level code splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const AudienceBuilder = lazy(() => import('./pages/AudienceBuilder'));

// Component-level code splitting
const HeavyComponent = lazy(() => import('./components/HeavyComponent'));

// Conditional component loading
const ConditionalComponent = ({ shouldLoad }: { shouldLoad: boolean }) => {
  const [Component, setComponent] = useState<React.ComponentType | null>(null);
  
  useEffect(() => {
    if (shouldLoad && !Component) {
      import('./HeavyComponent').then(module => {
        setComponent(() => module.default);
      });
    }
  }, [shouldLoad, Component]);
  
  if (!Component) return <div>Loading...</div>;
  
  return <Component />;
};
```

This component development guide provides the foundation for building all components in the Activation Manager application. Each component follows consistent patterns for maintainability, performance, and accessibility.