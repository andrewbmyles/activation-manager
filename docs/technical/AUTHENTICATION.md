# Authentication Implementation Guide

## Overview

The Activation Manager uses session-based authentication with secure password hashing. This document details the implementation, security measures, and usage guidelines.

## Authentication Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│   Frontend  │────▶│   Backend   │
│   (User)    │◀────│   (React)   │◀────│   (Flask)   │
└─────────────┘     └─────────────┘     └─────────────┘
      │                    │                    │
      │                    │                    │
      ▼                    ▼                    ▼
   Cookies            State Mgmt          Session Store
```

## Backend Implementation

### Core Components

#### 1. User Storage (simple-backend/app.py)
```python
from werkzeug.security import check_password_hash, generate_password_hash

# Simple user storage (in production, use database)
USERS = {
    'andrew@tobermory.ai': generate_password_hash('admin')
}
```

#### 2. Session Configuration
```python
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# CORS configuration with credentials
CORS(app, 
    supports_credentials=True, 
    origins=['https://tobermory.ai', 'http://localhost:3000']
)
```

#### 3. Authentication Decorator
```python
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

### API Endpoints

#### Login Endpoint
```python
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if email in USERS and check_password_hash(USERS[email], password):
        session['user'] = email
        return jsonify({
            'success': True,
            'user': email,
            'message': 'Login successful'
        })
    
    return jsonify({
        'success': False,
        'message': 'Invalid credentials'
    }), 401
```

#### Logout Endpoint
```python
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True, 'message': 'Logout successful'})
```

#### Status Check Endpoint
```python
@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    if 'user' in session:
        return jsonify({
            'authenticated': True,
            'user': session['user']
        })
    return jsonify({
        'authenticated': False
    })
```

### Protected Routes

All API endpoints that require authentication use the `@login_required` decorator:

```python
@app.route('/api/audiences', methods=['GET', 'POST'])
@login_required
def handle_audiences():
    # Only accessible to authenticated users
    # ...
```

## Frontend Implementation

### Authentication State Management (App.tsx)

```typescript
import React, { useState, useEffect } from 'react';

function App() {
  const [user, setUser] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/auth/status`, {
        credentials: 'include',
      });
      const data = await response.json();
      if (data.authenticated) {
        setUser(data.user);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userEmail: string) => {
    setUser(userEmail);
  };

  const handleLogout = async () => {
    try {
      await fetch(`${API_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Conditional rendering based on auth state
  return (
    <>
      {!user ? (
        <Login onLogin={handleLogin} />
      ) : (
        <AuthenticatedApp user={user} onLogout={handleLogout} />
      )}
    </>
  );
}
```

### Login Component (Login.tsx)

```typescript
interface LoginProps {
  onLogin: (user: string) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        onLogin(data.user);
        navigate('/');
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Login form UI */}
    </form>
  );
};
```

### Protected API Calls

All authenticated API calls must include credentials:

```typescript
// Example: Fetch audiences
const fetchAudiences = async () => {
  const response = await fetch(`${API_URL}/api/audiences`, {
    credentials: 'include', // Important: includes cookies
  });
  
  if (response.status === 401) {
    // Handle unauthorized - redirect to login
    handleLogout();
    return;
  }
  
  return response.json();
};
```

## Security Measures

### 1. Password Security
- **Hashing**: Werkzeug's `generate_password_hash()` with default settings
- **Algorithm**: PBKDF2 with SHA256
- **Salt**: Automatically generated and stored with hash
- **Iterations**: Default 600,000 (configurable)

### 2. Session Security
- **Storage**: Server-side only
- **Identifier**: Cryptographically secure random token
- **Cookie Flags**:
  - `HttpOnly`: Prevents JavaScript access
  - `Secure`: HTTPS only (in production)
  - `SameSite`: CSRF protection

### 3. CORS Configuration
```python
CORS(app, 
    supports_credentials=True,
    origins=[
        'https://tobermory.ai',
        'https://www.tobermory.ai',
        'http://localhost:3000'  # Development only
    ],
    allow_headers=['Content-Type'],
    methods=['GET', 'POST', 'OPTIONS']
)
```

### 4. Environment Variables
```bash
# Production deployment
SECRET_KEY=$(openssl rand -hex 32)
```

## User Management

### Adding New Users

Currently, users are hardcoded in the application. To add a new user:

1. Edit `simple-backend/app.py`:
```python
USERS = {
    'andrew@tobermory.ai': generate_password_hash('admin'),
    'newuser@example.com': generate_password_hash('their_password')
}
```

2. Redeploy the backend:
```bash
cd simple-backend
gcloud run deploy audience-manager-api --source .
```

### Future Improvements

For production, implement:
1. **Database Storage**: Store users in Cloud SQL
2. **Registration Flow**: Allow user self-registration
3. **Password Reset**: Email-based password recovery
4. **Two-Factor Authentication**: Additional security layer
5. **OAuth Integration**: Google/GitHub login

## Session Management

### Session Lifecycle
1. **Creation**: On successful login
2. **Duration**: 24 hours (default)
3. **Renewal**: Activity extends session
4. **Termination**: Explicit logout or timeout

### Session Storage
Currently using Flask's default session storage (client-side encrypted cookies).

For production, consider:
- Redis for centralized session storage
- Cloud Memorystore for managed Redis
- Firestore for serverless session storage

## Error Handling

### Common Authentication Errors

#### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```
**Cause**: Missing or invalid session
**Solution**: Redirect to login

#### 403 Forbidden
```json
{
  "error": "Access denied"
}
```
**Cause**: Valid session but insufficient permissions
**Solution**: Show error message

#### Invalid Credentials
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```
**Cause**: Wrong email/password
**Solution**: Show error, clear password field

## Testing Authentication

### Manual Testing
```bash
# Test login
curl -X POST https://api.tobermory.ai/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"andrew@tobermory.ai","password":"admin"}' \
  -c cookies.txt

# Test authenticated endpoint
curl https://api.tobermory.ai/api/audiences \
  -b cookies.txt

# Test logout
curl -X POST https://api.tobermory.ai/api/auth/logout \
  -b cookies.txt
```

### Automated Testing
```python
def test_authentication():
    # Test successful login
    response = client.post('/api/auth/login', 
        json={'email': 'test@example.com', 'password': 'test'})
    assert response.status_code == 200
    assert response.json['success'] == True
    
    # Test protected endpoint
    response = client.get('/api/audiences')
    assert response.status_code == 200
    
    # Test logout
    response = client.post('/api/auth/logout')
    assert response.status_code == 200
    
    # Test protected endpoint after logout
    response = client.get('/api/audiences')
    assert response.status_code == 401
```

## Deployment Considerations

### Environment Setup
```bash
# Set secret key during deployment
gcloud run deploy audience-manager-api \
    --set-env-vars "SECRET_KEY=$(openssl rand -hex 32)"
```

### Security Headers
Add these headers for production:
```python
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response
```

### Rate Limiting
Implement rate limiting to prevent brute force:
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # ... login logic
```

## Monitoring

### Key Metrics
- Failed login attempts
- Session duration
- Active sessions
- Authentication errors

### Logging
```python
import logging

logger = logging.getLogger(__name__)

@app.route('/api/auth/login', methods=['POST'])
def login():
    email = request.json.get('email')
    # ... authentication logic
    
    if success:
        logger.info(f"Successful login: {email}")
    else:
        logger.warning(f"Failed login attempt: {email}")
```

### Alerts
Set up alerts for:
- Multiple failed login attempts
- Unusual session patterns
- Authentication service errors