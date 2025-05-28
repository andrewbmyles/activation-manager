export default function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { action } = req.body;

  if (action === 'process') {
    res.status(200).json({
      status: 'variables_suggested',
      suggested_variables: {
        demographic: [
          {
            code: 'age_range',
            description: 'Age Range',
            type: 'demographic',
            relevance_score: 0.9,
            category: 'Demographics'
          },
          {
            code: 'income_level',
            description: 'Household Income',
            type: 'demographic',
            relevance_score: 0.85,
            category: 'Demographics'
          }
        ],
        behavioral: [
          {
            code: 'purchase_freq',
            description: 'Purchase Frequency',
            type: 'behavioral',
            relevance_score: 0.75,
            category: 'Behavioral'
          }
        ]
      }
    });
  } else if (action === 'confirm') {
    const segments = [];
    for (let i = 0; i < 4; i++) {
      segments.push({
        group_id: i,
        size: Math.floor(Math.random() * 40000) + 10000,
        size_percentage: Math.random() * 5 + 5,
        name: `Segment ${i + 1}`,
        dominantTraits: ['High Value', 'Engaged', 'Urban']
      });
    }

    res.status(200).json({
      status: 'complete',
      segments: segments,
      audience_id: `aud_${Math.floor(Math.random() * 9000) + 1000}`
    });
  } else {
    res.status(400).json({
      status: 'error',
      message: 'Unknown action'
    });
  }
}