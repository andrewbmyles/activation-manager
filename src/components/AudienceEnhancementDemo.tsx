import React, { useState } from 'react';
import { 
  Search, Plus, X, Filter, Sliders, Target, Users, 
  Zap, ChevronLeft, Database, ToggleLeft, ToggleRight 
} from 'lucide-react';

const AudienceEnhancementDemo: React.FC = () => {
  const [selectedVariables, setSelectedVariables] = useState([
    { code: 'HIGH_INCOME_URBAN', description: 'High income urban professionals', impact: 15.2, probability: 0.89 },
    { code: 'MILLENNIAL_TECH', description: 'Tech-savvy millennials', impact: 22.7, probability: 0.94 }
  ]);
  
  const [experimentScale, setExperimentScale] = useState(2.5);
  const [seedAudienceScale, setSeedAudienceScale] = useState(1.8);
  const [showManualSelection, setShowManualSelection] = useState(false);
  
  const [hardFilters, setHardFilters] = useState({
    excludeExistingCustomers: true,
    requireEmailPermission: true,
    excludeCompetitorCustomers: false,
    requireRecentActivity: true,
    excludeSuppressedUsers: true
  });

  const baseAudienceSize = 67842;
  const currentSize = 42156; // After variables applied
  
  const getScaledSize = () => {
    let filterReduction = 1.0;
    if (hardFilters.excludeExistingCustomers) filterReduction *= 0.85;
    if (hardFilters.requireEmailPermission) filterReduction *= 0.92;
    if (hardFilters.requireRecentActivity) filterReduction *= 0.88;
    if (hardFilters.excludeSuppressedUsers) filterReduction *= 0.97;
    
    return Math.round(currentSize * experimentScale * seedAudienceScale * filterReduction);
  };

  const searchResults = [
    { code: 'ECO_CONSCIOUS', description: 'Environmentally conscious consumers' },
    { code: 'LUXURY_BUYERS', description: 'Luxury goods purchasers' },
    { code: 'FITNESS_ENTHUSIASTS', description: 'Health and fitness focused individuals' }
  ];

  return (
    <div className="max-w-6xl mx-auto p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <button className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4">
          <ChevronLeft className="w-5 h-5" />
          Back to Audiences
        </button>
        
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Gaming-Enthusiast Gen Z Males
              </h1>
              <p className="text-gray-600 mt-1">
                Males between the ages of 18 and 24 who are interested in video games
              </p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-blue-600">
                {getScaledSize().toLocaleString()}
              </div>
              <div className="text-sm text-gray-500">Total Reach</div>
            </div>
          </div>
        </div>
      </div>

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
                      placeholder="Search for demographics, interests, behaviors..."
                      className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Search Results */}
                <div className="mb-4 border rounded-lg max-h-48 overflow-y-auto">
                  {searchResults.map((result, index) => (
                    <button
                      key={index}
                      className="w-full text-left px-4 py-2 hover:bg-gray-50 border-b last:border-b-0"
                    >
                      <div className="font-medium">{result.code}</div>
                      <div className="text-sm text-gray-600">{result.description}</div>
                    </button>
                  ))}
                </div>

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
                              -{variable.impact}% audience impact
                            </span>
                            <span className="text-green-600">
                              {(variable.probability * 100).toFixed(0)}% confidence
                            </span>
                          </div>
                        </div>
                        <button className="text-gray-400 hover:text-gray-600">
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
                    {['AGE_18_24', 'GENDER_MALE', 'GAMING_INTEREST'].map((varCode, index) => (
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
                <div className="text-xl font-semibold">{baseAudienceSize.toLocaleString()}</div>
              </div>
              
              <div>
                <div className="text-sm text-gray-500">After Refinements</div>
                <div className="text-xl font-semibold text-blue-600">
                  {currentSize.toLocaleString()}
                </div>
              </div>
              
              <div>
                <div className="text-sm text-gray-500">Final Reach</div>
                <div className="text-2xl font-bold text-green-600">
                  {getScaledSize().toLocaleString()}
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
          <div className="bg-blue-50 rounded-lg p-6">
            <h3 className="font-semibold text-blue-900 mb-2">Insights</h3>
            <ul className="space-y-2">
              <li className="text-sm text-blue-800 flex items-start gap-2">
                <Zap className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>High engagement rate among gaming demographics</span>
              </li>
              <li className="text-sm text-blue-800 flex items-start gap-2">
                <Zap className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>Strong purchasing power for digital products</span>
              </li>
            </ul>
          </div>

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

export default AudienceEnhancementDemo;