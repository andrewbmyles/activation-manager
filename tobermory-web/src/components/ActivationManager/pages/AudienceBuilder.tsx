import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2, Copy, Edit2, Users, Info, Sparkles, SlidersHorizontal } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { Audience, AudienceCriteria } from '../types';
import { audiences as sampleAudiences } from '../data/sampleData';
import { AudienceIcon } from '../AudienceIcon';
import { VariableSelector } from '../VariableSelector';
import { OperatorSelector } from '../OperatorSelector';
import { ValueInput } from '../ValueInput';
import { variableMetadata, VariableMetadata } from '../data/variableMetadata';
import { EnhancedNLAudienceBuilder } from '../EnhancedNLAudienceBuilder';

type AudienceType = '1st-party' | '3rd-party' | 'clean-room';
type AudienceSubtype = 'rampid' | 'uid2' | 'google-pair' | 'yahoo-connect' | 'maid' | 'postal-code' | 'prizm-segment' | 'partner-id';

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

interface ExtendedAudienceCriteria extends AudienceCriteria {
  variable?: VariableMetadata;
}

export function AudienceBuilder() {
  const queryClient = useQueryClient();
  const [selectedAudience, setSelectedAudience] = useState<Audience | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [criteria, setCriteria] = useState<ExtendedAudienceCriteria[]>([]);
  const [audienceType, setAudienceType] = useState<AudienceType>('1st-party');
  const [audienceSubtype, setAudienceSubtype] = useState<AudienceSubtype>('rampid');
  const [builderMode, setBuilderMode] = useState<'manual' | 'natural-language'>('manual');

  const { register, handleSubmit, reset, setValue } = useForm();

  const { data: audiences = [] } = useQuery({
    queryKey: ['audiences'],
    queryFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return sampleAudiences;
    },
  });

  const createAudience = useMutation({
    mutationFn: async (data: any) => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const newAudience: Audience = {
        id: Date.now().toString(),
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
        estimatedSize: Math.floor(Math.random() * 100000) + 10000,
        createdAt: new Date(),
        updatedAt: new Date(),
        platforms: [],
      };
      return newAudience;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audiences'] });
      setIsCreating(false);
      setCriteria([]);
      setAudienceType('1st-party');
      setAudienceSubtype('rampid');
      reset();
    },
  });

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
      
      // Ensure we're not in a state update conflict
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

  const onSubmit = (data: any) => {
    createAudience.mutate(data);
  };

  const startEdit = (audience: Audience) => {
    setSelectedAudience(audience);
    setIsCreating(true);
    setCriteria(audience.criteria.map(c => ({
      ...c,
      variable: variableMetadata.find(v => v.name === c.field),
    })));
    setAudienceType((audience as any).type || '1st-party');
    setAudienceSubtype((audience as any).subtype || 'rampid');
    setValue('name', audience.name);
    setValue('description', audience.description);
  };

  const estimateAudienceSize = () => {
    // Simple estimation logic based on criteria count and types
    if (criteria.length === 0) return 0;
    
    let baseSize = 1000000; // Start with 1M potential users
    let reduction = 1;
    
    criteria.forEach(criterion => {
      if (!criterion.variable || !criterion.value) return;
      
      // Apply different reduction factors based on variable type
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

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-semibold text-gray-800 mb-2">Audience Builder</h2>
          <p className="text-gray-500">Create and manage your audience segments</p>
        </div>
        <div className="flex items-center gap-4">
          {/* Mode Toggle */}
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
          <button
            onClick={() => {
              setIsCreating(true);
              setSelectedAudience(null);
              setCriteria([]);
              setAudienceType('1st-party');
              setAudienceSubtype('rampid');
              reset();
            }}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={20} />
            Create Audience
          </button>
        </div>
      </div>

      {builderMode === 'natural-language' && isCreating ? (
        <EnhancedNLAudienceBuilder />
      ) : isCreating ? (
        <div className="card">
          <h3 className="text-xl font-semibold text-gray-800 mb-6">
            {selectedAudience ? 'Edit Audience' : 'Create New Audience'}
          </h3>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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

            <div>
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
                  {criteria.map((criterion, index) => {
                    try {
                      return (
                        <div key={criterion.id} className="border border-gray-200 rounded-md p-4 bg-gray-50">
                          <div className="flex items-start gap-3">
                            <div className="flex-1 space-y-3">
                              <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
                                <div className="lg:col-span-1">
                                  <label className="block text-xs font-medium text-gray-600 mb-1">
                                    Variable
                                  </label>
                                  <VariableSelector
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
                  );
                } catch (error) {
                  console.error('Error rendering criterion:', criterion.id, error);
                  return (
                    <div key={criterion.id} className="border border-red-200 rounded-md p-4 bg-red-50">
                      <p className="text-red-600 text-sm">Error rendering this criterion. Please remove and try again.</p>
                      <button
                        type="button"
                        onClick={() => removeCriteria(criterion.id)}
                        className="mt-2 text-sm text-red-600 hover:text-red-800"
                      >
                        Remove
                      </button>
                    </div>
                  );
                }
              })}
                </div>
              )}
            </div>

            <div className="bg-primary/5 border border-primary/20 p-6 rounded-md">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Estimated Audience Size</p>
                  <p className="text-3xl font-semibold text-gray-800 mt-1">
                    {criteria.length > 0 && criteria.some(c => c.value) 
                      ? estimateAudienceSize().toLocaleString() 
                      : '—'} users
                  </p>
                </div>
                <Users className="text-primary/30" size={48} />
              </div>
              {criteria.length > 0 && (
                <p className="text-xs text-gray-500 mt-3">
                  This is an estimate based on your criteria. Actual audience size may vary.
                </p>
              )}
            </div>

            <div className="flex gap-3 pt-6 border-t border-gray-200">
              <button
                type="submit"
                disabled={createAudience.isPending}
                className="btn-primary flex-1"
              >
                {createAudience.isPending ? 'Saving...' : 'Save Audience'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsCreating(false);
                  setCriteria([]);
                  setAudienceType('1st-party');
                  setAudienceSubtype('rampid');
                  reset();
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      ) : builderMode === 'natural-language' ? (
        <EnhancedNLAudienceBuilder />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {audiences.map((audience) => (
            <div key={audience.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className="flex gap-3">
                  <div className="w-10 h-10 bg-primary/10 rounded-md flex items-center justify-center flex-shrink-0">
                    <AudienceIcon audienceName={audience.name} className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">{audience.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">{audience.description}</p>
                    {(audience as any).type && (
                      <div className="flex gap-2 mt-2">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {audienceTypeOptions.find(opt => opt.value === (audience as any).type)?.label || (audience as any).type}
                        </span>
                        {(audience as any).subtype && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            {audienceSubtypeOptions[(audience as any).type as AudienceType]?.find(opt => opt.value === (audience as any).subtype)?.label || (audience as any).subtype}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <button
                    onClick={() => startEdit(audience)}
                    className="p-1 text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    <Edit2 size={16} />
                  </button>
                  <button className="p-1 text-gray-500 hover:text-gray-700 transition-colors">
                    <Copy size={16} />
                  </button>
                </div>
              </div>

              <div className="space-y-2 mb-4">
                <p className="text-xs text-gray-600 font-medium">Criteria:</p>
                {audience.criteria.slice(0, 2).map((criterion) => (
                  <div key={criterion.id} className="text-xs bg-gray-100 px-3 py-1.5 rounded-md text-gray-700">
                    {criterion.field} {criterion.operator} {Array.isArray(criterion.value) ? criterion.value.join(', ') : criterion.value}
                  </div>
                ))}
                {audience.criteria.length > 2 && (
                  <p className="text-xs text-gray-500">+{audience.criteria.length - 2} more</p>
                )}
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-gray-600">
                  <Users size={16} />
                  <span className="text-sm font-medium">
                    {audience.estimatedSize.toLocaleString()}
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  Updated {new Date(audience.updatedAt).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}