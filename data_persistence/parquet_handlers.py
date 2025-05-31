"""
Parquet file handlers for persisting user audiences, platforms, and distributions.
Provides a file-based alternative to BigQuery for simpler deployments.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path


class ParquetDataHandler:
    """Base handler for Parquet file operations."""
    
    def __init__(self, base_path: str = "data/persistence"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_user_path(self, user_id: str, entity_type: str) -> Path:
        """Get the path for a user's data directory."""
        path = self.base_path / entity_type / f"user_id={user_id}"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def _get_partitioned_path(self, user_id: str, entity_type: str, date: datetime) -> Path:
        """Get partitioned path by year and month."""
        path = self._get_user_path(user_id, entity_type)
        year_month_path = path / f"year={date.year}" / f"month={date.month:02d}"
        year_month_path.mkdir(parents=True, exist_ok=True)
        return year_month_path


class AudienceHandler(ParquetDataHandler):
    """Handler for audience data persistence."""
    
    def __init__(self, base_path: str = "data/persistence"):
        super().__init__(base_path)
        self.schema = pa.schema([
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
    
    def save_audience(self, audience_data: Dict[str, Any]) -> str:
        """Save an audience to Parquet file."""
        # Generate ID if not provided
        if 'audience_id' not in audience_data:
            audience_data['audience_id'] = str(uuid.uuid4())
        
        # Add timestamps
        now = datetime.utcnow()
        audience_data['created_at'] = audience_data.get('created_at', now)
        audience_data['updated_at'] = now
        
        # Convert complex fields to JSON strings
        for field in ['variable_details', 'segments', 'metadata']:
            if field in audience_data and not isinstance(audience_data[field], str):
                audience_data[field] = json.dumps(audience_data[field])
        
        # Get file path
        file_path = self._get_partitioned_path(
            audience_data['user_id'], 
            'audiences', 
            audience_data['created_at']
        )
        file_name = file_path / f"audiences_{now.strftime('%Y%m')}.parquet"
        
        # Read existing data if file exists
        if file_name.exists():
            existing_df = pd.read_parquet(file_name)
            # Update if audience exists
            mask = existing_df['audience_id'] == audience_data['audience_id']
            if mask.any():
                for key, value in audience_data.items():
                    existing_df.loc[mask, key] = value
                df = existing_df
            else:
                # Append new audience
                new_df = pd.DataFrame([audience_data])
                df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            df = pd.DataFrame([audience_data])
        
        # Write to Parquet
        table = pa.Table.from_pandas(df, schema=self.schema)
        pq.write_table(table, file_name)
        
        return audience_data['audience_id']
    
    def get_audience(self, audience_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific audience by ID."""
        user_path = self._get_user_path(user_id, 'audiences')
        
        # Search through all partitions
        for parquet_file in user_path.rglob('*.parquet'):
            df = pd.read_parquet(parquet_file)
            mask = df['audience_id'] == audience_id
            if mask.any():
                audience = df[mask].iloc[0].to_dict()
                # Parse JSON fields
                for field in ['variable_details', 'segments', 'metadata']:
                    if field in audience and isinstance(audience[field], str):
                        audience[field] = json.loads(audience[field])
                return audience
        
        return None
    
    def list_audiences(self, user_id: str, status: Optional[str] = None, 
                      limit: int = 50) -> List[Dict[str, Any]]:
        """List audiences for a user."""
        user_path = self._get_user_path(user_id, 'audiences')
        all_audiences = []
        
        # Read all parquet files for the user
        for parquet_file in sorted(user_path.rglob('*.parquet'), reverse=True):
            df = pd.read_parquet(parquet_file)
            
            # Filter by status if provided
            if status:
                df = df[df['status'] == status]
            
            # Convert to list of dicts
            audiences = df.to_dict('records')
            for audience in audiences:
                # Parse JSON fields
                for field in ['variable_details', 'segments', 'metadata']:
                    if field in audience and isinstance(audience[field], str):
                        audience[field] = json.loads(audience[field])
            
            all_audiences.extend(audiences)
            
            # Stop if we have enough
            if len(all_audiences) >= limit:
                break
        
        # Sort by created_at and limit
        all_audiences.sort(key=lambda x: x['created_at'], reverse=True)
        return all_audiences[:limit]
    
    def update_audience_status(self, audience_id: str, user_id: str, status: str) -> bool:
        """Update the status of an audience."""
        audience = self.get_audience(audience_id, user_id)
        if audience:
            audience['status'] = status
            audience['updated_at'] = datetime.utcnow()
            self.save_audience(audience)
            return True
        return False


class PlatformHandler(ParquetDataHandler):
    """Handler for platform configuration persistence."""
    
    def __init__(self, base_path: str = "data/persistence"):
        super().__init__(base_path)
        self.schema = pa.schema([
            pa.field('platform_id', pa.string()),
            pa.field('user_id', pa.string()),
            pa.field('platform_type', pa.string()),
            pa.field('name', pa.string()),
            pa.field('created_at', pa.timestamp('ms')),
            pa.field('updated_at', pa.timestamp('ms')),
            pa.field('status', pa.string()),
            pa.field('credentials', pa.string()),  # Encrypted JSON
            pa.field('settings', pa.string()),  # JSON string
            pa.field('last_sync', pa.timestamp('ms', tz='UTC')),
            pa.field('sync_status', pa.string())
        ])
    
    def save_platform(self, platform_data: Dict[str, Any]) -> str:
        """Save a platform configuration."""
        # Generate ID if not provided
        if 'platform_id' not in platform_data:
            platform_data['platform_id'] = str(uuid.uuid4())
        
        # Add timestamps
        now = datetime.utcnow()
        platform_data['created_at'] = platform_data.get('created_at', now)
        platform_data['updated_at'] = now
        
        # Convert complex fields to JSON strings
        for field in ['credentials', 'settings']:
            if field in platform_data and not isinstance(platform_data[field], str):
                platform_data[field] = json.dumps(platform_data[field])
        
        # Platforms are not partitioned by date
        file_path = self._get_user_path(platform_data['user_id'], 'platforms')
        file_name = file_path / 'platforms.parquet'
        
        # Read existing data if file exists
        if file_name.exists():
            existing_df = pd.read_parquet(file_name)
            # Update if platform exists
            mask = existing_df['platform_id'] == platform_data['platform_id']
            if mask.any():
                for key, value in platform_data.items():
                    existing_df.loc[mask, key] = value
                df = existing_df
            else:
                # Append new platform
                new_df = pd.DataFrame([platform_data])
                df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            df = pd.DataFrame([platform_data])
        
        # Write to Parquet
        table = pa.Table.from_pandas(df, schema=self.schema)
        pq.write_table(table, file_name)
        
        return platform_data['platform_id']
    
    def get_platform(self, platform_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific platform by ID."""
        file_path = self._get_user_path(user_id, 'platforms') / 'platforms.parquet'
        
        if file_path.exists():
            df = pd.read_parquet(file_path)
            mask = df['platform_id'] == platform_id
            if mask.any():
                platform = df[mask].iloc[0].to_dict()
                # Parse JSON fields
                for field in ['credentials', 'settings']:
                    if field in platform and isinstance(platform[field], str):
                        platform[field] = json.loads(platform[field])
                return platform
        
        return None
    
    def list_platforms(self, user_id: str, platform_type: Optional[str] = None,
                      status: str = 'active') -> List[Dict[str, Any]]:
        """List platforms for a user."""
        file_path = self._get_user_path(user_id, 'platforms') / 'platforms.parquet'
        
        if not file_path.exists():
            return []
        
        df = pd.read_parquet(file_path)
        
        # Filter by status
        df = df[df['status'] == status]
        
        # Filter by platform type if provided
        if platform_type:
            df = df[df['platform_type'] == platform_type]
        
        # Convert to list of dicts
        platforms = df.to_dict('records')
        for platform in platforms:
            # Parse JSON fields
            for field in ['credentials', 'settings']:
                if field in platform and isinstance(platform[field], str):
                    platform[field] = json.loads(platform[field])
        
        return platforms


class DistributionHandler(ParquetDataHandler):
    """Handler for distribution tracking persistence."""
    
    def __init__(self, base_path: str = "data/persistence"):
        super().__init__(base_path)
        self.schema = pa.schema([
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
    
    def save_distribution(self, distribution_data: Dict[str, Any]) -> str:
        """Save a distribution record."""
        # Generate ID if not provided
        if 'distribution_id' not in distribution_data:
            distribution_data['distribution_id'] = str(uuid.uuid4())
        
        # Add timestamp
        now = datetime.utcnow()
        distribution_data['created_at'] = distribution_data.get('created_at', now)
        
        # Convert complex fields to JSON strings
        for field in ['match_results', 'error_details', 'metadata']:
            if field in distribution_data and not isinstance(distribution_data[field], str):
                distribution_data[field] = json.dumps(distribution_data[field])
        
        # Get file path
        file_path = self._get_partitioned_path(
            distribution_data['user_id'], 
            'distributions', 
            distribution_data['created_at']
        )
        file_name = file_path / f"distributions_{now.strftime('%Y%m')}.parquet"
        
        # Read existing data if file exists
        if file_name.exists():
            existing_df = pd.read_parquet(file_name)
            # Update if distribution exists
            mask = existing_df['distribution_id'] == distribution_data['distribution_id']
            if mask.any():
                for key, value in distribution_data.items():
                    existing_df.loc[mask, key] = value
                df = existing_df
            else:
                # Append new distribution
                new_df = pd.DataFrame([distribution_data])
                df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            df = pd.DataFrame([distribution_data])
        
        # Write to Parquet
        table = pa.Table.from_pandas(df, schema=self.schema)
        pq.write_table(table, file_name)
        
        return distribution_data['distribution_id']
    
    def get_distribution(self, distribution_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific distribution by ID."""
        user_path = self._get_user_path(user_id, 'distributions')
        
        # Search through all partitions
        for parquet_file in user_path.rglob('*.parquet'):
            df = pd.read_parquet(parquet_file)
            mask = df['distribution_id'] == distribution_id
            if mask.any():
                distribution = df[mask].iloc[0].to_dict()
                # Parse JSON fields
                for field in ['match_results', 'error_details', 'metadata']:
                    if field in distribution and isinstance(distribution[field], str):
                        distribution[field] = json.loads(distribution[field])
                return distribution
        
        return None
    
    def list_distributions_for_audience(self, audience_id: str, user_id: str, 
                                      limit: int = 10) -> List[Dict[str, Any]]:
        """List distributions for a specific audience."""
        user_path = self._get_user_path(user_id, 'distributions')
        all_distributions = []
        
        # Read all parquet files for the user
        for parquet_file in sorted(user_path.rglob('*.parquet'), reverse=True):
            df = pd.read_parquet(parquet_file)
            
            # Filter by audience_id
            df = df[df['audience_id'] == audience_id]
            
            # Convert to list of dicts
            distributions = df.to_dict('records')
            for dist in distributions:
                # Parse JSON fields
                for field in ['match_results', 'error_details', 'metadata']:
                    if field in dist and isinstance(dist[field], str):
                        dist[field] = json.loads(dist[field])
            
            all_distributions.extend(distributions)
            
            # Stop if we have enough
            if len(all_distributions) >= limit:
                break
        
        # Sort by created_at and limit
        all_distributions.sort(key=lambda x: x['created_at'], reverse=True)
        return all_distributions[:limit]
    
    def update_distribution_status(self, distribution_id: str, user_id: str, 
                                 status: str, match_results: Optional[Dict] = None,
                                 error_details: Optional[Dict] = None) -> bool:
        """Update the status of a distribution."""
        distribution = self.get_distribution(distribution_id, user_id)
        if distribution:
            distribution['status'] = status
            distribution['executed_at'] = datetime.utcnow()
            
            if match_results:
                distribution['match_results'] = match_results
            if error_details:
                distribution['error_details'] = error_details
            
            self.save_distribution(distribution)
            return True
        return False


# Example usage
if __name__ == "__main__":
    # Initialize handlers
    audience_handler = AudienceHandler()
    platform_handler = PlatformHandler()
    distribution_handler = DistributionHandler()
    
    # Example: Save an audience
    audience = {
        'user_id': 'user123',
        'name': 'High Income Millennials',
        'description': 'Millennials with household income over $100k',
        'status': 'active',
        'data_type': 'first_party',
        'original_query': 'millennials with high income',
        'selected_variables': ['AGE_25_34', 'INCOME_100K_PLUS', 'URBAN_METRO'],
        'variable_details': [
            {'code': 'AGE_25_34', 'description': 'Age 25-34', 'relevance_score': 0.95},
            {'code': 'INCOME_100K_PLUS', 'description': 'Income $100k+', 'relevance_score': 0.92}
        ],
        'segments': [
            {'segment_id': 'seg1', 'name': 'Urban Professionals', 'size': 125000, 'size_percentage': 8.5}
        ],
        'total_audience_size': 1470000,
        'metadata': {'campaign_id': 'camp123', 'tags': ['automotive', 'luxury']}
    }
    
    audience_id = audience_handler.save_audience(audience)
    print(f"Saved audience: {audience_id}")
    
    # Retrieve the audience
    retrieved = audience_handler.get_audience(audience_id, 'user123')
    print(f"Retrieved audience: {retrieved['name']}")
    
    # List audiences
    audiences = audience_handler.list_audiences('user123')
    print(f"Found {len(audiences)} audiences")