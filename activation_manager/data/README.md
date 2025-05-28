# Data Directory

This directory contains data files for the Activation Manager. Large embedding files are not included in the repository.

## Embeddings

The embedding files required for full functionality are:
- `variable_embeddings_full.npy` (283MB) - Full embeddings for 48,332 variables
- `all_variable_embeddings.parquet` (67MB) - Parquet format of embeddings

### Option 1: Download from Google Cloud Storage (Recommended)

```bash
# Install gsutil if not already installed
# pip install gsutil

# Download embeddings from GCS
gsutil cp gs://activation-manager-data/embeddings/* ./embeddings/
```

### Option 2: Generate Locally

```bash
# From the project root
python generate_full_embeddings.py
```

### Option 3: Use Mock Data

For development without the full dataset, the application will automatically use mock data with 4 sample variables.

## Directory Structure

```
data/
├── README.md          # This file
├── embeddings/        # Large embedding files (gitignored)
│   ├── variable_embeddings_full.npy
│   ├── all_variable_embeddings.parquet
│   └── ...
└── ...
```

## Notes

- The application will work with mock data if embeddings are not found
- For production deployment on GCP, embeddings are loaded from Cloud Storage
- Keep embedding files out of git to avoid repository bloat