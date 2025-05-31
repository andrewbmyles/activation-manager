"""
Metadata loader module to read actual variable names from CSV files.

This module handles loading and parsing the various metadata files
to extract the complete list of variables for the synthetic data generation.
"""

import pandas as pd
import os
import logging
from typing import Dict, List
import openpyxl

logger = logging.getLogger(__name__)

class MetadataLoader:
    def __init__(self, metadata_dir: str = "Variable Metadata"):
        self.metadata_dir = metadata_dir
        self.variables = {
            "opticks": [],
            "socialvalues": [],
            "demographics": [],
            "prizm": []
        }
        
    def load_all_metadata(self) -> Dict[str, List[str]]:
        """Load all metadata files and extract variable names."""
        logger.info("Loading metadata files...")
        
        # Load Opticks metadata
        self._load_opticks_metadata()
        
        # Load Social Values metadata
        self._load_socialvalues_metadata()
        
        # Load PRIZM metadata
        self._load_prizm_metadata()
        
        # Load Demographics metadata
        self._load_demographics_metadata()
        
        logger.info(f"Total variables loaded: {sum(len(v) for v in self.variables.values())}")
        return self.variables
    
    def _load_opticks_metadata(self):
        """Load Opticks (Numeris) metadata."""
        filepath = os.path.join(self.metadata_dir, "opticks-powered-by-numeris---metadata.csv")
        try:
            # Read with specific encoding to handle special characters
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            
            # Extract variable names (column 'Variable')
            if 'Variable' in df.columns:
                # Skip geography variables (CODE, GEO)
                variables = df[~df['Variable'].isin(['CODE', 'GEO'])]['Variable'].tolist()
                self.variables['opticks'] = variables
                logger.info(f"Loaded {len(variables)} Opticks variables")
            else:
                logger.warning("'Variable' column not found in Opticks metadata")
                
        except Exception as e:
            logger.error(f"Error loading Opticks metadata: {e}")
    
    def _load_socialvalues_metadata(self):
        """Load Social Values metadata."""
        filepath = os.path.join(self.metadata_dir, "socialvalues-metadata.csv")
        try:
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            
            if 'Variable' in df.columns:
                # Skip geography variables
                variables = df[~df['Variable'].isin(['CODE', 'GEO'])]['Variable'].tolist()
                self.variables['socialvalues'] = variables
                logger.info(f"Loaded {len(variables)} Social Values variables")
            else:
                logger.warning("'Variable' column not found in Social Values metadata")
                
        except Exception as e:
            logger.error(f"Error loading Social Values metadata: {e}")
    
    def _load_prizm_metadata(self):
        """Load PRIZM metadata."""
        filepath = os.path.join(self.metadata_dir, "prizm-licences-metadata.csv")
        try:
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            
            if 'Variable' in df.columns:
                # Extract non-geographic PRIZM variables
                exclude_vars = ['FSALDU', 'LATITUDE', 'LONGITUDE', 'COMMNAME']
                variables = df[~df['Variable'].isin(exclude_vars)]['Variable'].tolist()
                self.variables['prizm'] = variables
                logger.info(f"Loaded {len(variables)} PRIZM variables")
            else:
                logger.warning("'Variable' column not found in PRIZM metadata")
                
        except Exception as e:
            logger.error(f"Error loading PRIZM metadata: {e}")
    
    def _load_demographics_metadata(self):
        """Load Demographics metadata from Excel file."""
        filepath = os.path.join(self.metadata_dir, "demostats---metadata.xlsx")
        try:
            # Try to read Excel file
            df = pd.read_excel(filepath, engine='openpyxl')
            
            # Look for variable column (might be named differently)
            var_columns = ['Variable', 'VariableID', 'VARID', 'Field', 'Column']
            
            for col in var_columns:
                if col in df.columns:
                    variables = df[col].dropna().tolist()
                    # Filter out non-variable entries
                    variables = [v for v in variables if isinstance(v, str) and len(v) > 0]
                    self.variables['demographics'] = variables
                    logger.info(f"Loaded {len(variables)} Demographics variables from column '{col}'")
                    break
            else:
                logger.warning("No variable column found in Demographics metadata")
                
        except Exception as e:
            logger.error(f"Error loading Demographics metadata: {e}")
            logger.info("Attempting alternative loading method...")
            
            # Alternative: if openpyxl fails, try reading as CSV
            try:
                # Some Excel files can be read as CSV
                df = pd.read_csv(filepath.replace('.xlsx', '.csv'), encoding='utf-8-sig')
                if 'Variable' in df.columns:
                    variables = df['Variable'].dropna().tolist()
                    self.variables['demographics'] = variables
                    logger.info(f"Loaded {len(variables)} Demographics variables (CSV fallback)")
            except:
                logger.warning("Could not load Demographics metadata - using sample variables")
                # Provide sample demographics variables as fallback
                self.variables['demographics'] = [
                    'POP_TOTAL', 'POP_MALE', 'POP_FEMALE',
                    'AGE_0_14', 'AGE_15_24', 'AGE_25_34', 'AGE_35_44', 
                    'AGE_45_54', 'AGE_55_64', 'AGE_65_PLUS',
                    'HH_SIZE_1', 'HH_SIZE_2', 'HH_SIZE_3', 'HH_SIZE_4_PLUS',
                    'INCOME_UNDER_50K', 'INCOME_50K_100K', 'INCOME_100K_150K', 'INCOME_150K_PLUS',
                    'EDU_HIGH_SCHOOL', 'EDU_COLLEGE', 'EDU_UNIVERSITY'
                ]
    
    def get_all_variable_names(self) -> List[str]:
        """Get a flat list of all variable names."""
        all_vars = []
        for category_vars in self.variables.values():
            all_vars.extend(category_vars)
        return all_vars
    
    def get_variable_count_by_category(self) -> Dict[str, int]:
        """Get count of variables by category."""
        return {category: len(vars) for category, vars in self.variables.items()}
    
    def save_variable_list(self, output_file: str = "variable_list.txt"):
        """Save all variable names to a text file for reference."""
        with open(output_file, 'w') as f:
            f.write("SYNTHETIC DATA VARIABLE LIST\n")
            f.write("=" * 50 + "\n\n")
            
            for category, vars in self.variables.items():
                f.write(f"\n{category.upper()} VARIABLES ({len(vars)} variables)\n")
                f.write("-" * 30 + "\n")
                for var in sorted(vars):
                    f.write(f"{var}\n")
                    
        logger.info(f"Variable list saved to {output_file}")


# Standalone function to test metadata loading
def test_metadata_loading():
    """Test function to verify metadata loading."""
    loader = MetadataLoader()
    variables = loader.load_all_metadata()
    
    print("\nMetadata Loading Summary:")
    print("-" * 40)
    for category, count in loader.get_variable_count_by_category().items():
        print(f"{category.capitalize()}: {count} variables")
    
    print(f"\nTotal variables: {len(loader.get_all_variable_names())}")
    
    # Save variable list
    loader.save_variable_list()
    
    # Show sample variables from each category
    print("\nSample variables from each category:")
    print("-" * 40)
    for category, vars in variables.items():
        if vars:
            print(f"\n{category.capitalize()} (first 5):")
            for var in vars[:5]:
                print(f"  - {var}")


if __name__ == "__main__":
    test_metadata_loading()