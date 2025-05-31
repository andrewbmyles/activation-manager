import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { VariableSizeList as List } from 'react-window';
import { ChevronDown, Search, Info, ChevronRight, Loader2, Zap } from 'lucide-react';
import { clsx } from 'clsx';
import { variableMetadata, variableCategories, VariableMetadata } from '../data/variableMetadata';
import { useVariableSearch } from '../hooks/useVariableSearch';

interface VariableSelectorProps {
  value?: string;
  onChange: (variableId: string, variable: VariableMetadata) => void;
  placeholder?: string;
  className?: string;
}

interface FlattenedItem {
  type: 'category' | 'variable';
  category?: string;
  variable?: VariableMetadata;
  index: number;
  depth: number;
}

// Debounce hook
function useDebounce<T>(value: T, delay: number): T {
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

export function EnhancedVariableSelector({ 
  value, 
  onChange, 
  placeholder = "Select a variable", 
  className 
}: VariableSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [searchStats, setSearchStats] = useState<{ time: number; cached: boolean } | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<List>(null);

  // Use optimized search hook
  const { searchVariables, getVariablesByCategory, isSearching } = useVariableSearch(variableMetadata);

  // Debounced search value
  const debouncedSearch = useDebounce(search, 300);

  // Get selected variable
  const selectedVariable = variableMetadata.find(v => v.id === value);

  // Filter variables based on search with performance optimization
  const filteredData = useMemo(() => {
    const grouped: Record<string, VariableMetadata[]> = {};
    
    // If no search, group by category
    if (!debouncedSearch) {
      variableCategories.forEach(category => {
        const categoryVars = getVariablesByCategory(category);
        if (categoryVars.length > 0) {
          grouped[category] = categoryVars;
        }
      });
      return grouped;
    }

    // For search, we'll update this asynchronously
    return grouped;
  }, [debouncedSearch, getVariablesByCategory]);

  // Async search handling
  const [searchResults, setSearchResults] = useState<Record<string, VariableMetadata[]>>({});
  
  useEffect(() => {
    if (debouncedSearch) {
      searchVariables(debouncedSearch, { limit: 500 }).then(result => {
        // Group search results by category
        const grouped = variableCategories.reduce((acc, category) => {
          const categoryVars = result.results.filter(v => v.category === category);
          if (categoryVars.length > 0) {
            acc[category] = categoryVars;
          }
          return acc;
        }, {} as Record<string, VariableMetadata[]>);
        
        setSearchResults(grouped);
        setSearchStats({ time: result.searchTime, cached: result.fromCache });
      });
    } else {
      setSearchResults({});
      setSearchStats(null);
    }
  }, [debouncedSearch, searchVariables]);

  // Use search results when available, otherwise use filtered data
  const displayData = debouncedSearch ? searchResults : filteredData;

  // Flatten data for virtualization
  const flattenedData = useMemo(() => {
    const items: FlattenedItem[] = [];
    let index = 0;

    Object.entries(displayData).forEach(([category, variables]) => {
      // Add category header
      items.push({
        type: 'category',
        category,
        index: index++,
        depth: 0
      });

      // Add variables if category is expanded or searching
      if (expandedCategories.has(category) || debouncedSearch) {
        variables.forEach(variable => {
          items.push({
            type: 'variable',
            variable,
            category,
            index: index++,
            depth: variable.hierarchy || 1
          });
        });
      }
    });

    return items;
  }, [displayData, expandedCategories, debouncedSearch]);

  // Handle click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus search input when dropdown opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Reset search when closing
  useEffect(() => {
    if (!isOpen) {
      setSearch('');
    }
  }, [isOpen]);

  const toggleCategory = useCallback((category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  }, [expandedCategories]);

  const handleVariableSelect = useCallback((variable: VariableMetadata) => {
    onChange(variable.id, variable);
    setIsOpen(false);
    setSearch('');
  }, [onChange]);

  // Row renderer for react-window
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const item = flattenedData[index];
    
    if (item.type === 'category') {
      const variables = displayData[item.category!];
      const isExpanded = expandedCategories.has(item.category!) || debouncedSearch;
      
      return (
        <div style={style}>
          <button
            onClick={() => toggleCategory(item.category!)}
            className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors border-b border-gray-200"
          >
            <span className="font-medium text-gray-700">{item.category}</span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">
                {variables.length} variable{variables.length !== 1 ? 's' : ''}
              </span>
              <ChevronRight
                size={16}
                className={clsx(
                  "text-gray-400 transition-transform",
                  isExpanded && "transform rotate-90"
                )}
              />
            </div>
          </button>
        </div>
      );
    }

    const variable = item.variable!;
    const isSelected = value === variable.id;

    return (
      <div style={style}>
        <button
          onClick={() => handleVariableSelect(variable)}
          className={clsx(
            "w-full text-left px-4 py-2 hover:bg-gray-50 transition-colors flex items-start gap-3",
            item.depth > 1 && "pl-8",
            item.depth > 2 && "pl-12",
            isSelected && "bg-primary/5"
          )}
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className={clsx(
                "font-medium truncate",
                isSelected ? "text-primary" : "text-gray-800"
              )}>
                {variable.name}
              </span>
              {variable.tooltip && (
                <div className="group relative flex-shrink-0">
                  <Info size={14} className="text-gray-400" />
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-50">
                    <div className="bg-gray-900 text-white text-xs rounded px-3 py-2 whitespace-nowrap max-w-xs">
                      {variable.tooltip}
                      <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                        <div className="border-4 border-transparent border-t-gray-900"></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            {variable.description && (
              <p className="text-sm text-gray-500 mt-0.5 truncate">{variable.description}</p>
            )}
          </div>
          <div className="flex-shrink-0">
            <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
              {variable.dataType}
            </span>
          </div>
        </button>
      </div>
    );
  };

  // Calculate item height
  const getItemSize = useCallback((index: number) => {
    const item = flattenedData[index];
    if (item.type === 'category') return 52; // Category header height
    return item.variable?.description ? 64 : 48; // Variable height
  }, [flattenedData]);

  // Reset list cache when data changes
  useEffect(() => {
    if (listRef.current) {
      listRef.current.resetAfterIndex(0);
    }
  }, [flattenedData]);

  return (
    <div ref={dropdownRef} className={clsx("relative", className)}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full input-field flex items-center justify-between text-left"
      >
        <span className={clsx(
          "truncate",
          selectedVariable ? "text-gray-800" : "text-gray-400"
        )}>
          {selectedVariable ? selectedVariable.name : placeholder}
        </span>
        <ChevronDown 
          size={20} 
          className={clsx(
            "text-gray-400 transition-transform flex-shrink-0",
            isOpen && "transform rotate-180"
          )} 
        />
      </button>

      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white rounded-md shadow-lg border border-gray-200 overflow-hidden">
          {/* Search Input */}
          <div className="p-3 border-b border-gray-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                ref={inputRef}
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search 49,000+ variables..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary text-sm"
              />
              {isSearching && (
                <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 animate-spin" size={18} />
              )}
            </div>
          </div>

          {/* Virtualized Variables List */}
          <div className="relative">
            {flattenedData.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                {isSearching ? (
                  <div className="flex items-center justify-center gap-2">
                    <Loader2 className="animate-spin" size={20} />
                    <span>Searching...</span>
                  </div>
                ) : (
                  `No variables found matching "${search}"`
                )}
              </div>
            ) : (
              <List
                ref={listRef}
                height={400}
                itemCount={flattenedData.length}
                itemSize={getItemSize}
                width="100%"
                overscanCount={5}
              >
                {Row}
              </List>
            )}
          </div>

          {/* Footer with count and performance stats */}
          <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-600">
            <div className="flex items-center justify-between">
              <div>
                {debouncedSearch ? (
                  <span>
                    Found {flattenedData.filter(item => item.type === 'variable').length} variables
                  </span>
                ) : (
                  <span>
                    {Object.keys(displayData).length} categories • {variableMetadata.length.toLocaleString()} total variables
                  </span>
                )}
              </div>
              {searchStats && debouncedSearch && (
                <div className="flex items-center gap-2">
                  <Zap className={clsx(
                    "w-3 h-3",
                    searchStats.cached ? "text-green-600" : "text-blue-600"
                  )} />
                  <span className="text-gray-500">
                    {searchStats.time.toFixed(0)}ms
                    {searchStats.cached && " (cached)"}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}