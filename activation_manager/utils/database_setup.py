"""
SQLite Database Setup for Audience Builder Workflow
Cost-effective solution for demo purposes
"""

import sqlite3
import json
from datetime import datetime
import os

# Database file location
DB_PATH = os.path.join(os.path.dirname(__file__), 'audience_builder.db')

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Workflow states table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflow_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_prompt TEXT,
            workflow_stage TEXT,
            suggested_variables TEXT,
            confirmed_variables TEXT,
            data_path TEXT,
            results_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Audience segments table (integrates with existing audiences)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audience_segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audience_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            user_prompt TEXT,
            variables_used TEXT,
            segment_data TEXT,
            constraints_met BOOLEAN,
            total_records INTEGER,
            num_groups INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Variable usage analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS variable_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            variable_code TEXT NOT NULL,
            variable_name TEXT,
            usage_count INTEGER DEFAULT 0,
            last_used TIMESTAMP,
            success_rate REAL
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON workflow_states(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audience_id ON audience_segments(audience_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_variable_code ON variable_usage(variable_code)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at: {DB_PATH}")


class WorkflowDatabase:
    """Database interface for workflow persistence"""
    
    def __init__(self):
        self.db_path = DB_PATH
        if not os.path.exists(self.db_path):
            init_database()
    
    def save_workflow_state(self, session_id: str, state: dict) -> bool:
        """Save workflow state to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO workflow_states 
                (session_id, user_prompt, workflow_stage, suggested_variables, 
                 confirmed_variables, data_path, results_path, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                state.get('user_prompt', ''),
                state.get('workflow_stage', 'initial'),
                json.dumps(state.get('suggested_variables', [])),
                json.dumps(state.get('confirmed_variables', [])),
                state.get('data_path', ''),
                state.get('results_path', ''),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving workflow state: {e}")
            return False
    
    def get_workflow_state(self, session_id: str) -> dict:
        """Retrieve workflow state from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_prompt, workflow_stage, suggested_variables, 
                       confirmed_variables, data_path, results_path
                FROM workflow_states
                WHERE session_id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'user_prompt': row[0],
                    'workflow_stage': row[1],
                    'suggested_variables': json.loads(row[2]),
                    'confirmed_variables': json.loads(row[3]),
                    'data_path': row[4],
                    'results_path': row[5]
                }
            return {}
            
        except Exception as e:
            print(f"Error retrieving workflow state: {e}")
            return {}
    
    def save_audience_segment(self, audience_data: dict) -> str:
        """Save audience segment results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            audience_id = f"aud_{int(datetime.now().timestamp())}"
            
            cursor.execute('''
                INSERT INTO audience_segments 
                (audience_id, name, description, user_prompt, variables_used,
                 segment_data, constraints_met, total_records, num_groups)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                audience_id,
                audience_data.get('name', 'Untitled Audience'),
                audience_data.get('description', ''),
                audience_data.get('user_prompt', ''),
                json.dumps(audience_data.get('variables_used', [])),
                json.dumps(audience_data.get('segment_data', {})),
                audience_data.get('constraints_met', True),
                audience_data.get('total_records', 0),
                audience_data.get('num_groups', 0)
            ))
            
            conn.commit()
            conn.close()
            
            return audience_id
            
        except Exception as e:
            print(f"Error saving audience segment: {e}")
            return ""
    
    def get_audience_segment(self, audience_id: str) -> dict:
        """Retrieve audience segment by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, description, user_prompt, variables_used,
                       segment_data, constraints_met, total_records, num_groups,
                       created_at
                FROM audience_segments
                WHERE audience_id = ?
            ''', (audience_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'audience_id': audience_id,
                    'name': row[0],
                    'description': row[1],
                    'user_prompt': row[2],
                    'variables_used': json.loads(row[3]),
                    'segment_data': json.loads(row[4]),
                    'constraints_met': row[5],
                    'total_records': row[6],
                    'num_groups': row[7],
                    'created_at': row[8]
                }
            return {}
            
        except Exception as e:
            print(f"Error retrieving audience segment: {e}")
            return {}
    
    def update_variable_usage(self, variable_code: str, variable_name: str, success: bool = True):
        """Track variable usage for analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if variable exists
            cursor.execute('SELECT usage_count, success_rate FROM variable_usage WHERE variable_code = ?', 
                         (variable_code,))
            row = cursor.fetchone()
            
            if row:
                # Update existing
                usage_count = row[0] + 1
                success_rate = ((row[1] * row[0]) + (1 if success else 0)) / usage_count
                
                cursor.execute('''
                    UPDATE variable_usage 
                    SET usage_count = ?, success_rate = ?, last_used = ?
                    WHERE variable_code = ?
                ''', (usage_count, success_rate, datetime.now(), variable_code))
            else:
                # Insert new
                cursor.execute('''
                    INSERT INTO variable_usage 
                    (variable_code, variable_name, usage_count, success_rate, last_used)
                    VALUES (?, ?, ?, ?, ?)
                ''', (variable_code, variable_name, 1, 1.0 if success else 0.0, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating variable usage: {e}")
    
    def get_popular_variables(self, limit: int = 10) -> list:
        """Get most frequently used variables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT variable_code, variable_name, usage_count, success_rate
                FROM variable_usage
                ORDER BY usage_count DESC, success_rate DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'code': row[0],
                    'name': row[1],
                    'usage_count': row[2],
                    'success_rate': row[3]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Error getting popular variables: {e}")
            return []


# Test the database
if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Test workflow database
    db = WorkflowDatabase()
    
    # Test saving workflow state
    test_state = {
        'user_prompt': 'Find millennials interested in green products',
        'workflow_stage': 'variable_selection',
        'suggested_variables': ['AGE_RANGE', 'GREEN_PURCHASES'],
        'confirmed_variables': ['AGE_RANGE']
    }
    
    session_id = 'test_session_123'
    if db.save_workflow_state(session_id, test_state):
        print("✅ Workflow state saved")
    
    # Test retrieving workflow state
    retrieved = db.get_workflow_state(session_id)
    print(f"✅ Retrieved state: {retrieved}")
    
    # Test saving audience segment
    audience_data = {
        'name': 'Green Millennials',
        'description': 'Environmentally conscious young adults',
        'user_prompt': 'Find millennials interested in green products',
        'variables_used': ['AGE_RANGE', 'GREEN_PURCHASES'],
        'total_records': 1000,
        'num_groups': 8,
        'constraints_met': True
    }
    
    audience_id = db.save_audience_segment(audience_data)
    print(f"✅ Audience saved with ID: {audience_id}")
    
    # Test variable usage tracking
    db.update_variable_usage('AGE_RANGE', 'Age Range Categories', True)
    db.update_variable_usage('GREEN_PURCHASES', 'Green Product Purchases', True)
    
    popular = db.get_popular_variables()
    print(f"✅ Popular variables: {popular}")