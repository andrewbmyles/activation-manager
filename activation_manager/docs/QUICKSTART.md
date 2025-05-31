# Audience Builder - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.8+
- Your Anthropic API key (already in Secrets.md)
- Synthetic data file (already provided)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Flask API Server
```bash
python audience_api.py
```
The API will start on http://localhost:5000

### Step 3: Test the System
In a new terminal:
```bash
python test_audience_builder.py
```

### Step 4: Launch Web Interface
Open `NLWeb/static/audience_builder.html` in your browser or visit:
http://localhost:8000/static/audience_builder.html (if NLWeb is running)

## 🎯 Try These Examples

1. **Environmentally Conscious Millennials**
   ```
   Find environmentally conscious millennials with high disposable income in urban areas
   ```

2. **Tech-Savvy Professionals**
   ```
   Tech-savvy urban professionals interested in premium brands
   ```

3. **Family Segments**
   ```
   Young families with children who buy organic products
   ```

## 📊 What You'll Get

For each query, the system will:
1. **Analyze** your natural language request
2. **Select** relevant variables from the data
3. **Create** 5-10 balanced audience segments
4. **Display** key characteristics of each segment
5. **Visualize** the segments with interactive charts
6. **Export** results as CSV

## 🔧 Advanced Usage

### Using the API Directly

```bash
# Get variable suggestions
curl -X POST http://localhost:5000/api/variable_selector \
  -H "Content-Type: application/json" \
  -d '{"user_request": "millennials interested in sustainability"}'

# Run complete analysis
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"user_request": "urban professionals", "auto_select": true}'
```

### Integrating with NLWeb

1. Add to `NLWeb/code/webserver/WebServer.py`:
```python
elif path.startswith("/nlweb/audience"):
    from core.audienceHandler import AudienceHandler
    handler = AudienceHandler(query_params, SendChunkWrapper(send_chunk))
    await handler.runQuery()
    return
```

2. Start NLWeb server:
```bash
python NLWeb/code/app-file.py
```

3. Access at: http://localhost:8000/static/audience_builder.html

### Using Claude Integration

```python
from claude_nlweb_integration import ClaudeAudienceAssistant

assistant = ClaudeAudienceAssistant(api_key)
response = await assistant.process_user_request(
    "Find eco-conscious consumers with high income"
)
```

## 📈 Understanding the Results

Each segment includes:
- **Size**: Number of records (5-10% of total)
- **Key Variables**: Most distinctive characteristics
- **Demographics**: Age, location, income patterns
- **Behaviors**: Purchase patterns, preferences
- **Psychographics**: Values, lifestyle indicators

## 🛠️ Troubleshooting

### Flask API won't start
- Check if port 5000 is already in use
- Verify Python dependencies are installed

### No segments created
- Check if synthetic data file exists
- Verify variable codes match your data

### Claude integration fails
- Confirm API key in Secrets.md
- Check internet connection

## 📚 Next Steps

1. **Customize Variables**: Edit `variable_catalog.py` to match your data
2. **Adjust Constraints**: Modify segment size limits in `audience_builder.py`
3. **Add Features**: Extend the visualization options
4. **Production Deploy**: Set up proper authentication and scaling

## 🎉 You're Ready!

Start building audience segments with natural language queries. The system handles all the complexity - just describe who you're looking for!