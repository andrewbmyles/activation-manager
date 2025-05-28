export default function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const { audienceId } = req.query;

  // Generate sample CSV data
  let csvContent = 'segment_id,segment_name,size,percentage\n';
  for (let i = 0; i < 4; i++) {
    csvContent += `${i},Segment_${i + 1},${Math.floor(Math.random() * 40000) + 10000},${(Math.random() * 5 + 5).toFixed(2)}\n`;
  }

  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', `attachment; filename=audience_${audienceId}.csv`);
  res.status(200).send(csvContent);
}