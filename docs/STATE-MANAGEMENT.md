# State Management Guide

## Table of Contents
1. [State Management Overview](#state-management-overview)
2. [React Query for Server State](#react-query-for-server-state)
3. [Local State with React Hooks](#local-state-with-react-hooks)
4. [Form State Management](#form-state-management)
5. [URL State and Navigation](#url-state-and-navigation)
6. [Local Storage and Persistence](#local-storage-and-persistence)
7. [State Patterns and Best Practices](#state-patterns-and-best-practices)
8. [Error Handling](#error-handling)
9. [Performance Optimization](#performance-optimization)
10. [Testing State Logic](#testing-state-logic)

## State Management Overview

The Activation Manager uses a hybrid approach to state management, leveraging different strategies for different types of state:

### State Categories
- **Server State**: Data from APIs (React Query)
- **Client State**: UI state, form state (React hooks)
- **URL State**: Navigation, filters, pagination (React Router)
- **Persistent State**: User preferences (Local Storage)

### Architecture Principles
- **Colocation**: Keep state close to where it's used
- **Minimal State**: Only store what you can't derive
- **Single Source of Truth**: Avoid duplicate state
- **Predictable Updates**: Clear patterns for state changes

## React Query for Server State

### Query Client Setup
```typescript
// src/lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000,   // 10 minutes (formerly cacheTime)
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors
        if (error instanceof Error && 'status' in error) {
          return (error as any).status >= 500 && failureCount < 3;
        }
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      retry: false,
    },
  },
});
```

### Data Fetching Patterns
```typescript
// src/hooks/useAudiences.ts
export function useAudiences() {
  return useQuery({
    queryKey: ['audiences'],
    queryFn: async (): Promise<Audience[]> => {
      const response = await fetch('/api/audiences');
      if (!response.ok) {
        throw new Error('Failed to fetch audiences');
      }
      return response.json();
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useAudience(id: string) {
  return useQuery({
    queryKey: ['audiences', id],
    queryFn: async (): Promise<Audience> => {
      const response = await fetch(`/api/audiences/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch audience');
      }
      return response.json();
    },
    enabled: !!id, // Only run if id is provided
  });
}

// Infinite query for large datasets
export function useInfiniteAudiences() {
  return useInfiniteQuery({
    queryKey: ['audiences', 'infinite'],
    queryFn: async ({ pageParam = 1 }): Promise<PaginatedResponse<Audience>> => {
      const response = await fetch(`/api/audiences?page=${pageParam}&limit=20`);
      return response.json();
    },
    getNextPageParam: (lastPage) => 
      lastPage.hasNext ? lastPage.page + 1 : undefined,
    initialPageParam: 1,
  });
}
```

### Mutation Patterns
```typescript
// src/hooks/useAudienceActions.ts
export function useCreateAudience() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: CreateAudienceRequest): Promise<Audience> => {
      const response = await fetch('/api/audiences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to create audience');
      }
      
      return response.json();
    },
    onSuccess: (newAudience) => {
      // Update the audiences list
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

export function useUpdateAudience() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateAudienceRequest }) => {
      const response = await fetch(`/api/audiences/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      return response.json();
    },
    onSuccess: (updatedAudience, { id }) => {
      // Update the specific audience in cache
      queryClient.setQueryData(['audiences', id], updatedAudience);
      
      // Update the audiences list
      queryClient.setQueryData(['audiences'], (old: Audience[] = []) =>
        old.map(audience => 
          audience.id === id ? updatedAudience : audience
        )
      );
    },
  });
}

export function useDeleteAudience() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`/api/audiences/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Failed to delete audience');
      }
    },
    onSuccess: (_, deletedId) => {
      // Remove from audiences list
      queryClient.setQueryData(['audiences'], (old: Audience[] = []) =>
        old.filter(audience => audience.id !== deletedId)
      );
      
      // Remove individual audience cache
      queryClient.removeQueries({ queryKey: ['audiences', deletedId] });
    },
  });
}
```

### Cache Management
```typescript
// src/hooks/useCacheUtils.ts
export function useCacheUtils() {
  const queryClient = useQueryClient();
  
  const invalidateAudiences = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['audiences'] });
  }, [queryClient]);
  
  const refetchAudience = useCallback((id: string) => {
    queryClient.refetchQueries({ queryKey: ['audiences', id] });
  }, [queryClient]);
  
  const prefetchAudience = useCallback((id: string) => {
    queryClient.prefetchQuery({
      queryKey: ['audiences', id],
      queryFn: () => fetchAudience(id),
      staleTime: 10 * 60 * 1000, // 10 minutes
    });
  }, [queryClient]);
  
  const setAudienceData = useCallback((id: string, data: Audience) => {
    queryClient.setQueryData(['audiences', id], data);
  }, [queryClient]);
  
  return {
    invalidateAudiences,
    refetchAudience,
    prefetchAudience,
    setAudienceData,
  };
}
```

## Local State with React Hooks

### Component State Patterns
```typescript
// src/components/AudienceBuilder.tsx
export function AudienceBuilder() {
  // Simple state
  const [isCreating, setIsCreating] = useState(false);
  const [selectedAudience, setSelectedAudience] = useState<Audience | null>(null);
  
  // Complex state with reducer pattern
  const [criteriaState, dispatch] = useReducer(criteriaReducer, initialCriteriaState);
  
  // Derived state
  const hasUnsavedChanges = useMemo(() => {
    return criteriaState.criteria.length > 0 && !selectedAudience;
  }, [criteriaState.criteria, selectedAudience]);
  
  // State with custom hook
  const { audienceType, audienceSubtype, setAudienceType, setAudienceSubtype } = 
    useAudienceType();
  
  // Effect for state synchronization
  useEffect(() => {
    if (selectedAudience) {
      dispatch({ type: 'SET_CRITERIA', payload: selectedAudience.criteria });
    }
  }, [selectedAudience]);
  
  return (
    // Component JSX
  );
}

// Criteria reducer
interface CriteriaState {
  criteria: ExtendedAudienceCriteria[];
  estimatedSize: number;
  isCalculating: boolean;
}

type CriteriaAction = 
  | { type: 'ADD_CRITERIA'; payload: ExtendedAudienceCriteria }
  | { type: 'UPDATE_CRITERIA'; payload: { id: string; updates: Partial<ExtendedAudienceCriteria> } }
  | { type: 'REMOVE_CRITERIA'; payload: string }
  | { type: 'SET_CRITERIA'; payload: AudienceCriteria[] }
  | { type: 'SET_ESTIMATED_SIZE'; payload: number }
  | { type: 'SET_CALCULATING'; payload: boolean };

function criteriaReducer(state: CriteriaState, action: CriteriaAction): CriteriaState {
  switch (action.type) {
    case 'ADD_CRITERIA':
      return {
        ...state,
        criteria: [...state.criteria, action.payload],
      };
    
    case 'UPDATE_CRITERIA':
      return {
        ...state,
        criteria: state.criteria.map(criterion =>
          criterion.id === action.payload.id
            ? { ...criterion, ...action.payload.updates }
            : criterion
        ),
      };
    
    case 'REMOVE_CRITERIA':
      return {
        ...state,
        criteria: state.criteria.filter(criterion => criterion.id !== action.payload),
      };
    
    case 'SET_CRITERIA':
      return {
        ...state,
        criteria: action.payload.map(criterion => ({
          ...criterion,
          variable: variableMetadata.find(v => v.name === criterion.field),
        })),
      };
    
    case 'SET_ESTIMATED_SIZE':
      return {
        ...state,
        estimatedSize: action.payload,
        isCalculating: false,
      };
    
    case 'SET_CALCULATING':
      return {
        ...state,
        isCalculating: action.payload,
      };
    
    default:
      return state;
  }
}
```

### Custom Hooks for State Logic
```typescript
// src/hooks/useAudienceType.ts
export function useAudienceType(initialType: AudienceType = '1st-party') {
  const [audienceType, setAudienceType] = useState<AudienceType>(initialType);
  const [audienceSubtype, setAudienceSubtype] = useState<AudienceSubtype>('rampid');
  
  // Auto-update subtype when type changes
  useEffect(() => {
    const defaultSubtype = audienceSubtypeOptions[audienceType][0]?.value;
    if (defaultSubtype) {
      setAudienceSubtype(defaultSubtype);
    }
  }, [audienceType]);
  
  const updateType = useCallback((newType: AudienceType) => {
    setAudienceType(newType);
  }, []);
  
  const updateSubtype = useCallback((newSubtype: AudienceSubtype) => {
    setAudienceSubtype(newSubtype);
  }, []);
  
  return {
    audienceType,
    audienceSubtype,
    setAudienceType: updateType,
    setAudienceSubtype: updateSubtype,
  };
}

// src/hooks/useToggle.ts
export function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);
  
  const toggle = useCallback(() => setValue(v => !v), []);
  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);
  
  return [value, { toggle, setTrue, setFalse }] as const;
}

// src/hooks/useDebounce.ts
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);
  
  return debouncedValue;
}

// src/hooks/usePrevious.ts
export function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  
  useEffect(() => {
    ref.current = value;
  });
  
  return ref.current;
}
```

## Form State Management

### React Hook Form Integration
```typescript
// src/components/AudienceForm.tsx
interface AudienceFormProps {
  initialData?: Partial<Audience>;
  onSubmit: (data: AudienceFormData) => Promise<void>;
  onCancel?: () => void;
}

export function AudienceForm({ initialData, onSubmit, onCancel }: AudienceFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    getValues,
    reset,
    control,
    formState: { errors, isSubmitting, isDirty, isValid },
  } = useForm<AudienceFormData>({
    resolver: zodResolver(audienceFormSchema),
    defaultValues: {
      name: '',
      description: '',
      type: '1st-party',
      subtype: 'rampid',
      criteria: [],
      tags: [],
      ...initialData,
    },
    mode: 'onChange',
  });
  
  // Watch specific fields
  const audienceType = watch('type');
  const criteriaCount = watch('criteria.length');
  
  // Field array for dynamic criteria
  const { fields, append, remove, update } = useFieldArray({
    control,
    name: 'criteria',
  });
  
  // Form submission handler
  const onFormSubmit = async (data: AudienceFormData) => {
    try {
      await onSubmit(data);
      reset(); // Reset form after successful submission
    } catch (error) {
      console.error('Form submission error:', error);
      // Handle error (show toast, etc.)
    }
  };
  
  // Auto-save draft
  const formData = watch();
  const debouncedFormData = useDebounce(formData, 1000);
  
  useEffect(() => {
    if (isDirty) {
      localStorage.setItem('audience-draft', JSON.stringify(debouncedFormData));
    }
  }, [debouncedFormData, isDirty]);
  
  // Load draft on mount
  useEffect(() => {
    const draft = localStorage.getItem('audience-draft');
    if (draft && !initialData) {
      const parsedDraft = JSON.parse(draft);
      reset(parsedDraft);
    }
  }, [reset, initialData]);
  
  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
      {/* Form fields */}
      <FormField label="Name" error={errors.name?.message} required>
        <input
          {...register('name')}
          className={clsx('input-field', errors.name && 'input-error')}
        />
      </FormField>
      
      {/* Dynamic criteria fields */}
      {fields.map((field, index) => (
        <CriteriaField
          key={field.id}
          index={index}
          control={control}
          onRemove={() => remove(index)}
          errors={errors.criteria?.[index]}
        />
      ))}
      
      <button
        type="button"
        onClick={() => append(defaultCriteria)}
        className="btn-secondary"
      >
        Add Criteria
      </button>
      
      {/* Form actions */}
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={isSubmitting || !isValid}
          className="btn-primary"
        >
          {isSubmitting ? 'Saving...' : 'Save Audience'}
        </button>
        
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="btn-secondary"
          >
            Cancel
          </button>
        )}
      </div>
      
      {/* Form state indicators */}
      {isDirty && (
        <p className="text-sm text-orange-600">
          You have unsaved changes
        </p>
      )}
    </form>
  );
}
```

### Form Validation Patterns
```typescript
// src/lib/validation.ts
import { z } from 'zod';

// Base schemas
export const audienceTypeSchema = z.enum(['1st-party', '3rd-party', 'clean-room']);
export const criteriaOperatorSchema = z.enum([
  'equals', 'not_equals', 'contains', 'greater_than', 'less_than', 'between', 'in'
]);

// Complex validation schemas
export const criteriaSchema = z.object({
  variableId: z.string().min(1, 'Variable is required'),
  operator: criteriaOperatorSchema,
  value: z.union([
    z.string().min(1, 'Value is required'),
    z.number(),
    z.array(z.union([z.string(), z.number()])).min(1, 'At least one value required'),
  ]),
}).refine((data) => {
  // Custom validation based on operator
  if (data.operator === 'between' && typeof data.value === 'string') {
    return false; // Between operator requires array
  }
  return true;
}, {
  message: 'Invalid value for selected operator',
  path: ['value'],
});

export const audienceFormSchema = z.object({
  name: z.string()
    .min(1, 'Name is required')
    .max(100, 'Name must be less than 100 characters')
    .regex(/^[a-zA-Z0-9\s\-_]+$/, 'Name contains invalid characters'),
  description: z.string()
    .max(500, 'Description must be less than 500 characters')
    .optional(),
  type: audienceTypeSchema,
  subtype: z.string().min(1, 'Subtype is required'),
  criteria: z.array(criteriaSchema)
    .min(1, 'At least one criteria is required')
    .max(10, 'Maximum 10 criteria allowed'),
  tags: z.array(z.string()).max(5, 'Maximum 5 tags allowed'),
});

// Custom validation hooks
export function useFormValidation<T>(schema: z.ZodSchema<T>) {
  const validateField = useCallback((fieldName: string, value: any) => {
    try {
      const fieldSchema = schema.shape[fieldName as keyof typeof schema.shape];
      fieldSchema.parse(value);
      return null;
    } catch (error) {
      if (error instanceof z.ZodError) {
        return error.errors[0]?.message || 'Invalid value';
      }
      return 'Validation error';
    }
  }, [schema]);
  
  const validateForm = useCallback((data: T) => {
    try {
      schema.parse(data);
      return { isValid: true, errors: {} };
    } catch (error) {
      if (error instanceof z.ZodError) {
        const errors = error.errors.reduce((acc, err) => {
          const path = err.path.join('.');
          acc[path] = err.message;
          return acc;
        }, {} as Record<string, string>);
        return { isValid: false, errors };
      }
      return { isValid: false, errors: { form: 'Validation failed' } };
    }
  }, [schema]);
  
  return { validateField, validateForm };
}
```

## URL State and Navigation

### Search Params Management
```typescript
// src/hooks/useSearchParams.ts
export function useSearchParamsState<T>(
  key: string,
  defaultValue: T,
  serialize = JSON.stringify,
  deserialize = JSON.parse
) {
  const [searchParams, setSearchParams] = useSearchParams();
  
  const value = useMemo(() => {
    const param = searchParams.get(key);
    if (!param) return defaultValue;
    
    try {
      return deserialize(param);
    } catch {
      return defaultValue;
    }
  }, [searchParams, key, defaultValue, deserialize]);
  
  const setValue = useCallback((newValue: T) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev);
      if (newValue === defaultValue) {
        newParams.delete(key);
      } else {
        newParams.set(key, serialize(newValue));
      }
      return newParams;
    });
  }, [setSearchParams, key, defaultValue, serialize]);
  
  return [value, setValue] as const;
}

// Usage in components
export function AudienceList() {
  const [filters, setFilters] = useSearchParamsState('filters', {
    search: '',
    type: '',
    status: '',
  });
  
  const [sortConfig, setSortConfig] = useSearchParamsState('sort', {
    field: 'updatedAt',
    direction: 'desc',
  });
  
  const [page, setPage] = useSearchParamsState('page', 1, String, Number);
  
  return (
    // Component JSX with URL-synced state
  );
}
```

### Navigation State Management
```typescript
// src/hooks/useNavigation.ts
export function useNavigation() {
  const navigate = useNavigate();
  const location = useLocation();
  
  const navigateWithState = useCallback((
    to: string,
    state?: any,
    options?: { replace?: boolean }
  ) => {
    navigate(to, { 
      state, 
      replace: options?.replace 
    });
  }, [navigate]);
  
  const navigateBack = useCallback(() => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/dashboard');
    }
  }, [navigate]);
  
  const isCurrentPath = useCallback((path: string) => {
    return location.pathname === path;
  }, [location.pathname]);
  
  const getCurrentState = useCallback(() => {
    return location.state;
  }, [location.state]);
  
  return {
    navigate: navigateWithState,
    navigateBack,
    isCurrentPath,
    getCurrentState,
    currentPath: location.pathname,
  };
}
```

## Local Storage and Persistence

### Persistent State Hooks
```typescript
// src/hooks/useLocalStorage.ts
export function useLocalStorage<T>(
  key: string,
  defaultValue: T,
  options: {
    serialize?: (value: T) => string;
    deserialize?: (value: string) => T;
  } = {}
) {
  const {
    serialize = JSON.stringify,
    deserialize = JSON.parse,
  } = options;
  
  const [value, setValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? deserialize(item) : defaultValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return defaultValue;
    }
  });
  
  const setStoredValue = useCallback((newValue: T | ((val: T) => T)) => {
    try {
      const valueToStore = newValue instanceof Function ? newValue(value) : newValue;
      setValue(valueToStore);
      window.localStorage.setItem(key, serialize(valueToStore));
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, serialize, value]);
  
  const removeValue = useCallback(() => {
    try {
      setValue(defaultValue);
      window.localStorage.removeItem(key);
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, defaultValue]);
  
  return [value, setStoredValue, removeValue] as const;
}

// src/hooks/usePreferences.ts
export function usePreferences() {
  const [preferences, setPreferences] = useLocalStorage('user-preferences', {
    theme: 'light' as 'light' | 'dark' | 'system',
    sidebarCollapsed: false,
    defaultPageSize: 20,
    autoRefresh: true,
    refreshInterval: 30000,
    notifications: {
      email: true,
      push: false,
    },
  });
  
  const updatePreference = useCallback(<K extends keyof typeof preferences>(
    key: K,
    value: typeof preferences[K]
  ) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  }, [setPreferences]);
  
  return {
    preferences,
    updatePreference,
    setPreferences,
  };
}
```

### Session Storage for Temporary State
```typescript
// src/hooks/useSessionStorage.ts
export function useSessionStorage<T>(key: string, defaultValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch {
      return defaultValue;
    }
  });
  
  const setStoredValue = useCallback((newValue: T | ((val: T) => T)) => {
    try {
      const valueToStore = newValue instanceof Function ? newValue(value) : newValue;
      setValue(valueToStore);
      window.sessionStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.warn(`Error setting sessionStorage key "${key}":`, error);
    }
  }, [key, value]);
  
  return [value, setStoredValue] as const;
}

// Usage for form drafts and temporary state
export function useFormDraft(formId: string) {
  const [draft, setDraft] = useSessionStorage(`form-draft-${formId}`, null);
  
  const saveDraft = useCallback((data: any) => {
    setDraft({
      data,
      timestamp: Date.now(),
    });
  }, [setDraft]);
  
  const clearDraft = useCallback(() => {
    setDraft(null);
  }, [setDraft]);
  
  const hasDraft = draft && Date.now() - draft.timestamp < 24 * 60 * 60 * 1000; // 24 hours
  
  return {
    draft: hasDraft ? draft.data : null,
    saveDraft,
    clearDraft,
    hasDraft: !!hasDraft,
  };
}
```

## State Patterns and Best Practices

### State Composition Patterns
```typescript
// Compound state hook
export function useAudienceBuilder() {
  // Individual state pieces
  const { audiences, isLoading, createAudience } = useAudiences();
  const { audienceType, audienceSubtype, setAudienceType } = useAudienceType();
  const [criteriaState, dispatch] = useReducer(criteriaReducer, initialState);
  const { draft, saveDraft, clearDraft } = useFormDraft('audience-builder');
  
  // Derived state
  const estimatedSize = useMemo(() => 
    calculateAudienceSize(criteriaState.criteria), [criteriaState.criteria]
  );
  
  const hasUnsavedChanges = useMemo(() => 
    criteriaState.criteria.length > 0, [criteriaState.criteria]
  );
  
  // Combined actions
  const addCriteria = useCallback((criteria: AudienceCriteria) => {
    dispatch({ type: 'ADD_CRITERIA', payload: criteria });
    saveDraft({ type: audienceType, subtype: audienceSubtype, criteria });
  }, [dispatch, saveDraft, audienceType, audienceSubtype]);
  
  const saveAudience = useCallback(async (data: CreateAudienceRequest) => {
    await createAudience.mutateAsync(data);
    dispatch({ type: 'RESET' });
    clearDraft();
  }, [createAudience, dispatch, clearDraft]);
  
  return {
    // State
    audiences,
    isLoading,
    audienceType,
    audienceSubtype,
    criteria: criteriaState.criteria,
    estimatedSize,
    hasUnsavedChanges,
    draft,
    
    // Actions
    setAudienceType,
    addCriteria,
    updateCriteria: dispatch,
    saveAudience,
    clearDraft,
  };
}
```

### Error Boundary Integration
```typescript
// src/hooks/useErrorHandler.ts
export function useErrorHandler() {
  const [error, setError] = useState<Error | null>(null);
  
  const handleError = useCallback((error: Error | string) => {
    const errorObj = typeof error === 'string' ? new Error(error) : error;
    setError(errorObj);
    
    // Log to error reporting service
    console.error('Application error:', errorObj);
  }, []);
  
  const clearError = useCallback(() => {
    setError(null);
  }, []);
  
  // Automatically clear error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(clearError, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);
  
  return {
    error,
    handleError,
    clearError,
    hasError: !!error,
  };
}
```

### Performance Optimization
```typescript
// Memoization patterns
export function useOptimizedState<T>(
  initialState: T,
  dependencies: React.DependencyList
) {
  const [state, setState] = useState<T>(initialState);
  
  const memoizedState = useMemo(() => state, dependencies);
  
  const optimizedSetState = useCallback((
    newState: T | ((prevState: T) => T)
  ) => {
    setState(prev => {
      const nextState = typeof newState === 'function' 
        ? (newState as (prevState: T) => T)(prev)
        : newState;
      
      // Only update if state actually changed
      return JSON.stringify(prev) !== JSON.stringify(nextState) 
        ? nextState 
        : prev;
    });
  }, []);
  
  return [memoizedState, optimizedSetState] as const;
}

// Debounced state updates
export function useDebouncedState<T>(
  initialValue: T,
  delay: number
) {
  const [immediateValue, setImmediateValue] = useState<T>(initialValue);
  const [debouncedValue, setDebouncedValue] = useState<T>(initialValue);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(immediateValue);
    }, delay);
    
    return () => clearTimeout(timer);
  }, [immediateValue, delay]);
  
  return [debouncedValue, setImmediateValue, immediateValue] as const;
}
```

This comprehensive state management guide provides patterns and best practices for managing all types of state in the Activation Manager application, ensuring predictable and performant state updates throughout the application lifecycle.