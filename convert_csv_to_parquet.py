#!/usr/bin/env python3
"""Convert CSV variable file to Parquet format"""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path

def convert_csv_to_parquet():
    """Convert the CSV file to Parquet format"""
    # Paths
    csv_path = Path("data/Full_Variable_List_2022_CAN.csv")
    parquet_path = Path("data/variables_2022_can.parquet")
    
    print(f"Reading CSV from {csv_path}...")
    
    # Read CSV with proper encoding
    df = pd.read_csv(csv_path, encoding='utf-8', low_memory=False)
    
    print(f"Loaded {len(df)} variables")
    print(f"Columns: {df.columns.tolist()}")
    
    # Rename columns to match our expected format
    df = df.rename(columns={
        'VarId': 'code',
        'Description': 'description',
        'Category': 'category',
        'Theme': 'theme',
        'Context': 'context',
        'Product Vintage': 'type'
    })
    
    # Ensure all text columns are strings
    text_columns = ['code', 'description', 'category', 'type', 'theme', 'context']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna('').astype(str)
    
    # Add search-friendly lowercase columns
    df['description_lower'] = df['description'].str.lower()
    df['code_lower'] = df['code'].str.lower()
    
    # Save as Parquet
    print(f"Writing Parquet to {parquet_path}...")
    pq.write_table(pa.Table.from_pandas(df), parquet_path, compression='snappy')
    
    # Verify
    df_check = pd.read_parquet(parquet_path)
    print(f"Verified: {len(df_check)} variables written to Parquet")
    print(f"File size: {parquet_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    return parquet_path

if __name__ == "__main__":
    convert_csv_to_parquet()