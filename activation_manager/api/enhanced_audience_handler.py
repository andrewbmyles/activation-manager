"""
Enhanced Audience Handler with Workflow Implementation
Implements the exact workflow from the diagram with user confirmation steps
"""

import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import our existing components
from audience_builder import AudienceBuilder
from variable_catalog import get_full_catalog
from claude_nlweb_integration import ClaudeAudienceAssistant


class WorkflowState:
    """Maintains state between workflow steps"""
    def __init__(self):
        self.user_prompt = ""
        self.suggested_variables = []
        self.confirmed_variables = []
        self.retrieved_data = None
        self.clustered_data = None
        self.workflow_stage = "initial"
        self.conversation_history = []
        
    def to_dict(self):
        """Convert state to dictionary for storage"""
        return {
            "user_prompt": self.user_prompt,
            "suggested_variables": self.suggested_variables,
            "confirmed_variables": self.confirmed_variables,
            "workflow_stage": self.workflow_stage,
            "timestamp": datetime.now().isoformat()
        }


class EnhancedAudienceWorkflow:
    """
    Implements the complete workflow from the diagram
    with interactive user confirmation at each step
    """
    
    def __init__(self, api_key: str, data_path: str):
        self.api_key = api_key
        self.assistant = ClaudeAudienceAssistant(api_key)
        self.builder = AudienceBuilder(
            variable_catalog=get_full_catalog(),
            data_path=data_path
        )
        self.state = WorkflowState()
        self.builder.data_retriever.load_data()
        
    async def process_user_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Step 1: Process user prompt through Anthropic API
        """
        self.state.user_prompt = prompt
        self.state.workflow_stage = "analyzing_prompt"
        
        # Claude analyzes the prompt
        response = {
            "stage": "prompt_analysis",
            "message": "I'm analyzing your audience requirements...",
            "prompt": prompt
        }
        
        # Extract requirements using Claude
        requirements = await self._extract_requirements(prompt)
        
        response["requirements"] = requirements
        response["next_action"] = "variable_selection"
        
        return response
    
    async def _extract_requirements(self, prompt: str) -> Dict[str, List[str]]:
        """Extract demographic, behavioral, financial, and psychographic requirements"""
        # In production, this would use Claude to parse the prompt
        # For now, using keyword matching
        requirements = {
            "demographic": [],
            "behavioral": [],
            "financial": [],
            "psychographic": []
        }
        
        prompt_lower = prompt.lower()
        
        # Demographic keywords
        if any(word in prompt_lower for word in ["age", "millennials", "gender", "location", "urban", "rural"]):
            requirements["demographic"].append("age and location data")
            
        # Behavioral keywords
        if any(word in prompt_lower for word in ["purchase", "buy", "shop", "engage", "active"]):
            requirements["behavioral"].append("purchase behavior patterns")
            
        # Financial keywords
        if any(word in prompt_lower for word in ["income", "affluent", "budget", "spending", "disposable"]):
            requirements["financial"].append("income and spending data")
            
        # Psychographic keywords
        if any(word in prompt_lower for word in ["lifestyle", "values", "conscious", "interested", "preference"]):
            requirements["psychographic"].append("lifestyle and values data")
            
        return requirements
    
    async def select_variables(self) -> Dict[str, Any]:
        """
        Step 2: Variable Select Tool
        Analyzes request and suggests relevant variables
        """
        self.state.workflow_stage = "variable_selection"
        
        # Use the variable selector
        suggestions = self.builder.variable_selector.analyze_request(self.state.user_prompt)
        self.state.suggested_variables = suggestions[:10]  # Top 10
        
        response = {
            "stage": "variable_selection",
            "message": "Based on your requirements, I've identified these relevant variables:",
            "suggested_variables": [
                {
                    "code": var["code"],
                    "description": var["description"],
                    "type": var["type"],
                    "relevance_score": var["score"]
                }
                for var in self.state.suggested_variables
            ],
            "requires_confirmation": True,
            "next_action": "confirm_variables"
        }
        
        return response
    
    async def confirm_variables(self, confirmed_codes: List[str], feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Step 3: User confirms variable selection
        """
        self.state.workflow_stage = "variables_confirmed"
        
        if feedback:
            # Process user feedback and refine selection
            # In production, this would use Claude to understand the feedback
            pass
        
        self.state.confirmed_variables = confirmed_codes
        
        # Save the confirmed list for other tools
        self._save_variable_list()
        
        response = {
            "stage": "variables_confirmed",
            "message": f"Great! I've confirmed {len(confirmed_codes)} variables for your audience.",
            "confirmed_variables": confirmed_codes,
            "next_action": "data_retrieval"
        }
        
        return response
    
    def _save_variable_list(self):
        """Save confirmed variables for other tools to access"""
        save_path = "/tmp/audience_builder_variables.json"
        with open(save_path, 'w') as f:
            json.dump({
                "variables": self.state.confirmed_variables,
                "timestamp": datetime.now().isoformat(),
                "user_prompt": self.state.user_prompt
            }, f)
    
    async def retrieve_data(self) -> Dict[str, Any]:
        """
        Step 4: Data Pull and Preparation
        Calls data service API to retrieve values
        """
        self.state.workflow_stage = "data_retrieval"
        
        # Retrieve data using confirmed variables
        sample_size = int(os.getenv('SAMPLE_SIZE', '100'))
        data = self.builder.data_retriever.fetch_data(
            self.state.confirmed_variables,
            sample_size
        )
        
        self.state.retrieved_data = data
        
        # Save data for other tools
        self._save_retrieved_data(data)
        
        response = {
            "stage": "data_retrieved",
            "message": f"Successfully retrieved data for {len(data)} records.",
            "data_shape": {
                "rows": len(data),
                "columns": len(data.columns),
                "variables": list(data.columns)
            },
            "sample_preview": data.head(5).to_dict('records'),
            "next_action": "clustering"
        }
        
        return response
    
    def _save_retrieved_data(self, data):
        """Save retrieved data for clustering tool"""
        save_path = "/tmp/audience_builder_data.csv"
        data.to_csv(save_path, index=False)
    
    async def perform_clustering(self) -> Dict[str, Any]:
        """
        Step 5: K-Medians with constraints
        Groups data with 5-10% size constraints
        """
        self.state.workflow_stage = "clustering"
        
        # Run constrained clustering
        cluster_labels = self.builder.clusterer.fit_predict(self.state.retrieved_data)
        
        # Add cluster labels to data
        self.state.retrieved_data['Group'] = cluster_labels
        self.state.clustered_data = self.state.retrieved_data.sort_values('Group')
        
        # Get group statistics
        group_stats = self._calculate_group_stats()
        
        # Validate constraints
        constraints_met = all(5 <= stat['percentage'] <= 10 for stat in group_stats)
        
        response = {
            "stage": "clustering_complete",
            "message": f"Successfully created {len(group_stats)} audience segments.",
            "groups": group_stats,
            "constraints_met": constraints_met,
            "next_action": "view_results"
        }
        
        return response
    
    def _calculate_group_stats(self) -> List[Dict[str, Any]]:
        """Calculate statistics for each group"""
        stats = []
        total_rows = len(self.state.clustered_data)
        
        for group_id in sorted(self.state.clustered_data['Group'].unique()):
            group_data = self.state.clustered_data[self.state.clustered_data['Group'] == group_id]
            size = len(group_data)
            percentage = (size / total_rows) * 100
            
            stats.append({
                "group_id": int(group_id),
                "size": size,
                "percentage": round(percentage, 2),
                "constraint_status": "✓" if 5 <= percentage <= 10 else "✗"
            })
            
        return stats
    
    async def get_target_selection_table(self) -> Dict[str, Any]:
        """
        Step 6: Return Target Selection Table
        Organized by Group, then row with all data fields
        """
        self.state.workflow_stage = "complete"
        
        # Generate detailed profiles for each group
        profiles = self.builder.get_group_profiles()
        
        # Save final results
        self._save_final_results()
        
        response = {
            "stage": "workflow_complete",
            "message": "Your audience segments are ready!",
            "summary": {
                "total_records": len(self.state.clustered_data),
                "number_of_groups": len(profiles),
                "variables_used": len(self.state.confirmed_variables)
            },
            "groups": profiles,
            "export_available": True,
            "saved_locations": {
                "variables": "/tmp/audience_builder_variables.json",
                "data": "/tmp/audience_builder_data.csv",
                "results": "/tmp/audience_builder_results.csv"
            }
        }
        
        return response
    
    def _save_final_results(self):
        """Save final clustered results"""
        save_path = "/tmp/audience_builder_results.csv"
        self.state.clustered_data.to_csv(save_path, index=False)
    
    def export_results(self, format: str = "csv") -> str:
        """Export results in specified format"""
        if format == "csv":
            return self.state.clustered_data.to_csv(index=False)
        elif format == "json":
            return self.state.clustered_data.to_json(orient='records')
        else:
            raise ValueError(f"Unsupported format: {format}")


# Interactive CLI for testing the workflow
async def interactive_workflow_demo():
    """Interactive demonstration of the workflow"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    data_path = os.getenv('DATA_PATH')
    
    workflow = EnhancedAudienceWorkflow(api_key, data_path)
    
    print("🎯 Audience Builder Workflow Demo")
    print("="*50)
    
    # Step 1: User prompt
    prompt = input("\n📝 Enter your audience description:\n> ")
    if not prompt:
        prompt = "Find environmentally conscious millennials with high disposable income in urban areas"
        print(f"Using example: {prompt}")
    
    result = await workflow.process_user_prompt(prompt)
    print(f"\n✅ {result['message']}")
    print("Requirements identified:", json.dumps(result['requirements'], indent=2))
    
    # Step 2: Variable selection
    print("\n🔍 Selecting variables...")
    result = await workflow.select_variables()
    print(f"\n{result['message']}")
    
    for i, var in enumerate(result['suggested_variables'], 1):
        print(f"{i}. {var['description']} (Type: {var['type']}, Score: {var['relevance_score']})")
    
    # Step 3: Confirm variables
    print("\n❓ Enter variable numbers to confirm (comma-separated, or 'all'):")
    selection = input("> ").strip()
    
    if selection.lower() == 'all':
        confirmed = [var['code'] for var in result['suggested_variables']]
    else:
        indices = [int(x.strip())-1 for x in selection.split(',') if x.strip().isdigit()]
        confirmed = [result['suggested_variables'][i]['code'] for i in indices if i < len(result['suggested_variables'])]
    
    result = await workflow.confirm_variables(confirmed)
    print(f"\n✅ {result['message']}")
    
    # Step 4: Data retrieval
    print("\n📊 Retrieving data...")
    result = await workflow.retrieve_data()
    print(f"\n✅ {result['message']}")
    print(f"Data shape: {result['data_shape']['rows']} rows × {result['data_shape']['columns']} columns")
    
    # Step 5: Clustering
    print("\n🎲 Performing clustering with constraints...")
    result = await workflow.perform_clustering()
    print(f"\n✅ {result['message']}")
    print("\nGroup Distribution:")
    for group in result['groups']:
        print(f"  Group {group['group_id']}: {group['percentage']}% ({group['size']} records) {group['constraint_status']}")
    
    # Step 6: Final results
    print("\n📋 Generating final results...")
    result = await workflow.get_target_selection_table()
    print(f"\n✅ {result['message']}")
    print(f"\nResults saved to: {result['saved_locations']['results']}")
    
    # Export option
    export = input("\n💾 Export results? (y/n): ")
    if export.lower() == 'y':
        csv_data = workflow.export_results('csv')
        with open('audience_segments_export.csv', 'w') as f:
            f.write(csv_data)
        print("✅ Exported to: audience_segments_export.csv")


if __name__ == "__main__":
    # Run the interactive demo
    import asyncio
    asyncio.run(interactive_workflow_demo())