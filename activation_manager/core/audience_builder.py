"""
Audience Builder - Core Implementation
Natural language interface for audience segmentation using Claude
"""

import json
import numpy as np
import pandas as pd
import os
from typing import List, Dict, Any, Tuple, Optional
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
        """
        self.catalog = variable_catalog
        self.selected_variables = []
        
    def analyze_request(self, user_request: str) -> List[Dict[str, Any]]:
        """
        Parse user request and identify relevant variables
        """
        # Keywords mapping to variable types
        keyword_mappings = {
            "demographic": ["age", "gender", "location", "urban", "city", "rural", "postal", "geographic"],
            "behavioral": ["purchase", "buy", "engage", "active", "frequent", "habit", "activity", "usage"],
            "financial": ["income", "disposable", "spending", "affluent", "budget", "wealth", "money", "economic"],
            "psychographic": ["lifestyle", "values", "interests", "conscious", "preference", "attitude", "opinion"]
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
        return variable_scores[:15]  # Return top 15 most relevant
    
    def confirm_selection(self, selected_codes: List[str]) -> Dict[str, Any]:
        """Store confirmed variable selection"""
        self.selected_variables = selected_codes
        return {"status": "confirmed", "variables": self.selected_variables}


class DataRetriever:
    """
    Retrieves data values for selected variables
    """
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path
        self.data = None
        
    def load_data(self, path: str = None) -> pd.DataFrame:
        """Load data from CSV file"""
        if path:
            self.data_path = path
        if not self.data_path:
            raise ValueError("No data path provided. Cannot load data.")
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        self.data = pd.read_csv(self.data_path)
        return self.data
        
    def fetch_data(self, variable_codes: List[str], sample_size: int = None, include_special_columns: bool = True) -> pd.DataFrame:
        """
        Fetch data for selected variables
        """
        if self.data is None:
            if not self.data_path:
                raise AttributeError("No data loaded. Call load_data() first.")
            self.load_data()
            
        # Select columns that exist in the data
        available_columns = []
        for code in variable_codes:
            if code in self.data.columns:
                available_columns.append(code)
        
        # Include special columns only if requested and no specific variables were provided
        if include_special_columns and (not variable_codes or len(available_columns) == 0):
            for col in ['PostalCode', 'PRIZM_SEGMENT', 'LATITUDE', 'LONGITUDE']:
                if col in self.data.columns and col not in available_columns:
                    available_columns.append(col)
        
        # If no columns found, return empty DataFrame
        if not available_columns:
            return pd.DataFrame()
        
        # Sample data if requested
        if sample_size and sample_size < len(self.data):
            sampled_data = self.data[available_columns].sample(n=sample_size, random_state=42)
        else:
            sampled_data = self.data[available_columns]
            
        return sampled_data


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
        
        # Handle empty data
        if n_samples == 0:
            return np.array([])
        
        # Handle single sample
        if n_samples == 1:
            return np.array([0])
        
        min_cluster_size = int(n_samples * self.min_size_pct)
        max_cluster_size = int(n_samples * self.max_size_pct)
        
        # Ensure we have at least minimum viable clusters
        if max_cluster_size == 0:
            max_cluster_size = 1
        if min_cluster_size == 0:
            min_cluster_size = 1
        
        # Determine optimal number of clusters
        min_clusters = max(1, int(np.ceil(n_samples / max_cluster_size)))
        max_clusters = max(1, int(np.floor(n_samples / min_cluster_size)))
        
        # Handle both numeric and categorical data
        # First, get numeric columns
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        categorical_columns = data.select_dtypes(include=['object', 'category']).columns
        
        # Start with numeric data
        data_for_clustering = []
        
        if len(numeric_columns) > 0:
            data_for_clustering.append(data[numeric_columns])
        
        # Convert categorical to numeric using get_dummies
        if len(categorical_columns) > 0:
            categorical_dummies = pd.get_dummies(data[categorical_columns], drop_first=True)
            if len(categorical_dummies.columns) > 0:
                data_for_clustering.append(categorical_dummies)
        
        # Combine all data
        if len(data_for_clustering) == 0:
            # No valid data for clustering - return single cluster
            return np.zeros(n_samples, dtype=int)
        elif len(data_for_clustering) == 1:
            data_numeric = data_for_clustering[0]
        else:
            data_numeric = pd.concat(data_for_clustering, axis=1)
        
        # Handle case where no features exist after processing
        if data_numeric.shape[1] == 0:
            return np.zeros(n_samples, dtype=int)
        
        # Handle missing values
        if data_numeric.isnull().any().any():
            # Simple imputation - fill with median for numeric, mode for categorical
            data_numeric = data_numeric.fillna(data_numeric.median())
            # If still NaN (all NaN column), fill with 0
            data_numeric = data_numeric.fillna(0)
        
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
                
        # Ensure we always return valid labels
        if best_labels is None:
            # Fallback: assign all points to single cluster
            best_labels = np.zeros(n_samples, dtype=int)
            self.cluster_centers_ = np.mean(data_scaled, axis=0).reshape(1, -1)
        
        self.labels_ = best_labels
        return best_labels
    
    def _apply_size_constraints(self, data, labels, n_clusters, min_size, max_size):
        """
        Iteratively reassign points to satisfy size constraints
        """
        labels = labels.copy()
        n_samples = len(data)
        
        for iteration in range(10):  # Maximum iterations
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
                        cluster_sizes[cluster_id] -= 1
                        cluster_sizes[best_cluster] += 1
                        
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
    def __init__(self, variable_catalog: Dict, data_path: str = None):
        self.variable_selector = VariableSelector(variable_catalog)
        self.data_retriever = DataRetriever(data_path)
        self.clusterer = ConstrainedKMedians()
        self.results = None
        self.data_path = data_path
        
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
        group_stats = result.groupby('Group').size()
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
                if col not in ['Group', 'PostalCode', 'LATITUDE', 'LONGITUDE']:
                    if group_data[col].dtype == 'object':
                        # Categorical variable - get mode
                        mode_value = group_data[col].mode()[0]
                        mode_pct = (group_data[col] == mode_value).sum() / len(group_data) * 100
                        profile["characteristics"][col] = {
                            "dominant_value": mode_value,
                            "percentage": round(mode_pct, 1)
                        }
                    else:
                        # Numeric variable - get statistics
                        profile["characteristics"][col] = {
                            "median": round(group_data[col].median(), 2),
                            "mean": round(group_data[col].mean(), 2),
                            "std": round(group_data[col].std(), 2)
                        }
                        
            profiles[group_id] = profile
            
        return profiles