// Direct implementation for start_session endpoint - optimized for speed
export default async function handler(req, res) {
  // Fast path for OPTIONS
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }

  // Set CORS headers immediately
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  // Add cache control to prevent stale responses
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Generate session ID as fast as possible
  const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  // Return immediately - no async operations needed
  return res.status(200).json({
    session_id: sessionId,
    message: 'Session started. Please describe your target audience in natural language.',
    status: 'ready',
    features: {
      enhanced_variable_selection: true,
      prizm_analysis: true,
      metadata_integration: true
    }
  });
}