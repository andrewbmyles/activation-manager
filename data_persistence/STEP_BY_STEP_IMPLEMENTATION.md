# Step-by-Step Implementation Plan

## Phase 1: Backend Setup (Day 1)

### Step 1: Install Dependencies
```bash
# Add to requirements.txt
pyarrow>=8.0.0
pandas>=1.4.0
```

```bash
# Install dependencies
pip install pyarrow pandas
```

### Step 2: Start Persistence API
```bash
# Test the persistence API standalone
cd /Users/myles/Documents/Activation\ Manager
python api/persistence_api.py

# API will run on http://localhost:8081
# Test with: curl http://localhost:8081/api/health
```

### Step 3: Integrate with Main App
```python
# In main.py, add persistence API endpoints
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api.persistence_api import app as persistence_app

# Mount persistence routes
app.mount("/persist", WSGIMiddleware(persistence_app))
```

## Phase 2: Frontend Integration - Save Functionality (Day 2)

### Step 1: Add Save Button to EnhancedNLAudienceBuilder
```typescript
// In src/components/EnhancedNLAudienceBuilder.tsx
// Add after segment confirmation (around line 890)

const handleSaveAudience = async () => {
  try {
    const audienceData = {
      user_id: 'demo_user', // TODO: Get from auth context
      name: `Audience - ${new Date().toLocaleDateString()}`,
      description: originalUserQuery,
      data_type: selectedDataType?.id || 'first_party',
      original_query: originalUserQuery,
      selected_variables: Array.from(selectedVariables),
      variable_details: suggestedVariables.filter(v => 
        selectedVariables.has(v.code)
      ).map(v => ({
        code: v.code,
        description: v.description,
        relevance_score: v.relevance_score,
        type: v.type
      })),
      segments: segments.map(s => ({
        segment_id: s.group_id,
        name: s.name,
        size: s.size,
        size_percentage: s.size_percentage,
        characteristics: s.characteristics,
        prizm_segments: s.prizm_profile?.dominant_segments
      })),
      total_audience_size: segments.reduce((sum, s) => sum + s.size, 0),
      status: 'active',
      metadata: {
        created_from: 'nl_audience_builder',
        session_id: sessionId
      }
    };

    const response = await fetch('/api/audiences', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(audienceData)
    });

    const result = await response.json();
    
    if (result.success) {
      setAudienceId(result.audience_id);
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: '✅ Audience saved successfully! You can access it from the Saved Audiences page.'
      }]);
    }
  } catch (error) {
    console.error('Error saving audience:', error);
    setMessages(prev => [...prev, {
      type: 'assistant',
      content: '❌ Failed to save audience. Please try again.'
    }]);
  }
};

// Add save button in the UI (after Confirm Segments button)
<button
  onClick={handleSaveAudience}
  className="flex items-center gap-2 px-3 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600 text-sm"
>
  <Save size={16} />
  Save Audience
</button>
```

### Step 2: Add API Proxy Configuration
```typescript
// In src/config/api.ts
// Add persistence endpoints
export const PERSISTENCE_ENDPOINTS = {
  saveAudience: () => getApiUrl('api/audiences'),
  getAudience: (id: string) => getApiUrl(`api/audiences/${id}`),
  listAudiences: () => getApiUrl('api/audiences'),
  updateAudienceStatus: (id: string) => getApiUrl(`api/audiences/${id}/status`)
};
```

## Phase 3: Create Saved Audiences UI (Day 3)

### Step 1: Create SavedAudiences Page
```typescript
// Create src/pages/SavedAudiences.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Archive, Eye, RefreshCw, Download } from 'lucide-react';

export function SavedAudiences() {
  const [audiences, setAudiences] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAudiences();
  }, []);

  const fetchAudiences = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/audiences?user_id=demo_user');
      const data = await response.json();
      
      if (data.success) {
        setAudiences(data.audiences);
      }
    } catch (error) {
      console.error('Error fetching audiences:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewAudience = (audienceId: string) => {
    // Navigate to audience detail view
    navigate(`/audience/${audienceId}`);
  };

  const handleArchiveAudience = async (audienceId: string) => {
    if (!confirm('Are you sure you want to archive this audience?')) return;

    try {
      const response = await fetch(`/api/audiences/${audienceId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'demo_user',
          status: 'archived'
        })
      });

      if (response.ok) {
        fetchAudiences(); // Refresh list
      }
    } catch (error) {
      console.error('Error archiving audience:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="animate-spin text-gray-500" size={32} />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Saved Audiences</h1>
        <button
          onClick={() => navigate('/audience-builder')}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Create New Audience
        </button>
      </div>

      {audiences.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-600">No saved audiences yet.</p>
          <p className="text-sm text-gray-500 mt-2">
            Create your first audience using the Natural Language Audience Builder.
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {audiences.map(audience => (
            <div key={audience.audience_id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-800">{audience.name}</h3>
                  <p className="text-gray-600 mt-1">{audience.description}</p>
                  
                  <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Users size={14} />
                      {audience.total_audience_size?.toLocaleString() || 0} records
                    </span>
                    <span>•</span>
                    <span>{audience.segments?.length || 0} segments</span>
                    <span>•</span>
                    <span>Created {new Date(audience.created_at).toLocaleDateString()}</span>
                  </div>

                  {audience.selected_variables && (
                    <div className="mt-3">
                      <p className="text-xs text-gray-500 mb-1">Variables:</p>
                      <div className="flex flex-wrap gap-1">
                        {audience.selected_variables.slice(0, 5).map((varCode: string) => (
                          <span key={varCode} className="text-xs px-2 py-1 bg-gray-100 rounded">
                            {varCode}
                          </span>
                        ))}
                        {audience.selected_variables.length > 5 && (
                          <span className="text-xs px-2 py-1 text-gray-500">
                            +{audience.selected_variables.length - 5} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => handleViewAudience(audience.audience_id)}
                    className="p-2 hover:bg-gray-100 rounded-md transition-colors"
                    title="View Details"
                  >
                    <Eye size={18} className="text-gray-600" />
                  </button>
                  <button
                    onClick={() => {/* TODO: Implement export */}}
                    className="p-2 hover:bg-gray-100 rounded-md transition-colors"
                    title="Export"
                  >
                    <Download size={18} className="text-gray-600" />
                  </button>
                  <button
                    onClick={() => handleArchiveAudience(audience.audience_id)}
                    className="p-2 hover:bg-gray-100 rounded-md transition-colors"
                    title="Archive"
                  >
                    <Archive size={18} className="text-gray-600" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Step 2: Add Route to App.tsx
```typescript
// In src/App.tsx
import { SavedAudiences } from './pages/SavedAudiences';

// Add route
<Route path="/saved-audiences" element={<SavedAudiences />} />
```

### Step 3: Update Navigation
```typescript
// In src/components/Layout.tsx or navigation component
// Add menu item
<Link
  to="/saved-audiences"
  className="flex items-center gap-2 px-4 py-2 hover:bg-gray-100 rounded-md"
>
  <Database size={20} />
  Saved Audiences
</Link>
```

## Phase 4: Testing & Validation (Day 4)

### Step 1: Test Data Flow
```bash
# 1. Create a test audience through the UI
# 2. Check that data is saved
ls -la data/persistence/audiences/

# 3. Verify API response
curl http://localhost:8081/api/audiences?user_id=demo_user
```

### Step 2: Add Error Handling
```typescript
// Add to all API calls
try {
  const response = await fetch(url, options);
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || 'Unknown error');
  }
  
  return data;
} catch (error) {
  console.error('API call failed:', error);
  // Show user-friendly error message
}
```

## Phase 5: Production Deployment (Day 5)

### Step 1: Update app.yaml
```yaml
# Add to app.yaml
handlers:
- url: /api/audiences.*
  script: auto
- url: /api/platforms.*
  script: auto
- url: /api/distributions.*
  script: auto

env_variables:
  STORAGE_BACKEND: "parquet"
```

### Step 2: Update requirements.txt
```txt
# Add these lines
pyarrow==8.0.0
pandas==1.4.3
```

### Step 3: Deploy
```bash
# Deploy to GCP
gcloud app deploy

# Or deploy to Vercel with API routes
vercel --prod
```

## Quick Start Testing

### 1. Minimal Test Setup
```bash
# Terminal 1: Start main app
python main.py

# Terminal 2: Start persistence API
python api/persistence_api.py

# Terminal 3: Test save endpoint
curl -X POST http://localhost:8081/api/audiences \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "name": "Test Audience",
    "data_type": "first_party",
    "selected_variables": ["VAR1", "VAR2"],
    "status": "active"
  }'
```

### 2. Verify Data Saved
```bash
# Check files created
find data/persistence -name "*.parquet" -type f

# Should see something like:
# data/persistence/audiences/user_id=test_user/year=2025/month=05/audiences_202505.parquet
```

## Common Issues & Solutions

### Issue 1: CORS Errors
```python
# In persistence_api.py, already handled with:
CORS(app)
```

### Issue 2: Port Conflicts
```python
# Change port in persistence_api.py
port = int(os.environ.get('PORT', 8082))  # Change to different port
```

### Issue 3: File Permissions
```bash
# Ensure write permissions
chmod -R 755 data/persistence/
```

## Next Steps

1. **User Authentication**: Replace 'demo_user' with actual auth
2. **Platform Integration**: Add platform management UI
3. **Distribution Tracking**: Implement distribution workflow
4. **BigQuery Migration**: When ready for scale

## Success Checklist

- [ ] Persistence API running
- [ ] Save button appears in audience builder
- [ ] Audiences save successfully
- [ ] Saved audiences page shows list
- [ ] Archive functionality works
- [ ] Data persists after restart