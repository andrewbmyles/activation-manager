"""
Integrated Audience Handler using Enhanced Tools
Combines EnhancedVariableSelector and PRIZMAnalyzer into the workflow
"""

from enhanced_variable_selector_v2 import EnhancedVariableSelectorV2
from prizm_analyzer import PRIZMAnalyzer
from audience_builder import DataRetriever, ConstrainedKMedians
import json
import pandas as pd
from typing import Dict, Any, List, Optional
import os
from datetime import datetime
import asyncio
import aiohttp


class WorkflowState:
    """Maintains state throughout the workflow process"""
    def __init__(self):
        self.current_step = "initial"
        self.user_prompt = ""
        self.parsed_requirements = {}
        self.suggested_variables = []
        self.confirmed_variables = []
        self.data = None
        self.segments = []
        self.timestamp = datetime.now()


class IntegratedAudienceHandler:
    """
    Full workflow implementation with enhanced variable selection and PRIZM analysis
    """
    
    def __init__(self, anthropic_api_key: str, data_path: str = None):
        self.anthropic_api_key = anthropic_api_key
        self.claude_endpoint = 'https://api.anthropic.com/v1/messages'
        
        # Initialize enhanced components
        self.variable_selector = EnhancedVariableSelectorV2()
        self.data_retriever = DataRetriever(data_path)
        self.clusterer = ConstrainedKMedians()
        self.prizm_analyzer = PRIZMAnalyzer()
        
        # Load data
        if data_path:
            self.data_retriever.load_data()
        
        # Initialize state
        self.state = WorkflowState()
        
        # System prompt for Claude
        self.system_prompt = """You are an intelligent audience segmentation assistant that helps users create targeted audience groups.

When analyzing user requests:
1. Extract demographic criteria (age, location, gender, etc.)
2. Identify behavioral patterns (purchase history, engagement, etc.)
3. Note financial attributes (income, spending, credit, etc.)
4. Recognize psychographic traits (lifestyle, values, interests, etc.)

Be conversational and confirm understanding at each step."""
        
        # Session storage
        self.sessions = {}
    
    async def process_request(self, user_prompt: str, session_id: str = None) -> Dict[str, Any]:
        """
        Main entry point for processing user requests
        Routes to appropriate workflow step
        """
        if session_id and session_id in self.sessions:
            self.state = self.sessions[session_id]
        else:
            session_id = f"session_{datetime.now().timestamp()}"
            self.sessions[session_id] = self.state
        
        self.state.user_prompt = user_prompt
        
        # Route to appropriate step
        if self.state.current_step == "initial":
            return await self.analyze_prompt(user_prompt)
        elif self.state.current_step == "awaiting_confirmation":
            return await self.handle_variable_confirmation(user_prompt)
        elif self.state.current_step == "variables_confirmed":
            return await self.retrieve_and_cluster()
        
        return {"error": "Unknown workflow state"}
    
    async def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Step 1: Analyze user prompt and suggest variables
        """
        self.state.current_step = "analyzing"
        
        # Parse requirements using Claude
        parsed = await self._parse_with_claude(prompt)
        self.state.parsed_requirements = parsed
        
        # Use enhanced variable selector
        suggested = self.variable_selector.analyze_request(prompt, top_n=15)
        self.state.suggested_variables = suggested
        
        # Group by type for better presentation
        grouped_vars = {}
        for var in suggested:
            var_type = var['type']
            if var_type not in grouped_vars:
                grouped_vars[var_type] = []
            grouped_vars[var_type].append(var)
        
        self.state.current_step = "awaiting_confirmation"
        
        return {
            "status": "variables_suggested",
            "message": "Based on your requirements, I've identified these relevant variables:",
            "parsed_requirements": parsed,
            "suggested_variables": grouped_vars,
            "total_suggested": len(suggested),
            "next_action": "Please confirm the variables you'd like to use",
            "session_id": list(self.sessions.keys())[0]
        }
    
    async def _parse_with_claude(self, prompt: str) -> Dict[str, List[str]]:
        """
        Use Claude to parse natural language requirements
        """
        messages = [{
            "role": "user",
            "content": f"Extract demographic, behavioral, financial, and psychographic criteria from this request: {prompt}"
        }]
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': self.anthropic_api_key,
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                "model": "claude-opus-4-20250514",
                "messages": messages,
                "system": self.system_prompt,
                "max_tokens": 500
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.claude_endpoint, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Parse Claude's response
                        # For now, return a structured format
                        return {
                            "demographic": ["age", "location"],
                            "behavioral": ["purchase patterns"],
                            "financial": ["income level"],
                            "psychographic": ["lifestyle preferences"]
                        }
        except Exception as e:
            print(f"Claude API error: {e}")
            # Fallback to keyword parsing
            return self._fallback_parse(prompt)
    
    def _fallback_parse(self, prompt: str) -> Dict[str, List[str]]:
        """Fallback parsing using keywords"""
        prompt_lower = prompt.lower()
        requirements = {
            "demographic": [],
            "behavioral": [],
            "financial": [],
            "psychographic": []
        }
        
        # Simple keyword matching
        if any(word in prompt_lower for word in ["age", "young", "old", "millennial", "boomer"]):
            requirements["demographic"].append("age groups")
        if any(word in prompt_lower for word in ["urban", "city", "rural", "location"]):
            requirements["demographic"].append("location type")
        if any(word in prompt_lower for word in ["buy", "purchase", "shop", "engage"]):
            requirements["behavioral"].append("purchase behavior")
        if any(word in prompt_lower for word in ["income", "affluent", "wealthy", "budget"]):
            requirements["financial"].append("income level")
        if any(word in prompt_lower for word in ["lifestyle", "values", "conscious", "green"]):
            requirements["psychographic"].append("lifestyle values")
        
        return requirements
    
    async def handle_variable_confirmation(self, response: str) -> Dict[str, Any]:
        """
        Handle user's confirmation of variables
        """
        # Parse confirmed variable codes from response
        # In a real implementation, this would be more sophisticated
        confirmed_codes = []
        
        # Extract variable codes from the response
        for var in self.state.suggested_variables:
            if var['code'].lower() in response.lower() or var['description'].lower() in response.lower():
                confirmed_codes.append(var['code'])
        
        # If user said "all" or similar
        if any(word in response.lower() for word in ["all", "everything", "all of them"]):
            confirmed_codes = [var['code'] for var in self.state.suggested_variables]
        
        if not confirmed_codes:
            return {
                "status": "needs_clarification",
                "message": "I didn't catch which variables you'd like to use. Please specify the variable codes or say 'all' to use all suggestions."
            }
        
        self.state.confirmed_variables = confirmed_codes
        self.state.current_step = "variables_confirmed"
        
        return await self.retrieve_and_cluster()
    
    async def retrieve_and_cluster(self) -> Dict[str, Any]:
        """
        Retrieve data and perform clustering with PRIZM analysis
        """
        self.state.current_step = "retrieving_data"
        
        # Retrieve data
        data = self.data_retriever.fetch_data(self.state.confirmed_variables)
        
        if data.empty:
            return {
                "status": "error",
                "message": "No data available for the selected variables"
            }
        
        self.state.data = data
        self.state.current_step = "clustering"
        
        # Perform clustering
        cluster_labels = self.clusterer.fit_predict(data)
        data['Group'] = cluster_labels
        
        # Calculate statistics
        result = data.sort_values('Group').reset_index(drop=True)
        group_stats = result.groupby('Group').size()
        group_pcts = (group_stats / len(result) * 100).round(2)
        
        # Create detailed segment profiles
        segments = []
        
        # Check if we have PRIZM data
        has_prizm = 'PRIZM_CLUSTER' in result.columns
        prizm_insights = None
        
        if has_prizm:
            # Analyze with PRIZM
            prizm_insights = self.prizm_analyzer.analyze_segment_distribution(result)
        
        for group_id in sorted(result['Group'].unique()):
            group_data = result[result['Group'] == group_id]
            
            segment = {
                "group_id": int(group_id),
                "size": len(group_data),
                "size_percentage": float(group_pcts[group_id]),
                "characteristics": self._analyze_group_characteristics(group_data),
            }
            
            # Add PRIZM insights if available
            if prizm_insights and str(group_id) in prizm_insights['segment_profiles']:
                segment['prizm_profile'] = prizm_insights['segment_profiles'][str(group_id)]
            
            segments.append(segment)
        
        self.state.segments = segments
        self.state.data = result
        self.state.current_step = 'complete'
        
        response = {
            "status": "complete",
            "segments": segments,
            "total_records": len(result),
            "variables_used": self.state.confirmed_variables,
            "message": f"Successfully created {len(segments)} audience segments"
        }
        
        # Add PRIZM summary if available
        if prizm_insights:
            response['prizm_summary'] = prizm_insights.get('overall_summary', {})
            
        return response
    
    def _analyze_group_characteristics(self, group_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze characteristics of a group
        """
        characteristics = {}
        
        for col in group_data.columns:
            if col == 'Group':
                continue
                
            if group_data[col].dtype == 'object' or group_data[col].dtype == 'category':
                # Categorical variable
                value_counts = group_data[col].value_counts()
                mode_value = value_counts.index[0]
                mode_pct = (value_counts.iloc[0] / len(group_data) * 100)
                
                characteristics[col] = {
                    "type": "categorical",
                    "dominant_value": mode_value,
                    "dominant_percentage": round(mode_pct, 1),
                    "distribution": value_counts.to_dict()
                }
            else:
                # Numeric variable
                characteristics[col] = {
                    "type": "numeric",
                    "mean": round(group_data[col].mean(), 2),
                    "median": round(group_data[col].median(), 2),
                    "std": round(group_data[col].std(), 2)
                }
        
        return characteristics
    
    def export_results(self, format: str = "csv", include_prizm: bool = True) -> Any:
        """
        Export results in various formats
        """
        if self.state.data is None:
            return {"error": "No results to export"}
        
        if format == "csv":
            return self.state.data.to_csv(index=False)
        elif format == "json":
            export_data = {
                "segments": self.state.segments,
                "metadata": {
                    "created_at": self.state.timestamp.isoformat(),
                    "total_records": len(self.state.data),
                    "variables_used": self.state.confirmed_variables
                }
            }
            return json.dumps(export_data, indent=2)
        else:
            return {"error": f"Unsupported format: {format}"}


# Example usage
async def test_integrated_handler():
    """Test the integrated handler with enhanced tools"""
    
    # Initialize handler
    handler = IntegratedAudienceHandler(
        anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
        data_api_endpoint="http://localhost:5000/api/data",
        data_api_key="test_key"
    )
    
    # Test prompt
    prompt = "I need to find environmentally conscious millennials with high disposable income in urban areas for a new sustainable fashion line"
    
    print("🎯 Testing Integrated Audience Handler")
    print("="*50)
    print(f"Prompt: {prompt}\n")
    
    # Step 1: Analyze prompt
    result = await handler.process_request(prompt)
    print("Step 1 - Variable Selection:")
    print(f"Status: {result['status']}")
    print(f"Found {result['total_suggested']} relevant variables")
    
    # Display grouped variables
    for var_type, vars in result['suggested_variables'].items():
        print(f"\n{var_type.capitalize()} Variables:")
        for var in vars[:3]:  # Show top 3 per category
            print(f"  - {var['code']}: {var['description']} (score: {var['score']})")
    
    # Step 2: Confirm all variables (simulating user confirmation)
    session_id = result['session_id']
    confirmation = "Use all suggested variables"
    
    print(f"\nStep 2 - Confirming variables...")
    result = await handler.process_request(confirmation, session_id)
    
    if result['status'] == 'complete':
        print(f"\n✅ Success! Created {len(result['segments'])} segments")
        
        # Display segment summaries
        for segment in result['segments']:
            print(f"\nSegment {segment['group_id']}:")
            print(f"  Size: {segment['size']} ({segment['size_percentage']}%)")
            
            # Show PRIZM profile if available
            if 'prizm_profile' in segment:
                profile = segment['prizm_profile']
                print(f"  PRIZM Segments: {', '.join(profile['dominant_segments'][:3])}")
                print(f"  Key Traits: {', '.join(profile['key_behaviors'][:3])}")
        
        # Show overall PRIZM summary if available
        if 'prizm_summary' in result:
            summary = result['prizm_summary']
            print(f"\n📊 Overall PRIZM Summary:")
            print(f"  Diversity Score: {summary['diversity_score']}")
            print(f"  Market Potential: {summary['market_potential_index']}")


if __name__ == "__main__":
    asyncio.run(test_integrated_handler())