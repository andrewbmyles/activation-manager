# Activation Manager - Implementation Guide (Part 4)

## Variable Selector System

### Frontend Implementation

#### 1. Variable Selector Component
```typescript
// packages/frontend/src/components/VariableSelector/VariableSelector.tsx
import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { ChevronDown, Search, Info, ChevronRight } from 'lucide-react';
import { clsx } from 'clsx';
import { useVariables } from '@/hooks/useVariables';
import { Variable, VariableCategory } from '@shared/types';
import { Popover } from '@/components/ui/Popover';
import { useDebounce } from '@/hooks/useDebounce';

interface VariableSelectorProps {
  value?: string;
  onChange: (variableId: string, variable: Variable) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  error?: string;
}

export const VariableSelector: React.FC<VariableSelectorProps> = ({
  value,
  onChange,
  placeholder = 'Select a variable',
  disabled = false,
  className,
  error,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const debouncedSearch = useDebounce(search, 300);
  
  const { data: variables = [], isLoading } = useVariables();
  const selectedVariable = variables.find(v => v.id === value);

  // Filter and group variables
  const filteredAndGrouped = useMemo(() => {
    const filtered = variables.filter(variable => {
      if (!debouncedSearch) return true;
      
      const searchLower = debouncedSearch.toLowerCase();
      return (
        variable.name.toLowerCase().includes(searchLower) ||
        variable.description?.toLowerCase().includes(searchLower) ||
        variable.code.toLowerCase().includes(searchLower) ||
        variable.category.toLowerCase().includes(searchLower)
      );
    });

    // Group by category
    const grouped = filtered.reduce((acc, variable) => {
      if (!acc[variable.category]) {
        acc[variable.category] = [];
      }
      acc[variable.category].push(variable);
      return acc;
    }, {} as Record<VariableCategory, Variable[]>);

    // Sort variables within each category
    Object.values(grouped).forEach(vars => {
      vars.sort((a, b) => a.sortOrder - b.sortOrder);
    });

    return grouped;
  }, [variables, debouncedSearch]);

  const handleVariableSelect = useCallback((variable: Variable) => {
    onChange(variable.id, variable);
    setIsOpen(false);
    setSearch('');
  }, [onChange]);

  const toggleCategory = useCallback((category: string) => {
    setExpandedCategories(prev => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  }, []);

  // Auto-expand categories with search results
  useEffect(() => {
    if (debouncedSearch) {
      setExpandedCategories(new Set(Object.keys(filteredAndGrouped)));
    }
  }, [debouncedSearch, filteredAndGrouped]);

  return (
    <Popover
      isOpen={isOpen}
      onOpenChange={setIsOpen}
      trigger={
        <button
          type="button"
          disabled={disabled}
          className={clsx(
            'w-full flex items-center justify-between px-3 py-2',
            'border rounded-md transition-all',
            'focus:outline-none focus:ring-2 focus:ring-offset-2',
            disabled && 'opacity-50 cursor-not-allowed',
            error 
              ? 'border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:ring-primary',
            className
          )}
        >
          <span className={clsx(
            'truncate',
            selectedVariable ? 'text-gray-900' : 'text-gray-500'
          )}>
            {selectedVariable ? selectedVariable.name : placeholder}
          </span>
          <ChevronDown 
            className={clsx(
              'w-5 h-5 text-gray-400 transition-transform',
              isOpen && 'transform rotate-180'
            )}
          />
        </button>
      }
    >
      <div className="w-96 max-h-96 overflow-hidden flex flex-col">
        {/* Search Input */}
        <div className="p-3 border-b">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search variables..."
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              autoFocus
            />
          </div>
        </div>

        {/* Variables List */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center text-gray-500">Loading variables...</div>
          ) : Object.keys(filteredAndGrouped).length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              {search ? `No variables found for "${search}"` : 'No variables available'}
            </div>
          ) : (
            Object.entries(filteredAndGrouped).map(([category, categoryVars]) => (
              <CategorySection
                key={category}
                category={category as VariableCategory}
                variables={categoryVars}
                isExpanded={expandedCategories.has(category) || !!debouncedSearch}
                onToggle={() => toggleCategory(category)}
                onSelect={handleVariableSelect}
                selectedId={value}
                searchTerm={debouncedSearch}
              />
            ))
          )}
        </div>
      </div>
    </Popover>
  );
};

// Category Section Component
interface CategorySectionProps {
  category: VariableCategory;
  variables: Variable[];
  isExpanded: boolean;
  onToggle: () => void;
  onSelect: (variable: Variable) => void;
  selectedId?: string;
  searchTerm?: string;
}

const CategorySection: React.FC<CategorySectionProps> = ({
  category,
  variables,
  isExpanded,
  onToggle,
  onSelect,
  selectedId,
  searchTerm,
}) => {
  const categoryConfig = {
    [VariableCategory.DEMOGRAPHICS]: { icon: '👤', color: 'blue' },
    [VariableCategory.BEHAVIORAL]: { icon: '📊', color: 'green' },
    [VariableCategory.GEOGRAPHIC]: { icon: '🌍', color: 'purple' },
    [VariableCategory.TECHNOGRAPHIC]: { icon: '💻', color: 'orange' },
    [VariableCategory.TRANSACTIONAL]: { icon: '💳', color: 'pink' },
    [VariableCategory.ENGAGEMENT]: { icon: '📈', color: 'indigo' },
    [VariableCategory.CUSTOM]: { icon: '⚙️', color: 'gray' },
  };

  const config = categoryConfig[category] || { icon: '📁', color: 'gray' };

  return (
    <div className="border-b last:border-0">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">{config.icon}</span>
          <span className="font-medium text-gray-700">{category}</span>
          <span className="text-xs text-gray-500">
            {variables.length} variable{variables.length !== 1 ? 's' : ''}
          </span>
        </div>
        <ChevronRight
          className={clsx(
            'w-4 h-4 text-gray-400 transition-transform',
            isExpanded && 'transform rotate-90'
          )}
        />
      </button>

      {isExpanded && (
        <div className="bg-gray-50">
          {variables.map((variable) => (
            <VariableItem
              key={variable.id}
              variable={variable}
              onSelect={onSelect}
              isSelected={selectedId === variable.id}
              searchTerm={searchTerm}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Variable Item Component
interface VariableItemProps {
  variable: Variable;
  onSelect: (variable: Variable) => void;
  isSelected: boolean;
  searchTerm?: string;
}

const VariableItem: React.FC<VariableItemProps> = ({
  variable,
  onSelect,
  isSelected,
  searchTerm,
}) => {
  const highlightMatch = (text: string) => {
    if (!searchTerm) return text;
    
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200">{part}</mark>
      ) : (
        part
      )
    );
  };

  return (
    <button
      onClick={() => onSelect(variable)}
      className={clsx(
        'w-full text-left px-4 py-3 hover:bg-gray-100 transition-colors',
        'flex items-start gap-3',
        isSelected && 'bg-primary-50 hover:bg-primary-100'
      )}
    >
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className={clsx(
            'font-medium',
            isSelected ? 'text-primary' : 'text-gray-800'
          )}>
            {highlightMatch(variable.name)}
          </span>
          {variable.description && (
            <Tooltip content={variable.description}>
              <Info className="w-3 h-3 text-gray-400" />
            </Tooltip>
          )}
        </div>
        
        {variable.description && (
          <p className="text-sm text-gray-600 mt-1">
            {highlightMatch(variable.description)}
          </p>
        )}
        
        {variable.examples && variable.examples.length > 0 && (
          <p className="text-xs text-gray-500 mt-1">
            Examples: {variable.examples.slice(0, 3).join(', ')}
            {variable.examples.length > 3 && '...'}
          </p>
        )}
      </div>
      
      <div className="flex-shrink-0">
        <span className={clsx(
          'text-xs px-2 py-1 rounded',
          'bg-gray-100 text-gray-600'
        )}>
          {variable.dataType}
        </span>
      </div>
    </button>
  );
};
```

#### 2. Variable API Integration
```typescript
// packages/frontend/src/services/variable.service.ts
import { apiClient } from '@/lib/api-client';
import { Variable, VariableCategory } from '@shared/types';

export class VariableService {
  private static instance: VariableService;
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes

  static getInstance(): VariableService {
    if (!VariableService.instance) {
      VariableService.instance = new VariableService();
    }
    return VariableService.instance;
  }

  async getVariables(): Promise<Variable[]> {
    const cacheKey = 'variables:all';
    const cached = this.getFromCache(cacheKey);
    
    if (cached) {
      return cached;
    }

    const response = await apiClient.get<Variable[]>('/variables');
    this.setCache(cacheKey, response.data);
    
    return response.data;
  }

  async getVariable(id: string): Promise<Variable> {
    const cacheKey = `variable:${id}`;
    const cached = this.getFromCache(cacheKey);
    
    if (cached) {
      return cached;
    }

    const response = await apiClient.get<Variable>(`/variables/${id}`);
    this.setCache(cacheKey, response.data);
    
    return response.data;
  }

  async getCategories(): Promise<VariableCategory[]> {
    const response = await apiClient.get<VariableCategory[]>('/variables/categories');
    return response.data;
  }

  async searchVariables(query: string): Promise<Variable[]> {
    const response = await apiClient.get<Variable[]>('/variables/search', {
      params: { q: query },
    });
    return response.data;
  }

  async validateValue(
    variableId: string,
    operator: string,
    value: any
  ): Promise<{ valid: boolean; errors: string[] }> {
    const response = await apiClient.post('/variables/validate', {
      variableId,
      operator,
      value,
    });
    return response.data;
  }

  private getFromCache(key: string): any {
    const cached = this.cache.get(key);
    if (!cached) return null;
    
    if (Date.now() - cached.timestamp > this.CACHE_TTL) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data;
  }

  private setCache(key: string, data: any): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  clearCache(): void {
    this.cache.clear();
  }
}

// React Hook for Variables
export function useVariables() {
  const queryClient = useQueryClient();
  
  return useQuery({
    queryKey: ['variables'],
    queryFn: () => VariableService.getInstance().getVariables(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000,   // 10 minutes
    onError: (error) => {
      console.error('Failed to fetch variables:', error);
      // Show error notification
    },
  });
}

export function useVariable(id: string) {
  return useQuery({
    queryKey: ['variable', id],
    queryFn: () => VariableService.getInstance().getVariable(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useVariableValidation() {
  return useMutation({
    mutationFn: (params: {
      variableId: string;
      operator: string;
      value: any;
    }) => VariableService.getInstance().validateValue(
      params.variableId,
      params.operator,
      params.value
    ),
  });
}
```

### Backend Variable API Implementation

#### 1. Variable Controller
```typescript
// packages/backend/src/modules/variable/controllers/variable.controller.ts
import { Request, Response, NextFunction } from 'express';
import { injectable, inject } from 'inversify';
import { BaseController } from '@/common/base.controller';
import { VariableService } from '../services/variable.service';
import { requireAuth } from '@/common/guards';
import { validateQuery } from '@/common/validators';

@injectable()
export class VariableController extends BaseController {
  constructor(
    @inject(VariableService) private variableService: VariableService
  ) {
    super('VariableController');
  }

  @requireAuth()
  async list(req: Request, res: Response, next: NextFunction): Promise<void> {
    await this.execute(req, res, next, async () => {
      const variables = await this.variableService.findAll();
      return variables;
    });
  }

  @requireAuth()
  async findOne(req: Request, res: Response, next: NextFunction): Promise<void> {
    await this.execute(req, res, next, async () => {
      const variable = await this.variableService.findById(req.params.id);
      
      if (!variable) {
        throw new NotFoundException('Variable not found');
      }
      
      return variable;
    });
  }

  @requireAuth()
  async getCategories(req: Request, res: Response, next: NextFunction): Promise<void> {
    await this.execute(req, res, next, async () => {
      const categories = await this.variableService.getCategories();
      return categories;
    });
  }

  @requireAuth()
  async search(req: Request, res: Response, next: NextFunction): Promise<void> {
    await this.execute(req, res, next, async () => {
      const { q } = validateQuery(req.query, {
        q: { type: 'string', required: true, minLength: 1 },
      });
      
      const variables = await this.variableService.search(q);
      return variables;
    });
  }

  @requireAuth()
  async validateValue(req: Request, res: Response, next: NextFunction): Promise<void> {
    await this.execute(req, res, next, async () => {
      const { variableId, operator, value } = req.body;
      
      const result = await this.variableService.validateValue(
        variableId,
        operator,
        value
      );
      
      return result;
    });
  }
}

// Variable routes
export function setupVariableRoutes(controller: VariableController) {
  const router = Router();
  
  router.get('/', controller.list.bind(controller));
  router.get('/categories', controller.getCategories.bind(controller));
  router.get('/search', controller.search.bind(controller));
  router.get('/:id', controller.findOne.bind(controller));
  router.post('/validate', controller.validateValue.bind(controller));
  
  return router;
}
```

#### 2. Variable Repository with Caching
```typescript
// packages/backend/src/modules/variable/repositories/variable.repository.ts
import { injectable, inject } from 'inversify';
import { PrismaClient } from '@prisma/client';
import { Redis } from 'ioredis';
import { Variable } from '@shared/types';

@injectable()
export class VariableRepository {
  private readonly CACHE_PREFIX = 'variable:';
  private readonly CACHE_TTL = 3600; // 1 hour

  constructor(
    @inject('Prisma') private prisma: PrismaClient,
    @inject('Redis') private redis: Redis
  ) {}

  async findAll(): Promise<Variable[]> {
    const cacheKey = `${this.CACHE_PREFIX}all`;
    
    // Try cache first
    const cached = await this.redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    // Get from database
    const variables = await this.prisma.variable.findMany({
      where: { isActive: true },
      orderBy: [
        { category: 'asc' },
        { sortOrder: 'asc' },
      ],
    });

    // Cache the result
    await this.redis.setex(
      cacheKey,
      this.CACHE_TTL,
      JSON.stringify(variables)
    );

    return variables;
  }

  async findById(id: string): Promise<Variable | null> {
    const cacheKey = `${this.CACHE_PREFIX}${id}`;
    
    // Try cache first
    const cached = await this.redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    // Get from database
    const variable = await this.prisma.variable.findUnique({
      where: { id },
    });

    if (variable) {
      // Cache the result
      await this.redis.setex(
        cacheKey,
        this.CACHE_TTL,
        JSON.stringify(variable)
      );
    }

    return variable;
  }

  async findByCode(code: string): Promise<Variable | null> {
    return this.prisma.variable.findUnique({
      where: { code },
    });
  }

  async search(query: string): Promise<Variable[]> {
    return this.prisma.variable.findMany({
      where: {
        AND: [
          { isActive: true },
          {
            OR: [
              { name: { contains: query, mode: 'insensitive' } },
              { description: { contains: query, mode: 'insensitive' } },
              { code: { contains: query, mode: 'insensitive' } },
            ],
          },
        ],
      },
      orderBy: [
        { category: 'asc' },
        { sortOrder: 'asc' },
      ],
    });
  }

  async upsert(data: any): Promise<Variable> {
    const variable = await this.prisma.variable.upsert({
      where: { code: data.code },
      update: data,
      create: data,
    });

    // Invalidate cache
    await this.invalidateCache();

    return variable;
  }

  async invalidateCache(): Promise<void> {
    const keys = await this.redis.keys(`${this.CACHE_PREFIX}*`);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }
}
```

---

## Audience Builder Implementation

### Frontend Audience Builder

#### 1. Audience Builder Page Component
```typescript
// packages/frontend/src/pages/AudienceBuilder/AudienceBuilder.tsx
import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Plus, Trash2, Copy, Users } from 'lucide-react';
import { 
  useAudiences, 
  useCreateAudience, 
  useUpdateAudience,
  useAudience 
} from '@/hooks/useAudiences';
import { VariableSelector } from '@/components/VariableSelector';
import { OperatorSelector } from '@/components/OperatorSelector';
import { ValueInput } from '@/components/ValueInput';
import { AudienceList } from '@/components/AudienceList';
import { 
  AudienceFormData, 
  audienceFormSchema,
  AudienceCriteria,
  AudienceType,
  AudienceSubtype 
} from '@shared/types';

export const AudienceBuilder: React.FC = () => {
  const navigate = useNavigate();
  const { audienceId } = useParams();
  const isEditing = !!audienceId;

  const [isCreating, setIsCreating] = useState(false);
  const [criteria, setCriteria] = useState<AudienceCriteria[]>([]);
  const [estimatedSize, setEstimatedSize] = useState<number>(0);

  const { data: audiences = [], isLoading: audiencesLoading } = useAudiences();
  const { data: editingAudience } = useAudience(audienceId || '', {
    enabled: isEditing,
  });
  
  const createAudience = useCreateAudience();
  const updateAudience = useUpdateAudience();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AudienceFormData>({
    resolver: zodResolver(audienceFormSchema),
    defaultValues: {
      name: '',
      description: '',
      type: '1st-party',
      subtype: 'rampid',
      criteria: [],
    },
  });

  const audienceType = watch('type');

  // Load audience data for editing
  useEffect(() => {
    if (editingAudience) {
      reset({
        name: editingAudience.name,
        description: editingAudience.description,
        type: editingAudience.type,
        subtype: editingAudience.subtype,
      });
      setCriteria(editingAudience.criteria);
      setEstimatedSize(editingAudience.estimatedSize);
      setIsCreating(true);
    }
  }, [editingAudience, reset]);

  // Update subtype when type changes
  useEffect(() => {
    const subtypes = getSubtypesForType(audienceType);
    if (subtypes.length > 0) {
      setValue('subtype', subtypes[0].value);
    }
  }, [audienceType, setValue]);

  const handleCriteriaAdd = useCallback(() => {
    const newCriterion: AudienceCriteria = {
      id: `temp-${Date.now()}`,
      variableId: '',
      operator: 'equals',
      value: '',
      logicalOperator: 'AND',
    };
    setCriteria([...criteria, newCriterion]);
  }, [criteria]);

  const handleCriteriaUpdate = useCallback((
    id: string,
    updates: Partial<AudienceCriteria>
  ) => {
    setCriteria(criteria.map(c => 
      c.id === id ? { ...c, ...updates } : c
    ));
  }, [criteria]);

  const handleCriteriaRemove = useCallback((id: string) => {
    setCriteria(criteria.filter(c => c.id !== id));
  }, [criteria]);

  const handleVariableChange = useCallback((
    criterionId: string,
    variableId: string,
    variable: Variable
  ) => {
    handleCriteriaUpdate(criterionId, {
      variableId,
      variable,
      operator: variable.operators[0] || 'equals',
      value: '',
    });
  }, [handleCriteriaUpdate]);

  const onSubmit = async (data: AudienceFormData) => {
    try {
      const payload = {
        ...data,
        criteria: criteria.map(({ variable, ...c }) => c),
      };

      if (isEditing) {
        await updateAudience.mutateAsync({
          id: audienceId,
          data: payload,
        });
      } else {
        await createAudience.mutateAsync(payload);
      }

      setIsCreating(false);
      setCriteria([]);
      reset();
    } catch (error) {
      console.error('Failed to save audience:', error);
    }
  };

  const calculateEstimatedSize = useCallback(async () => {
    if (criteria.length === 0) {
      setEstimatedSize(0);
      return;
    }

    try {
      const response = await apiClient.post('/audiences/calculate-size', {
        criteria: criteria.map(({ variable, ...c }) => c),
      });
      setEstimatedSize(response.data.estimatedSize);
    } catch (error) {
      console.error('Failed to calculate size:', error);
    }
  }, [criteria]);

  // Recalculate size when criteria change
  useEffect(() => {
    const timer = setTimeout(calculateEstimatedSize, 500);
    return () => clearTimeout(timer);
  }, [criteria, calculateEstimatedSize]);

  if (!isCreating && !audiencesLoading) {
    return (
      <div>
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-semibold text-gray-900">
              Audience Builder
            </h1>
            <p className="text-gray-600 mt-2">
              Create and manage your audience segments
            </p>
          </div>
          <button
            onClick={() => setIsCreating(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Create Audience
          </button>
        </div>

        <AudienceList
          audiences={audiences}
          onEdit={(audience) => navigate(`/audiences/${audience.id}`)}
          onDuplicate={(audience) => {
            // Handle duplication
          }}
        />
      </div>
    );
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-gray-900">
          {isEditing ? 'Edit Audience' : 'Create New Audience'}
        </h1>
        <p className="text-gray-600 mt-2">
          Define your audience criteria to target specific users
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Information */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Basic Information</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Audience Name
              </label>
              <input
                {...register('name')}
                className={clsx(
                  'input-field',
                  errors.name && 'input-error'
                )}
                placeholder="e.g., High-Value Customers"
              />
              {errors.name && (
                <p className="text-sm text-red-600 mt-1">{errors.name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description (Optional)
              </label>
              <textarea
                {...register('description')}
                className="input-field"
                rows={3}
                placeholder="Describe this audience segment..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Audience Type
                </label>
                <select
                  {...register('type')}
                  className="input-field"
                >
                  {audienceTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data Source
                </label>
                <select
                  {...register('subtype')}
                  className="input-field"
                >
                  {getSubtypesForType(audienceType).map(subtype => (
                    <option key={subtype.value} value={subtype.value}>
                      {subtype.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Audience Criteria */}
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Audience Criteria</h2>
            <button
              type="button"
              onClick={handleCriteriaAdd}
              className="text-primary hover:text-primary-hover flex items-center gap-1"
            >
              <Plus className="w-4 h-4" />
              Add Criteria
            </button>
          </div>

          {criteria.length === 0 ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <p className="text-gray-500 mb-3">No criteria added yet</p>
              <button
                type="button"
                onClick={handleCriteriaAdd}
                className="btn-secondary"
              >
                Add First Criteria
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {criteria.map((criterion, index) => (
                <CriteriaRow
                  key={criterion.id}
                  criterion={criterion}
                  index={index}
                  isLast={index === criteria.length - 1}
                  onUpdate={(updates) => handleCriteriaUpdate(criterion.id, updates)}
                  onRemove={() => handleCriteriaRemove(criterion.id)}
                  onVariableChange={(variableId, variable) => 
                    handleVariableChange(criterion.id, variableId, variable)
                  }
                />
              ))}
            </div>
          )}
        </div>

        {/* Estimated Size */}
        <div className="card bg-primary-50 border-primary-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-700">Estimated Audience Size</p>
              <p className="text-3xl font-semibold text-gray-900 mt-1">
                {estimatedSize > 0 ? estimatedSize.toLocaleString() : '—'} users
              </p>
            </div>
            <Users className="w-12 h-12 text-primary-300" />
          </div>
          {criteria.length > 0 && estimatedSize > 0 && (
            <p className="text-xs text-gray-600 mt-3">
              This is an estimate based on your criteria. Actual audience size may vary.
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary flex-1"
          >
            {isSubmitting ? 'Saving...' : (isEditing ? 'Update Audience' : 'Create Audience')}
          </button>
          <button
            type="button"
            onClick={() => {
              setIsCreating(false);
              setCriteria([]);
              reset();
              if (isEditing) {
                navigate('/audiences');
              }
            }}
            className="btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

// Criteria Row Component
interface CriteriaRowProps {
  criterion: AudienceCriteria;
  index: number;
  isLast: boolean;
  onUpdate: (updates: Partial<AudienceCriteria>) => void;
  onRemove: () => void;
  onVariableChange: (variableId: string, variable: Variable) => void;
}

const CriteriaRow: React.FC<CriteriaRowProps> = ({
  criterion,
  index,
  isLast,
  onUpdate,
  onRemove,
  onVariableChange,
}) => {
  return (
    <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
      <div className="flex items-start gap-3">
        <div className="flex-1 space-y-3">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Variable
              </label>
              <VariableSelector
                value={criterion.variableId}
                onChange={onVariableChange}
                placeholder="Select variable"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Operator
              </label>
              <OperatorSelector
                value={criterion.operator}
                onChange={(operator) => onUpdate({ operator })}
                availableOperators={criterion.variable?.operators || ['equals']}
                disabled={!criterion.variableId}
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Value
              </label>
              <ValueInput
                value={criterion.value}
                onChange={(value) => onUpdate({ value })}
                variable={criterion.variable}
                operator={criterion.operator}
                disabled={!criterion.variableId}
              />
            </div>
          </div>
          
          {!isLast && (
            <div className="flex items-center gap-2 pt-2">
              <div className="flex-1 border-t border-gray-300" />
              <select
                value={criterion.logicalOperator}
                onChange={(e) => onUpdate({ logicalOperator: e.target.value as any })}
                className="text-xs font-medium text-gray-500 px-2 py-1 border border-gray-300 rounded"
              >
                <option value="AND">AND</option>
                <option value="OR">OR</option>
              </select>
              <div className="flex-1 border-t border-gray-300" />
            </div>
          )}
        </div>
        
        <button
          type="button"
          onClick={onRemove}
          className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
        >
          <Trash2 className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};
```

This completes Part 4 of the implementation guide, covering the Variable Selector System and Audience Builder Implementation. The guide continues with platform integration and distribution features.