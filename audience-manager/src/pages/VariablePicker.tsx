import React, { useState } from 'react';
import { Search, Check, RefreshCw, Download } from 'lucide-react';

interface Variable {
  code: string;
  description: string;
  category: string;
  type: string;
  score: number;
  search_method?: string;
  keywords?: string[];
}

interface VariablePickerSession {
  session_id: string;
  query: string;
  suggested_count: number;
  variables: Variable[];
  status: string;
}

const VariablePicker: React.FC = () => {
  const [query, setQuery] = useState('');
  const [session, setSession] = useState<VariablePickerSession | null>(null);
  const [selectedVariables, setSelectedVariables] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(false);
  const [refinementQuery, setRefinementQuery] = useState('');
  const [confirmedVariables, setConfirmedVariables] = useState<Variable[]>([]);
  const [showConfirmed, setShowConfirmed] = useState(false);

  // Start a new search
  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      // Use relative URL to leverage proxy
      const response = await fetch('/api/variable-picker/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 30 })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error:', errorText);
        throw new Error(`Search failed: ${response.status}`);
      }

      const data = await response.json();
      setSession(data);
      setSelectedVariables(new Set());
      setShowConfirmed(false);
    } catch (error: any) {
      console.error('Search error:', error);
      alert(`Failed to search variables: ${error?.message || error}\n\nMake sure the backend is running on port 5000.`);
    } finally {
      setIsLoading(false);
    }
  };

  // Refine the search
  const handleRefine = async () => {
    if (!refinementQuery.trim() || !session) return;

    setIsLoading(true);
    try {
      const excludeCodes = Array.from(selectedVariables);
      const response = await fetch(`/api/variable-picker/refine/${session.session_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          refinement: refinementQuery,
          exclude_codes: excludeCodes 
        })
      });

      if (!response.ok) throw new Error('Refinement failed');

      const data = await response.json();
      setSession(data);
      setRefinementQuery('');
    } catch (error) {
      console.error('Refinement error:', error);
      alert('Failed to refine search. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Toggle variable selection
  const toggleVariable = (code: string) => {
    const newSelected = new Set(selectedVariables);
    if (newSelected.has(code)) {
      newSelected.delete(code);
    } else {
      newSelected.add(code);
    }
    setSelectedVariables(newSelected);
  };

  // Confirm selected variables
  const handleConfirm = async () => {
    if (!session || selectedVariables.size === 0) return;

    setIsLoading(true);
    try {
      const response = await fetch(`/api/variable-picker/confirm/${session.session_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          confirmed_codes: Array.from(selectedVariables) 
        })
      });

      if (!response.ok) throw new Error('Confirmation failed');

      const data = await response.json();
      setConfirmedVariables(data.confirmed_variables);
      setShowConfirmed(true);
    } catch (error) {
      console.error('Confirmation error:', error);
      alert('Failed to confirm variables. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Export variables
  const handleExport = async (format: 'json' | 'csv' | 'list') => {
    if (!session) return;

    try {
      const response = await fetch(`/api/variable-picker/export/${session.session_id}?format=${format}`);
      
      if (!response.ok) throw new Error('Export failed');

      if (format === 'csv') {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `variables_${session.session_id}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        const data = await response.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `variables_${session.session_id}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export variables. Please try again.');
    }
  };

  // Reset to start new search
  const handleReset = () => {
    setQuery('');
    setSession(null);
    setSelectedVariables(new Set());
    setRefinementQuery('');
    setConfirmedVariables([]);
    setShowConfirmed(false);
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">Variable Picker</h1>
        <p className="text-sm text-gray-600 mt-1">
          Use natural language to find relevant variables for your analysis
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* Search Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Describe the variables you're looking for
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="e.g., young affluent millennials who shop online frequently"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={showConfirmed}
                />
                <button
                  onClick={handleSearch}
                  disabled={!query.trim() || isLoading || showConfirmed}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Search className="w-4 h-4" />
                  Search
                </button>
                {(session || showConfirmed) && (
                  <button
                    onClick={handleReset}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    New Search
                  </button>
                )}
              </div>
            </div>

            {/* Refinement Section */}
            {session && !showConfirmed && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Refine your search (optional)
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={refinementQuery}
                    onChange={(e) => setRefinementQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleRefine()}
                    placeholder="Add more criteria or exclude certain types"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    onClick={handleRefine}
                    disabled={!refinementQuery.trim() || isLoading}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-400"
                  >
                    Refine
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        {session && !showConfirmed && (
          <div className="bg-white rounded-lg shadow-sm">
            <div className="px-6 py-4 border-b flex justify-between items-center">
              <h2 className="text-lg font-semibold">
                Found {session.suggested_count} Variables
              </h2>
              <div className="text-sm text-gray-600">
                {selectedVariables.size} selected
              </div>
            </div>

            <div className="max-h-96 overflow-y-auto">
              {session.variables.map((variable) => (
                <div
                  key={variable.code}
                  className={`px-6 py-4 border-b hover:bg-gray-50 cursor-pointer transition-colors ${
                    selectedVariables.has(variable.code) ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => toggleVariable(variable.code)}
                >
                  <div className="flex items-start gap-3">
                    <div className={`mt-1 w-5 h-5 border-2 rounded flex items-center justify-center ${
                      selectedVariables.has(variable.code) 
                        ? 'bg-blue-600 border-blue-600' 
                        : 'border-gray-300'
                    }`}>
                      {selectedVariables.has(variable.code) && (
                        <Check className="w-3 h-3 text-white" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="font-medium text-gray-900">{variable.code}</div>
                          <div className="text-sm text-gray-600 mt-1">{variable.description}</div>
                          <div className="flex gap-4 mt-2 text-xs text-gray-500">
                            <span>Category: {variable.category}</span>
                            <span>Type: {variable.type}</span>
                            <span>Score: {variable.score.toFixed(1)}</span>
                            {variable.search_method && (
                              <span className="text-blue-600">
                                {variable.search_method === 'semantic' ? '🧠' : '🔤'} {variable.search_method}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="px-6 py-4 bg-gray-50 flex justify-between items-center">
              <button
                onClick={() => setSelectedVariables(new Set())}
                disabled={selectedVariables.size === 0}
                className="text-sm text-gray-600 hover:text-gray-900 disabled:text-gray-400"
              >
                Clear Selection
              </button>
              <button
                onClick={handleConfirm}
                disabled={selectedVariables.size === 0 || isLoading}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 flex items-center gap-2"
              >
                <Check className="w-4 h-4" />
                Confirm {selectedVariables.size} Variables
              </button>
            </div>
          </div>
        )}

        {/* Confirmed Variables Section */}
        {showConfirmed && confirmedVariables.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm">
            <div className="px-6 py-4 border-b bg-green-50">
              <h2 className="text-lg font-semibold text-green-900">
                ✓ {confirmedVariables.length} Variables Confirmed
              </h2>
            </div>

            <div className="max-h-96 overflow-y-auto">
              {confirmedVariables.map((variable) => (
                <div key={variable.code} className="px-6 py-4 border-b">
                  <div className="font-medium text-gray-900">{variable.code}</div>
                  <div className="text-sm text-gray-600 mt-1">{variable.description}</div>
                  <div className="flex gap-4 mt-2 text-xs text-gray-500">
                    <span>Category: {variable.category}</span>
                    <span>Type: {variable.type}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="px-6 py-4 bg-gray-50 flex gap-2">
              <button
                onClick={() => handleExport('json')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export JSON
              </button>
              <button
                onClick={() => handleExport('csv')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export CSV
              </button>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VariablePicker;