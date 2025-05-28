# Technical Documentation - Synthetic Data Generator

## Overview

The fixed synthetic data generator creates datasets with 5,072 columns representing all variables from the metadata files, generating the specified number of rows (default 100,000).

## Architecture Overview

The synthetic data generator consists of three core modules:

### 1. `generate_synthetic_data_fixed.py`
**Purpose**: Main generation engine with complete variable support

**Key Classes**:
- `SyntheticDataGenerator`: Orchestrates data generation for all 5,114 metadata variables
  
**Core Methods**:
- `generate_postal_code()`: Creates valid Canadian postal codes weighted by population density
- `assign_prizm_segment()`: Assigns segments based on configured percentages
- `generate_index_value()`: Produces behavioral indices using log-normal distribution with segment modifiers
- `add_spatial_correlation()`: Applies geographic smoothing to ensure nearby postal codes have similar values

**Algorithm**:
```
1. Load metadata → Extract variable names
2. For each record:
   - Generate postal code (population-weighted)
   - Assign PRIZM segment (percentage-weighted)
   - Generate coordinates (based on postal prefix)
   - Generate indices (log-normal + segment modifier)
3. Apply spatial correlation (FSA-based smoothing)
4. Validate and save
```

### 2. `config.py`
**Purpose**: Central configuration

**Key Data Structures**:
- `PRIZM_SEGMENTS`: Dictionary of 68 segments with behavioral modifiers
- `POSTAL_CODE_DISTRIBUTION`: Geographic weights and coordinates
- `VARIABLE_CATEGORIES`: Maps variable patterns to behavior types
- `INDEX_PARAMS`: Statistical parameters for index generation

### 3. `metadata_loader.py`
**Purpose**: Parse metadata files to extract variable names

**Key Methods**:
- `load_all_metadata()`: Reads CSV/Excel files, extracts variable columns
- File-specific loaders handle different formats and encodings

## Data Generation Logic

### Index Value Formula
```python
index = (postal_code_penetration / national_average) × 100
```

### Distribution Model
- **Base**: Log-normal distribution (μ=4.605, σ=0.4) → centered at 100
- **Modifiers**: Segment-specific multipliers (0.5x to 3.5x)
- **Bounds**: Clipped to [6, 1495]

### Spatial Correlation
- Groups by Forward Sortation Area (first 3 postal code chars)
- Blends individual values with FSA mean (70% weight)
- Ensures geographic clustering of behaviors

## Performance Characteristics

- **Memory**: O(n × m) where n = records, m = variables (5,072)
- **Time**: ~50 records/second with all 5,072 variables
- **Scalability**: Linear up to 1M records (larger requires batch processing)
- **File Size**: ~500MB per 100K records (CSV format)

## Dataset Specifications

### Column Count
- **Total**: 5,072 columns
- **Breakdown**:
  - Opticks/Numeris: 4,749 variables
  - Social Values: 272 variables
  - PRIZM: 93 variables  
  - Geographic: 4 core variables (PostalCode, LATITUDE, LONGITUDE, PRIZM_SEGMENT)
  - Excluded: Geographic identifiers (CODE, GEO, FSALDU) already represented

## Configuration Guide

### Adding New Segments
```python
PRIZM_SEGMENTS["XX"] = {
    "name": "Segment Name",
    "percentage": 1.5,
    "profile": {
        "modifiers": {
            "luxury_auto": 1.2,
            "technology": 2.1
        }
    }
}
```

### Customizing Geographic Distribution
```python
POSTAL_CODE_DISTRIBUTION["X"] = {
    "weight": 5.0,        # Population percentage
    "city": "City Name",
    "lat": 45.0,          # Base latitude
    "lon": -75.0,         # Base longitude
    "type": "urban"       # urban/suburban/rural
}
```

## Implementation Details

### Variable Loading
- Reads all CSV metadata files using pandas
- Extracts 'Variable' column from each file
- Filters out geographic duplicates (CODE, GEO, FSALDU)
- Total: 5,114 unique variables loaded

### Memory Optimization
- Spatial correlation applied in batches of 100 columns
- Progress logging every 5% of records
- Efficient numpy operations for index generation

## Error Handling

- Invalid metadata files: Falls back to sample variables
- Missing PRIZM percentages: Auto-normalizes to 100%
- Out-of-range indices: Clips to valid bounds
- Memory constraints: Use smaller batches via `-n` parameter
- Large datasets: Consider using `--test` mode first