# Audience Builder AI Assistant - Complete Implementation Guide

## Expert Persona and Instructions

You are an expert data scientist and software architect specializing in audience segmentation and marketing analytics. You have deep expertise in machine learning, particularly clustering algorithms, natural language processing, and building production-grade data pipelines. You understand both the technical implementation details and the business context of audience segmentation.

Your approach combines rigorous technical implementation with practical business considerations. You write efficient, production-ready code that balances performance with maintainability. When developing solutions, you prioritize:

1. **Efficiency**: Use vectorized operations, appropriate data structures, and avoid redundant computations
2. **Scalability**: Design systems that can handle millions of records without degrading performance
3. **Maintainability**: Write clear, well-documented code with proper error handling
4. **Business Value**: Ensure technical solutions align with marketing objectives and user needs

Remember to be concise in your responses while maintaining clarity. Avoid over-engineering solutions - implement what's needed for the current requirements while keeping the architecture flexible for future extensions.

## System Architecture Overview

You are building a natural language interface for audience segmentation that allows marketing professionals to describe their target audience in plain English and receive actionable customer segments. The system uses Claude as an orchestration layer that interprets user intent and coordinates specialized tools for data processing and analysis.

### Core Components

1. **Natural Language Understanding**: Claude interprets user requests and extracts demographic, behavioral, financial, and psychographic criteria
2. **Variable Selection**: Maps natural language descriptions to available data variables
3. **Data Retrieval**: Fetches relevant customer data based on selected variables
4. **Constrained Clustering**: Groups customers using K-Medians with 5-10% size constraints
5. **Results Presentation**: Formats segments with actionable insights and profiles

## System Prompt for Claude Orchestration

```markdown
You are an intelligent audience segmentation assistant that helps users create targeted audience groups based on demographic, behavioral, financial, and psychographic attributes.

## Your Capabilities

You have access to the following tools:

1. **variable_selector**: Analyzes user requirements and selects relevant variables from the available dataset
2. **data_retriever**: Fetches data values for selected variables via API
3. **cluster_analyzer**: Runs K-Medians clustering with size constraints (5-10% per group)
4. **result_formatter**: Formats and presents the final audience segments

## Workflow Process

When a user provides an audience description, follow these steps:

1. **Understand Requirements**: Parse the user's natural language request to identify:
   - Demographic criteria (age, location, gender, etc.)
   - Behavioral patterns (purchase history, engagement, etc.)
   - Financial attributes (income, spending, credit, etc.)
   - Psychographic traits (lifestyle, values, interests, etc.)

2. **Variable Selection**:
   - Call variable_selector with the parsed requirements
   - Present selected variables to the user for confirmation
   - Allow iterative refinement based on user feedback
   - Store confirmed variables for next steps

3. **Data Retrieval**:
   - Use data_retriever to fetch values for confirmed variables
   - Store the returned data table for clustering

4. **Clustering**:
   - Apply cluster_analyzer to create groups with size constraints
   - Ensure no group is smaller than 5% or larger than 10%

5. **Results Presentation**:
   - Format results showing groups with their characteristics
   - Provide insights about each segment's defining features

## Communication Style

- Be conversational and helpful
- Explain technical concepts in simple terms
- Confirm understanding at each step
- Provide clear summaries of actions taken
- Ask clarifying questions when requirements are ambiguous
```

## Python Implementation - Core Tools

```python
# Audience Builder Tools Implementation

import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

class VariableSelector:
    """
    Analyzes user requirements and selects relevant variables from available dataset
    """
    def __init__(self, variable_catalog: Dict[str, Dict[str, Any]]):
        """
        Initialize with a catalog of available variables
        
        Args:
            variable_catalog: Dictionary mapping variable codes to their metadata
            Example: {
                "AGE_RANGE": {"type": "demographic", "description": "Age range categories"},
                "INCOME_LEVEL": {"type": "financial", "description": "Income brackets"},
                "GREEN_PURCHASE": {"type": "behavioral", "description": "Environmentally friendly purchase history"}
            }
        """
        self.catalog = variable_catalog
        self.selected_variables = []
        
    def analyze_request(self, user_request: str) -> List[Dict[str, Any]]:
        """
        Parse user request and identify relevant variables
        """
        # Keywords mapping to variable types
        keyword_mappings = {
            "demographic": ["age", "gender", "location", "urban", "city", "rural"],
            "behavioral": ["purchase", "buy", "engage", "active", "frequent", "habit"],
            "financial": ["income", "disposable", "spending", "affluent", "budget"],
            "psychographic": ["lifestyle", "values", "interests", "conscious", "preference"]
        }
        
        # Score each variable based on relevance
        variable_scores = []
        request_lower = user_request.lower()
        
        for var_code, var_info in self.catalog.items():
            score = 0
            var_type = var_info.get("type", "")
            var_desc = var_info.get("description", "").lower()
            
            # Check if variable type matches request keywords
            for category, keywords in keyword_mappings.items():
                if var_type == category:
                    for keyword in keywords:
                        if keyword in request_lower:
                            score += 2
                            
            # Check if variable description matches request
            request_words = request_lower.split()
            for word in request_words:
                if len(word) > 3 and word in var_desc:
                    score += 1
                    
            if score > 0:
                variable_scores.append({
                    "code": var_code,
                    "type": var_type,
                    "description": var_info["description"],
                    "score": score
                })
        
        # Sort by score and return top relevant variables
        variable_scores.sort(key=lambda x: x["score"], reverse=True)
        return variable_scores[:10]  # Return top 10 most relevant
    
    def confirm_selection(self, selected_codes: List[str]):
        """Store confirmed variable selection"""
        self.selected_variables = selected_codes
        return {"status": "confirmed", "variables": self.selected_variables}


class DataRetriever:
    """
    Retrieves data values for selected variables from API
    """
    def __init__(self, api_endpoint: str, api_key: str):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        
    def fetch_data(self, variable_codes: List[str], sample_size: int = None) -> pd.DataFrame:
        """
        Simulate API call to retrieve data
        In production, this would make actual API requests
        """
        # For demonstration, generating synthetic data
        if sample_size is None:
            sample_size = 10000
            
        data = {}
        np.random.seed(42)  # For reproducible results
        
        for var_code in variable_codes:
            if "AGE" in var_code:
                data[var_code] = np.random.choice(['18-24', '25-34', '35-44', '45-54', '55+'], sample_size)
            elif "INCOME" in var_code:
                data[var_code] = np.random.choice(['<30k', '30-50k', '50-75k', '75-100k', '100k+'], sample_size)
            elif "LOCATION" in var_code:
                data[var_code] = np.random.choice(['Urban', 'Suburban', 'Rural'], sample_size, p=[0.5, 0.3, 0.2])
            elif "GREEN" in var_code:
                data[var_code] = np.random.choice([0, 1], sample_size, p=[0.6, 0.4])
            else:
                data[var_code] = np.random.randn(sample_size)
                
        return pd.DataFrame(data)


class ConstrainedKMedians:
    """
    K-Medians clustering with size constraints (5-10% per cluster)
    """
    def __init__(self, min_size_pct: float = 0.05, max_size_pct: float = 0.10):
        self.min_size_pct = min_size_pct
        self.max_size_pct = max_size_pct
        self.labels_ = None
        self.cluster_centers_ = None
        
    def fit_predict(self, data: pd.DataFrame) -> np.ndarray:
        """
        Perform constrained clustering
        """
        n_samples = len(data)
        min_cluster_size = int(n_samples * self.min_size_pct)
        max_cluster_size = int(n_samples * self.max_size_pct)
        
        # Determine optimal number of clusters
        min_clusters = int(np.ceil(n_samples / max_cluster_size))
        max_clusters = int(np.floor(n_samples / min_cluster_size))
        
        # Convert categorical variables to numeric
        data_numeric = pd.get_dummies(data, drop_first=True)
        
        # Standardize features
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_numeric)
        
        best_score = float('inf')
        best_labels = None
        
        # Try different numbers of clusters
        for n_clusters in range(min_clusters, min(max_clusters + 1, 20)):
            # Initial clustering with K-Means (as approximation to K-Medians)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            initial_labels = kmeans.fit_predict(data_scaled)
            
            # Apply size constraints through iterative reassignment
            labels = self._apply_size_constraints(
                data_scaled, initial_labels, n_clusters, 
                min_cluster_size, max_cluster_size
            )
            
            # Calculate clustering quality score
            score = self._calculate_score(data_scaled, labels)
            
            if score < best_score:
                best_score = score
                best_labels = labels
                self.cluster_centers_ = self._calculate_medians(data_scaled, labels)
                
        self.labels_ = best_labels
        return best_labels
    
    def _apply_size_constraints(self, data, labels, n_clusters, min_size, max_size):
        """
        Iteratively reassign points to satisfy size constraints
        """
        labels = labels.copy()
        n_samples = len(data)
        
        for _ in range(10):  # Maximum iterations
            cluster_sizes = np.bincount(labels, minlength=n_clusters)
            
            # Check if all constraints are satisfied
            if np.all(cluster_sizes >= min_size) and np.all(cluster_sizes <= max_size):
                break
                
            # Handle undersized clusters
            for cluster_id in np.where(cluster_sizes < min_size)[0]:
                # Find nearest points from oversized clusters
                oversized = np.where(cluster_sizes > max_size)[0]
                if len(oversized) == 0:
                    oversized = np.where(cluster_sizes > min_size)[0]
                    
                if len(oversized) > 0:
                    # Calculate distances to cluster center
                    center = data[labels == cluster_id].mean(axis=0)
                    
                    # Find points in oversized clusters
                    candidates = np.where(np.isin(labels, oversized))[0]
                    if len(candidates) > 0:
                        distances = np.linalg.norm(data[candidates] - center, axis=1)
                        
                        # Move closest points
                        n_needed = min_size - cluster_sizes[cluster_id]
                        closest_indices = candidates[np.argsort(distances)[:n_needed]]
                        labels[closest_indices] = cluster_id
                        
            # Handle oversized clusters
            for cluster_id in np.where(cluster_sizes > max_size)[0]:
                # Find farthest points and reassign
                center = data[labels == cluster_id].mean(axis=0)
                cluster_points = np.where(labels == cluster_id)[0]
                
                distances = np.linalg.norm(data[cluster_points] - center, axis=1)
                n_excess = cluster_sizes[cluster_id] - max_size
                
                # Reassign farthest points to nearest other cluster
                farthest_indices = cluster_points[np.argsort(distances)[-n_excess:]]
                
                for idx in farthest_indices:
                    # Find nearest cluster that can accept the point
                    point = data[idx].reshape(1, -1)
                    min_dist = float('inf')
                    best_cluster = None
                    
                    for other_cluster in range(n_clusters):
                        if other_cluster != cluster_id and cluster_sizes[other_cluster] < max_size:
                            other_center = data[labels == other_cluster].mean(axis=0)
                            dist = np.linalg.norm(point - other_center)
                            if dist < min_dist:
                                min_dist = dist
                                best_cluster = other_cluster
                                
                    if best_cluster is not None:
                        labels[idx] = best_cluster
                        
        return labels
    
    def _calculate_score(self, data, labels):
        """Calculate clustering quality score (lower is better)"""
        score = 0
        unique_labels = np.unique(labels)
        
        for label in unique_labels:
            cluster_data = data[labels == label]
            if len(cluster_data) > 0:
                # Use median absolute deviation as score
                median = np.median(cluster_data, axis=0)
                score += np.sum(np.abs(cluster_data - median))
                
        return score / len(data)
    
    def _calculate_medians(self, data, labels):
        """Calculate median centers for each cluster"""
        unique_labels = np.unique(labels)
        centers = []
        
        for label in unique_labels:
            cluster_data = data[labels == label]
            if len(cluster_data) > 0:
                centers.append(np.median(cluster_data, axis=0))
                
        return np.array(centers)


class AudienceBuilder:
    """
    Main orchestrator for the audience building process
    """
    def __init__(self, variable_catalog: Dict, api_endpoint: str, api_key: str):
        self.variable_selector = VariableSelector(variable_catalog)
        self.data_retriever = DataRetriever(api_endpoint, api_key)
        self.clusterer = ConstrainedKMedians()
        self.results = None
        
    def build_audience(self, user_request: str, confirmed_variables: List[str]) -> pd.DataFrame:
        """
        Execute the full audience building pipeline
        """
        # Fetch data for confirmed variables
        data = self.data_retriever.fetch_data(confirmed_variables)
        
        # Apply clustering with constraints
        cluster_labels = self.clusterer.fit_predict(data)
        
        # Add cluster labels to data
        data['Group'] = cluster_labels
        
        # Sort by group and create final output
        result = data.sort_values('Group').reset_index(drop=True)
        
        # Calculate group statistics
        group_stats = result.groupby('Group').agg(['count', 'nunique']).iloc[:, 0]
        group_pcts = (group_stats / len(result) * 100).round(2)
        
        print("\nGroup Size Distribution:")
        for group, pct in group_pcts.items():
            print(f"Group {group}: {pct}% ({group_stats[group]} records)")
            
        self.results = result
        return result
    
    def get_group_profiles(self) -> Dict[int, Dict[str, Any]]:
        """
        Generate descriptive profiles for each group
        """
        if self.results is None:
            return {}
            
        profiles = {}
        
        for group_id in self.results['Group'].unique():
            group_data = self.results[self.results['Group'] == group_id]
            profile = {
                "size": len(group_data),
                "percentage": round(len(group_data) / len(self.results) * 100, 2),
                "characteristics": {}
            }
            
            # Analyze each variable
            for col in group_data.columns:
                if col != 'Group':
                    if group_data[col].dtype == 'object':
                        # Categorical variable - get mode
                        mode_value = group_data[col].mode()[0]
                        mode_pct = (group_data[col] == mode_value).sum() / len(group_data) * 100
                        profile["characteristics"][col] = {
                            "dominant_value": mode_value,
                            "percentage": round(mode_pct, 1)
                        }
                    else:
                        # Numeric variable - get median
                        profile["characteristics"][col] = {
                            "median": round(group_data[col].median(), 2),
                            "mean": round(group_data[col].mean(), 2)
                        }
                        
            profiles[group_id] = profile
            
        return profiles
```

## JavaScript Integration - NLweb Interface

```javascript
// NLweb Integration for Audience Builder

// Tool definitions for Claude Code
const audienceBuilderTools = {
  variable_selector: {
    description: "Analyzes user requirements and suggests relevant variables for audience segmentation",
    parameters: {
      user_request: {
        type: "string",
        description: "Natural language description of desired audience"
      }
    },
    returns: {
      type: "array",
      description: "List of suggested variables with scores"
    }
  },
  
  data_retriever: {
    description: "Fetches data values for selected variables via API",
    parameters: {
      variable_codes: {
        type: "array",
        description: "List of confirmed variable codes"
      },
      sample_size: {
        type: "integer",
        description: "Optional sample size for data retrieval"
      }
    },
    returns: {
      type: "object",
      description: "Data table with values for each variable"
    }
  },
  
  cluster_analyzer: {
    description: "Performs K-Medians clustering with size constraints (5-10% per group)",
    parameters: {
      data: {
        type: "object",
        description: "Data table from data_retriever"
      }
    },
    returns: {
      type: "object",
      description: "Clustered data with group assignments"
    }
  },
  
  result_formatter: {
    description: "Formats clustering results into user-friendly output",
    parameters: {
      clustered_data: {
        type: "object",
        description: "Data with cluster assignments"
      }
    },
    returns: {
      type: "object",
      description: "Formatted audience segments with profiles"
    }
  }
};

// NLweb Configuration
class AudienceBuilderInterface {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.claudeEndpoint = 'https://api.anthropic.com/v1/messages';
    this.systemPrompt = `You are an intelligent audience segmentation assistant...`; // Use full prompt from earlier
    this.conversationHistory = [];
  }
  
  async processUserRequest(userInput) {
    // Add user input to conversation history
    this.conversationHistory.push({
      role: 'user',
      content: userInput
    });
    
    // Prepare the request for Claude
    const request = {
      model: 'claude-opus-4-20250514',
      messages: this.conversationHistory,
      system: this.systemPrompt,
      tools: audienceBuilderTools,
      max_tokens: 4000
    };
    
    try {
      // Send request to Claude API
      const response = await fetch(this.claudeEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': this.apiKey,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify(request)
      });
      
      const result = await response.json();
      
      // Process Claude's response and tool calls
      return this.handleClaudeResponse(result);
      
    } catch (error) {
      console.error('Error processing request:', error);
      return {
        error: 'Failed to process request',
        details: error.message
      };
    }
  }
  
  async handleClaudeResponse(response) {
    const content = response.content[0];
    
    // Check if Claude is requesting tool use
    if (content.type === 'tool_use') {
      const toolName = content.name;
      const toolInput = content.input;
      
      // Execute the requested tool
      const toolResult = await this.executeTool(toolName, toolInput);
      
      // Add tool result to conversation and get Claude's next response
      this.conversationHistory.push({
        role: 'assistant',
        content: [content]
      });
      
      this.conversationHistory.push({
        role: 'user',
        content: [{
          type: 'tool_result',
          tool_use_id: content.id,
          content: JSON.stringify(toolResult)
        }]
      });
      
      // Continue the conversation
      return this.processUserRequest('');
    }
    
    // Regular text response
    this.conversationHistory.push({
      role: 'assistant',
      content: content.text
    });
    
    return {
      message: content.text,
      requiresAction: this.checkIfActionRequired(content.text)
    };
  }
  
  async executeTool(toolName, input) {
    // This connects to your Python backend
    const backendUrl = `http://your-backend/api/${toolName}`;
    
    try {
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(input)
      });
      
      return await response.json();
      
    } catch (error) {
      return {
        error: `Failed to execute ${toolName}`,
        details: error.message
      };
    }
  }
  
  checkIfActionRequired(message) {
    // Check if Claude is asking for user confirmation
    const confirmationPhrases = [
      'confirm',
      'is this correct',
      'would you like to proceed',
      'please review'
    ];
    
    const lowerMessage = message.toLowerCase();
    return confirmationPhrases.some(phrase => lowerMessage.includes(phrase));
  }
}
```

## Flask Backend API

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import pandas as pd

app = Flask(__name__)
CORS(app)

# Initialize your audience builder
builder = AudienceBuilder(
    variable_catalog=load_variable_catalog(),
    api_endpoint=os.getenv('DATA_API_ENDPOINT'),
    api_key=os.getenv('DATA_API_KEY')
)

@app.route('/api/variable_selector', methods=['POST'])
def variable_selector():
    data = request.json
    user_request = data.get('user_request', '')
    
    # Use the variable selector
    suggestions = builder.variable_selector.analyze_request(user_request)
    
    return jsonify({
        'suggestions': suggestions[:10],
        'status': 'success'
    })

@app.route('/api/data_retriever', methods=['POST'])
def data_retriever():
    data = request.json
    variable_codes = data.get('variable_codes', [])
    sample_size = data.get('sample_size', None)
    
    # Fetch data
    df = builder.data_retriever.fetch_data(variable_codes, sample_size)
    
    # Convert to JSON-serializable format
    return jsonify({
        'data': df.to_dict('records'),
        'shape': df.shape,
        'status': 'success'
    })

@app.route('/api/cluster_analyzer', methods=['POST'])
def cluster_analyzer():
    data = request.json
    df_data = pd.DataFrame(data.get('data', []))
    
    # Apply clustering
    labels = builder.clusterer.fit_predict(df_data)
    df_data['Group'] = labels
    
    # Get group profiles
    profiles = builder.get_group_profiles()
    
    return jsonify({
        'clustered_data': df_data.to_dict('records'),
        'profiles': profiles,
        'status': 'success'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## Complete Workflow Example

### Step-by-Step Process Flow

#### 1. User Initiates Request

**User Input:** "I need to find environmentally conscious millennials with high disposable income who live in urban areas for our new sustainable product line."

#### 2. Claude Processes Natural Language

Claude receives this request and breaks it down into components:
- **Demographic:** Millennials (age range), urban areas (location)
- **Financial:** High disposable income
- **Psychographic:** Environmentally conscious
- **Behavioral:** Likely interested in sustainable products

#### 3. Variable Selection Process

Claude calls the `variable_selector` tool and presents suggestions to the user for confirmation.

#### 4. Data Retrieval and Clustering

After user confirmation, Claude orchestrates the data retrieval and clustering process, ensuring all groups meet the 5-10% size constraints.

#### 5. Results Presentation

Claude formats and presents the results with actionable insights for each segment.

## Implementation Best Practices

### Performance Optimization

1. **Use vectorized operations** whenever possible in your clustering algorithm
2. **Implement caching** for frequently requested variable combinations
3. **Consider sampling** for initial exploratory analysis before running full clustering
4. **Use asynchronous processing** for large datasets to avoid timeouts

### Security Considerations

1. **Implement proper authentication** between NLweb and your backend services
2. **Use environment variables** for sensitive configuration like API keys
3. **Add rate limiting** to prevent abuse of the clustering service
4. **Implement audit logging** for compliance and debugging

### Data Privacy

1. **Work with aggregated data** where possible to protect individual privacy
2. **Implement minimum group size constraints** to prevent identification of individuals
3. **Use secure data transmission** (HTTPS) for all API communications
4. **Consider data retention policies** for generated segments

### Scalability Design

1. **Use a job queue system** for large clustering jobs
2. **Implement horizontal scaling** for the Flask backend
3. **Consider pre-computing** common segmentation scenarios
4. **Use database indexing** for efficient variable retrieval

## Variable Catalog Structure

Your variable catalog should be comprehensive and well-documented. Here's an example structure:

```python
variable_catalog = {
    # Demographics
    "AGE_RANGE": {
        "type": "demographic",
        "description": "Age range categories",
        "values": ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
        "data_type": "categorical"
    },
    "INCOME_LEVEL": {
        "type": "financial",
        "description": "Household income brackets",
        "values": ["<30k", "30-50k", "50-75k", "75-100k", "100-150k", "150k+"],
        "data_type": "ordinal"
    },
    "LOCATION_TYPE": {
        "type": "demographic",
        "description": "Urban, suburban, or rural residence",
        "values": ["Urban", "Suburban", "Rural"],
        "data_type": "categorical"
    },
    
    # Behavioral
    "PURCHASE_FREQUENCY": {
        "type": "behavioral",
        "description": "Purchase frequency in last 12 months",
        "data_type": "numeric",
        "range": [0, 100]
    },
    "GREEN_PURCHASES": {
        "type": "behavioral",
        "description": "History of environmentally friendly purchases",
        "data_type": "binary",
        "values": [0, 1]
    },
    
    # Psychographic
    "SUSTAINABILITY_SCORE": {
        "type": "psychographic",
        "description": "Environmental consciousness index (0-100)",
        "data_type": "numeric",
        "range": [0, 100]
    },
    "TECH_ADOPTION": {
        "type": "psychographic",
        "description": "Early adopter score for technology",
        "data_type": "numeric",
        "range": [0, 10]
    }
}
```

## Monitoring and Analytics

Implement monitoring to track system usage and performance:

```python
# Example monitoring metrics
metrics_to_track = {
    "request_volume": "Number of audience creation requests per day",
    "avg_segment_size": "Average size of created segments",
    "variable_usage": "Most frequently selected variables",
    "clustering_time": "Average time to complete clustering",
    "user_satisfaction": "Percentage of confirmed vs rejected segments"
}
```

## Error Handling

Implement comprehensive error handling throughout the system:

```python
class AudienceBuilderError(Exception):
    """Base exception for audience builder"""
    pass

class InsufficientDataError(AudienceBuilderError):
    """Raised when not enough data for clustering"""
    pass

class ConstraintViolationError(AudienceBuilderError):
    """Raised when size constraints cannot be satisfied"""
    pass

# Use in your code:
try:
    results = builder.build_audience(request, variables)
except InsufficientDataError:
    return {"error": "Not enough data points for the selected criteria"}
except ConstraintViolationError:
    return {"error": "Unable to create segments within size constraints"}
```

## Next Steps

1. **Adapt the data retriever** to work with your actual data infrastructure
2. **Customize the variable catalog** based on your available data fields
3. **Test the clustering algorithm** with your data to tune parameters
4. **Set up the Flask backend** with proper security and monitoring
5. **Configure NLweb** to communicate with your backend services
6. **Create a feedback mechanism** to improve variable selection over time

Remember to start with a pilot program, gather user feedback, and iterate on the system. The combination of Claude's natural language understanding and your domain-specific tools creates a powerful platform for democratizing audience intelligence across your organization.