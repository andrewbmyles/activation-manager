"""
Claude + NLWeb Integration for Audience Builder
Provides natural language interface using Claude API
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime


class ClaudeAudienceAssistant:
    """
    Claude-powered assistant for audience segmentation
    Integrates with NLWeb for natural language processing
    """
    
    def __init__(self, api_key: str, backend_url: str = "http://localhost:5000"):
        self.api_key = api_key
        self.claude_endpoint = "https://api.anthropic.com/v1/messages"
        self.backend_url = backend_url
        self.conversation_history = []
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt for Claude"""
        return """You are an intelligent audience segmentation assistant that helps users create targeted audience groups based on demographic, behavioral, financial, and psychographic attributes.

## Your Capabilities

You have access to the following tools through the backend API:

1. **variable_selector**: Analyzes user requirements and selects relevant variables from the available dataset
2. **data_retriever**: Fetches data values for selected variables
3. **cluster_analyzer**: Runs K-Medians clustering with size constraints (5-10% per group)
4. **analyze**: Complete analysis combining variable selection and clustering

## Workflow Process

When a user provides an audience description, follow these steps:

1. **Understand Requirements**: Parse the user's natural language request to identify:
   - Demographic criteria (age, location, gender, etc.)
   - Behavioral patterns (purchase history, engagement, etc.)
   - Financial attributes (income, spending, credit, etc.)
   - Psychographic traits (lifestyle, values, interests, etc.)

2. **Variable Selection**:
   - Call the backend API to analyze the request
   - Present selected variables to the user for confirmation
   - Allow iterative refinement based on user feedback

3. **Clustering & Results**:
   - Apply clustering to create groups with size constraints
   - Present results showing groups with their characteristics
   - Provide actionable insights about each segment

## Communication Style

- Be conversational and helpful
- Explain technical concepts in simple terms
- Confirm understanding at each step
- Provide clear summaries of actions taken
- Ask clarifying questions when requirements are ambiguous

## Available Variables

The system has access to various variable types including:
- Demographics: Age ranges, location types, PRIZM segments
- Financial: Income levels, disposable income
- Behavioral: Purchase frequency, online shopping, media consumption
- Psychographic: Environmental consciousness, technology adoption, lifestyle preferences"""
    
    async def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """
        Process user request through Claude and backend API
        """
        # Add user input to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get Claude's interpretation
        claude_response = await self._get_claude_response()
        
        # Check if we should make backend API calls
        if self._should_analyze(claude_response):
            # Make backend API call
            api_response = await self._call_backend_api(user_input)
            
            # Format the results
            formatted_response = self._format_api_response(api_response)
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": formatted_response
            })
            
            return {
                "message": formatted_response,
                "api_response": api_response,
                "status": "success"
            }
        else:
            # Just return Claude's response
            self.conversation_history.append({
                "role": "assistant",
                "content": claude_response
            })
            
            return {
                "message": claude_response,
                "status": "success"
            }
    
    async def _get_claude_response(self) -> str:
        """Get response from Claude API"""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Use environment variables for cost-efficient development
        model = os.getenv('CLAUDE_MODEL', 'claude-3-haiku-20240307')
        max_tokens = int(os.getenv('CLAUDE_MAX_TOKENS', '500'))
        
        data = {
            "model": model,
            "messages": self.conversation_history,
            "system": self.system_prompt,
            "max_tokens": max_tokens
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.claude_endpoint, headers=headers, json=data) as response:
                result = await response.json()
                return result["content"][0]["text"]
    
    def _should_analyze(self, claude_response: str) -> bool:
        """Determine if we should make backend API calls"""
        # Check if Claude's response indicates we should proceed with analysis
        analyze_indicators = [
            "let me analyze",
            "i'll help you find",
            "let's create",
            "i'll segment",
            "searching for"
        ]
        
        response_lower = claude_response.lower()
        return any(indicator in response_lower for indicator in analyze_indicators)
    
    async def _call_backend_api(self, user_request: str) -> Dict[str, Any]:
        """Call the backend API for audience analysis"""
        endpoint = f"{self.backend_url}/api/analyze"
        
        data = {
            "user_request": user_request,
            "auto_select": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=data) as response:
                return await response.json()
    
    def _format_api_response(self, api_response: Dict[str, Any]) -> str:
        """Format API response into user-friendly message"""
        if api_response.get("status") != "success":
            return f"I encountered an error: {api_response.get('error', 'Unknown error')}"
        
        profiles = api_response.get("profiles", {})
        selected_vars = api_response.get("selected_variables", [])
        
        # Build response message
        message = f"I've successfully created {len(profiles)} audience segments based on your requirements.\n\n"
        
        message += f"**Variables Used ({len(selected_vars)}):**\n"
        for var in selected_vars[:5]:  # Show first 5
            message += f"- {var}\n"
        if len(selected_vars) > 5:
            message += f"- ... and {len(selected_vars) - 5} more\n"
        
        message += "\n**Audience Segments:**\n\n"
        
        for group_id, profile in profiles.items():
            message += f"**Group {int(group_id) + 1}** ({profile['percentage']}% - {profile['size']} records)\n"
            
            # Show top characteristics
            message += "Key Characteristics:\n"
            char_count = 0
            for var_code, stats in profile.get('characteristics', {}).items():
                if char_count >= 3:
                    break
                if 'dominant_value' in stats:
                    message += f"- {var_code}: {stats['dominant_value']} ({stats['percentage']:.1f}%)\n"
                elif 'mean' in stats:
                    message += f"- {var_code}: Average {stats['mean']:.1f}\n"
                char_count += 1
            
            message += "\n"
        
        message += "Would you like me to refine these segments or export the results?"
        
        return message


class NLWebInterface:
    """
    NLWeb interface for browser-based interaction
    """
    
    def __init__(self, claude_api_key: str):
        self.assistant = ClaudeAudienceAssistant(claude_api_key)
        
    def get_javascript_integration(self) -> str:
        """Get JavaScript code for NLWeb integration"""
        return '''
// NLWeb Integration for Audience Builder

class AudienceBuilderChat {
    constructor(apiKey, backendUrl = 'http://localhost:5000') {
        this.apiKey = apiKey;
        this.backendUrl = backendUrl;
        this.conversationHistory = [];
    }
    
    async sendMessage(userInput) {
        try {
            // Call the Python backend which integrates with Claude
            const response = await fetch(`${this.backendUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userInput,
                    conversation_history: this.conversationHistory
                })
            });
            
            const result = await response.json();
            
            // Update conversation history
            this.conversationHistory.push({
                role: 'user',
                content: userInput
            });
            
            this.conversationHistory.push({
                role: 'assistant',
                content: result.message
            });
            
            return result;
            
        } catch (error) {
            console.error('Error:', error);
            return {
                error: 'Failed to process request',
                details: error.message
            };
        }
    }
    
    displayResults(results) {
        // Format and display the results in HTML
        if (results.api_response && results.api_response.profiles) {
            const profiles = results.api_response.profiles;
            let html = '<div class="audience-results">';
            
            for (const [groupId, profile] of Object.entries(profiles)) {
                html += `
                    <div class="audience-group">
                        <h3>Group ${parseInt(groupId) + 1}</h3>
                        <p>Size: ${profile.size} (${profile.percentage}%)</p>
                        <div class="characteristics">
                            <!-- Add characteristics here -->
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
            return html;
        }
        
        return `<div class="message">${results.message}</div>`;
    }
}

// Initialize the chat interface
const audienceChat = new AudienceBuilderChat('${this.apiKey}');
'''


# Demo usage
async def demo_claude_integration():
    """Demonstrate Claude integration"""
    # Load API key from secrets
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    
    assistant = ClaudeAudienceAssistant(api_key)
    
    # Test requests
    test_requests = [
        "I need to find environmentally conscious millennials with high disposable income in urban areas",
        "Show me tech-savvy professionals who are early adopters",
        "Find families with children interested in organic products"
    ]
    
    print("CLAUDE INTEGRATION DEMO")
    print("="*80)
    
    for request in test_requests[:1]:  # Test first request
        print(f"\nUser: {request}")
        print("\nProcessing...")
        
        try:
            response = await assistant.process_user_request(request)
            print(f"\nAssistant: {response['message']}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n" + "-"*80)


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_claude_integration())