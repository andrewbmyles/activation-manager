#!/usr/bin/env python3
"""
Fixed Canadian Consumer Behavior Synthetic Data Generator
Generates complete dataset with all metadata variables
"""

import pandas as pd
import numpy as np
import random
import string
from typing import Dict, List, Tuple, Optional
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

class SyntheticDataGenerator:
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
        self.variable_categories = VARIABLE_CATEGORIES
        self.index_params = INDEX_PARAMS
        
        # Validate and normalize PRIZM percentages
        self._normalize_prizm_percentages()
        
    def _normalize_prizm_percentages(self):
        """Ensure PRIZM segment percentages sum to 100%."""
        total_pct = sum(seg["percentage"] for seg in self.prizm_segments.values())
        
        if abs(total_pct - 100) > 0.1:
            logger.info(f"Normalizing PRIZM percentages from {total_pct:.2f}% to 100%")
            for seg in self.prizm_segments.values():
                seg["percentage"] = seg["percentage"] / total_pct * 100
    
    def generate_postal_code(self) -> str:
        """Generate a valid Canadian postal code."""
        # Select prefix based on population distribution
        prefixes = list(self.postal_code_distribution.keys())
        weights = [self.postal_code_distribution[p]["weight"] for p in prefixes]
        prefix = np.random.choice(prefixes, p=np.array(weights)/sum(weights))
        
        # Valid letters for postal codes
        valid_letters = 'ABCEGHJKLMNPRSTVWXYZ'
        
        # Generate complete postal code
        digit1 = str(random.randint(0, 9))
        letter1 = random.choice(valid_letters)
        digit2 = str(random.randint(0, 9))
        letter2 = random.choice(valid_letters)
        digit3 = str(random.randint(0, 9))
        
        return f"{prefix}{digit1}{letter1} {digit2}{letter2}{digit3}"
    
    def generate_coordinates(self, postal_code: str) -> Tuple[float, float]:
        """Generate realistic lat/long coordinates for a postal code."""
        prefix = postal_code[0]
        
        if prefix in self.postal_code_distribution:
            base_lat = self.postal_code_distribution[prefix]["lat"]
            base_lon = self.postal_code_distribution[prefix]["lon"]
            urban_type = self.postal_code_distribution[prefix]["type"]
            
            # Add variation based on urban density
            if urban_type == "urban":
                lat_var = np.random.normal(0, 0.1)
                lon_var = np.random.normal(0, 0.1)
            elif urban_type == "suburban":
                lat_var = np.random.normal(0, 0.2)
                lon_var = np.random.normal(0, 0.2)
            else:  # rural
                lat_var = np.random.normal(0, 0.5)
                lon_var = np.random.normal(0, 0.5)
            
            lat = base_lat + lat_var
            lon = base_lon + lon_var
        else:
            lat = np.random.uniform(42.0, 60.0)
            lon = np.random.uniform(-140.0, -52.0)
            
        return round(lat, 6), round(lon, 6)
    
    def assign_prizm_segment(self) -> str:
        """Assign a PRIZM segment based on distribution percentages."""
        segments = list(self.prizm_segments.keys())
        weights = [self.prizm_segments[s]["percentage"] for s in segments]
        return np.random.choice(segments, p=np.array(weights)/sum(weights))
    
    def get_variable_category(self, variable_name: str) -> Optional[str]:
        """Determine the category of a variable based on its name."""
        var_lower = variable_name.lower()
        
        for category, config in self.variable_categories.items():
            for pattern in config["patterns"]:
                if pattern.lower() in var_lower:
                    return category
                    
        return None
    
    def generate_index_value(self, segment_code: str, variable_name: str) -> int:
        """Generate an index value based on segment profile and variable type."""
        segment_profile = self.prizm_segments[segment_code]["profile"]
        
        # Get the appropriate modifier for this variable
        modifier = 1.0
        category = self.get_variable_category(variable_name)
        
        if category and category in self.variable_categories:
            modifier_key = self.variable_categories[category]["modifier_key"]
            modifier = segment_profile["modifiers"].get(modifier_key, 1.0)
        
        # Generate base value using log-normal distribution
        base_value = np.random.lognormal(
            mean=self.index_params["lognormal_mean"], 
            sigma=self.index_params["lognormal_sigma"]
        )
        
        # Apply segment modifier
        adjusted_value = base_value * modifier
        
        # Add controlled noise
        noise_level = 5 if modifier < 1.5 else 10
        noise = np.random.normal(0, noise_level)
        final_value = adjusted_value + noise
        
        # Special rules for extreme modifiers
        if modifier > 2.5:  # High affinity segments
            if np.random.random() < 0.15:  # 15% chance of outlier
                final_value = np.random.uniform(250, 500)
        elif modifier < 0.5:  # Low affinity segments
            final_value = final_value * 0.5
        
        # Clip to valid range
        return int(np.clip(final_value, 
                          self.index_params["min_value"], 
                          self.index_params["max_value"]))
    
    def generate_base_population(self, segment_code: str) -> int:
        """Generate base population values."""
        segment_profile = self.prizm_segments[segment_code]["profile"]
        
        # Base on income level and urban density
        income_factor = segment_profile["income_level"] / 3.0
        urban_factor = segment_profile["urban_density"] / 3.0
        
        # Higher income and urban areas tend to have smaller household sizes
        mean_pop = 1200 - (income_factor * 200) - (urban_factor * 100)
        
        # Add variation
        population = int(np.random.normal(mean_pop, 200))
        
        # Ensure reasonable bounds
        return max(500, min(2500, population))
    
    def add_spatial_correlation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add spatial correlation to make nearby postal codes have similar values."""
        logger.info("Applying spatial correlation...")
        
        # Group by Forward Sortation Area (first 3 characters)
        df['FSA'] = df['PostalCode'].str[:3]
        
        # Identify numeric columns to smooth (exclude geography and segment)
        exclude_cols = ['PostalCode', 'LATITUDE', 'LONGITUDE', 'PRIZM_SEGMENT', 'FSA']
        numeric_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Apply spatial smoothing
        correlation_strength = self.index_params["spatial_correlation"]
        
        # Process in batches to handle large number of columns efficiently
        batch_size = 100
        for i in range(0, len(numeric_cols), batch_size):
            batch_cols = numeric_cols[i:i+batch_size]
            
            for col in batch_cols:
                # Calculate FSA group statistics
                fsa_means = df.groupby('FSA')[col].transform('mean')
                
                # Apply smoothing
                df[col] = (correlation_strength * fsa_means + 
                          (1 - correlation_strength) * df[col]).round().astype(int)
        
        # Drop the temporary FSA column
        df.drop('FSA', axis=1, inplace=True)
        
        return df
    
    def generate_dataset(self) -> pd.DataFrame:
        """Generate the complete synthetic dataset with all variables."""
        logger.info(f"Starting generation of {self.num_records:,} records with {len(self.all_variables)} variables...")
        
        # Initialize data list
        data = []
        
        # Progress tracking
        checkpoint_interval = max(1000, self.num_records // 20)
        
        # Generate records
        for i in range(self.num_records):
            if i % checkpoint_interval == 0 and i > 0:
                progress_pct = (i / self.num_records) * 100
                logger.info(f"Progress: {i:,} records generated ({progress_pct:.1f}%)")
            
            record = {}
            
            # Generate core geographic data
            postal_code = self.generate_postal_code()
            lat, lon = self.generate_coordinates(postal_code)
            segment = self.assign_prizm_segment()
            
            record['PostalCode'] = postal_code
            record['LATITUDE'] = lat
            record['LONGITUDE'] = lon
            record['PRIZM_SEGMENT'] = segment
            
            # Generate values for ALL variables from metadata
            for var in self.all_variables:
                # Skip geographic identifiers that we already have
                if var.upper() in ['CODE', 'GEO', 'FSALDU', 'LATITUDE', 'LONGITUDE']:
                    continue
                    
                # Handle different variable types
                if var.endswith('HP') or 'POPULATION' in var.upper() or var in ['NBAS12HP', 'SVBAS15HP']:
                    # Base population variables
                    record[var] = self.generate_base_population(segment)
                else:
                    # Regular index variables
                    record[var] = self.generate_index_value(segment, var)
            
            data.append(record)
        
        # Create DataFrame
        logger.info(f"Creating DataFrame with {len(data)} records and {len(data[0]) if data else 0} columns...")
        df = pd.DataFrame(data)
        
        # Apply spatial correlation
        df = self.add_spatial_correlation(df)
        
        # Add NBAS12HP percentage column
        if 'NBAS12HP' in df.columns:
            total_nbas12hp = df['NBAS12HP'].sum()
            df['NBAS12HP_PCT'] = (df['NBAS12HP'] / total_nbas12hp * 100).round(6)
            logger.info(f"Added NBAS12HP_PCT column (total NBAS12HP: {total_nbas12hp:,})")
        
        logger.info(f"Data generation complete! Generated {len(df):,} rows with {len(df.columns)} columns")
        return df
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, any]:
        """Validate the generated data meets quality requirements."""
        logger.info("Validating generated data...")
        
        validation_results = {
            "summary": {
                "total_records": len(df),
                "total_columns": len(df.columns),
                "variables_from_metadata": len(self.all_variables),
                "timestamp": datetime.now().isoformat()
            },
            "postal_codes": {
                "valid_format": True,
                "unique_count": df['PostalCode'].nunique(),
                "sample": df['PostalCode'].head(5).tolist()
            },
            "indices": {
                "overall_mean": 0,
                "outlier_percentage": 0,
                "variables_checked": 0
            },
            "segments": {
                "distribution_accuracy": {},
                "total_segments": len(df['PRIZM_SEGMENT'].unique())
            },
            "quality_checks": {
                "all_passed": True,
                "failed_checks": []
            }
        }
        
        # Validate postal code format
        postal_pattern = r'^[A-Z]\d[A-Z] \d[A-Z]\d$'
        invalid_postcodes = ~df['PostalCode'].str.match(postal_pattern)
        if invalid_postcodes.any():
            validation_results["postal_codes"]["valid_format"] = False
            validation_results["quality_checks"]["all_passed"] = False
            validation_results["quality_checks"]["failed_checks"].append("Invalid postal code format")
        
        # Validate index values (exclude base population variables)
        index_cols = []
        for col in df.columns:
            if col not in ['PostalCode', 'LATITUDE', 'LONGITUDE', 'PRIZM_SEGMENT']:
                if not col.endswith('HP') and 'POPULATION' not in col.upper():
                    index_cols.append(col)
        
        if index_cols:
            # Sample columns if too many
            sample_cols = index_cols[:100] if len(index_cols) > 100 else index_cols
            all_indices = df[sample_cols].values.flatten()
            overall_mean = np.mean(all_indices)
            outlier_pct = (all_indices > self.index_params["outlier_threshold"]).sum() / len(all_indices) * 100
            
            validation_results["indices"]["overall_mean"] = round(overall_mean, 2)
            validation_results["indices"]["outlier_percentage"] = round(outlier_pct, 2)
            validation_results["indices"]["variables_checked"] = len(sample_cols)
            
            # Check if mean is close to 100
            if abs(overall_mean - 100) > 10:
                validation_results["quality_checks"]["all_passed"] = False
                validation_results["quality_checks"]["failed_checks"].append(
                    f"Overall mean ({overall_mean:.2f}) deviates from target (100)"
                )
        
        # Validate PRIZM segment distribution
        actual_dist = df['PRIZM_SEGMENT'].value_counts(normalize=True) * 100
        
        for segment, actual_pct in actual_dist.items():
            expected_pct = self.prizm_segments.get(segment, {}).get("percentage", 0)
            difference = abs(actual_pct - expected_pct)
            
            validation_results["segments"]["distribution_accuracy"][segment] = {
                "actual": round(actual_pct, 2),
                "expected": round(expected_pct, 2),
                "difference": round(difference, 2)
            }
            
            # Flag large deviations
            if difference > 1.0:  # More than 1% difference
                validation_results["quality_checks"]["all_passed"] = False
                validation_results["quality_checks"]["failed_checks"].append(
                    f"Segment {segment} distribution off by {difference:.2f}%"
                )
        
        return validation_results
    
    def save_dataset(self, df: pd.DataFrame, output_dir: str = "output"):
        """Save the dataset and accompanying files."""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save main dataset
        data_filename = f"synthetic_consumer_data_{self.num_records}_{timestamp}.csv"
        data_filepath = os.path.join(output_dir, data_filename)
        
        logger.info(f"Saving dataset to {data_filepath}...")
        df.to_csv(data_filepath, index=False)
        logger.info(f"Dataset saved successfully ({os.path.getsize(data_filepath) / 1024 / 1024:.1f} MB)")
        
        # Save validation report
        validation_results = self.validate_data(df)
        report_filename = f"validation_report_{timestamp}.json"
        report_filepath = os.path.join(output_dir, report_filename)
        
        with open(report_filepath, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        # Save metadata summary
        metadata_summary = {
            "generation_timestamp": timestamp,
            "records_generated": len(df),
            "columns_generated": len(df.columns),
            "variables_by_source": {
                "opticks": len(self.variables["opticks"]),
                "socialvalues": len(self.variables["socialvalues"]),
                "demographics": len(self.variables["demographics"]),
                "prizm": len(self.variables["prizm"]),
                "total_from_metadata": len(self.all_variables)
            },
            "sample_variables": {
                "first_10": list(df.columns[:10]),
                "last_10": list(df.columns[-10:])
            },
            "prizm_segments_used": len(self.prizm_segments),
            "parameters": self.index_params
        }
        
        summary_filename = f"generation_summary_{timestamp}.json"
        summary_filepath = os.path.join(output_dir, summary_filename)
        
        with open(summary_filepath, 'w') as f:
            json.dump(metadata_summary, f, indent=2)
        
        logger.info(f"All files saved to {output_dir}/")
        
        return {
            "data_file": data_filepath,
            "validation_report": report_filepath,
            "generation_summary": summary_filepath
        }


def main():
    """Main execution function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Generate synthetic Canadian consumer behavior data with all metadata variables"
    )
    parser.add_argument(
        '-n', '--num-records',
        type=int,
        default=100000,
        help='Number of records to generate (default: 100,000)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='output',
        help='Output directory for generated files (default: output)'
    )
    parser.add_argument(
        '-m', '--metadata-dir',
        type=str,
        default='Variable Metadata',
        help='Directory containing metadata files (default: Variable Metadata)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Generate a small test dataset (1,000 records)'
    )
    
    args = parser.parse_args()
    
    # Override num_records if test mode
    if args.test:
        args.num_records = 1000
        logger.info("Test mode: Generating 1,000 records")
    
    # Initialize generator
    try:
        generator = SyntheticDataGenerator(
            num_records=args.num_records,
            metadata_dir=args.metadata_dir
        )
    except Exception as e:
        logger.error(f"Failed to initialize generator: {e}")
        sys.exit(1)
    
    # Generate dataset
    try:
        df = generator.generate_dataset()
    except Exception as e:
        logger.error(f"Failed to generate dataset: {e}")
        sys.exit(1)
    
    # Save results
    try:
        file_paths = generator.save_dataset(df, args.output_dir)
    except Exception as e:
        logger.error(f"Failed to save dataset: {e}")
        sys.exit(1)
    
    # Print summary
    print("\n" + "="*60)
    print("SYNTHETIC DATA GENERATION COMPLETE")
    print("="*60)
    print(f"Records generated: {len(df):,}")
    print(f"Variables included: {len(df.columns)}")
    print(f"  - From Opticks: {len(generator.variables['opticks'])}")
    print(f"  - From Social Values: {len(generator.variables['socialvalues'])}")
    print(f"  - From PRIZM: {len(generator.variables['prizm'])}")
    print(f"  - Geographic: 4 (PostalCode, LATITUDE, LONGITUDE, PRIZM_SEGMENT)")
    print(f"  - Calculated: 1 (NBAS12HP_PCT)")
    print(f"\nFiles created:")
    for file_type, filepath in file_paths.items():
        print(f"  - {file_type}: {filepath}")
    
    # Show sample data
    print("\nSample of generated data (first 5 rows, first 10 columns):")
    print(df.iloc[:5, :10])
    
    # Show validation summary
    with open(file_paths['validation_report'], 'r') as f:
        validation = json.load(f)
    
    print(f"\nValidation Summary:")
    print(f"  - Total records: {validation['summary']['total_records']:,}")
    print(f"  - Total columns: {validation['summary']['total_columns']}")
    print(f"  - Overall mean index: {validation['indices']['overall_mean']}")
    print(f"  - Outlier percentage: {validation['indices']['outlier_percentage']}%")
    print(f"  - Quality checks passed: {validation['quality_checks']['all_passed']}")
    
    if not validation['quality_checks']['all_passed']:
        print("\nQuality issues detected:")
        for issue in validation['quality_checks']['failed_checks']:
            print(f"  - {issue}")


if __name__ == "__main__":
    main()