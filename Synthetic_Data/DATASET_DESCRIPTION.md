# Synthetic Canadian Consumer Behavior Dataset

## File Specifications
- **Format**: CSV (UTF-8 encoded)
- **Size**: ~5MB per 1,000 records (~500MB for 100K records)
- **Dimensions**: 100,000 rows × 5,072 columns (configurable)

## Data Structure

### Geographic Identifiers (4 columns)
- `PostalCode`: Canadian postal code (format: A1A 1A1)
- `LATITUDE`: Decimal latitude (42.0 to 60.0)
- `LONGITUDE`: Decimal longitude (-140.0 to -52.0)
- `PRIZM_SEGMENT`: Two-digit lifestyle segment code (01-68)

### Behavioral Indices (5,068 columns)
- **Source**: Opticks/Numeris (4,749), Social Values (272), PRIZM (93)
- **Format**: Integer indices ranging 6-1495
- **Interpretation**: 100 = national average; 200 = twice national average
- **Distribution**: Log-normal, right-skewed with ~3-10% outliers >250

## Key Characteristics
- **Geographic Distribution**: Weighted by Canadian population density (40% urban, 35% suburban, 25% rural)
- **Spatial Correlation**: Adjacent postal codes show 60-80% similar behaviors
- **PRIZM Segmentation**: 68 lifestyle segments with distinct behavioral profiles
- **No PII**: Completely synthetic data with no connection to real individuals

## Variable Examples
- `NBAS12HP`: Household population 12+ (base)
- `Q470010C01`: Distance driven per year - None
- `SV00001`: Acceptance of Violence index
- `PRIZM`: Segment identifiers with behavioral modifiers

## Use Cases
Suitable for testing analytics platforms, machine learning models, business intelligence systems, and geographic analysis tools requiring realistic Canadian consumer behavior patterns.