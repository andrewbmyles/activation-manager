// Mock API service for local development
// This simulates the Vercel serverless functions locally

import { variableMetadata } from '../data/variableMetadata';

interface SessionResponse {
  session_id: string;
  message?: string;
  status?: string;
  features?: any;
}

interface ProcessResponse {
  status: string;
  suggested_variables?: any;
  segments?: any[];
  audience_id?: string;
  message?: string;
}

class MockApiService {
  private sessions: Map<string, any> = new Map();

  async startSession(): Promise<SessionResponse> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.sessions.set(sessionId, {
      created: Date.now(),
      state: 'ready'
    });
    
    return {
      session_id: sessionId,
      message: 'Session started. Please describe your target audience.',
      status: 'ready',
      features: {
        enhanced_variable_selection: true,
        prizm_analysis: true,
        metadata_integration: true
      }
    };
  }

  async processRequest(sessionId: string, action: string, payload: any): Promise<ProcessResponse> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    if (!this.sessions.has(sessionId)) {
      throw new Error('Invalid session');
    }

    if (action === 'process') {
      const userInput = payload?.input || '';
      const suggestedVariables = this.analyzeInput(userInput);
      
      return {
        status: 'variables_suggested',
        suggested_variables: suggestedVariables,
        message: 'Variables identified successfully'
      };
    }
    
    if (action === 'confirm') {
      const segments = this.generateSegments();
      
      return {
        status: 'complete',
        segments: segments,
        audience_id: `aud_${Date.now()}`,
        message: 'Segments created successfully'
      };
    }
    
    throw new Error('Unknown action');
  }

  private analyzeInput(input: string): any {
    const lowerInput = input.toLowerCase();
    const suggested: any = {
      demographic: [],
      behavioral: [],
      psychographic: [],
      financial: []
    };

    // Search through actual variable metadata
    variableMetadata.forEach(variable => {
      const lowerName = variable.name.toLowerCase();
      const lowerDesc = (variable.description || '').toLowerCase();
      let relevanceScore = 0;

      // Check if input contains keywords from variable name or description
      const words = lowerInput.split(' ');
      words.forEach(word => {
        if (word.length > 3) { // Skip short words
          if (lowerName.includes(word) || lowerDesc.includes(word)) {
            relevanceScore += 0.3;
          }
        }
      });

      // Boost score for exact category matches
      if (lowerInput.includes('demographic') && variable.category === 'Demographics') {
        relevanceScore += 0.2;
      } else if (lowerInput.includes('behavior') && variable.category === 'Behavioral') {
        relevanceScore += 0.2;
      } else if (lowerInput.includes('psychographic') && variable.category === 'Psychographic') {
        relevanceScore += 0.2;
      } else if (lowerInput.includes('financial') && variable.category === 'Financial') {
        relevanceScore += 0.2;
      }

      // Specific keyword matching
      if ((lowerInput.includes('age') || lowerInput.includes('young') || lowerInput.includes('millennial')) && 
          lowerName.includes('age')) {
        relevanceScore += 0.4;
      }
      if ((lowerInput.includes('income') || lowerInput.includes('affluent') || lowerInput.includes('wealthy')) && 
          (lowerName.includes('income') || lowerName.includes('wealth'))) {
        relevanceScore += 0.4;
      }
      if ((lowerInput.includes('urban') || lowerInput.includes('city') || lowerInput.includes('rural')) && 
          (lowerName.includes('location') || lowerName.includes('urban'))) {
        relevanceScore += 0.4;
      }
      if ((lowerInput.includes('education') || lowerInput.includes('college') || lowerInput.includes('degree')) && 
          lowerName.includes('education')) {
        relevanceScore += 0.4;
      }

      // If we have a relevant match, add to appropriate category
      if (relevanceScore > 0.3) {
        const categoryMap: any = {
          'Demographics': 'demographic',
          'Behavioral': 'behavioral',
          'Psychographic': 'psychographic',
          'Financial': 'financial'
        };
        
        const categoryKey = categoryMap[variable.category] || 'demographic';
        suggested[categoryKey].push({
          code: variable.id,
          description: variable.name,
          type: categoryKey,
          relevance_score: Math.min(relevanceScore, 0.95),
          category: variable.category,
          operators: variable.operators
        });
      }
    });

    // Sort each category by relevance score
    Object.keys(suggested).forEach(key => {
      suggested[key].sort((a: any, b: any) => b.relevance_score - a.relevance_score);
      // Limit to top 5 per category
      suggested[key] = suggested[key].slice(0, 5);
    });

    // Ensure we have at least some suggestions
    if (Object.values(suggested).every((arr: any) => arr.length === 0)) {
      // Add some default high-value variables
      const defaults = ['age', 'income_level', 'location_type', 'education_level'];
      defaults.forEach(id => {
        const variable = variableMetadata.find(v => v.id === id);
        if (variable) {
          const categoryMap: any = {
            'Demographics': 'demographic',
            'Behavioral': 'behavioral',
            'Psychographic': 'psychographic',
            'Financial': 'financial'
          };
          const categoryKey = categoryMap[variable.category] || 'demographic';
          suggested[categoryKey].push({
            code: variable.id,
            description: variable.name,
            type: categoryKey,
            relevance_score: 0.70,
            category: variable.category,
            operators: variable.operators
          });
        }
      });
    }

    return suggested;
  }

  private generateSegments(): any[] {
    const segments = [];
    const names = [
      'High-Value Enthusiasts',
      'Growth Opportunity',
      'Emerging Adopters',
      'Stable Core'
    ];
    const traits = [
      ['Frequent Buyers', 'Premium Oriented', 'Brand Loyal'],
      ['Moderate Activity', 'Price Conscious', 'Expanding Usage'],
      ['New to Category', 'Digital Native', 'Trend Aware'],
      ['Consistent Behavior', 'Value Seeking', 'Reliable']
    ];

    for (let i = 0; i < 4; i++) {
      const size = Math.floor(Math.random() * 30000) + 20000;
      segments.push({
        group_id: i,
        size: size,
        size_percentage: 5 + Math.random() * 5, // 5-10%
        name: names[i],
        dominantTraits: traits[i]
      });
    }

    return segments;
  }
}

// Export singleton instance
export const mockApi = new MockApiService();