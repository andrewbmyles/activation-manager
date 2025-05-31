import { useState, useEffect, useCallback, useRef } from 'react';
import { VariableMetadata } from '../data/variableMetadata';

interface SearchResult {
  results: VariableMetadata[];
  totalCount: number;
  searchTime: number;
  fromCache: boolean;
}

interface SearchCache {
  [query: string]: {
    results: VariableMetadata[];
    timestamp: number;
  };
}

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
const MAX_CACHE_SIZE = 100;

export function useVariableSearch(allVariables: VariableMetadata[]) {
  const [isSearching, setIsSearching] = useState(false);
  const searchCache = useRef<SearchCache>({});
  const cacheKeys = useRef<string[]>([]);

  // Clean up old cache entries
  const cleanCache = useCallback(() => {
    const now = Date.now();
    const keysToRemove: string[] = [];

    Object.entries(searchCache.current).forEach(([key, value]) => {
      if (now - value.timestamp > CACHE_DURATION) {
        keysToRemove.push(key);
      }
    });

    keysToRemove.forEach(key => {
      delete searchCache.current[key];
      const index = cacheKeys.current.indexOf(key);
      if (index > -1) {
        cacheKeys.current.splice(index, 1);
      }
    });
  }, []);

  // Manage cache size
  const addToCache = useCallback((query: string, results: VariableMetadata[]) => {
    // Clean old entries first
    cleanCache();

    // If cache is full, remove oldest entry
    if (cacheKeys.current.length >= MAX_CACHE_SIZE) {
      const oldestKey = cacheKeys.current.shift();
      if (oldestKey) {
        delete searchCache.current[oldestKey];
      }
    }

    // Add new entry
    searchCache.current[query] = {
      results,
      timestamp: Date.now()
    };
    cacheKeys.current.push(query);
  }, [cleanCache]);

  // Optimized search function
  const searchVariables = useCallback(async (
    query: string,
    options?: {
      limit?: number;
      categories?: string[];
      onlyWithDescriptions?: boolean;
    }
  ): Promise<SearchResult> => {
    const startTime = performance.now();
    const searchKey = `${query}_${JSON.stringify(options || {})}`;

    // Check cache first
    const cached = searchCache.current[searchKey];
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      return {
        results: cached.results,
        totalCount: cached.results.length,
        searchTime: 0,
        fromCache: true
      };
    }

    setIsSearching(true);

    try {
      const searchLower = query.toLowerCase().trim();
      
      if (!searchLower) {
        setIsSearching(false);
        return {
          results: [],
          totalCount: 0,
          searchTime: performance.now() - startTime,
          fromCache: false
        };
      }

      // Perform search with optimizations
      let results = allVariables.filter(variable => {
        // Apply category filter if specified
        if (options?.categories && !options.categories.includes(variable.category)) {
          return false;
        }

        // Apply description filter if specified
        if (options?.onlyWithDescriptions && !variable.description) {
          return false;
        }

        // Search optimization: check most likely fields first
        if (variable.name.toLowerCase().includes(searchLower)) return true;
        if (variable.id.toLowerCase().includes(searchLower)) return true;
        
        // Only search description for longer queries
        if (searchLower.length > 2 && variable.description?.toLowerCase().includes(searchLower)) {
          return true;
        }

        // Search in examples for very specific queries
        if (searchLower.length > 4 && variable.examples) {
          return variable.examples.some(ex => ex.toLowerCase().includes(searchLower));
        }

        return false;
      });

      // Sort results by relevance
      results = results.sort((a, b) => {
        // Exact matches first
        const aExact = a.name.toLowerCase() === searchLower || a.id.toLowerCase() === searchLower;
        const bExact = b.name.toLowerCase() === searchLower || b.id.toLowerCase() === searchLower;
        if (aExact && !bExact) return -1;
        if (!aExact && bExact) return 1;

        // Then by name starts with
        const aStarts = a.name.toLowerCase().startsWith(searchLower);
        const bStarts = b.name.toLowerCase().startsWith(searchLower);
        if (aStarts && !bStarts) return -1;
        if (!aStarts && bStarts) return 1;

        // Then by sort order
        return a.sortOrder - b.sortOrder;
      });

      // Apply limit if specified
      const limitedResults = options?.limit ? results.slice(0, options.limit) : results;

      // Cache the results
      addToCache(searchKey, limitedResults);

      const searchTime = performance.now() - startTime;

      setIsSearching(false);
      return {
        results: limitedResults,
        totalCount: results.length,
        searchTime,
        fromCache: false
      };
    } catch (error) {
      console.error('Search error:', error);
      setIsSearching(false);
      return {
        results: [],
        totalCount: 0,
        searchTime: performance.now() - startTime,
        fromCache: false
      };
    }
  }, [allVariables, addToCache]);

  // Get variables by category with caching
  const getVariablesByCategory = useCallback((category: string): VariableMetadata[] => {
    const cacheKey = `category_${category}`;
    const cached = searchCache.current[cacheKey];
    
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      return cached.results;
    }

    const results = allVariables
      .filter(v => v.category === category)
      .sort((a, b) => {
        if (a.hierarchy !== b.hierarchy) return a.hierarchy - b.hierarchy;
        return a.sortOrder - b.sortOrder;
      });

    addToCache(cacheKey, results);
    return results;
  }, [allVariables, addToCache]);

  // Periodic cache cleanup
  useEffect(() => {
    const interval = setInterval(cleanCache, 60000); // Clean every minute
    return () => clearInterval(interval);
  }, [cleanCache]);

  return {
    searchVariables,
    getVariablesByCategory,
    isSearching,
    clearCache: () => {
      searchCache.current = {};
      cacheKeys.current = [];
    }
  };
}