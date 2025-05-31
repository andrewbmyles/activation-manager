"""
Variable Picker Tool - Standalone NL interface for variable selection
Follows the same workflow as audience builder but stops after variable confirmation
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from .variable_selector import VariableSelector

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
        
        # Initialize variable selector
        try:
            self.selector = VariableSelector(openai_api_key=openai_api_key)
            logger.info(f"Initialized variable selector with {len(self.selector.variables)} variables")
            
            # Check if embeddings are available
            if self.selector.embeddings is None or self.selector.openai_client is None:
                self.use_embeddings = False
                logger.warning("Embeddings not available, using keyword search only")
        except Exception as e:
            logger.error(f"Failed to initialize variable selector: {e}")
            raise
    
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
        
        # Get variables using unified search
        try:
            # Search with both keyword and semantic methods
            search_results = self.selector.search(
                query=nl_query,
                top_k=top_k,
                use_semantic=self.use_embeddings,
                use_keyword=True
            )
            
            # Format results to match expected structure
            suggested_variables = []
            for result in search_results:
                formatted_result = {
                    'code': result.get('code', result.get('VarId', '')),
                    'description': result.get('description', result.get('Description', '')),
                    'category': result.get('category', result.get('Category', '')),
                    'type': result.get('type', result.get('Theme', 'general')),
                    'score': result.get('score', 0),
                    'search_method': result.get('match_type', 'unknown'),
                    'keywords': result.get('keywords', []),
                    'product': result.get('product', result.get('ProductName', '')),
                    'context': result.get('context', result.get('Context', ''))
                }
                suggested_variables.append(formatted_result)
                
        except Exception as e:
            logger.error(f"Error in variable search: {e}")
            suggested_variables = []
        
        # Update session
        session.suggested_variables = suggested_variables
        
        # Prepare response
        search_methods = ['keyword']
        if self.use_embeddings and any(v.get('search_method') == 'semantic' for v in suggested_variables):
            search_methods.append('semantic')
        
        response = {
            'session_id': session_id,
            'query': nl_query,
            'suggested_count': len(suggested_variables),
            'variables': suggested_variables,
            'search_methods_used': search_methods,
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