# Data Persistence Schema Design

## Overview
This document outlines the schema design for persisting user audiences, platforms, and distributions using both BigQuery and Parquet file options.

## Core Entities

### 1. Audiences
Stores user-created audience definitions with their variables and segments.

```json
{
  "audience_id": "string (UUID)",
  "user_id": "string",
  "name": "string",
  "description": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "status": "draft|active|archived",
  "data_type": "first_party|third_party|clean_room",
  "original_query": "string",
  "selected_variables": ["array of variable codes"],
  "variable_details": [
    {
      "code": "string",
      "description": "string",
      "relevance_score": "float",
      "type": "string"
    }
  ],
  "segments": [
    {
      "segment_id": "string",
      "name": "string",
      "size": "integer",
      "size_percentage": "float",
      "characteristics": "json",
      "prizm_segments": ["array"]
    }
  ],
  "total_audience_size": "integer",
  "metadata": {
    "tags": ["array"],
    "campaign_id": "string",
    "notes": "string"
  }
}
```

### 2. Platforms
Stores platform configurations for distribution.

```json
{
  "platform_id": "string (UUID)",
  "user_id": "string",
  "platform_type": "the_trade_desk|google_ads|facebook|amazon_dsp|etc",
  "name": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "status": "active|inactive",
  "credentials": {
    "encrypted": true,
    "api_key": "encrypted_string",
    "account_id": "string",
    "additional_config": "encrypted_json"
  },
  "settings": {
    "default_match_rate": "float",
    "auto_refresh": "boolean",
    "refresh_frequency": "daily|weekly|monthly"
  },
  "last_sync": "timestamp",
  "sync_status": "success|failed|pending"
}
```

### 3. Distributions
Tracks audience distributions to platforms.

```json
{
  "distribution_id": "string (UUID)",
  "user_id": "string",
  "audience_id": "string",
  "platform_id": "string",
  "created_at": "timestamp",
  "scheduled_at": "timestamp",
  "executed_at": "timestamp",
  "status": "scheduled|processing|completed|failed",
  "distribution_type": "initial|refresh|incremental",
  "segments_distributed": ["array of segment_ids"],
  "match_results": {
    "total_records": "integer",
    "matched_records": "integer",
    "match_rate": "float",
    "platform_audience_id": "string"
  },
  "error_details": {
    "error_code": "string",
    "error_message": "string",
    "retry_count": "integer"
  },
  "metadata": {
    "campaign_name": "string",
    "cost_estimate": "float",
    "approval_status": "pending|approved|rejected",
    "approved_by": "string"
  }
}
```

### 4. Users (Optional)
Basic user information for multi-tenancy.

```json
{
  "user_id": "string",
  "email": "string",
  "organization": "string",
  "created_at": "timestamp",
  "last_login": "timestamp",
  "permissions": ["array"],
  "quota": {
    "max_audiences": "integer",
    "max_distributions_per_month": "integer",
    "current_usage": "json"
  }
}
```

## BigQuery Schema

### audiences table
```sql
CREATE TABLE `project.dataset.audiences` (
  audience_id STRING NOT NULL,
  user_id STRING NOT NULL,
  name STRING NOT NULL,
  description STRING,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  status STRING NOT NULL,
  data_type STRING NOT NULL,
  original_query STRING,
  selected_variables ARRAY<STRING>,
  variable_details JSON,
  segments JSON,
  total_audience_size INT64,
  metadata JSON,
  PRIMARY KEY (audience_id) NOT ENFORCED
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, status;
```

### platforms table
```sql
CREATE TABLE `project.dataset.platforms` (
  platform_id STRING NOT NULL,
  user_id STRING NOT NULL,
  platform_type STRING NOT NULL,
  name STRING NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  status STRING NOT NULL,
  credentials JSON,  -- Encrypted
  settings JSON,
  last_sync TIMESTAMP,
  sync_status STRING,
  PRIMARY KEY (platform_id) NOT ENFORCED
)
CLUSTER BY user_id, platform_type;
```

### distributions table
```sql
CREATE TABLE `project.dataset.distributions` (
  distribution_id STRING NOT NULL,
  user_id STRING NOT NULL,
  audience_id STRING NOT NULL,
  platform_id STRING NOT NULL,
  created_at TIMESTAMP NOT NULL,
  scheduled_at TIMESTAMP,
  executed_at TIMESTAMP,
  status STRING NOT NULL,
  distribution_type STRING,
  segments_distributed ARRAY<STRING>,
  match_results JSON,
  error_details JSON,
  metadata JSON,
  PRIMARY KEY (distribution_id) NOT ENFORCED
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, audience_id, status;
```

## Parquet File Structure

### Directory Structure
```
data/
├── audiences/
│   ├── user_id=user123/
│   │   ├── year=2025/
│   │   │   ├── month=05/
│   │   │   │   └── audiences_2025_05.parquet
├── platforms/
│   ├── user_id=user123/
│   │   └── platforms.parquet
└── distributions/
    ├── user_id=user123/
    │   ├── year=2025/
    │   │   ├── month=05/
    │   │   │   └── distributions_2025_05.parquet
```

### Parquet Schema (PyArrow)
```python
import pyarrow as pa

# Audiences Schema
audiences_schema = pa.schema([
    pa.field('audience_id', pa.string()),
    pa.field('user_id', pa.string()),
    pa.field('name', pa.string()),
    pa.field('description', pa.string()),
    pa.field('created_at', pa.timestamp('ms')),
    pa.field('updated_at', pa.timestamp('ms')),
    pa.field('status', pa.string()),
    pa.field('data_type', pa.string()),
    pa.field('original_query', pa.string()),
    pa.field('selected_variables', pa.list_(pa.string())),
    pa.field('variable_details', pa.string()),  # JSON string
    pa.field('segments', pa.string()),  # JSON string
    pa.field('total_audience_size', pa.int64()),
    pa.field('metadata', pa.string())  # JSON string
])

# Platforms Schema
platforms_schema = pa.schema([
    pa.field('platform_id', pa.string()),
    pa.field('user_id', pa.string()),
    pa.field('platform_type', pa.string()),
    pa.field('name', pa.string()),
    pa.field('created_at', pa.timestamp('ms')),
    pa.field('updated_at', pa.timestamp('ms')),
    pa.field('status', pa.string()),
    pa.field('credentials', pa.string()),  # Encrypted JSON
    pa.field('settings', pa.string()),  # JSON string
    pa.field('last_sync', pa.timestamp('ms')),
    pa.field('sync_status', pa.string())
])

# Distributions Schema
distributions_schema = pa.schema([
    pa.field('distribution_id', pa.string()),
    pa.field('user_id', pa.string()),
    pa.field('audience_id', pa.string()),
    pa.field('platform_id', pa.string()),
    pa.field('created_at', pa.timestamp('ms')),
    pa.field('scheduled_at', pa.timestamp('ms')),
    pa.field('executed_at', pa.timestamp('ms')),
    pa.field('status', pa.string()),
    pa.field('distribution_type', pa.string()),
    pa.field('segments_distributed', pa.list_(pa.string())),
    pa.field('match_results', pa.string()),  # JSON string
    pa.field('error_details', pa.string()),  # JSON string
    pa.field('metadata', pa.string())  # JSON string
])
```

## Access Patterns

### Common Queries
1. **Get all audiences for a user**
   - Filter: `user_id = ? AND status != 'archived'`
   - Sort: `created_at DESC`

2. **Get audience details with segments**
   - Filter: `audience_id = ?`
   - Include: All fields

3. **Get distribution history for an audience**
   - Filter: `audience_id = ? AND user_id = ?`
   - Sort: `created_at DESC`

4. **Get active platforms for a user**
   - Filter: `user_id = ? AND status = 'active'`

5. **Get recent distributions**
   - Filter: `user_id = ? AND created_at > ?`
   - Sort: `created_at DESC`
   - Limit: 50

## Security Considerations

1. **Encryption**
   - Platform credentials must be encrypted at rest
   - Use Google Cloud KMS or similar for key management

2. **Access Control**
   - Implement row-level security based on user_id
   - Service accounts with minimal permissions

3. **Data Retention**
   - Archive old distributions after 90 days
   - Keep audience definitions indefinitely (user data)

4. **PII Protection**
   - No PII in audience definitions
   - Aggregate data only