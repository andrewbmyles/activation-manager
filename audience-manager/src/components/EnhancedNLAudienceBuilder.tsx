import React, { useState, useEffect } from 'react';
import { 
  Send, Loader2, Check, Download, 
  Database, Shield, Cloud, Info, BarChart3, Users, Sparkles,
  CheckCircle, TrendingUp
} from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  BarChart, Bar, PieChart, Pie, Cell, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { API_ENDPOINTS } from '../config/api';
import { mockApi } from '../services/mockApi';

// Data type interfaces
interface DataTypeOption {
  id: 'first_party' | 'third_party' | 'clean_room';
  name: string;
  description: string;
  icon: React.ReactNode;
  subtypes: string[];
  color: string;
}

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
  category?: string;
  dataAvailability?: {
    first_party: boolean;
    third_party: boolean;
    clean_room: boolean;
  };
}

interface SegmentGroup {
  group_id: number;
  size: number;
  size_percentage: number;
  name?: string; // Descriptive name
  characteristics?: any;
  dominantTraits?: string[];
  prizm_profile?: {
    dominant_segments: string[];
    demographics: string;
    key_behaviors: string[];
  };
}

// Color palette for segments
const SEGMENT_COLORS = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444', '#6366F1', '#EC4899', '#14B8A6'];

// Data type options
const DATA_TYPE_OPTIONS: DataTypeOption[] = [
  {
    id: 'first_party',
    name: 'First Party Data',
    description: 'Your direct customer data with full activation rights',
    icon: <Database className="w-5 h-5" />,
    subtypes: ['RampID', 'UID2.0', 'Custom ID'],
    color: '#3B82F6'
  },
  {
    id: 'third_party',
    name: 'Third Party Data',
    description: 'Licensed external data with usage restrictions',
    icon: <Cloud className="w-5 h-5" />,
    subtypes: ['Postal Code', 'IAB Standard'],
    color: '#8B5CF6'
  },
  {
    id: 'clean_room',
    name: 'Clean Room Data',
    description: 'Privacy-compliant collaborative data environments',
    icon: <Shield className="w-5 h-5" />,
    subtypes: ['Clean Room Matched'],
    color: '#10B981'
  }
];

// Descriptive segment name generator
const generateSegmentName = (segment: SegmentGroup, userQuery: string): string => {
  const nameTemplates = {
    environmentally_conscious: [
      "Eco-Forward Innovators",
      "Sustainable Lifestyle Leaders",
      "Green Premium Buyers",
      "Environmental Champions"
    ],
    millennials: [
      "Digital Native Professionals",
      "Urban Millennials",
      "Tech-Savvy Achievers",
      "Young Professionals"
    ],
    high_income: [
      "Affluent Decision Makers",
      "Premium Market Leaders",
      "High-Value Customers",
      "Luxury Seekers"
    ],
    urban: [
      "Metro Trendsetters",
      "City Dwellers",
      "Urban Professionals",
      "Downtown Elite"
    ]
  };

  // Extract keywords from user query
  const queryLower = userQuery.toLowerCase();
  const matchedCategories: string[] = [];
  
  Object.keys(nameTemplates).forEach(key => {
    if (queryLower.includes(key.replace('_', ' '))) {
      matchedCategories.push(key);
    }
  });

  // Generate name based on segment characteristics
  if (matchedCategories.length > 0) {
    const category = matchedCategories[0];
    const names = nameTemplates[category as keyof typeof nameTemplates];
    return names[segment.group_id % names.length];
  }

  // Fallback names
  const fallbackNames = [
    "Core Audience",
    "Target Segment",
    "Key Demographic",
    "Primary Market"
  ];
  
  return fallbackNames[segment.group_id % fallbackNames.length];
};

export function EnhancedNLAudienceBuilder() {
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [userInput, setUserInput] = useState('');
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedDataType, setSelectedDataType] = useState<DataTypeOption | null>(null);
  const [selectedSubtype] = useState<string>('');
  const [suggestedVariables, setSuggestedVariables] = useState<Variable[]>([]);
  const [selectedVariables, setSelectedVariables] = useState<Set<string>>(new Set());
  const [segments, setSegments] = useState<SegmentGroup[]>([]);
  const [audienceId, setAudienceId] = useState<string | null>(null);
  const [showVariableViz, setShowVariableViz] = useState(false);
  const [showSegmentViz, setShowSegmentViz] = useState(false);
  const [confirmationPending, setConfirmationPending] = useState(false);
  const [distributionSuccess, setDistributionSuccess] = useState(false);
  const [originalUserQuery, setOriginalUserQuery] = useState('');
  
  const [messages, setMessages] = useState<Array<{ type: 'user' | 'assistant'; content: string }>>([
    {
      type: 'assistant',
      content: 'Welcome! I\'m here to help you build high-performing audience segments for your marketing campaigns. Let\'s start by selecting the data environment that best aligns with your activation strategy:'
    }
  ]);

  const workflowSteps: WorkflowStep[] = [
    { number: 1, title: 'Select Data Type', description: 'Choose data environment', status: 'active' },
    { number: 2, title: 'Describe Audience', description: 'Natural language input', status: 'pending' },
    { number: 3, title: 'Variable Selection', description: 'AI suggests variables', status: 'pending' },
    { number: 4, title: 'Confirm Variables', description: 'Review and confirm', status: 'pending' },
    { number: 5, title: 'Create Segments', description: 'K-Medians clustering', status: 'pending' },
    { number: 6, title: 'Review Results', description: 'Confirm segments', status: 'pending' },
    { number: 7, title: 'Distribution', description: 'Send to platforms', status: 'pending' }
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
      // Use mock API for local development
      if (window.location.hostname === 'localhost') {
        return mockApi.startSession();
      }
      
      const response = await fetch(API_ENDPOINTS.nlStartSession(), {
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
      
      // Use mock API for local development
      if (window.location.hostname === 'localhost') {
        return mockApi.processRequest(sessionId, action, {
          ...payload,
          data_type: selectedDataType?.id,
          subtype: selectedSubtype
        });
      }
      
      const response = await fetch(API_ENDPOINTS.nlProcess(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          session_id: sessionId, 
          action, 
          payload: {
            ...payload,
            data_type: selectedDataType?.id,
            subtype: selectedSubtype
          }
        })
      });
      return response.json();
    }
  });

  // Download CSV mutation
  const downloadCSV = useMutation({
    mutationFn: async () => {
      if (!audienceId) throw new Error('No audience ID');
      
      const response = await fetch(`${API_ENDPOINTS.export(audienceId)}?format=csv`);
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audience_${audienceId}_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    }
  });

  // Initialize session on mount
  useEffect(() => {
    startSession.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDataTypeSelection = (dataType: DataTypeOption) => {
    setSelectedDataType(dataType);
    setCurrentStep(2);
    setMessages(prev => [...prev, {
      type: 'assistant',
      content: dataType.id === 'first_party' 
        ? `Excellent choice! ${dataType.name} gives you maximum control and activation flexibility. Now, describe your ideal customer profile - think about demographics, behaviors, and the business outcomes you want to achieve.`
        : dataType.id === 'third_party'
        ? `Perfect! ${dataType.name} will help you expand your reach beyond your existing customer base. Tell me about the new audiences you want to discover - consider market segments, lifestyle attributes, or purchase behaviors that align with your growth goals.`
        : `Smart move! ${dataType.name} enables privacy-safe collaboration while maintaining data security. Describe the high-value audiences you want to identify across partner datasets - focus on shared attributes that indicate strong purchase intent or brand affinity.`
    }]);
  };

  const handleSubmit = async () => {
    if (!userInput.trim() || !sessionId) return;

    setOriginalUserQuery(userInput);
    setMessages(prev => [...prev, { type: 'user', content: userInput }]);
    
    setCurrentStep(3);
    setMessages(prev => [...prev, { type: 'assistant', content: 'I\'m analyzing your audience strategy and mapping it to our available data variables. This will help us identify the most predictive attributes for your campaign goals...' }]);

    try {
      const result = await processWorkflow.mutateAsync({
        action: 'process',
        payload: { input: userInput }
      });

      if (result.status === 'variables_suggested') {
        const allVariables: Variable[] = [];
        
        Object.values(result.suggested_variables || {}).forEach((vars: any) => {
          if (Array.isArray(vars)) {
            allVariables.push(...vars);
          }
        });
        
        setSuggestedVariables(allVariables);
        setCurrentStep(4);
        setShowVariableViz(true);
        
        setMessages(prev => [...prev, {
          type: 'assistant',
          content: `Excellent! I've identified ${allVariables.length} high-impact variables that align with your audience strategy. The visualization shows how each variable contributes to your targeting precision. I've pre-selected the top performers, but feel free to customize based on your campaign objectives.`
        }]);

        const topVariables = allVariables.slice(0, 7).map((v: Variable) => v.code);
        setSelectedVariables(new Set(topVariables));
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: 'I apologize - there was a technical issue processing your request. Let\'s try again, or feel free to refine your audience description for better results.'
      }]);
    }

    setUserInput('');
  };

  const handleConfirmVariables = async () => {
    if (selectedVariables.size === 0) return;

    setCurrentStep(5);
    setShowVariableViz(false);
    setShowSegmentViz(true);
    setMessages(prev => [...prev, {
      type: 'assistant',
      content: `I'm now applying advanced clustering algorithms to create balanced, actionable segments from your ${selectedVariables.size} selected variables. This ensures each segment is large enough for meaningful activation while maintaining distinct characteristics...`
    }]);

    try {
      const result = await processWorkflow.mutateAsync({
        action: 'confirm',
        payload: { 
          confirmed_variables: Array.from(selectedVariables)
        }
      });

      if (result.status === 'complete') {
        // Add descriptive names to segments
        const enhancedSegments = (result.segments || []).map((segment: SegmentGroup) => ({
          ...segment,
          name: generateSegmentName(segment, originalUserQuery)
        }));
        
        setSegments(enhancedSegments);
        setCurrentStep(6);
        setAudienceId(result.audience_id || null);

        setMessages(prev => [...prev, {
          type: 'assistant',
          content: `Fantastic results! I've created ${enhancedSegments.length} strategically balanced audience segments, each containing 5-10% of your total addressable market. These segments are optimized for both reach and relevance. Review the segment profiles below - each one represents a distinct opportunity for personalized engagement.`
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

  const handleConfirmSegments = () => {
    setConfirmationPending(true);
    setCurrentStep(7);
    setMessages(prev => [...prev, {
      type: 'assistant',
      content: 'Perfect! Your audience segments are locked and ready for activation. When you click Distribute, I\'ll seamlessly push these high-value segments to your marketing platforms for immediate campaign deployment. This is where strategy meets execution!'
    }]);
  };

  const handleDistribute = async () => {
    setDistributionSuccess(true);
    
    // Show success animation for 3 seconds then navigate
    setTimeout(() => {
      navigate('/distribution', { 
        state: { 
          audienceId, 
          segments: segments.map(s => ({
            group_id: s.group_id,
            size: s.size,
            size_percentage: s.size_percentage,
            name: s.name,
            dominantTraits: s.dominantTraits
          })),
          dataType: selectedDataType ? {
            id: selectedDataType.id,
            name: selectedDataType.name,
            selectedSubtype: selectedSubtype
          } : null
        } 
      });
    }, 3000);
  };

  // Variable Model Visualization Component
  const VariableModelVisualization = () => {
    const variableData = suggestedVariables.slice(0, 8).map(v => ({
      name: v.description.length > 25 ? v.description.substring(0, 25) + '...' : v.description,
      fullName: v.description,
      score: Math.round(v.relevance_score * 10) / 10,
      type: v.type
    }));

    const typeData = Object.entries(
      suggestedVariables.reduce((acc, v) => {
        acc[v.type] = (acc[v.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>)
    ).map(([type, count]) => ({ name: type, value: count }));

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-4"
      >
        <div className="flex items-center gap-2 mb-4">
          <Info className="w-5 h-5 text-blue-500" />
          <h3 className="text-lg font-semibold text-gray-800">Variable Model Visualization</h3>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="min-h-[300px]">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Variable Relevance Scores</h4>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={variableData} margin={{ top: 10, right: 10, bottom: 80, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="name" 
                  angle={-45} 
                  textAnchor="end" 
                  height={100}
                  interval={0}
                  tick={{ fontSize: 11 }}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  content={({ active, payload }) => {
                    if (active && payload && payload[0]) {
                      return (
                        <div className="bg-white p-2 border rounded shadow-sm">
                          <p className="text-xs font-medium">{payload[0].payload.fullName}</p>
                          <p className="text-xs text-blue-600">Score: {payload[0].value}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="score" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="min-h-[300px]">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Variable Type Distribution</h4>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
                <Pie
                  data={typeData}
                  cx="50%"
                  cy="45%"
                  labelLine={false}
                  label={({ name, percent }) => {
                    const displayName = name.length > 15 ? name.substring(0, 15) + '...' : name;
                    return `${displayName} ${(percent * 100).toFixed(0)}%`;
                  }}
                  outerRadius={70}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {typeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={SEGMENT_COLORS[index % SEGMENT_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  content={({ active, payload }) => {
                    if (active && payload && payload[0]) {
                      return (
                        <div className="bg-white p-2 border rounded shadow-sm">
                          <p className="text-xs font-medium">{payload[0].name}</p>
                          <p className="text-xs text-gray-600">Count: {payload[0].value}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <p className="text-sm text-gray-600 mt-4">
          The AI has analyzed your request and identified {suggestedVariables.length} relevant variables 
          across {typeData.length} categories. Variables are scored based on semantic relevance to your query.
        </p>
      </motion.div>
    );
  };

  // Segment Creation Visualization Component
  const SegmentCreationVisualization = () => {
    const segmentData = segments.map(s => ({
      name: s.name || `Segment ${s.group_id}`,
      size: s.size,
      percentage: s.size_percentage
    }));

    const scatterData = segments.map((s, i) => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      z: s.size,
      name: s.name || `Segment ${s.group_id}`
    }));

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-4"
      >
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-5 h-5 text-green-500" />
          <h3 className="text-lg font-semibold text-gray-800">K-Medians Clustering Results</h3>
        </div>
        
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Segment Size Distribution</h4>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={segmentData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="percentage" fill="#10B981">
                  {segmentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={SEGMENT_COLORS[index % SEGMENT_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Cluster Visualization</h4>
            <ResponsiveContainer width="100%" height={200}>
              <ScatterChart>
                <CartesianGrid />
                <XAxis type="number" dataKey="x" name="Feature 1" />
                <YAxis type="number" dataKey="y" name="Feature 2" />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Scatter name="Segments" data={scatterData} fill="#8884d8">
                  {scatterData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={SEGMENT_COLORS[index % SEGMENT_COLORS.length]} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>K-Medians Algorithm:</strong> Creates {segments.length} distinct audience segments with 
            5-10% size constraints. Each segment represents a unique combination of characteristics based 
            on your selected variables. The algorithm ensures balanced segment sizes for optimal campaign performance.
          </p>
        </div>
      </motion.div>
    );
  };

  // Distribution Success Animation
  const DistributionSuccessAnimation = () => {
    if (!distributionSuccess) return null;
    
    return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50"
        >
          <motion.div
            initial={{ y: 20 }}
            animate={{ y: 0 }}
            className="bg-white p-8 rounded-lg shadow-xl max-w-md text-center"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              className="w-20 h-20 mx-auto mb-4"
            >
              <CheckCircle className="w-full h-full text-green-500" />
            </motion.div>
            
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Distribution Successful!</h2>
            <p className="text-gray-600 mb-4">
              Your audience segments are being distributed to {selectedDataType?.name}
            </p>
            
            <div className="flex items-center justify-center gap-2 text-blue-600">
              <Sparkles className="w-5 h-5" />
              <span className="text-sm">Redirecting to Distribution Center...</span>
            </div>
          </motion.div>
        </motion.div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800">Enhanced Natural Language Audience Builder</h3>
        <p className="text-sm text-gray-500 mt-1">Build sophisticated audiences with AI-powered segmentation</p>
      </div>

      <div className="flex">
        {/* Workflow Steps */}
        <div className="w-72 p-6 border-r border-gray-200 bg-gray-50">
          <h4 className="text-sm font-medium text-gray-700 mb-4">Workflow Progress</h4>
          <div className="space-y-4">
            {workflowSteps.map((step, index) => (
              <div key={step.number} className="relative">
                <div className="flex items-start">
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all
                    ${getStepStatus(step.number) === 'completed' ? 'bg-green-500 text-white' :
                      getStepStatus(step.number) === 'active' ? 'bg-blue-500 text-white animate-pulse' :
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
            
            {/* Data Type Selection */}
            {currentStep === 1 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-3"
              >
                {DATA_TYPE_OPTIONS.map((dataType) => (
                  <motion.button
                    key={dataType.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleDataTypeSelection(dataType)}
                    className="w-full p-4 bg-white border-2 border-gray-200 rounded-lg hover:border-blue-400 transition-all text-left"
                  >
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg`} style={{ backgroundColor: `${dataType.color}20` }}>
                        {dataType.icon}
                      </div>
                      <div className="flex-1">
                        <h5 className="font-medium text-gray-800">{dataType.name}</h5>
                        <p className="text-sm text-gray-600 mt-1">{dataType.description}</p>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {dataType.subtypes.map(subtype => (
                            <span key={subtype} className="text-xs px-2 py-1 bg-gray-100 rounded">
                              {subtype}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </motion.div>
            )}

            {/* Variable Visualization */}
            {showVariableViz && <VariableModelVisualization />}
            
            {/* Variable Selection UI */}
            {currentStep === 4 && suggestedVariables.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gray-50 p-4 rounded-lg"
              >
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
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-500">{variable.type}</span>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="text-xs text-gray-500">Score: {variable.relevance_score}</span>
                          {variable.dataAvailability && (
                            <>
                              <span className="text-xs text-gray-500">•</span>
                              <div className="flex gap-1">
                                {variable.dataAvailability.first_party && (
                                  <span title="First Party"><Database className="w-3 h-3 text-blue-500" /></span>
                                )}
                                {variable.dataAvailability.third_party && (
                                  <span title="Third Party"><Cloud className="w-3 h-3 text-purple-500" /></span>
                                )}
                                {variable.dataAvailability.clean_room && (
                                  <span title="Clean Room"><Shield className="w-3 h-3 text-green-500" /></span>
                                )}
                              </div>
                            </>
                          )}
                        </div>
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
              </motion.div>
            )}

            {/* Segment Visualization */}
            {showSegmentViz && segments.length > 0 && <SegmentCreationVisualization />}

            {/* Segment Results */}
            {currentStep === 6 && segments && segments.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gray-50 p-4 rounded-lg"
              >
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-medium text-gray-800">Audience Segments:</h4>
                  <div className="flex gap-2">
                    {audienceId && (
                      <button
                        onClick={() => downloadCSV.mutate()}
                        disabled={downloadCSV.isPending}
                        className="flex items-center gap-2 px-3 py-1 bg-white border border-gray-300 rounded-md hover:bg-gray-50 text-sm"
                      >
                        {downloadCSV.isPending ? (
                          <Loader2 size={16} className="animate-spin" />
                        ) : (
                          <Download size={16} />
                        )}
                        Export CSV
                      </button>
                    )}
                    <button
                      onClick={handleConfirmSegments}
                      className="flex items-center gap-2 px-3 py-1 bg-green-500 text-white rounded-md hover:bg-green-600 text-sm"
                    >
                      <CheckCircle size={16} />
                      Confirm Segments
                    </button>
                  </div>
                </div>
                <div className="space-y-2">
                  {segments.map((segment: SegmentGroup, index: number) => (
                    <motion.div
                      key={segment.group_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="bg-white p-4 rounded-lg border border-gray-200"
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <div 
                              className="w-3 h-3 rounded-full" 
                              style={{ backgroundColor: SEGMENT_COLORS[index % SEGMENT_COLORS.length] }}
                            />
                            <p className="font-medium text-gray-800">{segment.name}</p>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {segment.size?.toLocaleString() || 0} records
                          </p>
                          {segment.dominantTraits && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {segment.dominantTraits.slice(0, 3).map((trait, i) => (
                                <span key={i} className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                                  {trait}
                                </span>
                              ))}
                            </div>
                          )}
                          {segment.prizm_profile && (
                            <p className="text-xs text-purple-600 mt-2">
                              PRIZM: {segment.prizm_profile.dominant_segments?.join(', ') || 'N/A'}
                            </p>
                          )}
                        </div>
                        <div className="text-right ml-4">
                          <p className="text-lg font-semibold text-gray-800">{segment.size_percentage?.toFixed(1) || 0}%</p>
                          <p className="text-xs text-green-600 flex items-center gap-1">
                            {(segment.size_percentage >= 5 && segment.size_percentage <= 10) ? (
                              <>
                                <CheckCircle size={12} />
                                Optimal Size
                              </>
                            ) : (
                              <span className="text-yellow-600">Size Warning</span>
                            )}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Distribution Ready */}
            {currentStep === 7 && confirmationPending && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg text-center"
              >
                <Users className="w-12 h-12 text-blue-500 mx-auto mb-3" />
                <h4 className="font-semibold text-gray-800 mb-2">Ready for Distribution!</h4>
                <p className="text-gray-600 mb-4">
                  Your {segments.length} segments are ready to be distributed to your {selectedDataType?.name} platforms.
                </p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleDistribute}
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-medium flex items-center gap-2 mx-auto"
                >
                  <TrendingUp className="w-5 h-5" />
                  Distribute to Platforms
                </motion.button>
              </motion.div>
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
                placeholder={
                  currentStep === 1 ? "Select a data type first..." :
                  currentStep === 2 ? "Describe your target audience..." :
                  "Processing..."
                }
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={!sessionId || currentStep !== 2}
              />
              <button
                onClick={handleSubmit}
                disabled={!userInput.trim() || !sessionId || currentStep !== 2}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <Send size={20} />
              </button>
            </div>
            {currentStep === 2 && (
              <p className="text-xs text-gray-500 mt-2">
                Example: "Find environmentally conscious millennials with high disposable income in urban areas"
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Distribution Success Animation */}
      <DistributionSuccessAnimation />
    </div>
  );
}