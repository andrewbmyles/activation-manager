# GCP-specific configuration
import os
from google.cloud import storage, secretmanager
import json

class GCPConfig:
    """Configuration handler for GCP deployment"""
    
    def __init__(self):
        self.project_id = os.environ.get('PROJECT_ID', '')
        self.dataset_bucket = os.environ.get('DATASET_BUCKET', '')
        self._secrets_client = None
        self._storage_client = None
    
    @property
    def secrets_client(self):
        """Lazy load secrets client"""
        if not self._secrets_client:
            self._secrets_client = secretmanager.SecretManagerServiceClient()
        return self._secrets_client
    
    @property
    def storage_client(self):
        """Lazy load storage client"""
        if not self._storage_client:
            self._storage_client = storage.Client()
        return self._storage_client
    
    def get_secret(self, secret_id: str) -> str:
        """Retrieve secret from Secret Manager"""
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
            response = self.secrets_client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"Error accessing secret {secret_id}: {e}")
            return os.environ.get(secret_id.upper().replace('-', '_'), '')
    
    def download_dataset(self, filename: str, local_path: str = '/tmp/dataset.csv'):
        """Download dataset from GCS"""
        try:
            bucket = self.storage_client.bucket(self.dataset_bucket)
            blob = bucket.blob(filename)
            blob.download_to_filename(local_path)
            return local_path
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            return None
    
    def get_database_url(self):
        """Get database URL from secret or environment"""
        return self.get_secret('database-url') or os.environ.get('DATABASE_URL', '')
    
    def get_redis_url(self):
        """Get Redis URL"""
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        return f"redis://{redis_host}:6379"

# Initialize config
gcp_config = GCPConfig()