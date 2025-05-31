"""
Fixed Parquet file handlers for persisting user audiences, platforms, and distributions.
Handles missing fields and timestamp conversions properly.
"""

import os
import json
import uuid
import threading
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
        self._write_lock = threading.Lock()
    
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
    
    def _ensure_datetime(self, value):
        """Ensure value is a datetime object."""
        if isinstance(value, str):
            return pd.to_datetime(value)
        elif isinstance(value, datetime):
            return value
        else:
            return datetime.utcnow()


class AudienceHandler(ParquetDataHandler):
    """Handler for audience data persistence."""
    
    def __init__(self, base_path: str = "data/persistence"):
        super().__init__(base_path)
    
    def save_audience(self, audience_data: Dict[str, Any]) -> str:
        """Save an audience to Parquet file."""
        # Generate ID if not provided
        audience_id = audience_data.get('audience_id', f'aud_{uuid.uuid4().hex[:8]}')
        
        # Add timestamps
        now = datetime.utcnow()
        
        # Create complete record with defaults
        record = {
            'audience_id': audience_id,
            'user_id': audience_data['user_id'],
            'name': audience_data.get('name', 'Untitled Audience'),
            'description': audience_data.get('description', ''),
            'created_at': self._ensure_datetime(audience_data.get('created_at', now)),
            'updated_at': now,
            'status': audience_data.get('status', 'active'),
            'data_type': audience_data.get('data_type', 'first_party'),
            'original_query': audience_data.get('original_query', ''),
            'selected_variables': json.dumps(audience_data.get('selected_variables', [])),
            'variable_details': json.dumps(audience_data.get('variable_details', [])),
            'segments': json.dumps(audience_data.get('segments', [])),
            'total_audience_size': audience_data.get('total_audience_size', 0),
            'metadata': json.dumps(audience_data.get('metadata', {}))
        }
        
        # Get file path
        file_path = self._get_partitioned_path(
            record['user_id'], 
            'audiences', 
            record['created_at']
        )
        file_name = file_path / f"audiences_{now.strftime('%Y%m')}.parquet"
        
        # Use lock for thread-safe writes
        with self._write_lock:
            # Read existing data if file exists
            if file_name.exists():
                existing_df = pd.read_parquet(file_name)
                # Update if audience exists
                mask = existing_df['audience_id'] == audience_id
                if mask.any():
                    for key, value in record.items():
                        existing_df.loc[mask, key] = value
                    df = existing_df
                else:
                    # Append new audience
                    new_df = pd.DataFrame([record])
                    df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                df = pd.DataFrame([record])
            
            # Write to Parquet without strict schema
            df.to_parquet(file_name, index=False)
        
        return audience_id
    
    def get_audience(self, audience_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific audience by ID."""
        user_path = self._get_user_path(user_id, 'audiences')
        
        # Search through all partitions
        for parquet_file in user_path.rglob('*.parquet'):
            try:
                df = pd.read_parquet(parquet_file)
                mask = df['audience_id'] == audience_id
                if mask.any():
                    audience = df[mask].iloc[0].to_dict()
                    # Parse JSON fields
                    for field in ['selected_variables', 'variable_details', 'segments', 'metadata']:
                        if field in audience and isinstance(audience[field], str):
                            try:
                                audience[field] = json.loads(audience[field])
                            except:
                                audience[field] = []
                    # Convert timestamps to ISO format
                    for field in ['created_at', 'updated_at']:
                        if field in audience and pd.notna(audience[field]):
                            audience[field] = pd.to_datetime(audience[field]).isoformat()
                    return audience
            except Exception as e:
                continue
        
        return None
    
    def list_audiences(self, user_id: str, status: Optional[str] = None, 
                      limit: int = 50) -> List[Dict[str, Any]]:
        """List audiences for a user."""
        user_path = self._get_user_path(user_id, 'audiences')
        all_audiences = []
        
        # Read all parquet files for the user
        for parquet_file in sorted(user_path.rglob('*.parquet'), reverse=True):
            try:
                df = pd.read_parquet(parquet_file)
                
                # Filter by status if provided
                if status:
                    df = df[df['status'] == status]
                
                # Convert to list of dicts
                audiences = df.to_dict('records')
                for audience in audiences:
                    # Parse JSON fields
                    for field in ['selected_variables', 'variable_details', 'segments', 'metadata']:
                        if field in audience and isinstance(audience[field], str):
                            try:
                                audience[field] = json.loads(audience[field])
                            except:
                                audience[field] = []
                    # Convert timestamps to ISO format
                    for field in ['created_at', 'updated_at']:
                        if field in audience and pd.notna(audience[field]):
                            audience[field] = pd.to_datetime(audience[field]).isoformat()
                
                all_audiences.extend(audiences)
                
                # Stop if we have enough
                if len(all_audiences) >= limit:
                    break
            except Exception as e:
                continue
        
        # Sort by created_at descending
        all_audiences.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return all_audiences[:limit]
    
    def update_audience_status(self, audience_id: str, user_id: str, 
                             new_status: str) -> bool:
        """Update the status of an audience."""
        audience = self.get_audience(audience_id, user_id)
        if audience:
            audience['status'] = new_status
            audience['updated_at'] = datetime.utcnow()
            self.save_audience(audience)
            return True
        return False


class PlatformHandler(ParquetDataHandler):
    """Handler for platform configuration persistence."""
    
    def __init__(self, base_path: str = "data/persistence"):
        super().__init__(base_path)
    
    def save_platform(self, platform_data: Dict[str, Any]) -> str:
        """Save a platform configuration."""
        # Generate ID if not provided
        platform_id = platform_data.get('platform_id', f'plat_{uuid.uuid4().hex[:8]}')
        
        # Add timestamps
        now = datetime.utcnow()
        
        # Create complete record
        record = {
            'platform_id': platform_id,
            'user_id': platform_data['user_id'],
            'platform_type': platform_data['platform_type'],
            'name': platform_data['name'],
            'created_at': self._ensure_datetime(platform_data.get('created_at', now)),
            'updated_at': now,
            'status': platform_data.get('status', 'connected'),
            'credentials': json.dumps(platform_data.get('credentials', {})),
            'settings': json.dumps(platform_data.get('settings', {})),
            'last_sync': self._ensure_datetime(platform_data.get('last_sync', now))
        }
        
        # Get file path (not partitioned for platforms)
        file_path = self._get_user_path(record['user_id'], 'platforms')
        file_name = file_path / 'platforms.parquet'
        
        # Use lock for thread-safe writes
        with self._write_lock:
            # Read existing data if file exists
            if file_name.exists():
                existing_df = pd.read_parquet(file_name)
                # Update if platform exists
                mask = existing_df['platform_id'] == platform_id
                if mask.any():
                    for key, value in record.items():
                        existing_df.loc[mask, key] = value
                    df = existing_df
                else:
                    # Append new platform
                    new_df = pd.DataFrame([record])
                    df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                df = pd.DataFrame([record])
            
            # Write to Parquet
            df.to_parquet(file_name, index=False)
        
        return platform_id
    
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
                # Convert timestamps
                for field in ['created_at', 'updated_at', 'last_sync']:
                    if field in platform and pd.notna(platform[field]):
                        platform[field] = pd.to_datetime(platform[field]).isoformat()
                return platform
        
        return None
    
    def list_platforms(self, user_id: str) -> List[Dict[str, Any]]:
        """List all platforms for a user."""
        file_path = self._get_user_path(user_id, 'platforms') / 'platforms.parquet'
        
        if file_path.exists():
            df = pd.read_parquet(file_path)
            platforms = df.to_dict('records')
            
            for platform in platforms:
                # Parse JSON fields
                for field in ['credentials', 'settings']:
                    if field in platform and isinstance(platform[field], str):
                        platform[field] = json.loads(platform[field])
                # Convert timestamps
                for field in ['created_at', 'updated_at', 'last_sync']:
                    if field in platform and pd.notna(platform[field]):
                        platform[field] = pd.to_datetime(platform[field]).isoformat()
            
            return platforms
        
        return []
    
    def update_platform_status(self, platform_id: str, user_id: str, 
                             new_status: str) -> bool:
        """Update the status of a platform."""
        platform = self.get_platform(platform_id, user_id)
        if platform:
            platform['status'] = new_status
            platform['updated_at'] = datetime.utcnow()
            self.save_platform(platform)
            return True
        return False


class DistributionHandler(ParquetDataHandler):
    """Handler for distribution history persistence."""
    
    def __init__(self, base_path: str = "data/persistence"):
        super().__init__(base_path)
    
    def save_distribution(self, distribution_data: Dict[str, Any]) -> str:
        """Save a distribution record."""
        # Generate ID if not provided
        distribution_id = distribution_data.get('distribution_id', f'dist_{uuid.uuid4().hex[:8]}')
        
        # Add timestamps
        now = datetime.utcnow()
        
        # Create complete record
        record = {
            'distribution_id': distribution_id,
            'user_id': distribution_data['user_id'],
            'audience_id': distribution_data['audience_id'],
            'platform_id': distribution_data['platform_id'],
            'audience_name': distribution_data.get('audience_name', ''),
            'platform_name': distribution_data.get('platform_name', ''),
            'platform_type': distribution_data.get('platform_type', ''),
            'created_at': self._ensure_datetime(distribution_data.get('created_at', now)),
            'scheduled_at': self._ensure_datetime(distribution_data.get('scheduled_at', now)),
            'completed_at': self._ensure_datetime(distribution_data.get('completed_at')) if distribution_data.get('completed_at') else None,
            'status': distribution_data.get('status', 'pending'),
            'segments_distributed': json.dumps(distribution_data.get('segments_distributed', [])),
            'total_records': distribution_data.get('total_records', 0),
            'matched_records': distribution_data.get('matched_records', 0),
            'match_rate': distribution_data.get('match_rate', 0.0),
            'error_message': distribution_data.get('error_message', ''),
            'metadata': json.dumps(distribution_data.get('metadata', {}))
        }
        
        # Get file path
        file_path = self._get_partitioned_path(
            record['user_id'], 
            'distributions', 
            record['created_at']
        )
        file_name = file_path / f"distributions_{now.strftime('%Y%m')}.parquet"
        
        # Use lock for thread-safe writes
        with self._write_lock:
            # Read existing data if file exists
            if file_name.exists():
                existing_df = pd.read_parquet(file_name)
                # Update if distribution exists
                mask = existing_df['distribution_id'] == distribution_id
                if mask.any():
                    for key, value in record.items():
                        existing_df.loc[mask, key] = value
                    df = existing_df
                else:
                    # Append new distribution
                    new_df = pd.DataFrame([record])
                    df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                df = pd.DataFrame([record])
            
            # Write to Parquet
            df.to_parquet(file_name, index=False)
        
        return distribution_id
    
    def get_distribution(self, distribution_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific distribution by ID."""
        user_path = self._get_user_path(user_id, 'distributions')
        
        # Search through all partitions
        for parquet_file in user_path.rglob('*.parquet'):
            try:
                df = pd.read_parquet(parquet_file)
                mask = df['distribution_id'] == distribution_id
                if mask.any():
                    distribution = df[mask].iloc[0].to_dict()
                    # Parse JSON fields
                    for field in ['segments_distributed', 'metadata']:
                        if field in distribution and isinstance(distribution[field], str):
                            distribution[field] = json.loads(distribution[field])
                    # Convert timestamps
                    for field in ['created_at', 'scheduled_at', 'completed_at']:
                        if field in distribution and pd.notna(distribution[field]):
                            distribution[field] = pd.to_datetime(distribution[field]).isoformat()
                    return distribution
            except:
                continue
        
        return None
    
    def list_distributions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List distributions for a user."""
        user_path = self._get_user_path(user_id, 'distributions')
        all_distributions = []
        
        # Read all parquet files for the user
        for parquet_file in sorted(user_path.rglob('*.parquet'), reverse=True):
            try:
                df = pd.read_parquet(parquet_file)
                
                # Convert to list of dicts
                distributions = df.to_dict('records')
                for distribution in distributions:
                    # Parse JSON fields
                    for field in ['segments_distributed', 'metadata']:
                        if field in distribution and isinstance(distribution[field], str):
                            distribution[field] = json.loads(distribution[field])
                    # Convert timestamps
                    for field in ['created_at', 'scheduled_at', 'completed_at']:
                        if field in distribution and pd.notna(distribution[field]):
                            distribution[field] = pd.to_datetime(distribution[field]).isoformat()
                
                all_distributions.extend(distributions)
                
                # Stop if we have enough
                if len(all_distributions) >= limit:
                    break
            except:
                continue
        
        # Sort by created_at descending
        all_distributions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return all_distributions[:limit]
    
    def update_distribution_status(self, distribution_id: str, user_id: str, 
                                 new_status: str, metadata: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Update the status of a distribution."""
        distribution = self.get_distribution(distribution_id, user_id)
        if distribution:
            distribution['status'] = new_status
            
            # Update metadata if provided
            if metadata:
                current_metadata = distribution.get('metadata', {})
                if isinstance(current_metadata, str):
                    current_metadata = json.loads(current_metadata)
                current_metadata.update(metadata)
                distribution['metadata'] = current_metadata
                
                # Update specific fields from metadata
                if 'match_rate' in metadata:
                    distribution['match_rate'] = metadata['match_rate']
                if 'matched_records' in metadata:
                    distribution['matched_records'] = metadata['matched_records']
                if 'completed_at' in metadata:
                    distribution['completed_at'] = metadata['completed_at']
            
            # Mark as completed if status is completed
            if new_status == 'completed' and not distribution.get('completed_at'):
                distribution['completed_at'] = datetime.utcnow()
            
            self.save_distribution(distribution)
            return distribution
        return None