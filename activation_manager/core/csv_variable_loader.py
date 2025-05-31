"""
CSV Variable Loader
Loads variables from the Full Variable List CSV file
"""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CSVVariableLoader:
    """Loads variables from the Full Variable List CSV"""
    
    def __init__(self):
        self.variables = {}
        # Try multiple paths for different environments
        possible_paths = [
            Path(__file__).parent.parent.parent / "data" / "Full_Variable_List_2022_CAN.csv",  # Development
            Path("/srv/data/Full_Variable_List_2022_CAN.csv"),  # App Engine
            Path("data/Full_Variable_List_2022_CAN.csv"),  # Relative path
        ]
        
        self.csv_path = None
        for path in possible_paths:
            if path.exists():
                self.csv_path = path
                break
                
        if not self.csv_path:
            # Default to first option
            self.csv_path = possible_paths[0]
            
        self.load_variables()
    
    def load_variables(self):
        """Load variables from CSV file"""
        if not self.csv_path.exists():
            logger.error(f"CSV file not found: {self.csv_path}")
            return
            
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    var_id = row.get('VarId', '').strip()
                    if var_id:
                        self.variables[var_id] = {
                            'code': var_id,
                            'description': row.get('Description', '').strip(),
                            'category': row.get('Category', '').strip(),
                            'theme': row.get('Theme', '').strip(),
                            'product_name': row.get('ProductName', '').strip(),
                            'context': row.get('Context', '').strip(),
                            'consumption_flag': row.get('Consumption Flag', '').strip(),
                            'vintage': row.get('Product Vintage', '').strip(),
                            'sort_order': int(row.get('SortOrder', 0)) if row.get('SortOrder', '').isdigit() else 0
                        }
                
            logger.info(f"Loaded {len(self.variables)} variables from CSV")
            
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
    
    def get_variable(self, var_id: str) -> Optional[Dict]:
        """Get a specific variable by ID"""
        return self.variables.get(var_id)
    
    def get_all_variables(self) -> Dict[str, Dict]:
        """Get all variables"""
        return self.variables
    
    def search_by_description(self, query: str, limit: int = 50) -> List[Dict]:
        """Simple text search in descriptions"""
        query_lower = query.lower()
        results = []
        
        for var_id, var in self.variables.items():
            description = var.get('description', '').lower()
            category = var.get('category', '').lower()
            context = var.get('context', '').lower()
            
            # Simple scoring based on matches
            score = 0
            if query_lower in description:
                score += 10
            if query_lower in category:
                score += 5
            if query_lower in context:
                score += 3
                
            # Partial word matches
            for word in query_lower.split():
                if word in description:
                    score += 2
                if word in category:
                    score += 1
                    
            if score > 0:
                results.append({
                    **var,
                    'score': score
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def get_variables_by_theme(self, theme: str) -> List[Dict]:
        """Get all variables for a specific theme"""
        theme_lower = theme.lower()
        return [
            var for var in self.variables.values()
            if var.get('theme', '').lower() == theme_lower
        ]
    
    def get_variables_by_category(self, category: str) -> List[Dict]:
        """Get all variables for a specific category"""
        category_lower = category.lower()
        return [
            var for var in self.variables.values()
            if var.get('category', '').lower() == category_lower
        ]