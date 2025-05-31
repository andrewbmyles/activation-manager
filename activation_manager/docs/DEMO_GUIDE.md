# Activation Manager Demo Guide

## 🚀 Everything is Ready!

Both servers are running and ready for your demo:

### 1. **React Frontend**: http://localhost:3000
- The Audience Manager interface is live
- Natural Language mode toggle is available in the top-right

### 2. **Unified API**: http://localhost:5001
- Handles both manual and NL audience building
- Enhanced tools are integrated

## Demo Walkthrough

### Step 1: Access the Application
1. Open your browser to http://localhost:3000
2. You'll see the Audience Manager dashboard

### Step 2: Try Natural Language Mode
1. Click the "Natural Language" toggle in the top-right corner
2. The interface will switch to the NL workflow view

### Step 3: Create an Audience Using Natural Language
1. In the text input, try prompts like:
   - "Find environmentally conscious millennials with high disposable income in urban areas"
   - "Target tech-savvy families with children who shop online frequently"
   - "Identify affluent seniors interested in travel and luxury products"

2. The system will:
   - Analyze your request using the enhanced variable selector
   - Show relevant variables from your metadata files (Opticks, PRIZM, SocialValues)
   - Allow you to confirm or adjust the selection

3. After confirmation:
   - Data retrieval begins
   - K-Medians clustering runs with 5-10% constraints
   - Results show with PRIZM segment analysis

### Step 4: View Results
- Each segment shows:
  - Size and percentage
  - Key characteristics
  - PRIZM profile (if available)
  - Marketing implications

### Step 5: Export Data
- Click export to download the segmented audience
- Available in CSV or JSON format

## Key Features Demonstrated

### 1. **Enhanced Variable Selection**
- Uses your actual metadata files
- Intelligent fuzzy matching
- Category-based relevance scoring

### 2. **PRIZM Integration**
- Rich segment descriptions
- Demographic and behavioral insights
- Marketing recommendations

### 3. **Constraint Satisfaction**
- All groups maintain 5-10% size
- Balanced segment distribution

### 4. **Seamless Workflow**
- Natural language input
- Interactive confirmation
- Real-time processing

## Technical Details

### Components Running:
- **Frontend**: React TypeScript app with Tailwind CSS
- **Backend**: Flask API with async support
- **Database**: SQLite for persistence
- **Tools**: Enhanced variable selector, PRIZM analyzer, K-Medians clustering

### Data Sources:
- Synthetic consumer data (1000 records)
- Variable metadata from CSV/Excel files
- PRIZM segment profiles

## Troubleshooting

If you encounter issues:

1. **Check API Health**: 
   ```bash
   curl http://localhost:5001/api/health
   ```

2. **View API Logs**:
   ```bash
   tail -f "/Users/myles/Documents/Activation Manager/api_server.log"
   ```

3. **Restart Services**:
   ```bash
   # Kill existing processes
   pkill -f "python.*unified_api"
   
   # Restart API
   cd "/Users/myles/Documents/Activation Manager"
   python unified_api.py &
   ```

## Next Steps After Demo

1. Connect to production data sources
2. Add real Anthropic API key for Claude integration
3. Deploy to cloud infrastructure
4. Add user authentication
5. Implement feedback collection

The demo is ready to showcase the power of natural language audience building!