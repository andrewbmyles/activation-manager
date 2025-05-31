# Data Persistence Implementation Guide

## Overview

This guide explains how to implement data persistence for saving user audiences, platforms, and distributions in the Activation Manager application.

## Architecture

### Storage Options

1. **Parquet Files** (Default)
   - Simple file-based storage
   - No external dependencies
   - Good for single-server deployments
   - Partitioned by user and date

2. **BigQuery** (Enterprise)
   - Scalable cloud storage
   - SQL query capabilities
   - Better for multi-server deployments
   - Built-in analytics

## Quick Start

### 1. Parquet Storage (Recommended for Getting Started)

```bash
# No additional setup required!
# Files are automatically created in data/persistence/

# Start the persistence API
python api/persistence_api.py
```

### 2. BigQuery Storage

```bash
# Set up BigQuery project
export GOOGLE_CLOUD_PROJECT=your-project-id
export STORAGE_BACKEND=bigquery

# Run setup script
bq mk --dataset activation_manager
bq query < data_persistence/bigquery_setup.sql

# Start the persistence API
python api/persistence_api.py
```

## API Integration

### Frontend Integration

Add these API calls to your React components:

#### Save Audience
```javascript
// In EnhancedNLAudienceBuilder.tsx, after segment creation
const saveAudience = async () => {
  const audienceData = {
    user_id: currentUser.id,  // Get from auth context
    name: audienceName,
    description: audienceDescription,
    data_type: selectedDataType.id,
    original_query: originalUserQuery,
    selected_variables: Array.from(selectedVariables),
    variable_details: suggestedVariables.filter(v => 
      selectedVariables.has(v.code)
    ),
    segments: segments,
    total_audience_size: segments.reduce((sum, s) => sum + s.size, 0),
    status: 'active',
    metadata: {
      campaign_id: campaignId,
      tags: audienceTags
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
    showSuccessMessage('Audience saved successfully!');
  }
};
```

#### List Saved Audiences
```javascript
// In a new SavedAudiences component
const fetchAudiences = async () => {
  const response = await fetch(`/api/audiences?user_id=${currentUser.id}`);
  const data = await response.json();
  
  if (data.success) {
    setAudiences(data.audiences);
  }
};
```

#### Platform Management
```javascript
// Save platform configuration
const savePlatform = async (platformData) => {
  const response = await fetch('/api/platforms', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: currentUser.id,
      platform_type: 'the_trade_desk',
      name: 'My Trade Desk Account',
      credentials: {
        api_key: encryptedApiKey,  // Encrypt on frontend
        account_id: accountId
      },
      settings: {
        default_match_rate: 0.7,
        auto_refresh: true,
        refresh_frequency: 'weekly'
      }
    })
  });
};
```

#### Distribution Tracking
```javascript
// Create distribution record
const createDistribution = async () => {
  const response = await fetch('/api/distributions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: currentUser.id,
      audience_id: audienceId,
      platform_id: selectedPlatform.id,
      scheduled_at: scheduledDate,
      segments_distributed: selectedSegments.map(s => s.segment_id),
      metadata: {
        campaign_name: campaignName,
        approval_status: 'pending'
      }
    })
  });
};
```

## UI Components

### 1. Saved Audiences Page

Create `src/pages/SavedAudiences.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Archive, Download, Eye, Trash2 } from 'lucide-react';

export function SavedAudiences() {
  const [audiences, setAudiences] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAudiences();
  }, []);

  const fetchAudiences = async () => {
    try {
      const response = await fetch(`/api/audiences?user_id=${currentUser.id}`);
      const data = await response.json();
      setAudiences(data.audiences);
    } finally {
      setLoading(false);
    }
  };

  const handleViewAudience = (audienceId: string) => {
    navigate(`/audience/${audienceId}`);
  };

  const handleArchiveAudience = async (audienceId: string) => {
    const response = await fetch(`/api/audiences/${audienceId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: currentUser.id,
        status: 'archived'
      })
    });

    if (response.ok) {
      fetchAudiences(); // Refresh list
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Saved Audiences</h1>
      
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="grid gap-4">
          {audiences.map(audience => (
            <div key={audience.audience_id} className="bg-white p-4 rounded-lg shadow">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">{audience.name}</h3>
                  <p className="text-sm text-gray-600">{audience.description}</p>
                  <div className="flex gap-4 mt-2 text-sm text-gray-500">
                    <span>{audience.total_audience_size.toLocaleString()} records</span>
                    <span>{audience.segments?.length || 0} segments</span>
                    <span>Created {new Date(audience.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleViewAudience(audience.audience_id)}
                    className="p-2 hover:bg-gray-100 rounded"
                  >
                    <Eye size={18} />
                  </button>
                  <button
                    onClick={() => handleArchiveAudience(audience.audience_id)}
                    className="p-2 hover:bg-gray-100 rounded"
                  >
                    <Archive size={18} />
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

### 2. Platform Management Component

```typescript
// src/components/PlatformManager.tsx
export function PlatformManager() {
  const [platforms, setPlatforms] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);

  // Fetch and display platforms
  // Add/edit platform forms
  // Test connection functionality
}
```

### 3. Distribution History

```typescript
// src/components/DistributionHistory.tsx
export function DistributionHistory({ audienceId }: { audienceId: string }) {
  const [distributions, setDistributions] = useState([]);

  // Show distribution timeline
  // Display match rates
  // Show error details if any
}
```

## Security Considerations

### 1. User Authentication
```javascript
// Add user context
const currentUser = {
  id: 'user123',  // From auth provider
  email: 'user@example.com',
  organization: 'org123'
};
```

### 2. Credential Encryption
```javascript
// Frontend encryption before saving
import CryptoJS from 'crypto-js';

const encryptCredentials = (credentials) => {
  const encrypted = CryptoJS.AES.encrypt(
    JSON.stringify(credentials),
    process.env.REACT_APP_ENCRYPTION_KEY
  ).toString();
  return encrypted;
};
```

### 3. Access Control
- All API endpoints require user_id
- Users can only access their own data
- Implement row-level security in BigQuery

## Deployment

### Environment Variables
```bash
# .env
STORAGE_BACKEND=parquet  # or bigquery
GOOGLE_CLOUD_PROJECT=your-project-id
ENCRYPTION_KEY=your-secret-key
```

### Docker Support
```dockerfile
# Add to existing Dockerfile
COPY data_persistence/ /app/data_persistence/
RUN pip install pyarrow pandas google-cloud-bigquery
```

### App Engine Configuration
```yaml
# app.yaml
env_variables:
  STORAGE_BACKEND: 'parquet'
  
handlers:
- url: /api/audiences.*
  script: api.persistence_api.app
- url: /api/platforms.*
  script: api.persistence_api.app
- url: /api/distributions.*
  script: api.persistence_api.app
```

## Testing

### Unit Tests
```python
# test_persistence.py
def test_save_audience():
    handler = AudienceHandler()
    audience_data = {
        'user_id': 'test_user',
        'name': 'Test Audience',
        'data_type': 'first_party',
        'selected_variables': ['VAR1', 'VAR2']
    }
    
    audience_id = handler.save_audience(audience_data)
    assert audience_id is not None
    
    # Retrieve and verify
    retrieved = handler.get_audience(audience_id, 'test_user')
    assert retrieved['name'] == 'Test Audience'
```

### Integration Tests
```javascript
// Frontend integration test
it('should save and retrieve audience', async () => {
  // Create audience through UI
  // Save it
  // Navigate to saved audiences
  // Verify it appears in list
});
```

## Migration from Existing Data

If you have existing audiences in memory or other storage:

```python
# migration_script.py
def migrate_existing_audiences():
    # Load existing data
    existing_audiences = load_from_old_storage()
    
    # Initialize handler
    handler = AudienceHandler()
    
    # Migrate each audience
    for audience in existing_audiences:
        handler.save_audience(audience)
    
    print(f"Migrated {len(existing_audiences)} audiences")
```

## Monitoring

### Metrics to Track
- Storage usage per user
- API response times
- Failed distribution attempts
- Platform sync success rates

### Logging
```python
import logging

logger = logging.getLogger(__name__)

# In API endpoints
logger.info(f"Audience created: {audience_id} for user: {user_id}")
logger.error(f"Distribution failed: {distribution_id} - {error}")
```

## Next Steps

1. **Immediate**: Start with Parquet storage for simplicity
2. **Short-term**: Add UI components for viewing saved items
3. **Medium-term**: Implement platform integrations
4. **Long-term**: Migrate to BigQuery for scale

## Support

For questions or issues:
- Check the error logs in `data/persistence/logs/`
- Review the API response error messages
- Ensure proper user authentication is in place