import React, { useState, useEffect } from 'react';
import { Send, Loader2, Check, Download } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';

interface WorkflowStep {
  number: number;
  title: string;
  description: string;
  status: 'pending' | 'active' | 'completed';
}

interface Variable {
  code: string;
  description: string;
  type: string;
  relevance_score: number;
}

interface SegmentGroup {
  group_id: number;
  size: number;
  size_percentage: number;
  characteristics?: any;
  prizm_profile?: {
    dominant_segments: string[];
    demographics: string;
    key_behaviors: string[];
  };
}

export function NLAudienceBuilder() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [userInput, setUserInput] = useState('');
  const [currentStep, setCurrentStep] = useState(1);
  const [suggestedVariables, setSuggestedVariables] = useState<Variable[]>([]);
  const [selectedVariables, setSelectedVariables] = useState<Set<string>>(new Set());
  const [segments, setSegments] = useState<SegmentGroup[]>([]);
  const [audienceId, setAudienceId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Array<{ type: 'user' | 'assistant'; content: string }>>([
    {
      type: 'assistant',
      content: 'Hello! I can help you build audience segments using natural language. Just describe the audience you want to target, and I\'ll guide you through the process. Let\'s get started!'
    }
  ]);

  const workflowSteps: WorkflowStep[] = [
    { number: 1, title: 'Describe Audience', description: 'Natural language input', status: 'active' },
    { number: 2, title: 'Variable Selection', description: 'AI suggests variables', status: 'pending' },
    { number: 3, title: 'Confirm Variables', description: 'Review and confirm', status: 'pending' },
    { number: 4, title: 'Retrieve Data', description: 'Fetch variable data', status: 'pending' },
    { number: 5, title: 'Create Segments', description: 'K-Medians clustering', status: 'pending' },
    { number: 6, title: 'View Results', description: 'Segmented audience', status: 'pending' }
  ];

  // Update workflow steps based on current step
  const getStepStatus = (stepNumber: number): WorkflowStep['status'] => {
    if (stepNumber < currentStep) return 'completed';
    if (stepNumber === currentStep) return 'active';
    return 'pending';
  };

  // Start session mutation
  const startSession = useMutation({
    mutationFn: async () => {
      const response = await fetch('http://localhost:5001/api/nl/start_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      return response.json();
    },
    onSuccess: (data) => {
      setSessionId(data.session_id);
    }
  });

  // Process workflow mutation
  const processWorkflow = useMutation({
    mutationFn: async ({ action, payload }: { action: string; payload?: any }) => {
      if (!sessionId) throw new Error('No session ID');
      
      const response = await fetch('http://localhost:5001/api/nl/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, action, payload })
      });
      return response.json();
    }
  });

  // Initialize session on mount
  useEffect(() => {
    startSession.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = async () => {
    if (!userInput.trim() || !sessionId) return;

    // Add user message
    setMessages(prev => [...prev, { type: 'user', content: userInput }]);
    
    // Process prompt with new integrated handler
    setCurrentStep(2);
    setMessages(prev => [...prev, { type: 'assistant', content: 'Analyzing your requirements...' }]);

    try {
      // Use the integrated handler's process action
      const result = await processWorkflow.mutateAsync({
        action: 'process',
        payload: { input: userInput }
      });

      if (result.status === 'variables_suggested') {
        // Handle variable suggestions
        const allVariables: Variable[] = [];
        
        // Flatten grouped variables from the enhanced selector
        Object.values(result.suggested_variables || {}).forEach((vars: any) => {
          if (Array.isArray(vars)) {
            allVariables.push(...vars);
          }
        });
        
        setSuggestedVariables(allVariables);
        setCurrentStep(3);
        
        setMessages(prev => [...prev, {
          type: 'assistant',
          content: `I found ${allVariables.length} relevant variables for your audience. Please review and confirm the selection below.`
        }]);

        // Auto-select top variables
        const topVariables = allVariables.slice(0, 7).map((v: Variable) => v.code);
        setSelectedVariables(new Set(topVariables));
        
      } else if (result.status === 'complete') {
        // If it completed in one step, show results
        setSegments(result.segments || []);
        setCurrentStep(6);
        setAudienceId(result.audience_id || null);
        
        setMessages(prev => [...prev, {
          type: 'assistant',
          content: `✅ Successfully created ${(result.segments || []).length} audience segments!`
        }]);
      }

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    }

    setUserInput('');
  };

  const handleConfirmVariables = async () => {
    if (selectedVariables.size === 0) return;

    setCurrentStep(4);
    setMessages(prev => [...prev, {
      type: 'assistant',
      content: `Confirming ${selectedVariables.size} variables and processing...`
    }]);

    try {
      // Create confirmation string for the integrated handler
      const confirmationText = `Use these variables: ${Array.from(selectedVariables).join(', ')}`;
      
      const result = await processWorkflow.mutateAsync({
        action: 'process',
        payload: { input: confirmationText }
      });

      if (result.status === 'complete') {
        setSegments(result.segments || []);
        setCurrentStep(6);
        setAudienceId(result.audience_id || null);

        setMessages(prev => [...prev, {
          type: 'assistant',
          content: `✅ Successfully created ${(result.segments || []).length} audience segments! All segments meet the 5-10% size constraints.`
        }]);
      } else {
        setMessages(prev => [...prev, {
          type: 'assistant',
          content: result.message || 'Processing continues...'
        }]);
      }

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: 'Error during processing. Please try again.'
      }]);
    }
  };

  const handleExport = () => {
    if (!audienceId) return;
    window.open(`http://localhost:5001/api/export/${audienceId}?format=csv`, '_blank');
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800">Natural Language Audience Builder</h3>
        <p className="text-sm text-gray-500 mt-1">Describe your target audience in plain English</p>
      </div>

      <div className="flex">
        {/* Workflow Steps */}
        <div className="w-64 p-6 border-r border-gray-200 bg-gray-50">
          <h4 className="text-sm font-medium text-gray-700 mb-4">Workflow Progress</h4>
          <div className="space-y-4">
            {workflowSteps.map((step, index) => (
              <div key={step.number} className="relative">
                <div className="flex items-start">
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                    ${getStepStatus(step.number) === 'completed' ? 'bg-green-500 text-white' :
                      getStepStatus(step.number) === 'active' ? 'bg-blue-500 text-white' :
                      'bg-gray-200 text-gray-600'}
                  `}>
                    {getStepStatus(step.number) === 'completed' ? <Check size={16} /> : step.number}
                  </div>
                  <div className="ml-3 flex-1">
                    <p className={`text-sm font-medium ${
                      getStepStatus(step.number) === 'active' ? 'text-gray-900' : 'text-gray-600'
                    }`}>
                      {step.title}
                    </p>
                    <p className="text-xs text-gray-500">{step.description}</p>
                  </div>
                </div>
                {index < workflowSteps.length - 1 && (
                  <div className="absolute left-4 top-8 w-0.5 h-8 bg-gray-300" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          {/* Chat Messages */}
          <div className="h-96 overflow-y-auto p-6 space-y-4">
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`
                  max-w-2xl px-4 py-2 rounded-lg
                  ${message.type === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-800'}
                `}>
                  {message.content}
                </div>
              </div>
            ))}
            
            {/* Variable Selection UI */}
            {currentStep === 3 && suggestedVariables.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-800 mb-3">Select Variables:</h4>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {suggestedVariables.map((variable) => (
                    <label key={variable.code} className="flex items-center p-2 hover:bg-gray-100 rounded cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedVariables.has(variable.code)}
                        onChange={(e) => {
                          const newSelected = new Set(selectedVariables);
                          if (e.target.checked) {
                            newSelected.add(variable.code);
                          } else {
                            newSelected.delete(variable.code);
                          }
                          setSelectedVariables(newSelected);
                        }}
                        className="mr-3"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-800">{variable.description}</p>
                        <p className="text-xs text-gray-500">{variable.type} • Score: {variable.relevance_score}</p>
                      </div>
                    </label>
                  ))}
                </div>
                <button
                  onClick={handleConfirmVariables}
                  disabled={selectedVariables.size === 0}
                  className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  Confirm Selection ({selectedVariables.size} variables)
                </button>
              </div>
            )}

            {/* Segment Results */}
            {currentStep === 6 && segments && segments.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-medium text-gray-800">Audience Segments:</h4>
                  {audienceId && (
                    <button
                      onClick={handleExport}
                      className="flex items-center gap-2 px-3 py-1 bg-white border border-gray-300 rounded-md hover:bg-gray-50 text-sm"
                    >
                      <Download size={16} />
                      Export CSV
                    </button>
                  )}
                </div>
                <div className="space-y-2">
                  {segments.map((segment: any) => (
                    <div key={segment.group_id} className="bg-white p-3 rounded border border-gray-200">
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium text-gray-800">Segment {segment.group_id}</p>
                          <p className="text-sm text-gray-600">{segment.size?.toLocaleString() || 0} records</p>
                          {segment.prizm_profile && (
                            <p className="text-xs text-blue-600 mt-1">
                              PRIZM: {segment.prizm_profile.dominant_segments?.[0] || 'N/A'}
                            </p>
                          )}
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-semibold text-gray-800">{segment.size_percentage?.toFixed(1) || 0}%</p>
                          <p className="text-xs text-green-600">
                            {(segment.size_percentage >= 5 && segment.size_percentage <= 10) ? '✓' : '✗'} Constraint
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {processWorkflow.isPending && (
              <div className="flex justify-center">
                <Loader2 className="animate-spin text-gray-500" size={24} />
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
                placeholder="Describe your target audience..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={!sessionId || currentStep !== 1}
              />
              <button
                onClick={handleSubmit}
                disabled={!userInput.trim() || !sessionId || currentStep !== 1}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <Send size={20} />
              </button>
            </div>
            {currentStep === 1 && (
              <p className="text-xs text-gray-500 mt-2">
                Example: "Find environmentally conscious millennials with high disposable income in urban areas"
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}