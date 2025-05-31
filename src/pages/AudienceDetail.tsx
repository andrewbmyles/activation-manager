import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ChevronLeft, Users, Target, Sliders, ToggleLeft, ToggleRight,
  Database, Search, Plus, X, Filter, Zap
} from 'lucide-react';

interface Variable {
  code: string;
  description: string;
  score?: number;
  impact?: number;
}

interface AudienceData {
  id: string;
  name: string;
  enhanced_name?: string;
  description: string;
  natural_language_criteria?: string;
  audience_size: number;
  created_at: string;
  selected_variables: string[];
  insights?: string[];
  data_type?: string;
}

const AudienceDetail: React.FC = () => {
  const { audienceId } = useParams<{ audienceId: string }>();
  const navigate = useNavigate();
  
  // State
  const [audience, setAudience] = useState<AudienceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showManualSelection, setShowManualSelection] = useState(false);
  
  // Semantic Variable Picker State
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Variable[]>([]);
  const [selectedVariables, setSelectedVariables] = useState<Variable[]>([]);
  const [searching, setSearching] = useState(false);
  const [currentAudienceSize, setCurrentAudienceSize] = useState(0);
  
  // Slider State
  const [experimentScale, setExperimentScale] = useState(1.0);
  const [seedAudienceScale, setSeedAudienceScale] = useState(1.0);
  
  // Toggle State
  const [hardFilters, setHardFilters] = useState({
    excludeExistingCustomers: false,
    requireEmailPermission: true,
    excludeCompetitorCustomers: false,
    requireRecentActivity: true,
    excludeSuppressedUsers: true
  });

  useEffect(() => {
    loadAudience();
  }, [audienceId]);

  const loadAudience = async () => {
    try {
      const response = await fetch(`/api/audiences/${audienceId}?user_id=demo_user`);
      const data = await response.json();
      
      if (data.success && data.audience) {
        setAudience(data.audience);
        setCurrentAudienceSize(data.audience.audience_size);
      } else {
        // Use mock data for demo purposes
        const mockAudience = {
          id: audienceId || 'demo-audience',
          name: 'Gaming Enthusiasts Q4',
          enhanced_name: 'Gaming-Enthusiast Gen Z Males',
          description: 'Find males aged 18-24 interested in gaming',
          natural_language_criteria: 'Males between ages 18-24 who are interested in video games',
          audience_size: 67842,
          selected_variables: ['AGE_18_24', 'GENDER_MALE', 'GAMING_INTEREST'],
          insights: [
            'Focused audience of 68K+ targeted users',
            'Digital-native generation',
            'High engagement with gaming content'
          ],
          created_at: new Date().toISOString()
        };
        setAudience(mockAudience);
        setCurrentAudienceSize(mockAudience.audience_size);
      }
    } catch (error) {
      console.error('Error loading audience:', error);
      // Use mock data on error
      const mockAudience = {
        id: audienceId || 'demo-audience',
        name: 'Gaming Enthusiasts Q4',
        enhanced_name: 'Gaming-Enthusiast Gen Z Males',
        description: 'Find males aged 18-24 interested in gaming',
        natural_language_criteria: 'Males between ages 18-24 who are interested in video games',
        audience_size: 67842,
        selected_variables: ['AGE_18_24', 'GENDER_MALE', 'GAMING_INTEREST'],
        insights: [
          'Focused audience of 68K+ targeted users',
          'Digital-native generation',
          'High engagement with gaming content'
        ],
        created_at: new Date().toISOString()
      };
      setAudience(mockAudience);
      setCurrentAudienceSize(mockAudience.audience_size);
    } finally {
      setLoading(false);
    }
  };

  const searchVariables = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setSearching(true);
    try {
      const response = await fetch('/api/enhanced-variable-picker/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 10 })
      });
      
      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Error searching variables:', error);
    } finally {
      setSearching(false);
    }
  };

  const addVariable = (variable: Variable) => {
    if (selectedVariables.length >= 3) {
      alert('You can add up to 3 variables only.');
      return;
    }

    // Add variable with impact calculation
    const impact = Math.random() * 0.3 + 0.1; // 10-40% reduction
    const newSize = Math.round(currentAudienceSize * (1 - impact));
    const probability = Math.random() * 0.3 + 0.7; // 70-100% confidence
    
    const variableWithImpact = {
      ...variable,
      impact: impact * 100,
      probability
    };
    
    setSelectedVariables([...selectedVariables, variableWithImpact]);
    setCurrentAudienceSize(newSize);
    setSearchQuery('');
    setSearchResults([]);
  };

  const removeVariable = (index: number) => {
    const removed = selectedVariables[index];
    const restoredSize = Math.round(currentAudienceSize / (1 - removed.impact! / 100));
    
    setSelectedVariables(selectedVariables.filter((_, i) => i !== index));
    setCurrentAudienceSize(restoredSize);
  };

  const getScaledAudienceSize = () => {
    const baseSize = currentAudienceSize;
    const experimentMultiplier = experimentScale;
    const seedMultiplier = seedAudienceScale;
    
    // Apply filters impact
    let filterReduction = 1.0;
    if (hardFilters.excludeExistingCustomers) filterReduction *= 0.85;
    if (hardFilters.requireEmailPermission) filterReduction *= 0.92;
    if (hardFilters.excludeCompetitorCustomers) filterReduction *= 0.95;
    if (hardFilters.requireRecentActivity) filterReduction *= 0.88;
    if (hardFilters.excludeSuppressedUsers) filterReduction *= 0.97;
    
    return Math.round(baseSize * experimentMultiplier * seedMultiplier * filterReduction);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading audience...</div>
      </div>
    );
  }

  if (!audience) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Audience not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ChevronLeft className="w-5 h-5" />
            Back to Audiences
          </button>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {audience.enhanced_name || audience.name}
                </h1>
                <p className="text-gray-600 mt-1">{audience.description}</p>
                {audience.natural_language_criteria && (
                  <p className="text-sm text-gray-500 mt-2">
                    {audience.natural_language_criteria}
                  </p>
                )}
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-blue-600">
                  {getScaledAudienceSize().toLocaleString()}
                </div>
                <div className="text-sm text-gray-500">Total Reach</div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Variable Picker & Controls */}
          <div className="lg:col-span-2 space-y-6">
            {/* Semantic Variable Picker */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-600" />
                Audience Refinement
              </h2>
              
              {!showManualSelection ? (
                <div>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Add targeting variables (up to 3)
                    </label>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => {
                          setSearchQuery(e.target.value);
                          searchVariables(e.target.value);
                        }}
                        placeholder="Search for demographics, interests, behaviors..."
                        className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  {/* Search Results */}
                  {searchResults.length > 0 && (
                    <div className="mb-4 border rounded-lg max-h-48 overflow-y-auto">
                      {searchResults.map((result, index) => (
                        <button
                          key={index}
                          onClick={() => addVariable(result)}
                          className="w-full text-left px-4 py-2 hover:bg-gray-50 border-b last:border-b-0"
                        >
                          <div className="font-medium">{result.code}</div>
                          <div className="text-sm text-gray-600">{result.description}</div>
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Selected Variables */}
                  <div className="space-y-2">
                    {selectedVariables.map((variable, index) => (
                      <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="font-medium">{variable.code}</div>
                            <div className="text-sm text-gray-600">{variable.description}</div>
                            <div className="flex items-center gap-4 mt-2 text-sm">
                              <span className="text-red-600">
                                -{variable.impact?.toFixed(1)}% audience impact
                              </span>
                              <span className="text-green-600">
                                {((variable as any).probability * 100).toFixed(0)}% confidence
                              </span>
                            </div>
                          </div>
                          <button
                            onClick={() => removeVariable(index)}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <X className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={() => setShowManualSelection(true)}
                    className="mt-4 text-sm text-blue-600 hover:text-blue-700"
                  >
                    Switch to Manual Selection →
                  </button>
                </div>
              ) : (
                <div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-medium mb-2">Original Audience Criteria</h3>
                    <div className="space-y-2 text-sm">
                      {audience.selected_variables.map((varCode, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <Database className="w-4 h-4 text-gray-400" />
                          <span>{varCode}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <button
                    onClick={() => setShowManualSelection(false)}
                    className="mt-4 text-sm text-blue-600 hover:text-blue-700"
                  >
                    ← Back to Semantic Selection
                  </button>
                </div>
              )}
            </div>

            {/* Sliders */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Sliders className="w-5 h-5 text-blue-600" />
                Scaling Controls
              </h2>
              
              <div className="space-y-6">
                {/* Experiments Slider */}
                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-medium text-gray-700">
                      Experiments (Test & Control)
                    </label>
                    <span className="text-sm font-semibold text-blue-600">
                      {experimentScale.toFixed(2)}x
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="10"
                    step="0.25"
                    value={experimentScale}
                    onChange={(e) => setExperimentScale(parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0.5x</span>
                    <span>10x</span>
                  </div>
                </div>

                {/* Seed Audience Scaling */}
                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-medium text-gray-700">
                      Seed Audience Scaling
                    </label>
                    <span className="text-sm font-semibold text-blue-600">
                      {seedAudienceScale.toFixed(2)}x
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="10"
                    step="0.25"
                    value={seedAudienceScale}
                    onChange={(e) => setSeedAudienceScale(parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0.5x</span>
                    <span>10x</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Hard Filters */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Filter className="w-5 h-5 text-blue-600" />
                Activation Filters
              </h2>
              
              <div className="space-y-3">
                {Object.entries(hardFilters).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between py-2">
                    <label className="text-sm text-gray-700">
                      {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                    </label>
                    <button
                      onClick={() => setHardFilters({ ...hardFilters, [key]: !value })}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        value ? 'bg-blue-600' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          value ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Summary & Actions */}
          <div className="space-y-6">
            {/* Audience Summary */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4">Audience Summary</h2>
              
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-gray-500">Base Size</div>
                  <div className="text-xl font-semibold">
                    {audience.audience_size.toLocaleString()}
                  </div>
                </div>
                
                <div>
                  <div className="text-sm text-gray-500">After Refinements</div>
                  <div className="text-xl font-semibold text-blue-600">
                    {currentAudienceSize.toLocaleString()}
                  </div>
                </div>
                
                <div>
                  <div className="text-sm text-gray-500">Final Reach</div>
                  <div className="text-2xl font-bold text-green-600">
                    {getScaledAudienceSize().toLocaleString()}
                  </div>
                </div>
                
                <hr className="my-4" />
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Experiment Scale</span>
                    <span className="font-medium">{experimentScale.toFixed(2)}x</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Seed Scale</span>
                    <span className="font-medium">{seedAudienceScale.toFixed(2)}x</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Active Filters</span>
                    <span className="font-medium">
                      {Object.values(hardFilters).filter(v => v).length}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Insights */}
            {audience.insights && audience.insights.length > 0 && (
              <div className="bg-blue-50 rounded-lg p-6">
                <h3 className="font-semibold text-blue-900 mb-2">Insights</h3>
                <ul className="space-y-2">
                  {audience.insights.map((insight, index) => (
                    <li key={index} className="text-sm text-blue-800 flex items-start gap-2">
                      <Zap className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>{insight}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Actions */}
            <div className="space-y-3">
              <button className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium">
                Activate Audience
              </button>
              <button className="w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-200 transition-colors font-medium">
                Export Configuration
              </button>
            </div>
          </div>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{
        __html: `
          .slider::-webkit-slider-thumb {
            appearance: none;
            width: 16px;
            height: 16px;
            background: #2563eb;
            cursor: pointer;
            border-radius: 50%;
          }
          
          .slider::-moz-range-thumb {
            width: 16px;
            height: 16px;
            background: #2563eb;
            cursor: pointer;
            border-radius: 50%;
            border: none;
          }
        `
      }} />
    </div>
  );
};

export default AudienceDetail;