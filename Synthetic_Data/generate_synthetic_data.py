#!/usr/bin/env python3
"""
Canadian Consumer Behavior Synthetic Data Generator

This script generates synthetic consumer behavior data across Canadian postal codes,
using PRIZM segmentation as the foundation for realistic data distribution.
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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    def __init__(self, num_records: int = 100000):
        self.num_records = num_records
        self.prizm_segments = self._initialize_prizm_segments()
        self.postal_code_prefixes = self._initialize_postal_prefixes()
        self.variable_metadata = self._load_variable_metadata()
        
    def _initialize_prizm_segments(self) -> Dict:
        """Initialize PRIZM segments with their distribution percentages."""
        # These are example segments - in production, load from PRIZM Quick Reference Guide
        # Format: segment_code: (name, percentage, profile)
        segments = {
            "01": {
                "name": "Cosmopolitan Elite",
                "percentage": 1.8,
                "profile": {
                    "income": "very_high",
                    "urban": True,
                    "luxury_affinity": 2.5,
                    "tech_adoption": 2.0
                }
            },
            "02": {
                "name": "Suburban Gentry", 
                "percentage": 2.3,
                "profile": {
                    "income": "high",
                    "urban": False,
                    "luxury_affinity": 1.8,
                    "tech_adoption": 1.5
                }
            },
            "03": {
                "name": "Grads & Pads",
                "percentage": 1.9,
                "profile": {
                    "income": "medium",
                    "urban": True,
                    "luxury_affinity": 0.7,
                    "tech_adoption": 2.2
                }
            },
            "04": {
                "name": "Young Digerati",
                "percentage": 2.1,
                "profile": {
                    "income": "medium_high",
                    "urban": True,
                    "luxury_affinity": 1.2,
                    "tech_adoption": 2.8
                }
            },
            "05": {
                "name": "Famille Fusionnée",
                "percentage": 2.5,
                "profile": {
                    "income": "medium",
                    "urban": False,
                    "luxury_affinity": 0.9,
                    "tech_adoption": 1.1
                }
            },
            # Add more segments to total 100%
            # This is a simplified version - full implementation would have all 68 PRIZM segments
        }
        
        # Normalize percentages to ensure they sum to 100
        total_pct = sum(s["percentage"] for s in segments.values())
        for seg in segments.values():
            seg["percentage"] = seg["percentage"] / total_pct * 100
            
        return segments
    
    def _initialize_postal_prefixes(self) -> Dict[str, Dict]:
        """Initialize Canadian postal code prefixes with population weights."""
        prefixes = {
            # Ontario
            "M": {"weight": 15.0, "city": "Toronto", "type": "urban"},
            "L": {"weight": 8.0, "city": "Mississauga/Hamilton", "type": "suburban"},
            "K": {"weight": 5.0, "city": "Ottawa", "type": "urban"},
            "N": {"weight": 4.0, "city": "London", "type": "urban"},
            
            # Quebec
            "H": {"weight": 10.0, "city": "Montreal", "type": "urban"},
            "J": {"weight": 6.0, "city": "Montreal Region", "type": "suburban"},
            "G": {"weight": 3.0, "city": "Quebec City", "type": "urban"},
            
            # British Columbia
            "V": {"weight": 12.0, "city": "Vancouver", "type": "urban"},
            
            # Alberta
            "T": {"weight": 8.0, "city": "Calgary/Edmonton", "type": "urban"},
            
            # Other provinces (simplified)
            "R": {"weight": 2.5, "city": "Winnipeg", "type": "urban"},
            "S": {"weight": 2.0, "city": "Saskatchewan", "type": "mixed"},
            "E": {"weight": 2.0, "city": "New Brunswick", "type": "mixed"},
            "B": {"weight": 2.5, "city": "Nova Scotia", "type": "mixed"},
            "C": {"weight": 1.0, "city": "PEI", "type": "rural"},
            "A": {"weight": 1.5, "city": "Newfoundland", "type": "mixed"},
            
            # Territories
            "X": {"weight": 0.3, "city": "NWT/Nunavut", "type": "rural"},
            "Y": {"weight": 0.2, "city": "Yukon", "type": "rural"},
        }
        
        # Add remaining weight as general distribution
        total_weight = sum(p["weight"] for p in prefixes.values())
        remaining = 100 - total_weight
        
        # Distribute remaining weight proportionally
        for prefix in prefixes.values():
            prefix["weight"] = prefix["weight"] + (prefix["weight"] / total_weight * remaining)
            
        return prefixes
    
    def _load_variable_metadata(self) -> Dict[str, List[str]]:
        """Load variable names from metadata files."""
        variables = {
            "opticks": [],
            "socialvalues": [],
            "demographics": [],
            "geography": ["PostalCode", "LATITUDE", "LONGITUDE", "PRIZM_SEGMENT"]
        }
        
        # In production, these would be loaded from the actual CSV files
        # For now, using a representative sample
        variables["opticks"] = [
            "NBAS12HP", "Q470010C01", "Q470010C02", "Q470010C03", "Q470010C04",
            "Q470010C05", "Q4700100I0", "Q4700100A0", "Q470030C01", "Q470030C02",
            "Q470030C03", "Q470030C04", "Q470030C05", "Q470030C06", "Q470020C01",
            "Q470020C03", "Q470020C04", "Q470020C05", "Q470020C06", "Q470020C07"
        ]
        
        variables["socialvalues"] = [
            "SVBAS15HP", "SV00001", "SV00002", "SV00003", "SV00004", "SV00005",
            "SV00301", "SV00006", "SV00007", "SV00302", "SV00008", "SV00009",
            "SV00010", "SV00011", "SV00012", "SV00013", "SV00014", "SV00015"
        ]
        
        return variables
    
    def generate_postal_code(self) -> str:
        """Generate a valid Canadian postal code."""
        # Select prefix based on population distribution
        prefixes = list(self.postal_code_prefixes.keys())
        weights = [self.postal_code_prefixes[p]["weight"] for p in prefixes]
        prefix = np.random.choice(prefixes, p=np.array(weights)/sum(weights))
        
        # Generate the rest of the postal code
        digit1 = random.randint(0, 9)
        letter1 = random.choice(string.ascii_uppercase.replace('D', '').replace('F', '').replace('I', '').replace('O', '').replace('Q', '').replace('U', ''))
        
        digit2 = random.randint(0, 9)
        letter2 = random.choice(string.ascii_uppercase.replace('D', '').replace('F', '').replace('I', '').replace('O', '').replace('Q', '').replace('U', ''))
        digit3 = random.randint(0, 9)
        
        return f"{prefix}{digit1}{letter1} {digit2}{letter2}{digit3}"
    
    def assign_prizm_segment(self) -> str:
        """Assign a PRIZM segment based on distribution percentages."""
        segments = list(self.prizm_segments.keys())
        weights = [self.prizm_segments[s]["percentage"] for s in segments]
        return np.random.choice(segments, p=np.array(weights)/sum(weights))
    
    def generate_index_value(self, segment_code: str, variable_type: str, 
                           base_mean: float = 100) -> int:
        """
        Generate an index value based on segment profile and variable type.
        Index = (Postal_Code_Penetration / National_Average) × 100
        """
        segment_profile = self.prizm_segments[segment_code]["profile"]
        
        # Determine modifier based on segment profile and variable type
        modifier = 1.0
        
        if "luxury" in variable_type.lower() or "premium" in variable_type.lower():
            modifier = segment_profile.get("luxury_affinity", 1.0)
        elif "tech" in variable_type.lower() or "digital" in variable_type.lower():
            modifier = segment_profile.get("tech_adoption", 1.0)
        
        # Generate base value using log-normal distribution
        # Parameters tuned to center around 100 with realistic spread
        base_value = np.random.lognormal(mean=4.605, sigma=0.4) 
        
        # Apply segment modifier
        adjusted_value = base_value * modifier
        
        # Add some random variation
        noise = np.random.normal(0, 5)
        final_value = adjusted_value + noise
        
        # Clip to valid range and convert to integer
        return int(np.clip(final_value, 6, 1495))
    
    def generate_coordinates(self, postal_code: str) -> Tuple[float, float]:
        """Generate realistic lat/long coordinates for a postal code."""
        prefix = postal_code[0]
        
        # Base coordinates for major cities (simplified)
        city_coords = {
            "M": (43.65, -79.38),  # Toronto
            "H": (45.50, -73.57),  # Montreal
            "V": (49.28, -123.12), # Vancouver
            "T": (51.05, -114.07), # Calgary
            "K": (45.42, -75.69),  # Ottawa
            "L": (43.59, -79.64),  # Mississauga
        }
        
        if prefix in city_coords:
            base_lat, base_lon = city_coords[prefix]
            # Add small random variation (roughly 50km radius)
            lat = base_lat + np.random.normal(0, 0.2)
            lon = base_lon + np.random.normal(0, 0.2)
        else:
            # For other prefixes, generate within Canada's bounds
            lat = np.random.uniform(42.0, 60.0)
            lon = np.random.uniform(-140.0, -52.0)
            
        return round(lat, 6), round(lon, 6)
    
    def add_spatial_correlation(self, df: pd.DataFrame, correlation_strength: float = 0.7):
        """Add spatial correlation to make nearby postal codes have similar values."""
        logger.info("Applying spatial correlation...")
        
        # Group by first 3 characters of postal code (Forward Sortation Area)
        df['FSA'] = df['PostalCode'].str[:3]
        
        # For each numeric column (excluding geography), apply smoothing within FSA
        numeric_cols = [col for col in df.columns if col.startswith(('Q', 'SV', 'NBAS', 'SVBAS'))]
        
        for col in numeric_cols:
            # Calculate FSA means
            fsa_means = df.groupby('FSA')[col].transform('mean')
            
            # Blend individual values with FSA mean
            df[col] = (correlation_strength * fsa_means + 
                      (1 - correlation_strength) * df[col]).round().astype(int)
            
        df.drop('FSA', axis=1, inplace=True)
        return df
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, any]:
        """Validate the generated data meets quality requirements."""
        logger.info("Validating generated data...")
        
        validation_results = {
            "total_records": len(df),
            "postal_code_valid": True,
            "index_ranges_valid": True,
            "mean_indices": {},
            "outlier_percentages": {},
            "segment_distribution": {}
        }
        
        # Check postal code format
        postal_pattern = r'^[A-Z]\d[A-Z] \d[A-Z]\d$'
        invalid_postcodes = ~df['PostalCode'].str.match(postal_pattern)
        if invalid_postcodes.any():
            validation_results["postal_code_valid"] = False
            
        # Check index value ranges and statistics
        index_cols = [col for col in df.columns if col.startswith(('Q', 'SV'))]
        
        for col in index_cols:
            col_data = df[col]
            mean_val = col_data.mean()
            outlier_pct = (col_data > 250).sum() / len(col_data) * 100
            
            validation_results["mean_indices"][col] = round(mean_val, 2)
            validation_results["outlier_percentages"][col] = round(outlier_pct, 2)
            
            # Check if values are within valid range
            if col_data.min() < 6 or col_data.max() > 1495:
                validation_results["index_ranges_valid"] = False
                
        # Check PRIZM segment distribution
        segment_counts = df['PRIZM_SEGMENT'].value_counts(normalize=True) * 100
        for segment, actual_pct in segment_counts.items():
            expected_pct = self.prizm_segments.get(segment, {}).get("percentage", 0)
            validation_results["segment_distribution"][segment] = {
                "actual": round(actual_pct, 2),
                "expected": round(expected_pct, 2),
                "difference": round(abs(actual_pct - expected_pct), 2)
            }
            
        return validation_results
    
    def generate_dataset(self) -> pd.DataFrame:
        """Generate the complete synthetic dataset."""
        logger.info(f"Starting generation of {self.num_records} synthetic records...")
        
        # Initialize data storage
        data = []
        
        # Generate records
        for i in range(self.num_records):
            if i % 10000 == 0:
                logger.info(f"Generated {i} records...")
                
            record = {}
            
            # Generate geographic data
            postal_code = self.generate_postal_code()
            lat, lon = self.generate_coordinates(postal_code)
            segment = self.assign_prizm_segment()
            
            record['PostalCode'] = postal_code
            record['LATITUDE'] = lat
            record['LONGITUDE'] = lon
            record['PRIZM_SEGMENT'] = segment
            
            # Generate behavioral indices
            # Opticks variables (media/automotive)
            for var in self.variable_metadata["opticks"]:
                if var == "NBAS12HP":
                    # Base population variable
                    record[var] = np.random.randint(800, 2000)
                else:
                    record[var] = self.generate_index_value(segment, var)
                    
            # Social values variables
            for var in self.variable_metadata["socialvalues"]:
                if var == "SVBAS15HP":
                    # Base population variable
                    record[var] = np.random.randint(800, 2000)
                else:
                    record[var] = self.generate_index_value(segment, var)
                    
            data.append(record)
            
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Apply spatial correlation
        df = self.add_spatial_correlation(df)
        
        logger.info("Data generation complete!")
        return df
    
    def save_dataset(self, df: pd.DataFrame, filename: str = None):
        """Save the dataset to CSV file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"synthetic_consumer_data_{timestamp}.csv"
            
        filepath = os.path.join(os.getcwd(), filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Dataset saved to: {filepath}")
        
        # Save validation report
        validation_results = self.validate_data(df)
        report_filename = filename.replace('.csv', '_validation_report.json')
        with open(report_filename, 'w') as f:
            json.dump(validation_results, f, indent=2)
        logger.info(f"Validation report saved to: {report_filename}")
        
        return filepath, report_filename


def main():
    """Main execution function."""
    # Configuration
    NUM_RECORDS = 100000  # Change this to generate more or fewer records
    
    # Initialize generator
    generator = SyntheticDataGenerator(num_records=NUM_RECORDS)
    
    # Generate dataset
    df = generator.generate_dataset()
    
    # Validate and save
    filepath, report_path = generator.save_dataset(df)
    
    # Print summary statistics
    print(f"\nDataset Generation Complete!")
    print(f"Records generated: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"File saved to: {filepath}")
    print(f"Validation report: {report_path}")
    
    # Show sample of data
    print("\nSample of generated data:")
    print(df.head())
    
    # Show basic statistics
    print("\nBasic statistics for index variables:")
    index_cols = [col for col in df.columns if col.startswith(('Q', 'SV'))]
    print(df[index_cols[:5]].describe())


if __name__ == "__main__":
    main()