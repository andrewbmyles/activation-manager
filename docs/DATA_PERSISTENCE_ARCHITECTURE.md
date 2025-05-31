# Data Persistence Architecture

## Overview

The data persistence layer provides durable storage for user-created audiences, platform configurations, and distribution history. It's designed for scalability, performance, and data isolation.

## Architecture Principles

1. **User Isolation**: Strict data separation by user ID
2. **Performance**: Optimized for read-heavy workloads
3. **Scalability**: Partitioned storage prevents single-file bottlenecks
4. **Flexibility**: Easy migration path from files to cloud storage
5. **Thread Safety**: Concurrent operations handled gracefully

## Storage Design

### Parquet File Storage (Current)

```
data/persistence/
├── audiences/
│   └── user_id={user_id}/
│       └── year={year}/
│           └── month={month}/
│               └── audiences_{yyyymm}.parquet
├── platforms/
│   └── user_id={user_id}/
│       └── platforms.parquet
└── distributions/
    └── user_id={user_id}/
        └── year={year}/
            └── month={month}/
                └── distributions_{yyyymm}.parquet
```

**Benefits:**
- Columnar storage for efficient queries
- Built-in compression
- Schema evolution support
- Excellent for analytical workloads

### BigQuery Storage (Future)

```sql
-- Audiences table
CREATE TABLE activation_manager.audiences (
  audience_id STRING NOT NULL,
  user_id STRING NOT NULL,
  name STRING,
  description STRING,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  status STRING,
  data_type STRING,
  original_query STRING,
  selected_variables ARRAY<STRING>,
  variable_details JSON,
  segments JSON,
  total_audience_size INT64,
  metadata JSON
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, status;
```

## Component Architecture

### 1. Storage Layer

```python
ParquetDataHandler (Base Class)
├── AudienceHandler
│   ├── save_audience()
│   ├── get_audience()
│   ├── list_audiences()
│   └── update_audience_status()
├── PlatformHandler
│   ├── save_platform()
│   ├── get_platform()
│   ├── list_platforms()
│   └── update_platform_status()
└── DistributionHandler
    ├── save_distribution()
    ├── get_distribution()
    ├── list_distributions()
    └── update_distribution_status()
```

### 2. API Layer

```
Flask API Endpoints
├── /api/audiences
│   ├── POST   - Create audience
│   ├── GET    - List audiences
│   └── /{id}
│       ├── GET    - Get specific audience
│       └── /status
│           └── PUT - Update status
├── /api/platforms
│   ├── POST   - Save platform
│   ├── GET    - List platforms
│   └── /{id}
│       ├── GET    - Get platform
│       └── /status
│           └── PUT - Update status
└── /api/distributions
    ├── POST   - Create distribution
    ├── GET    - List distributions
    └── /{id}
        ├── GET    - Get distribution
        └── /status
            └── PUT - Update status
```

### 3. Frontend Integration

```typescript
// React Components
EnhancedNLAudienceBuilder
├── handleSaveAudience()      // Save logic
└── Save Button               // UI trigger

SavedAudiences Page
├── fetchAudiences()          // List retrieval
├── handleArchiveAudience()   // Archive action
└── Audience List View        // Display component
```

## Data Flow

### Save Operation

```
1. User clicks "Save Audience"
2. Frontend collects audience data
3. POST /api/audiences
4. Backend validates data
5. AudienceHandler.save_audience()
6. Acquire write lock
7. Read existing parquet file (if exists)
8. Append/update data
9. Write updated parquet file
10. Release lock
11. Return audience_id
12. Frontend shows success message
```

### Retrieval Operation

```
1. User navigates to Saved Audiences
2. GET /api/audiences?user_id=X
3. AudienceHandler.list_audiences()
4. Scan user's partition directories
5. Read parquet files
6. Filter by status (if requested)
7. Sort by created_at DESC
8. Limit results
9. Parse JSON fields
10. Return audience list
11. Frontend renders list
```

## Performance Optimizations

### 1. Partitioning Strategy
- **By User**: Isolates data access patterns
- **By Date**: Prevents unbounded file growth
- **Monthly Files**: Balances file size vs. file count

### 2. Caching (Future)
```python
# Redis cache layer
cache_key = f"audiences:{user_id}:list"
cached = redis.get(cache_key)
if cached:
    return json.loads(cached)
```

### 3. Query Optimization
- Read only required partitions
- Use Parquet column pruning
- Implement pagination at storage level

## Security Considerations

### 1. User Isolation
```python
def get_audience(self, audience_id: str, user_id: str):
    # Always filter by user_id first
    user_path = self._get_user_path(user_id, 'audiences')
    # Only search within user's directory
```

### 2. Input Validation
- Sanitize user inputs
- Validate JSON structure
- Enforce size limits

### 3. Credential Storage
```python
# Platform credentials are encrypted
credentials = {
    'encrypted': encrypt(api_key),
    'account_id': account_id
}
```

## Scalability Path

### Phase 1: Single Server (Current)
- Local Parquet files
- Thread locks for concurrency
- Suitable for < 10K users

### Phase 2: Distributed Storage
- Move files to GCS
- Use GCS FUSE for compatibility
- Add caching layer

### Phase 3: BigQuery Migration
- ETL Parquet → BigQuery
- Real-time streaming inserts
- SQL analytics capabilities

### Phase 4: Global Scale
- Multi-region replication
- CDN for read caching
- Eventual consistency model

## Monitoring & Maintenance

### Metrics to Track
```python
# Storage metrics
- Total storage size per user
- File count per partition
- Average file size
- Query response times

# Usage metrics
- Audiences created per day
- API call frequency
- Error rates by endpoint
- User retention
```

### Maintenance Tasks
1. **Daily**: Monitor storage growth
2. **Weekly**: Check error logs
3. **Monthly**: Archive old data
4. **Quarterly**: Performance review

## Error Handling

### Graceful Degradation
```python
try:
    audience_id = handler.save_audience(data)
except Exception as e:
    logger.error(f"Save failed: {e}")
    # Return error but don't crash app
    return jsonify({'error': 'Save temporarily unavailable'}), 503
```

### Retry Logic
```python
@retry(max_attempts=3, backoff=exponential)
def save_with_retry(self, data):
    return self.save_audience(data)
```

## Testing Strategy

### Unit Tests
- Test each handler method
- Mock file operations
- Verify thread safety

### Integration Tests
- Full API → Storage flow
- Multi-user scenarios
- Concurrent operations

### Load Tests
- 1000 concurrent saves
- 10K audience listings
- Storage growth simulation

## Migration Guide

### From CSV to Parquet
```python
# One-time migration script
df = pd.read_csv('old_audiences.csv')
handler = AudienceHandler()
for _, row in df.iterrows():
    handler.save_audience(row.to_dict())
```

### From Parquet to BigQuery
```python
# Batch upload
from google.cloud import bigquery
client = bigquery.Client()
table = client.get_table('activation_manager.audiences')
job = client.load_table_from_dataframe(df, table)
```

## Future Enhancements

1. **Real-time Sync**: WebSocket updates for shared audiences
2. **Versioning**: Track audience modifications
3. **Collaboration**: Share audiences between users
4. **Analytics**: Built-in audience insights
5. **Webhooks**: Notify external systems of changes

## Conclusion

The data persistence architecture provides a solid foundation for audience management with clear upgrade paths as the system scales. The current Parquet-based implementation offers excellent performance for single-server deployments while maintaining compatibility with future cloud migrations.