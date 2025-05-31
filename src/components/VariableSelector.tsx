import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Search, Info, ChevronRight } from 'lucide-react';
import { clsx } from 'clsx';
import { variableMetadata, variableCategories, VariableMetadata } from '../data/variableMetadata';

interface VariableSelectorProps {
  value?: string;
  onChange: (variableId: string, variable: VariableMetadata) => void;
  placeholder?: string;
  className?: string;
}

export function VariableSelector({ value, onChange, placeholder = "Select a variable", className }: VariableSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Get selected variable
  const selectedVariable = variableMetadata.find(v => v.id === value);

  // Filter variables based on search
  const filteredVariables = variableMetadata.filter(variable => {
    const searchLower = search.toLowerCase();
    return (
      variable.name.toLowerCase().includes(searchLower) ||
      variable.category.toLowerCase().includes(searchLower) ||
      variable.description?.toLowerCase().includes(searchLower) ||
      variable.id.toLowerCase().includes(searchLower)
    );
  });

  // Group variables by category
  const groupedVariables = variableCategories.reduce((acc, category) => {
    const categoryVars = filteredVariables
      .filter(v => v.category === category)
      .sort((a, b) => {
        // Sort by hierarchy first, then by sortOrder
        if (a.hierarchy !== b.hierarchy) return a.hierarchy - b.hierarchy;
        return a.sortOrder - b.sortOrder;
      });
    
    if (categoryVars.length > 0) {
      acc[category] = categoryVars;
    }
    return acc;
  }, {} as Record<string, VariableMetadata[]>);

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

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const handleVariableSelect = (variable: VariableMetadata) => {
    onChange(variable.id, variable);
    setIsOpen(false);
    setSearch('');
  };

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
        <div className="absolute z-50 mt-1 w-full bg-white rounded-md shadow-lg border border-gray-200 max-h-96 overflow-hidden">
          {/* Search Input */}
          <div className="p-3 border-b border-gray-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                ref={inputRef}
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search variables..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary text-sm"
              />
            </div>
          </div>

          {/* Variables List */}
          <div className="overflow-y-auto max-h-80">
            {Object.keys(groupedVariables).length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No variables found matching "{search}"
              </div>
            ) : (
              Object.entries(groupedVariables).map(([category, variables]) => (
                <div key={category} className="border-b border-gray-100 last:border-0">
                  {/* Category Header */}
                  <button
                    onClick={() => toggleCategory(category)}
                    className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <span className="font-medium text-gray-700">{category}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500">
                        {variables.length} variable{variables.length !== 1 ? 's' : ''}
                      </span>
                      <ChevronRight
                        size={16}
                        className={clsx(
                          "text-gray-400 transition-transform",
                          (expandedCategories.has(category) || search) && "transform rotate-90"
                        )}
                      />
                    </div>
                  </button>

                  {/* Variables in Category */}
                  {(expandedCategories.has(category) || search) && (
                    <div className="bg-white">
                      {variables.map((variable) => (
                        <button
                          key={variable.id}
                          onClick={() => handleVariableSelect(variable)}
                          className={clsx(
                            "w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors flex items-start gap-3",
                            variable.hierarchy > 1 && "pl-8",
                            variable.hierarchy > 2 && "pl-12",
                            value === variable.id && "bg-primary/5"
                          )}
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className={clsx(
                                "font-medium",
                                value === variable.id ? "text-primary" : "text-gray-800"
                              )}>
                                {variable.name}
                              </span>
                              {variable.tooltip && (
                                <div className="group relative">
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
                              <p className="text-sm text-gray-500 mt-1">{variable.description}</p>
                            )}
                            {variable.examples && variable.examples.length > 0 && (
                              <p className="text-xs text-gray-400 mt-1">
                                Examples: {variable.examples.slice(0, 3).join(', ')}
                                {variable.examples.length > 3 && '...'}
                              </p>
                            )}
                          </div>
                          <div className="flex-shrink-0">
                            <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                              {variable.dataType}
                            </span>
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}