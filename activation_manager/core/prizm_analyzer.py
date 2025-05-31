"""
PRIZM Segment Analyzer
Analyzes and describes audience segments using PRIZM methodology
"""

import pandas as pd
from typing import Dict, List, Any
import json


class PRIZMAnalyzer:
    """
    Analyzes segments using PRIZM segment definitions
    Provides rich descriptions of audience characteristics
    """
    
    def __init__(self):
        # PRIZM segment definitions (based on typical PRIZM segments)
        # In production, this would be extracted from the PDF
        self.segment_profiles = self._load_segment_profiles()
        self.prizm_segments = self.segment_profiles  # Alias for backward compatibility
    
    def _load_segment_profiles(self):
        """Load PRIZM segment profiles"""
        return {
            "01": {
                "name": "Cosmopolitan Elite",
                "description": "Affluent, highly educated professionals in major metros",
                "demographics": {
                    "age": "35-54",
                    "income": "$150,000+",
                    "education": "Graduate degree",
                    "location": "Urban cores"
                },
                "behaviors": [
                    "Luxury travel",
                    "Premium brands",
                    "Investment focused",
                    "Technology early adopters"
                ],
                "psychographics": [
                    "Career-driven",
                    "Cultured",
                    "Environmentally conscious",
                    "Global mindset"
                ]
            },
            "02": {
                "name": "Suburban Prosperity",
                "description": "Wealthy families in upscale suburban neighborhoods",
                "demographics": {
                    "age": "35-54",
                    "income": "$100,000-$150,000",
                    "education": "College+",
                    "location": "Suburban"
                },
                "behaviors": [
                    "Family-oriented purchases",
                    "Home improvement",
                    "Youth sports/activities",
                    "SUV owners"
                ],
                "psychographics": [
                    "Family-focused",
                    "Community-oriented",
                    "Education-valued",
                    "Traditional values"
                ]
            },
            "03": {
                "name": "Young Digerati",
                "description": "Tech-savvy young professionals in trendy neighborhoods",
                "demographics": {
                    "age": "25-34",
                    "income": "$75,000-$100,000",
                    "education": "College degree",
                    "location": "Urban/Inner suburbs"
                },
                "behaviors": [
                    "Online everything",
                    "Streaming services",
                    "Fitness focused",
                    "Ride-sharing users"
                ],
                "psychographics": [
                    "Tech-native",
                    "Experience-seekers",
                    "Socially conscious",
                    "Work-life balance"
                ]
            },
            "04": {
                "name": "Country Comfort",
                "description": "Middle-income families in rural areas",
                "demographics": {
                    "age": "35-54",
                    "income": "$50,000-$75,000",
                    "education": "High school/Some college",
                    "location": "Rural/Small town"
                },
                "behaviors": [
                    "DIY projects",
                    "Outdoor recreation",
                    "Truck ownership",
                    "Local shopping"
                ],
                "psychographics": [
                    "Traditional values",
                    "Self-reliant",
                    "Community-focused",
                    "Practical mindset"
                ]
            },
            "05": {
                "name": "Urban Achievers",
                "description": "Young, educated singles and couples in city centers",
                "demographics": {
                    "age": "25-34",
                    "income": "$50,000-$75,000",
                    "education": "College degree",
                    "location": "Urban"
                },
                "behaviors": [
                    "Public transit users",
                    "Restaurant frequenters",
                    "Apartment renters",
                    "Cultural event attendees"
                ],
                "psychographics": [
                    "Career-building",
                    "Social",
                    "Culturally diverse",
                    "Environmentally aware"
                ]
            }
        }
        
        # Add more segments as needed...
        for i in range(6, 11):
            self.prizm_segments[f"{i:02d}"] = {
                "name": f"Segment {i:02d}",
                "description": f"Standard demographic segment {i}",
                "demographics": {
                    "age": "25-54",
                    "income": "$50,000-$100,000",
                    "education": "Varied",
                    "location": "Mixed"
                },
                "behaviors": ["General consumer behaviors"],
                "psychographics": ["Mainstream values"]
            }
    
    def analyze_segment_distribution(self, segment_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the distribution of PRIZM segments in clustered data
        
        Args:
            segment_data: DataFrame with 'Group' and 'PRIZM_CLUSTER' columns
            
        Returns:
            Analysis with segment_profiles and overall_summary keys
        """
        # Handle different column names - check for both PRIZM_SEGMENT and PRIZM_CLUSTER
        prizm_col = None
        for col in ['PRIZM_CLUSTER', 'PRIZM_SEGMENT']:
            if col in segment_data.columns:
                prizm_col = col
                break
        
        if prizm_col is None:
            # Return structure that tests expect with error handling
            return {
                "segment_profiles": {},
                "overall_summary": {
                    "total_segments": 0,
                    "diversity_score": 0.0,
                    "top_segments": [],
                    "market_potential_index": 0.0
                },
                "error": "No PRIZM_SEGMENT column found in data"
            }
        
        segment_profiles = {}
        all_prizm_segments = []
        
        for group_id in segment_data['Group'].unique():
            group_data = segment_data[segment_data['Group'] == group_id]
            
            # Get PRIZM segment distribution
            prizm_dist = group_data[prizm_col].value_counts()
            all_prizm_segments.extend(group_data[prizm_col].tolist())
            
            # Create dominant segments list
            dominant_segments = [str(seg) for seg in prizm_dist.index[:3]]
            
            # Get demographics and behaviors
            demographics = "Mixed demographics"
            key_behaviors = ["General behaviors"]
            psychographics = ["Mainstream values"]
            marketing_implications = "Standard marketing approach"
            
            # If we have a known segment, use its data
            if len(dominant_segments) > 0:
                first_segment = dominant_segments[0]
                segment_key = first_segment if first_segment in self.prizm_segments else f"{int(first_segment):02d}" if first_segment.isdigit() else None
                
                if segment_key and segment_key in self.prizm_segments:
                    segment_info = self.prizm_segments[segment_key]
                    demographics = f"{segment_info['demographics']['age']}, {segment_info['demographics']['income']}"
                    key_behaviors = segment_info['behaviors'][:3]
                    psychographics = segment_info['psychographics'][:3]
                    marketing_implications = "; ".join(self._get_marketing_implications(segment_info))
            
            segment_profiles[str(group_id)] = {
                "dominant_segments": dominant_segments,
                "demographics": demographics,
                "key_behaviors": key_behaviors,
                "psychographics": psychographics,
                "marketing_implications": marketing_implications
            }
        
        # Calculate overall summary
        unique_segments = len(set(all_prizm_segments))
        total_segments = len(all_prizm_segments)
        diversity_score = unique_segments / total_segments if total_segments > 0 else 0.0
        
        # Get top segments
        from collections import Counter
        segment_counts = Counter(all_prizm_segments)
        top_segments = [seg for seg, count in segment_counts.most_common(5)]
        
        # Calculate market potential (simple heuristic)
        market_potential = min(10.0, diversity_score * 10 + len(segment_profiles))
        
        overall_summary = {
            "total_segments": unique_segments,
            "diversity_score": round(diversity_score, 3),
            "top_segments": top_segments,
            "market_potential_index": round(market_potential, 1)
        }
        
        return {
            "segment_profiles": segment_profiles,
            "overall_summary": overall_summary
        }
    
    def _get_segment_profile(self, segment_name: str) -> Dict[str, Any]:
        """
        Get profile for a specific segment by name
        
        Args:
            segment_name: Name of the PRIZM segment
            
        Returns:
            Segment profile dictionary
        """
        # Search by name
        for code, profile in self.prizm_segments.items():
            if profile['name'] == segment_name:
                return profile
        
        # Return default profile if not found
        return {
            "name": segment_name,
            "description": f"Profile for {segment_name}",
            "demographics": {
                "age": "Mixed",
                "income": "Varied",
                "education": "Mixed",
                "location": "Various"
            },
            "behaviors": ["General consumer behaviors"],
            "psychographics": ["Mainstream values"]
        }
    
    def _get_marketing_implications(self, segment_info: Dict) -> List[str]:
        """Generate marketing implications based on segment characteristics"""
        implications = []
        
        # Based on income
        if "$150,000+" in segment_info['demographics'].get('income', ''):
            implications.append("Target with premium/luxury offerings")
        elif "$100,000" in segment_info['demographics'].get('income', ''):
            implications.append("Focus on value-premium balance")
        else:
            implications.append("Emphasize value and practicality")
            
        # Based on location
        if "Urban" in segment_info['demographics'].get('location', ''):
            implications.append("Digital-first marketing approach")
        elif "Rural" in segment_info['demographics'].get('location', ''):
            implications.append("Traditional media mix important")
            
        # Based on behaviors
        behaviors_str = ' '.join(segment_info.get('behaviors', []))
        if 'online' in behaviors_str.lower() or 'tech' in behaviors_str.lower():
            implications.append("Leverage social media and digital channels")
        if 'family' in behaviors_str.lower():
            implications.append("Family-oriented messaging")
            
        return implications[:3]  # Top 3 implications
    
    def create_audience_narrative(self, group_analysis: Dict) -> str:
        """
        Create a natural language narrative describing the audience
        
        Args:
            group_analysis: Analysis from analyze_segment_distribution
            
        Returns:
            Human-readable narrative
        """
        narratives = []
        
        for group_id, info in group_analysis.items():
            if 'error' not in info:
                narrative = f"**{group_id}** ({info['percentage']}% of audience):\n"
                
                if 'dominant_prizm_name' in info:
                    narrative += f"This segment is primarily composed of '{info['dominant_prizm_name']}' - {info['description']}. "
                    narrative += f"They are typically {info['key_demographics']['age']} years old, "
                    narrative += f"with {info['key_demographics']['income']} household income, "
                    narrative += f"living in {info['key_demographics']['location']} areas.\n\n"
                    
                    narrative += "Key behaviors include: " + ", ".join(info['likely_behaviors']) + ".\n"
                    narrative += "They value: " + ", ".join(info['psychographic_traits']) + ".\n\n"
                    
                    narrative += "Marketing approach: " + "; ".join(info['marketing_implications']) + "."
                else:
                    narrative += f"This is a mixed demographic segment representing {info['percentage']}% of the audience."
                    
                narratives.append(narrative)
                
        return "\n\n".join(narratives)
    
    def get_segment_compatibility_score(self, segment_code: str, target_attributes: List[str]) -> float:
        """
        Calculate how well a PRIZM segment matches target attributes
        
        Args:
            segment_code: PRIZM segment code
            target_attributes: List of desired attributes
            
        Returns:
            Compatibility score (0-1)
        """
        if segment_code not in self.prizm_segments:
            return 0.0
            
        segment = self.prizm_segments[segment_code]
        matches = 0
        total_checks = 0
        
        # Convert segment data to searchable text
        segment_text = json.dumps(segment).lower()
        
        # Check each target attribute
        for attribute in target_attributes:
            attr_lower = attribute.lower()
            total_checks += 1
            
            # Direct match
            if attr_lower in segment_text:
                matches += 1
            # Partial matches for common terms
            elif any(term in attr_lower for term in ['high income', 'affluent']) and \
                 any(term in segment_text for term in ['150,000+', '100,000']):
                matches += 0.7
            elif 'millennial' in attr_lower and '25-34' in segment_text:
                matches += 0.8
            elif 'urban' in attr_lower and 'urban' in segment_text:
                matches += 1
            elif 'environmental' in attr_lower and 'conscious' in segment_text:
                matches += 0.6
                
        return matches / total_checks if total_checks > 0 else 0.0


# Test the analyzer
if __name__ == "__main__":
    analyzer = PRIZMAnalyzer()
    
    # Create sample data
    sample_data = pd.DataFrame({
        'Group': [0, 0, 0, 1, 1, 1, 2, 2, 2],
        'PRIZM_SEGMENT': ['01', '01', '03', '02', '02', '04', '03', '05', '05']
    })
    
    # Analyze segments
    analysis = analyzer.analyze_segment_distribution(sample_data)
    
    # Print analysis
    print("Segment Analysis:")
    print("=" * 80)
    for group, info in analysis.items():
        print(f"\n{group}:")
        print(json.dumps(info, indent=2))
        
    # Create narrative
    print("\n\nAudience Narrative:")
    print("=" * 80)
    narrative = analyzer.create_audience_narrative(analysis)
    print(narrative)