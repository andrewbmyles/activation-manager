# Canadian Consumer Behavior Synthetic Data Generator

A sophisticated Python application for generating realistic synthetic consumer behavior data across Canadian postal codes using PRIZM segmentation.

## Features

- **Realistic Geographic Distribution**: Generates postal codes following actual Canadian population density patterns
- **PRIZM Segmentation**: Incorporates 68 PRIZM lifestyle segments with accurate distribution percentages  
- **Multiple Data Sources**: Integrates variables from Opticks/Numeris, Social Values, Demographics, and PRIZM metadata
- **Spatial Correlation**: Ensures nearby postal codes have similar behavioral patterns
- **Comprehensive Validation**: Includes quality checks and validation reporting
- **Scalable Architecture**: Efficiently generates datasets from 1,000 to 1M+ records

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required dependencies:
```bash
pip install pandas numpy openpyxl
```

## Usage

### Basic Usage

Generate 100,000 records (default):
```bash
python generate_synthetic_data_fixed.py
```

### Advanced Options

```bash
# Generate 1 million records
python generate_synthetic_data_fixed.py -n 1000000

# Specify custom output directory
python generate_synthetic_data_fixed.py -o my_output_folder

# Generate small test dataset (1,000 records)
python generate_synthetic_data_fixed.py --test

# Use custom metadata directory
python generate_synthetic_data_fixed.py -m "path/to/metadata"
```

### Command Line Arguments

- `-n, --num-records`: Number of records to generate (default: 100,000)
- `-o, --output-dir`: Output directory for generated files (default: output)
- `-m, --metadata-dir`: Directory containing metadata files (default: Variable Metadata)
- `--test`: Generate a small test dataset for testing (1,000 records)

## Output Files

The generator creates three files in the output directory:

1. **synthetic_consumer_data_[records]_[timestamp].csv**: The main dataset with 5,000+ columns
2. **validation_report_[timestamp].json**: Data quality validation results
3. **generation_summary_[timestamp].json**: Generation parameters and metadata

### Dataset Size
- **Columns**: 5,072 (includes all variables from metadata files)
  - Opticks/Numeris: 4,749 variables
  - Social Values: 272 variables  
  - PRIZM: 93 variables
  - Geographic: 4 core variables
- **Rows**: Configurable (default 100,000, scalable to 1M+)

## Data Structure

### Geographic Variables
- `PostalCode`: Canadian postal code (format: A1A 1A1)
- `LATITUDE`: Latitude coordinate
- `LONGITUDE`: Longitude coordinate  
- `PRIZM_SEGMENT`: Two-digit PRIZM segment code

### Behavioral Indices
- **Range**: 6 to 1495
- **Average**: 100 (national average)
- **Interpretation**: Index of 200 = twice the national average penetration

### Variable Categories
- **Opticks/Numeris**: Media consumption and automotive behaviors
- **Social Values**: Psychographic trends and attitudes
- **Demographics**: Population, age, income, education variables
- **PRIZM**: Lifestyle and geo-demographic variables

## Configuration

### Modifying PRIZM Segments

Edit `config.py` to adjust segment profiles:

```python
PRIZM_SEGMENTS = {
    "01": {
        "name": "Cosmopolitan Elite",
        "percentage": 1.82,
        "profile": {
            "modifiers": {
                "luxury_auto": 3.2,
                "premium_brands": 2.8,
                # ... more modifiers
            }
        }
    }
    # ... more segments
}
```

### Adding Variable Categories

Add new behavioral categories in `config.py`:

```python
VARIABLE_CATEGORIES = {
    "my_category": {
        "patterns": ["pattern1", "pattern2"],
        "modifier_key": "my_modifier"
    }
}
```

## Validation

The generator performs automatic validation including:

- Postal code format verification
- Index value range checks (6-1495)
- Overall mean approximation (should be ~100)
- Outlier frequency validation
- PRIZM segment distribution accuracy
- Spatial correlation checks

View detailed validation results in the generated `validation_report_*.json` file.

## Examples

### Loading and Analyzing Generated Data

```python
import pandas as pd

# Load the generated data
df = pd.read_csv('output/synthetic_consumer_data_100000_20240101_120000.csv')

# View basic statistics
print(df.describe())

# Check PRIZM segment distribution
print(df['PRIZM_SEGMENT'].value_counts(normalize=True) * 100)

# Analyze spatial patterns
print(df.groupby(df['PostalCode'].str[:3])['Q470010C01'].mean())
```

### Custom Generation Script

```python
from generate_synthetic_data_fixed import SyntheticDataGenerator

# Create generator with custom parameters
generator = SyntheticDataGenerator(num_records=50000)

# Generate data with all 5,072 variables
df = generator.generate_dataset()

# Apply custom processing
# ... your code here ...

# Save with validation
generator.save_dataset(df, output_dir='custom_output')
```

## Troubleshooting

### Common Issues

1. **FileNotFoundError**: Ensure metadata files are in the correct directory
2. **Memory Error**: For large datasets (1M+), ensure sufficient RAM (8GB+ recommended)
3. **Slow Generation**: Expected performance is ~10,000 records/second on modern hardware

### Performance Tips

- Use the `--test` flag to validate your setup with a small dataset first
- For datasets over 1M records, consider generating in batches
- Disable logging for maximum performance in production
- Large datasets (100K+ rows × 5K+ columns) require significant memory (8-16GB RAM)
- Generation time: ~20-30 seconds per 1,000 records with all variables

## Data Privacy & Usage

This generator creates entirely synthetic data with no connection to real individuals. The data is suitable for:

- Software testing and development
- Analytics platform demos
- Machine learning model training
- Academic research
- Business intelligence testing

## Support

For issues or questions:
1. Check the validation report for data quality issues
2. Review the generation summary for configuration details
3. Examine log output for detailed error messages

## License

This synthetic data generator is provided as-is for testing and development purposes.