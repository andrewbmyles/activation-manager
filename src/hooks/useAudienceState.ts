import { useState, useCallback, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface AudienceState {
  // Basic audience info
  id: string | null;
  name: string;
  description: string;
  enhanced_name?: string;
  natural_language_criteria?: string;
  
  // Type configuration
  audienceType: '1st-party' | '3rd-party' | 'clean-room';
  audienceSubtype: string;
  
  // Criteria
  criteria: any[];
  selectedVariables: any[];
  
  // Size calculations
  baseSize: number;
  currentSize: number;
  scaledSize: number;
  
  // Scaling controls
  experimentScale: number;
  seedAudienceScale: number;
  
  // Filters
  hardFilters: {
    excludeExistingCustomers: boolean;
    requireEmailPermission: boolean;
    excludeCompetitorCustomers: boolean;
    requireRecentActivity: boolean;
    excludeSuppressedUsers: boolean;
  };
  
  // UI state
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  isDirty: boolean;
}

const initialState: AudienceState = {
  id: null,
  name: '',
  description: '',
  audienceType: '1st-party',
  audienceSubtype: 'rampid',
  criteria: [],
  selectedVariables: [],
  baseSize: 1000000,
  currentSize: 1000000,
  scaledSize: 1000000,
  experimentScale: 1.0,
  seedAudienceScale: 1.0,
  hardFilters: {
    excludeExistingCustomers: false,
    requireEmailPermission: true,
    excludeCompetitorCustomers: false,
    requireRecentActivity: true,
    excludeSuppressedUsers: true
  },
  isLoading: false,
  isSaving: false,
  error: null,
  isDirty: false
};

export function useAudienceState(audienceId?: string) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<AudienceState>(initialState);
  const [undoStack, setUndoStack] = useState<AudienceState[]>([]);
  const [redoStack, setRedoStack] = useState<AudienceState[]>([]);

  // Load audience data
  const loadAudience = useCallback(async (id: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await fetch(`/api/audiences/${id}?user_id=demo_user`);
      const data = await response.json();
      
      if (data.success && data.audience) {
        setState(prev => ({
          ...prev,
          id: data.audience.id,
          name: data.audience.name,
          description: data.audience.description,
          enhanced_name: data.audience.enhanced_name,
          natural_language_criteria: data.audience.natural_language_criteria,
          baseSize: data.audience.audience_size || data.audience.estimatedSize,
          currentSize: data.audience.audience_size || data.audience.estimatedSize,
          criteria: data.audience.criteria || [],
          selectedVariables: data.audience.selected_variables || [],
          audienceType: data.audience.type || '1st-party',
          audienceSubtype: data.audience.subtype || 'rampid',
          isLoading: false,
          isDirty: false
        }));
      } else {
        setState(prev => ({ ...prev, isLoading: false, error: 'Failed to load audience' }));
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        isLoading: false, 
        error: 'Error loading audience: ' + (error as Error).message 
      }));
    }
  }, []);

  // Calculate scaled size
  const calculateScaledSize = useCallback(() => {
    const { currentSize, experimentScale, seedAudienceScale, hardFilters } = state;
    
    let filterReduction = 1.0;
    if (hardFilters.excludeExistingCustomers) filterReduction *= 0.85;
    if (hardFilters.requireEmailPermission) filterReduction *= 0.92;
    if (hardFilters.excludeCompetitorCustomers) filterReduction *= 0.95;
    if (hardFilters.requireRecentActivity) filterReduction *= 0.88;
    if (hardFilters.excludeSuppressedUsers) filterReduction *= 0.97;
    
    const scaledSize = Math.round(currentSize * experimentScale * seedAudienceScale * filterReduction);
    
    setState(prev => ({ ...prev, scaledSize }));
  }, [state.currentSize, state.experimentScale, state.seedAudienceScale, state.hardFilters]);

  // Update functions with undo support
  const updateWithUndo = useCallback((updates: Partial<AudienceState>) => {
    setUndoStack(prev => [...prev, state]);
    setRedoStack([]);
    setState(prev => ({ ...prev, ...updates, isDirty: true }));
  }, [state]);

  const undo = useCallback(() => {
    if (undoStack.length > 0) {
      const previousState = undoStack[undoStack.length - 1];
      setRedoStack(prev => [...prev, state]);
      setUndoStack(prev => prev.slice(0, -1));
      setState(previousState);
    }
  }, [undoStack, state]);

  const redo = useCallback(() => {
    if (redoStack.length > 0) {
      const nextState = redoStack[redoStack.length - 1];
      setUndoStack(prev => [...prev, state]);
      setRedoStack(prev => prev.slice(0, -1));
      setState(nextState);
    }
  }, [redoStack, state]);

  // Save audience
  const saveAudience = useCallback(async () => {
    setState(prev => ({ ...prev, isSaving: true, error: null }));
    
    try {
      const endpoint = state.id 
        ? `/api/audiences/${state.id}` 
        : '/api/audiences';
      
      const method = state.id ? 'PUT' : 'POST';
      
      const response = await fetch(endpoint, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: state.name,
          description: state.description,
          type: state.audienceType,
          subtype: state.audienceSubtype,
          criteria: state.criteria,
          estimatedSize: state.scaledSize,
          enhanced_name: state.enhanced_name,
          natural_language_criteria: state.natural_language_criteria,
          selected_variables: state.selectedVariables
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setState(prev => ({ 
          ...prev, 
          id: data.audience.id,
          isSaving: false, 
          isDirty: false 
        }));
        queryClient.invalidateQueries({ queryKey: ['audiences'] });
        return data.audience;
      } else {
        throw new Error(data.error || 'Failed to save audience');
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        isSaving: false, 
        error: 'Error saving audience: ' + (error as Error).message 
      }));
      return null;
    }
  }, [state, queryClient]);

  // Auto-save functionality
  useEffect(() => {
    if (state.isDirty && !state.isSaving) {
      const timer = setTimeout(() => {
        // Auto-save logic here if desired
        console.log('Auto-save triggered (not implemented)');
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [state.isDirty, state.isSaving]);

  // Recalculate scaled size when dependencies change
  useEffect(() => {
    calculateScaledSize();
  }, [calculateScaledSize]);

  // Load audience on mount if ID provided
  useEffect(() => {
    if (audienceId) {
      loadAudience(audienceId);
    }
  }, [audienceId, loadAudience]);

  return {
    state,
    actions: {
      updateName: (name: string) => updateWithUndo({ name }),
      updateDescription: (description: string) => updateWithUndo({ description }),
      updateType: (audienceType: AudienceState['audienceType']) => updateWithUndo({ audienceType }),
      updateSubtype: (audienceSubtype: string) => updateWithUndo({ audienceSubtype }),
      updateCriteria: (criteria: any[]) => updateWithUndo({ criteria }),
      updateSelectedVariables: (selectedVariables: any[]) => updateWithUndo({ selectedVariables }),
      updateExperimentScale: (experimentScale: number) => updateWithUndo({ experimentScale }),
      updateSeedScale: (seedAudienceScale: number) => updateWithUndo({ seedAudienceScale }),
      updateHardFilters: (hardFilters: AudienceState['hardFilters']) => updateWithUndo({ hardFilters }),
      saveAudience,
      loadAudience,
      undo,
      redo,
      reset: () => {
        setState(initialState);
        setUndoStack([]);
        setRedoStack([]);
      }
    },
    computed: {
      canUndo: undoStack.length > 0,
      canRedo: redoStack.length > 0,
      hasChanges: state.isDirty
    }
  };
}