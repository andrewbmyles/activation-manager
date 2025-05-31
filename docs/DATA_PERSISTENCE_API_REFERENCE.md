# Data Persistence API Reference

## Overview

The Data Persistence API provides RESTful endpoints for managing audiences, platforms, and distributions. All endpoints require user authentication (currently using demo_user).

## Base URL

```
Production: https://tobermory.ai/api
Development: http://localhost:8080/api
```

## Authentication

Currently using `user_id` parameter. Will be replaced with proper JWT authentication.

## Endpoints

### Audiences

#### Create/Save Audience

```http
POST /api/audiences
Content-Type: application/json

{
  "user_id": "string",
  "name": "string",
  "description": "string",
  "data_type": "first_party|third_party|clean_room",
  "original_query": "string",
  "selected_variables": ["string"],
  "variable_details": [
    {
      "code": "string",
      "description": "string",
      "relevance_score": 0.95,
      "type": "string",
      "category": "string"
    }
  ],
  "segments": [
    {
      "segment_id": 0,
      "name": "string",
      "size": 0,
      "size_percentage": 0.0,
      "characteristics": {},
      "prizm_segments": ["string"]
    }
  ],
  "total_audience_size": 0,
  "status": "draft|active|archived",
  "metadata": {
    "created_from": "string",
    "session_id": "string",
    "tags": ["string"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "audience_id": "aud_12345678",
  "message": "Audience saved successfully"
}
```

#### Get Audience

```http
GET /api/audiences/{audience_id}?user_id={user_id}
```

**Response:**
```json
{
  "success": true,
  "audience": {
    "audience_id": "aud_12345678",
    "user_id": "demo_user",
    "name": "Audience - 5/30/2025",
    "description": "Environmentally conscious millennials",
    "created_at": "2025-05-30T12:00:00Z",
    "updated_at": "2025-05-30T12:00:00Z",
    "status": "active",
    "data_type": "first_party",
    "original_query": "environmentally conscious millennials",
    "selected_variables": ["ENV_CONSCIOUS", "AGE_25_34"],
    "variable_details": [...],
    "segments": [...],
    "total_audience_size": 250000,
    "metadata": {...}
  }
}
```

#### List Audiences

```http
GET /api/audiences?user_id={user_id}&status={status}&limit={limit}
```

**Query Parameters:**
- `user_id` (required): User identifier
- `status` (optional): Filter by status (active, archived, draft)
- `limit` (optional): Maximum results to return (default: 50)

**Response:**
```json
{
  "success": true,
  "audiences": [
    {
      "audience_id": "aud_12345678",
      "name": "Audience - 5/30/2025",
      "description": "...",
      "total_audience_size": 250000,
      "segments": [...],
      "created_at": "2025-05-30T12:00:00Z",
      "status": "active"
    }
  ],
  "count": 10
}
```

#### Update Audience Status

```http
PUT /api/audiences/{audience_id}/status
Content-Type: application/json

{
  "user_id": "string",
  "status": "draft|active|archived"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Audience status updated to archived"
}
```

### Platforms (Future)

#### Save Platform Configuration

```http
POST /api/platforms
Content-Type: application/json

{
  "user_id": "string",
  "platform_type": "the_trade_desk|meta|google_ads|amazon_dsp",
  "name": "string",
  "credentials": {
    "encrypted": "string",
    "account_id": "string"
  },
  "settings": {
    "default_match_rate": 0.7,
    "auto_refresh": true,
    "refresh_frequency": "daily|weekly|monthly"
  },
  "status": "connected|disconnected|pending"
}
```

#### List Platforms

```http
GET /api/platforms?user_id={user_id}
```

### Distributions (Future)

#### Create Distribution

```http
POST /api/distributions
Content-Type: application/json

{
  "user_id": "string",
  "audience_id": "string",
  "platform_id": "string",
  "scheduled_at": "2025-05-30T12:00:00Z",
  "segments_distributed": [0, 1, 2],
  "metadata": {
    "campaign_name": "string",
    "approval_status": "pending|approved|rejected"
  }
}
```

#### Update Distribution Status

```http
PUT /api/distributions/{distribution_id}/status
Content-Type: application/json

{
  "user_id": "string",
  "status": "pending|in_progress|completed|failed",
  "metadata": {
    "match_rate": 0.72,
    "matched_records": 180000,
    "error_message": "string"
  }
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "details": "Additional error details",
  "code": "ERROR_CODE"
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (missing/invalid parameters)
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (persistence not enabled)

## Data Formats

### Timestamps
All timestamps are in ISO 8601 format: `YYYY-MM-DDTHH:mm:ss.sssZ`

### IDs
- Audience IDs: `aud_` prefix + 8 character hex
- Platform IDs: `plat_` prefix + 8 character hex  
- Distribution IDs: `dist_` prefix + 8 character hex

### Variable Details Structure
```json
{
  "code": "ENV_CONSCIOUS",
  "description": "Environmentally Conscious",
  "relevance_score": 0.95,
  "type": "psychographic",
  "category": "Psychographic"
}
```

### Segment Structure
```json
{
  "segment_id": 0,
  "name": "Eco-Forward Innovators",
  "size": 125000,
  "size_percentage": 8.2,
  "characteristics": {
    "avg_income": "$120,000",
    "primary_age": "28-32",
    "top_interests": ["sustainability", "technology"]
  },
  "prizm_segments": ["Young Digerati", "Bohemian Mix"]
}
```

## Rate Limits

Currently no rate limits implemented. Future versions will include:
- 100 requests per minute per user
- 1000 audiences per user
- 50MB max request size

## Webhooks (Future)

Planned webhook events:
- `audience.created`
- `audience.updated`
- `audience.archived`
- `distribution.completed`
- `distribution.failed`

## SDK Examples

### Python
```python
import requests

# Save audience
response = requests.post(
    "https://tobermory.ai/api/audiences",
    json={
        "user_id": "demo_user",
        "name": "My Audience",
        "data_type": "first_party",
        "selected_variables": ["VAR1", "VAR2"],
        "status": "active"
    }
)
audience_id = response.json()["audience_id"]

# List audiences
response = requests.get(
    "https://tobermory.ai/api/audiences",
    params={"user_id": "demo_user", "status": "active"}
)
audiences = response.json()["audiences"]
```

### JavaScript
```javascript
// Save audience
const response = await fetch('/api/audiences', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'demo_user',
    name: 'My Audience',
    data_type: 'first_party',
    selected_variables: ['VAR1', 'VAR2'],
    status: 'active'
  })
});
const { audience_id } = await response.json();

// List audiences
const response = await fetch('/api/audiences?user_id=demo_user');
const { audiences } = await response.json();
```

## Migration Guide

For migrating from in-memory to persistent storage:

1. Export existing audiences to JSON
2. Transform to match new schema
3. POST each audience to `/api/audiences`
4. Verify with GET requests
5. Update frontend to use new endpoints