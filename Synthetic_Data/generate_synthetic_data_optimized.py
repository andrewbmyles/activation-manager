#!/usr/bin/env python3
"""
Optimized Canadian Consumer Behavior Synthetic Data Generator
Faster generation using vectorized operations
"""

import pandas as pd
import numpy as np
import random
import string
from typing import Dict, List, Tuple
import logging
from datetime import datetime
import os
import json
import sys
import argparse

# Import configuration and metadata loader
from config import PRIZM_SEGMENTS, VARIABLE_CATEGORIES, POSTAL_CODE_DISTRIBUTION, INDEX_PARAMS
from metadata_loader import MetadataLoader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedSyntheticDataGenerator:
    def __init__(self, num_records: int = 100000, metadata_dir: str = "Variable Metadata"):
        self.num_records = num_records
        self.metadata_dir = metadata_dir
        
        # Load metadata
        logger.info("Loading metadata files...")
        self.metadata_loader = MetadataLoader(metadata_dir)
        self.variables = self.metadata_loader.load_all_metadata()
        self.all_variables = self.metadata_loader.get_all_variable_names()
        
        logger.info(f"Loaded {len(self.all_variables)} variables from metadata files")
        
        # Use configuration
        self.prizm_segments = PRIZM_SEGMENTS
        self.postal_code_distribution = POSTAL_CODE_DISTRIBUTION
        self.index_params = INDEX_PARAMS
        
        # Normalize PRIZM percentages
        self._normalize_prizm_percentages()
        
        # Pre-compute distributions for efficiency
        self._prepare_distributions()
        
    def _normalize_prizm_percentages(self):
        """Ensure PRIZM segment percentages sum to 100%."""
        total_pct = sum(seg["percentage"] for seg in self.prizm_segments.values())
        if abs(total_pct - 100) > 0.1:
            logger.info(f"Normalizing PRIZM percentages from {total_pct:.2f}% to 100%")
            for seg in self.prizm_segments.values():
                seg["percentage"] = seg["percentage"] / total_pct * 100
    
    def _prepare_distributions(self):
        """Pre-compute distribution parameters for faster generation."""
        # Postal code prefix weights
        self.postal_prefixes = list(self.postal_code_distribution.keys())
        self.postal_weights = np.array([self.postal_code_distribution[p]["weight"] for p in self.postal_prefixes])
        self.postal_weights = self.postal_weights / self.postal_weights.sum()
        
        # PRIZM segment weights
        self.prizm_codes = list(self.prizm_segments.keys())
        self.prizm_weights = np.array([self.prizm_segments[s]["percentage"] for s in self.prizm_codes])
        self.prizm_weights = self.prizm_weights / self.prizm_weights.sum()
        
        # Valid postal code letters
        self.valid_letters = list('ABCEGHJKLMNPRSTVWXYZ')
    
    def generate_postal_codes_batch(self, n: int) -> List[str]:
        """Generate n postal codes efficiently."""
        # Select prefixes
        prefixes = np.random.choice(self.postal_prefixes, size=n, p=self.postal_weights)
        
        # Generate random components
        digits1 = np.random.randint(0, 10, size=n)
        letters1 = np.random.choice(self.valid_letters, size=n)
        digits2 = np.random.randint(0, 10, size=n)
        letters2 = np.random.choice(self.valid_letters, size=n)
        digits3 = np.random.randint(0, 10, size=n)
        
        # Combine into postal codes
        postal_codes = [f"{p}{d1}{l1} {d2}{l2}{d3}" 
                       for p, d1, l1, d2, l2, d3 
                       in zip(prefixes, digits1, letters1, digits2, letters2, digits3)]
        
        return postal_codes
    
    def generate_coordinates_batch(self, postal_codes: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """Generate coordinates for a batch of postal codes."""
        lats = np.zeros(len(postal_codes))
        lons = np.zeros(len(postal_codes))
        
        for i, pc in enumerate(postal_codes):
            prefix = pc[0]
            if prefix in self.postal_code_distribution:
                base_lat = self.postal_code_distribution[prefix]["lat"]
                base_lon = self.postal_code_distribution[prefix]["lon"]
                urban_type = self.postal_code_distribution[prefix]["type"]
                
                # Add variation based on type
                if urban_type == "urban":
                    lat_var, lon_var = np.random.normal(0, 0.1, 2)
                elif urban_type == "suburban":
                    lat_var, lon_var = np.random.normal(0, 0.2, 2)
                else:
                    lat_var, lon_var = np.random.normal(0, 0.5, 2)
                
                lats[i] = base_lat + lat_var
                lons[i] = base_lon + lon_var
            else:
                lats[i] = np.random.uniform(42.0, 60.0)
                lons[i] = np.random.uniform(-140.0, -52.0)
        
        return np.round(lats, 6), np.round(lons, 6)
    
    def generate_indices_vectorized(self, segments: np.ndarray, variable_name: str, n: int) -> np.ndarray:
        """Generate indices for a variable using vectorized operations."""
        # Base values using log-normal
        base_values = np.random.lognormal(
            mean=self.index_params["lognormal_mean"],
            sigma=self.index_params["lognormal_sigma"],
            size=n
        )
        
        # Apply segment modifiers
        modifiers = np.ones(n)
        
        # Determine variable category
        var_category = self.get_variable_category(variable_name)
        if var_category and var_category in VARIABLE_CATEGORIES:
            modifier_key = VARIABLE_CATEGORIES[var_category]["modifier_key"]
            
            # Apply modifiers based on segments
            for i, seg in enumerate(segments):
                if seg in self.prizm_segments:
                    profile = self.prizm_segments[seg]["profile"]
                    modifiers[i] = profile["modifiers"].get(modifier_key, 1.0)
        
        # Apply modifiers and noise
        adjusted_values = base_values * modifiers
        noise = np.random.normal(0, 5, n)
        final_values = adjusted_values + noise
        
        # Clip to valid range
        return np.clip(final_values, self.index_params["min_value"], 
                      self.index_params["max_value"]).astype(int)
    
    def get_variable_category(self, variable_name: str) -> str:
        """Determine variable category."""
        var_lower = variable_name.lower()
        for category, config in VARIABLE_CATEGORIES.items():
            for pattern in config["patterns"]:
                if pattern.lower() in var_lower:
                    return category
        return None
    
    def generate_dataset(self) -> pd.DataFrame:
        """Generate the complete dataset using optimized methods."""
        logger.info(f"Starting optimized generation of {self.num_records:,} records...")
        
        # Generate core data in batches
        logger.info("Generating postal codes and geographic data...")
        postal_codes = self.generate_postal_codes_batch(self.num_records)
        lats, lons = self.generate_coordinates_batch(postal_codes)
        segments = np.random.choice(self.prizm_codes, size=self.num_records, p=self.prizm_weights)
        
        # Initialize DataFrame with core columns
        data = {
            'PostalCode': postal_codes,
            'LATITUDE': lats,
            'LONGITUDE': lons,
            'PRIZM_SEGMENT': segments
        }
        
        # Generate base population variables
        logger.info("Generating base population variables...")
        for var in self.all_variables:
            if var.upper() in ['CODE', 'GEO', 'FSALDU', 'LATITUDE', 'LONGITUDE']:
                continue
            
            if var.endswith('HP') or 'POPULATION' in var.upper() or var in ['NBAS12HP', 'SVBAS15HP']:
                # Base population with segment variation
                base_pop = np.random.normal(1200, 200, self.num_records)
                data[var] = np.clip(base_pop, 500, 2500).astype(int)
        
        # Create initial DataFrame
        df = pd.DataFrame(data)
        
        # Generate behavioral indices in batches
        logger.info("Generating behavioral indices...")
        batch_size = 100  # Process 100 variables at a time
        index_vars = [v for v in self.all_variables 
                     if v not in data and v.upper() not in ['CODE', 'GEO', 'FSALDU']]
        
        for i in range(0, len(index_vars), batch_size):
            batch_vars = index_vars[i:i+batch_size]
            if i % 500 == 0:
                logger.info(f"Processing variables {i} to {i+len(batch_vars)}...")
            
            for var in batch_vars:
                df[var] = self.generate_indices_vectorized(segments, var, self.num_records)
        
        # Apply spatial correlation
        logger.info("Applying spatial correlation...")
        df = self.add_spatial_correlation_optimized(df)
        
        # Add NBAS12HP percentage column
        if 'NBAS12HP' in df.columns:
            total_nbas12hp = df['NBAS12HP'].sum()
            df['NBAS12HP_PCT'] = (df['NBAS12HP'] / total_nbas12hp * 100).round(6)
            logger.info(f"Added NBAS12HP_PCT column (total NBAS12HP: {total_nbas12hp:,})")
        
        logger.info(f"Data generation complete! Generated {len(df):,} rows with {len(df.columns)} columns")
        return df
    
    def add_spatial_correlation_optimized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply spatial correlation using vectorized operations."""
        # Create FSA column
        df['FSA'] = df['PostalCode'].str[:3]
        
        # Get numeric columns (exclude identifiers)
        exclude_cols = ['PostalCode', 'LATITUDE', 'LONGITUDE', 'PRIZM_SEGMENT', 'FSA']
        numeric_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Apply correlation by FSA groups
        correlation_strength = self.index_params["spatial_correlation"]
        
        # Group by FSA and apply smoothing
        for col in numeric_cols:
            fsa_means = df.groupby('FSA')[col].transform('mean')
            df[col] = (correlation_strength * fsa_means + 
                      (1 - correlation_strength) * df[col]).round().astype(int)
        
        df.drop('FSA', axis=1, inplace=True)
        return df
    
    def save_dataset(self, df: pd.DataFrame, output_dir: str = "output"):
        """Save the dataset and reports."""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save main dataset
        data_filename = f"synthetic_consumer_data_{self.num_records}_{timestamp}.csv"
        data_filepath = os.path.join(output_dir, data_filename)
        
        logger.info(f"Saving dataset to {data_filepath}...")
        df.to_csv(data_filepath, index=False)
        logger.info(f"Dataset saved successfully ({os.path.getsize(data_filepath) / 1024 / 1024:.1f} MB)")
        
        # Create summary
        summary = {
            "generation_timestamp": timestamp,
            "records_generated": len(df),
            "columns_generated": len(df.columns),
            "variables_by_source": {
                "opticks": len(self.variables["opticks"]),
                "socialvalues": len(self.variables["socialvalues"]),
                "prizm": len(self.variables["prizm"]),
                "total": len(self.all_variables)
            },
            "file_size_mb": round(os.path.getsize(data_filepath) / 1024 / 1024, 1)
        }
        
        summary_filename = f"generation_summary_{timestamp}.json"
        summary_filepath = os.path.join(output_dir, summary_filename)
        
        with open(summary_filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"All files saved to {output_dir}/")
        
        return {
            "data_file": data_filepath,
            "generation_summary": summary_filepath
        }


def main():
    parser = argparse.ArgumentParser(description="Optimized synthetic data generator")
    parser.add_argument('-n', '--num-records', type=int, default=100000)
    parser.add_argument('-o', '--output-dir', type=str, default='output')
    args = parser.parse_args()
    
    # Initialize and run generator
    generator = OptimizedSyntheticDataGenerator(num_records=args.num_records)
    df = generator.generate_dataset()
    file_paths = generator.save_dataset(df, args.output_dir)
    
    # Print summary
    print("\n" + "="*60)
    print("SYNTHETIC DATA GENERATION COMPLETE")
    print("="*60)
    print(f"Records generated: {len(df):,}")
    print(f"Variables included: {len(df.columns)}")
    print(f"  - From metadata: {len(generator.all_variables)}")
    print(f"  - Geographic: 4")
    print(f"  - Calculated: 1 (NBAS12HP_PCT)")
    print(f"\nFiles created:")
    for file_type, filepath in file_paths.items():
        print(f"  - {file_type}: {filepath}")


if __name__ == "__main__":
    main()