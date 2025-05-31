#!/usr/bin/env python3
"""Quick test to verify the data generator works with a subset of variables."""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

# Test with limited variables
def test_generation():
    print("Testing synthetic data generation with limited variables...")
    
    # Create test data with core structure
    num_records = 100
    data = []
    
    # Simple PRIZM segments for testing
    segments = ["01", "02", "03", "04", "05"]
    
    for i in range(num_records):
        record = {
            "PostalCode": f"M5V {i%9}A{i%10}",
            "LATITUDE": 43.65 + np.random.normal(0, 0.1),
            "LONGITUDE": -79.38 + np.random.normal(0, 0.1),
            "PRIZM_SEGMENT": np.random.choice(segments),
            "NBAS12HP": np.random.randint(800, 2000),
            "Q470010C01": int(np.random.lognormal(4.605, 0.4)),
            "Q470010C02": int(np.random.lognormal(4.605, 0.4)),
            "SV00001": int(np.random.lognormal(4.605, 0.4)),
            "SV00002": int(np.random.lognormal(4.605, 0.4))
        }
        
        # Clip values to valid range
        for key in ["Q470010C01", "Q470010C02", "SV00001", "SV00002"]:
            record[key] = max(6, min(1495, record[key]))
            
        data.append(record)
    
    df = pd.DataFrame(data)
    
    # Save test output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/test_data_{timestamp}.csv"
    df.to_csv(output_file, index=False)
    
    # Basic validation
    print(f"\nGenerated {len(df)} records")
    print(f"Columns: {list(df.columns)}")
    print(f"\nSample data:")
    print(df.head())
    
    # Check statistics
    index_cols = ["Q470010C01", "Q470010C02", "SV00001", "SV00002"]
    mean_values = df[index_cols].mean()
    
    print(f"\nMean values:")
    for col, mean in mean_values.items():
        print(f"  {col}: {mean:.2f}")
    
    print(f"\nOverall mean: {mean_values.mean():.2f}")
    print(f"File saved to: {output_file}")
    
    return df

if __name__ == "__main__":
    test_generation()