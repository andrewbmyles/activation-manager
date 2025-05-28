"""
Variable Picker Tool - Standalone NL interface for variable selection
Follows the same workflow as audience builder but stops after variable confirmation
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from .enhanced_variable_selector_v2 import EnhancedVariableSelectorV2
from .enhanced_variable_selector_v5 import EnhancedVariableSelectorV5

logger = logging.getLogger(__name__)

@dataclass
class VariablePickerSession:
    """Represents a variable picker session"""
    session_id: str
    created_at: datetime
    nl_query: str
    suggested_variables: List[Dict[str, Any]]
    confirmed_variables: List[Dict[str, Any]]
    status: str  # 'in_progress', 'confirmed', 'cancelled'
    metadata: Dict[str, Any]

class VariablePickerTool:
    """
    Standalone variable picker tool with NL interface
    """
    
    def __init__(self, use_embeddings: bool = True, openai_api_key: Optional[str] = None):
        """
        Initialize the variable picker tool
        
        Args:
            use_embeddings: Whether to use embeddings for semantic search
            openai_api_key: OpenAI API key for embeddings
        """
        self.use_embeddings = use_embeddings
        self.sessions = {}
        
        # Initialize variable selectors
        self.selector_v2 = EnhancedVariableSelectorV2(use_full_dataset=True)
        
        if use_embeddings and openai_api_key:
            try:
                self.selector_v5 = EnhancedVariableSelectorV5(openai_api_key=openai_api_key)
                logger.info("Initialized with embeddings support")
            except Exception as e:
                logger.warning(f"Failed to initialize embeddings: {e}")
                self.selector_v5 = None
                self.use_embeddings = False
        else:
            self.selector_v5 = None
            self.use_embeddings = False
    
    def start_session(self, session_id: str, nl_query: str) -> VariablePickerSession:
        """
        Start a new variable picker session
        
        Args:
            session_id: Unique session identifier
            nl_query: Natural language query from user
            
        Returns:
            VariablePickerSession object
        """
        # Create new session
        session = VariablePickerSession(
            session_id=session_id,
            created_at=datetime.now(),
            nl_query=nl_query,
            suggested_variables=[],
            confirmed_variables=[],
            status='in_progress',
            metadata={}
        )
        
        # Store session
        self.sessions[session_id] = session
        
        logger.info(f"Started variable picker session: {session_id}")
        return session
    
    def process_nl_query(self, session_id: str, nl_query: str, top_k: int = 20) -> Dict[str, Any]:
        """
        Process natural language query and return suggested variables
        
        Args:
            session_id: Session identifier
            nl_query: Natural language query
            top_k: Number of variables to return
            
        Returns:
            Dictionary with suggested variables and metadata
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        session.nl_query = nl_query
        
        # Get variables using both methods if available
        suggested_variables = []
        
        # Method 1: Enhanced keyword/TF-IDF search
        try:
            v2_results = self.selector_v2.analyze_request(nl_query, top_n=top_k)
            for result in v2_results:
                result['search_method'] = 'keyword'
                suggested_variables.append(result)
        except Exception as e:
            logger.error(f"Error in V2 search: {e}")
        
        # Method 2: Embeddings-based semantic search
        if self.use_embeddings and self.selector_v5:
            try:
                v5_results = self.selector_v5.search_variables(nl_query, k=top_k, use_embeddings=True)
                
                # Add V5 results that aren't duplicates
                existing_codes = {var.get('code', var.get('variable_id', '')) for var in suggested_variables}
                
                for result in v5_results:
                    var_id = result.get('variable_id', '')
                    if var_id and var_id not in existing_codes:
                        # Format V5 result to match V2 structure
                        formatted_result = {
                            'code': var_id,
                            'description': result.get('description', ''),
                            'category': result.get('category', ''),
                            'type': result.get('type', 'general'),
                            'score': result.get('score', 0),
                            'search_method': result.get('method', 'semantic'),
                            'keywords': result.get('keywords', [])
                        }
                        suggested_variables.append(formatted_result)
                        existing_codes.add(var_id)
            except Exception as e:
                logger.error(f"Error in V5 search: {e}")
        
        # Sort by score and limit to top_k
        suggested_variables.sort(key=lambda x: x.get('score', 0), reverse=True)
        suggested_variables = suggested_variables[:top_k]
        
        # Update session
        session.suggested_variables = suggested_variables
        
        # Prepare response
        response = {
            'session_id': session_id,
            'query': nl_query,
            'suggested_count': len(suggested_variables),
            'variables': suggested_variables,
            'search_methods_used': ['keyword'] + (['semantic'] if self.use_embeddings else []),
            'status': 'suggestions_ready'
        }
        
        return response
    
    def refine_search(self, session_id: str, refinement_query: str, 
                     exclude_codes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Refine the search based on user feedback
        
        Args:
            session_id: Session identifier
            refinement_query: Additional criteria or refinement
            exclude_codes: Variable codes to exclude from results
            
        Returns:
            Updated suggestions
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Combine original query with refinement
        combined_query = f"{session.nl_query} {refinement_query}"
        
        # Get new results
        response = self.process_nl_query(session_id, combined_query, top_k=30)
        
        # Filter out excluded codes if provided
        if exclude_codes:
            filtered_variables = []
            for var in response['variables']:
                if var.get('code') not in exclude_codes:
                    filtered_variables.append(var)
            response['variables'] = filtered_variables[:20]  # Limit to top 20
            response['suggested_count'] = len(response['variables'])
        
        response['refinement_applied'] = True
        return response
    
    def confirm_variables(self, session_id: str, 
                         confirmed_variable_codes: List[str]) -> Dict[str, Any]:
        """
        Confirm selected variables
        
        Args:
            session_id: Session identifier
            confirmed_variable_codes: List of confirmed variable codes
            
        Returns:
            Confirmation response with variable details
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Find full details for confirmed variables
        confirmed_variables = []
        for code in confirmed_variable_codes:
            # Look in suggested variables first
            for var in session.suggested_variables:
                if var.get('code') == code:
                    confirmed_variables.append(var)
                    break
        
        # Update session
        session.confirmed_variables = confirmed_variables
        session.status = 'confirmed'
        
        # Prepare response
        response = {
            'session_id': session_id,
            'status': 'confirmed',
            'confirmed_count': len(confirmed_variables),
            'confirmed_variables': confirmed_variables,
            'original_query': session.nl_query,
            'timestamp': datetime.now().isoformat()
        }
        
        return response
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of a session"""
        if session_id not in self.sessions:
            return {'error': f'Session {session_id} not found'}
        
        session = self.sessions[session_id]
        
        return {
            'session_id': session_id,
            'status': session.status,
            'created_at': session.created_at.isoformat(),
            'nl_query': session.nl_query,
            'suggested_count': len(session.suggested_variables),
            'confirmed_count': len(session.confirmed_variables),
            'confirmed_variables': session.confirmed_variables if session.status == 'confirmed' else []
        }
    
    def cancel_session(self, session_id: str) -> Dict[str, Any]:
        """Cancel a session"""
        if session_id not in self.sessions:
            return {'error': f'Session {session_id} not found'}
        
        session = self.sessions[session_id]
        session.status = 'cancelled'
        
        return {
            'session_id': session_id,
            'status': 'cancelled',
            'message': 'Session cancelled successfully'
        }
    
    def export_confirmed_variables(self, session_id: str, format: str = 'json') -> Any:
        """
        Export confirmed variables in specified format
        
        Args:
            session_id: Session identifier
            format: Export format ('json', 'csv', 'list')
            
        Returns:
            Exported data in requested format
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        if session.status != 'confirmed':
            raise ValueError(f"Session {session_id} has no confirmed variables")
        
        if format == 'json':
            return {
                'session_id': session_id,
                'query': session.nl_query,
                'confirmed_at': datetime.now().isoformat(),
                'variables': session.confirmed_variables
            }
        
        elif format == 'csv':
            # Return CSV-ready data
            csv_data = []
            for var in session.confirmed_variables:
                csv_data.append({
                    'code': var.get('code', ''),
                    'description': var.get('description', ''),
                    'category': var.get('category', ''),
                    'type': var.get('type', ''),
                    'score': var.get('score', 0)
                })
            return csv_data
        
        elif format == 'list':
            # Simple list of variable codes
            return [var.get('code', '') for var in session.confirmed_variables]
        
        else:
            raise ValueError(f"Unsupported format: {format}")