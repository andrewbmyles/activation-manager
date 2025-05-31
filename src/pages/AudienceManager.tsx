import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ChevronLeft, Target, Sliders, Filter, Zap, Edit2, Save, X,
  Plus, Trash2, Info, Sparkles, SlidersHorizontal, Database, Search
} from 'lucide-react';
import { useForm } from 'react-hook-form';
import { Audience, AudienceCriteria } from '../types';
import { audiences as sampleAudiences } from '../data/sampleData';
import { EnhancedVariableSelector } from '../components/EnhancedVariableSelector';
import { OperatorSelector } from '../components/OperatorSelector';
import { ValueInput } from '../components/ValueInput';
import { variableMetadata, VariableMetadata } from '../data/variableMetadata';
import { EnhancedNLAudienceBuilder } from '../components/EnhancedNLAudienceBuilder';

// Types
type Mode = 'view' | 'edit' | 'create';
type BuilderMode = 'manual' | 'natural-language';
type AudienceType = '1st-party' | '3rd-party' | 'clean-room';
type AudienceSubtype = 'rampid' | 'uid2' | 'google-pair' | 'yahoo-connect' | 'maid' | 'postal-code' | 'prizm-segment' | 'partner-id';

interface Variable {
  code: string;
  description: string;
  score?: number;
  impact?: number;
  probability?: number;
}

interface ExtendedAudienceCriteria extends AudienceCriteria {
  variable?: VariableMetadata;
}

interface AudienceData extends Audience {
  enhanced_name?: string;
  natural_language_criteria?: string;
  insights?: string[];
  data_type?: string;
  selected_variables?: string[];
  audience_size?: number;
}

// Constants
const audienceTypeOptions = [
  { value: '1st-party', label: '1st Party Data' },
  { value: '3rd-party', label: '3rd Party Data' },
  { value: 'clean-room', label: 'Clean Room Data' }
] as const;

const audienceSubtypeOptions: Record<AudienceType, { value: AudienceSubtype; label: string }[]> = {
  '1st-party': [
    { value: 'rampid', label: 'RampID' },
    { value: 'uid2', label: 'UID2.0' },
    { value: 'google-pair', label: 'Google PAIR' },
    { value: 'yahoo-connect', label: 'Yahoo! Connect' },
    { value: 'maid', label: 'MAID' }
  ],
  '3rd-party': [
    { value: 'postal-code', label: 'Postal Code' },
    { value: 'prizm-segment', label: 'PRIZM Segment' }
  ],
  'clean-room': [
    { value: 'partner-id', label: 'PartnerID' }
  ]
};

const AudienceManager: React.FC = () => {
  const { audienceId } = useParams<{ audienceId?: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  // Mode management
  const [mode, setMode] = useState<Mode>(audienceId ? 'view' : 'create');
  const [builderMode, setBuilderMode] = useState<BuilderMode>('manual');
  
  // Form state
  const { register, handleSubmit, reset, setValue } = useForm();
  
  // Audience state
  const [audience, setAudience] = useState<AudienceData | null>(null);
  const [loading, setLoading] = useState(audienceId ? true : false);
  const [criteria, setCriteria] = useState<ExtendedAudienceCriteria[]>([]);
  const [audienceType, setAudienceType] = useState<AudienceType>('1st-party');
  const [audienceSubtype, setAudienceSubtype] = useState<AudienceSubtype>('rampid');
  
  // Semantic Variable Picker State
  const [showManualSelection, setShowManualSelection] = useState(false);
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

  // Load audience data
  useEffect(() => {
    if (audienceId) {
      loadAudience();
    }
  }, [audienceId]);

  const loadAudience = async () => {
    if (!audienceId) return;
    
    try {
      const response = await fetch(`/api/audiences/${audienceId}?user_id=demo_user`);
      const data = await response.json();
      
      if (data.success && data.audience) {
        setAudience(data.audience);
        setCurrentAudienceSize(data.audience.audience_size || data.audience.estimatedSize);
        
        // Initialize form values
        setValue('name', data.audience.name);
        setValue('description', data.audience.description);
        
        // Initialize criteria
        if (data.audience.criteria) {
          setCriteria(data.audience.criteria.map((c: any) => ({
            ...c,
            variable: variableMetadata.find(v => v.name === c.field)
          })));
        }
        
        // Initialize type settings
        if (data.audience.type && data.audience.type in audienceSubtypeOptions) {
          const type = data.audience.type as AudienceType;
          setAudienceType(type);
          setAudienceSubtype(data.audience.subtype || audienceSubtypeOptions[type][0].value);
        }
      } else {
        // Use mock data for demo
        const mockAudience: AudienceData = {
          id: audienceId,
          name: 'Gaming Enthusiasts Q4',
          enhanced_name: 'Gaming-Enthusiast Gen Z Males',
          description: 'Find males aged 18-24 interested in gaming',
          natural_language_criteria: 'Males between ages 18-24 who are interested in video games',
          estimatedSize: 67842,
          type: '1st-party',
          subtype: 'rampid',
          selected_variables: ['AGE_18_24', 'GENDER_MALE', 'GAMING_INTEREST'],
          insights: [
            'Focused audience of 68K+ targeted users',
            'Digital-native generation',
            'High engagement with gaming content'
          ],
          criteria: [],
          platforms: [],
          createdAt: new Date(),
          updatedAt: new Date()
        };
        setAudience(mockAudience);
        setCurrentAudienceSize(mockAudience.estimatedSize);
        setValue('name', mockAudience.name);
        setValue('description', mockAudience.description);
      }
    } catch (error) {
      console.error('Error loading audience:', error);
    } finally {
      setLoading(false);
    }
  };

  // Query for audiences list
  const { data: audiences = [] } = useQuery({
    queryKey: ['audiences'],
    queryFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return sampleAudiences;
    },
    enabled: mode === 'create' && !audienceId
  });

  // Save audience mutation
  const saveAudience = useMutation({
    mutationFn: async (data: any) => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const audienceData: AudienceData = {
        id: audience?.id || Date.now().toString(),
        name: data.name,
        description: data.description,
        type: audienceType,
        subtype: audienceSubtype,
        criteria: criteria.map(c => ({
          id: c.id,
          type: c.variable?.category.toLowerCase() as any || 'demographic',
          field: c.variable?.name || c.field,
          operator: c.operator,
          value: c.value,
        })),
        estimatedSize: getScaledAudienceSize(),
        createdAt: audience?.createdAt || new Date(),
        updatedAt: new Date(),
        platforms: audience?.platforms || [],
        enhanced_name: data.enhanced_name,
        natural_language_criteria: data.natural_language_criteria,
        selected_variables: selectedVariables.map(v => v.code)
      };
      
      return audienceData;
    },
    onSuccess: (savedAudience) => {
      queryClient.invalidateQueries({ queryKey: ['audiences'] });
      setAudience(savedAudience);
      setMode('view');
      
      // Navigate to the audience detail page if creating new
      if (!audienceId) {
        navigate(`/audiences/${savedAudience.id}`);
      }
    }
  });

  // Criteria management
  const addCriteria = () => {
    const newCriteria: ExtendedAudienceCriteria = {
      id: Date.now().toString(),
      type: 'demographic',
      field: '',
      operator: 'equals',
      value: '',
    };
    setCriteria(prevCriteria => [...prevCriteria, newCriteria]);
  };

  const removeCriteria = (id: string) => {
    setCriteria(prevCriteria => prevCriteria.filter(c => c.id !== id));
  };

  const updateCriteria = (id: string, updates: Partial<ExtendedAudienceCriteria>) => {
    setCriteria(prevCriteria => 
      prevCriteria.map(c => c.id === id ? { ...c, ...updates } : c)
    );
  };

  const handleVariableChange = (criterionId: string, variableId: string, variable: VariableMetadata) => {
    try {
      if (!variable) {
        console.error('No variable metadata provided for:', variableId);
        return;
      }
      
      setTimeout(() => {
        updateCriteria(criterionId, {
          field: variableId,
          variable: variable,
          operator: (variable.operators?.[0] || 'equals') as any,
          value: '',
        });
      }, 0);
    } catch (error) {
      console.error('Error updating variable:', error);
    }
  };

  // Semantic search functions
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

    const impact = Math.random() * 0.3 + 0.1;
    const newSize = Math.round(currentAudienceSize * (1 - impact));
    const probability = Math.random() * 0.3 + 0.7;
    
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

  // Size calculations
  const getScaledAudienceSize = () => {
    const baseSize = currentAudienceSize || estimateAudienceSize();
    const experimentMultiplier = experimentScale;
    const seedMultiplier = seedAudienceScale;
    
    let filterReduction = 1.0;
    if (hardFilters.excludeExistingCustomers) filterReduction *= 0.85;
    if (hardFilters.requireEmailPermission) filterReduction *= 0.92;
    if (hardFilters.excludeCompetitorCustomers) filterReduction *= 0.95;
    if (hardFilters.requireRecentActivity) filterReduction *= 0.88;
    if (hardFilters.excludeSuppressedUsers) filterReduction *= 0.97;
    
    return Math.round(baseSize * experimentMultiplier * seedMultiplier * filterReduction);
  };

  const estimateAudienceSize = () => {
    if (criteria.length === 0) return 1000000;
    
    let baseSize = 1000000;
    let reduction = 1;
    
    criteria.forEach(criterion => {
      if (!criterion.variable || !criterion.value) return;
      
      switch (criterion.variable.category) {
        case 'Demographics':
          reduction *= 0.8;
          break;
        case 'Behavioral':
          reduction *= 0.6;
          break;
        case 'Transactional':
          reduction *= 0.5;
          break;
        case 'Custom Attributes':
          reduction *= 0.4;
          break;
        default:
          reduction *= 0.7;
      }
    });
    
    return Math.floor(baseSize * reduction);
  };

  // Form submission
  const onSubmit = (data: any) => {
    saveAudience.mutate({
      ...data,
      enhanced_name: audience?.enhanced_name,
      natural_language_criteria: audience?.natural_language_criteria
    });
  };

  // Mode switching
  const enterEditMode = () => {
    setMode('edit');
    if (audience) {
      setValue('name', audience.name);
      setValue('description', audience.description);
    }
  };

  const cancelEdit = () => {
    setMode(audienceId ? 'view' : 'create');
    reset();
    if (audience) {
      loadAudience();
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading audience...</div>
      </div>
    );
  }

  // Natural Language Mode
  if (builderMode === 'natural-language' && (mode === 'create' || mode === 'edit')) {
    return <EnhancedNLAudienceBuilder />;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          {audienceId && (
            <button
              onClick={() => navigate('/audiences')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
            >
              <ChevronLeft className="w-5 h-5" />
              Back to Audiences
            </button>
          )}
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                {mode === 'view' ? (
                  <>
                    <h1 className="text-2xl font-bold text-gray-900">
                      {audience?.enhanced_name || audience?.name || 'New Audience'}
                    </h1>
                    <p className="text-gray-600 mt-1">{audience?.description}</p>
                    {audience?.natural_language_criteria && (
                      <p className="text-sm text-gray-500 mt-2">
                        {audience.natural_language_criteria}
                      </p>
                    )}
                  </>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Audience Name
                      </label>
                      <input
                        {...register('name', { required: true })}
                        className="input-field"
                        placeholder="e.g., High-Value Customers"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description
                      </label>
                      <textarea
                        {...register('description')}
                        className="input-field"
                        rows={2}
                        placeholder="Describe this audience segment..."
                      />
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex items-start gap-4 ml-6">
                {mode === 'view' && (
                  <>
                    <div className="text-right">
                      <div className="text-3xl font-bold text-blue-600">
                        {getScaledAudienceSize().toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-500">Total Reach</div>
                    </div>
                    <button
                      onClick={enterEditMode}
                      className="btn-primary flex items-center gap-2"
                    >
                      <Edit2 size={20} />
                      Edit Audience
                    </button>
                  </>
                )}
                
                {mode === 'create' && (
                  <div className="flex items-center gap-4">
                    <div className="flex bg-gray-100 rounded-lg p-1">
                      <button
                        onClick={() => setBuilderMode('manual')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all ${
                          builderMode === 'manual' 
                            ? 'bg-white shadow-sm text-gray-900' 
                            : 'text-gray-600 hover:text-gray-900'
                        }`}
                      >
                        <SlidersHorizontal size={18} />
                        Manual Builder
                      </button>
                      <button
                        onClick={() => setBuilderMode('natural-language')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all ${
                          builderMode === 'natural-language' 
                            ? 'bg-white shadow-sm text-gray-900' 
                            : 'text-gray-600 hover:text-gray-900'
                        }`}
                      >
                        <Sparkles size={18} />
                        Natural Language
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Variable Picker & Controls */}
            <div className="lg:col-span-2 space-y-6">
              {/* Audience Type Selection (Edit/Create modes) */}
              {(mode === 'edit' || mode === 'create') && (
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h2 className="text-lg font-semibold mb-4">Audience Configuration</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Audience Type
                      </label>
                      <select
                        value={audienceType}
                        onChange={(e) => {
                          const newType = e.target.value as AudienceType;
                          setAudienceType(newType);
                          setAudienceSubtype(audienceSubtypeOptions[newType][0].value);
                        }}
                        className="input-field"
                      >
                        {audienceTypeOptions.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Data Source
                      </label>
                      <select
                        value={audienceSubtype}
                        onChange={(e) => setAudienceSubtype(e.target.value as AudienceSubtype)}
                        className="input-field"
                      >
                        {audienceSubtypeOptions[audienceType].map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Criteria Builder (Edit/Create modes) */}
              {(mode === 'edit' || mode === 'create') && (
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center gap-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Audience Criteria
                      </label>
                      <div className="group relative">
                        <Info size={16} className="text-gray-400" />
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-50">
                          <div className="bg-gray-900 text-white text-xs rounded px-3 py-2 w-64">
                            Build your audience by combining multiple criteria. Each criterion narrows down your audience.
                            <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                              <div className="border-4 border-transparent border-t-gray-900"></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={addCriteria}
                      className="text-sm text-primary hover:text-primary-hover flex items-center gap-1 font-medium transition-colors"
                    >
                      <Plus size={16} />
                      Add Criteria
                    </button>
                  </div>

                  {criteria.length === 0 ? (
                    <div className="border-2 border-dashed border-gray-300 rounded-md p-8 text-center">
                      <p className="text-gray-500 mb-3">No criteria added yet</p>
                      <button
                        type="button"
                        onClick={addCriteria}
                        className="btn-secondary"
                      >
                        Add First Criteria
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {criteria.map((criterion, index) => (
                        <div key={criterion.id} className="border border-gray-200 rounded-md p-4 bg-gray-50">
                          <div className="flex items-start gap-3">
                            <div className="flex-1 space-y-3">
                              <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
                                <div className="lg:col-span-1">
                                  <label className="block text-xs font-medium text-gray-600 mb-1">
                                    Variable
                                  </label>
                                  <EnhancedVariableSelector
                                    value={criterion.field}
                                    onChange={(variableId, variable) => handleVariableChange(criterion.id, variableId, variable)}
                                    placeholder="Select variable"
                                  />
                                </div>
                                <div>
                                  <label className="block text-xs font-medium text-gray-600 mb-1">
                                    Operator
                                  </label>
                                  <OperatorSelector
                                    value={criterion.operator}
                                    onChange={(operator) => updateCriteria(criterion.id, { operator: operator as any })}
                                    availableOperators={criterion.variable?.operators || ['equals']}
                                  />
                                </div>
                                <div>
                                  <label className="block text-xs font-medium text-gray-600 mb-1">
                                    Value
                                  </label>
                                  <ValueInput
                                    value={criterion.value}
                                    onChange={(value) => updateCriteria(criterion.id, { value })}
                                    variable={criterion.variable || null}
                                    operator={criterion.operator}
                                  />
                                </div>
                              </div>
                              {index < criteria.length - 1 && (
                                <div className="flex items-center gap-2 pt-2">
                                  <div className="flex-1 border-t border-gray-300"></div>
                                  <span className="text-xs font-medium text-gray-500 px-2">AND</span>
                                  <div className="flex-1 border-t border-gray-300"></div>
                                </div>
                              )}
                            </div>
                            <button
                              type="button"
                              onClick={() => removeCriteria(criterion.id)}
                              className="p-2 text-secondary-red hover:text-secondary-red/80 hover:bg-secondary-red/10 rounded-md transition-colors"
                            >
                              <Trash2 size={20} />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Semantic Variable Picker (View mode) */}
              {mode === 'view' && (
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
                                    {(variable.probability! * 100).toFixed(0)}% confidence
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
                          {audience?.selected_variables?.map((varCode, index) => (
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
              )}

              {/* Sliders */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Sliders className="w-5 h-5 text-blue-600" />
                  Scaling Controls
                </h2>
                
                <div className="space-y-6">
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
                        type="button"
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
                      {(audience?.estimatedSize || estimateAudienceSize()).toLocaleString()}
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
              {audience?.insights && audience.insights.length > 0 && mode === 'view' && (
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
                {mode === 'view' ? (
                  <>
                    <button type="button" className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium">
                      Activate Audience
                    </button>
                    <button type="button" className="w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-200 transition-colors font-medium">
                      Export Configuration
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      type="submit"
                      disabled={saveAudience.isPending}
                      className="w-full btn-primary flex items-center justify-center gap-2"
                    >
                      <Save size={20} />
                      {saveAudience.isPending ? 'Saving...' : 'Save Audience'}
                    </button>
                    <button
                      type="button"
                      onClick={cancelEdit}
                      className="w-full btn-secondary"
                    >
                      Cancel
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </form>
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

export default AudienceManager;