# Fix Variable Picker Search Issue

## Problem
The Variable Picker search is not working because the backend server is not running.

## Solution

### 1. Start the Backend Server

Open a terminal and run:
```bash
cd "/Users/myles/Documents/Activation Manager"
./start-backend.sh
```

Or manually:
```bash
cd "/Users/myles/Documents/Activation Manager"
python3 main.py
```

The backend will start on port 8080.

### 2. Start the Frontend (if not already running)

In a separate terminal:
```bash
cd "/Users/myles/Documents/Activation Manager/audience-manager"
npm start
```

The frontend will start on port 3000.

### 3. Access Variable Picker

1. Go to http://localhost:3000
2. Login with password: demo2024
3. Click "Natural Language Multi-Variate Audience Builder" in the sidebar
4. Enter your search query and click Search

## Technical Details

- **Backend**: Flask server running on port 8080 (main.py)
- **Frontend**: React app running on port 3000 with proxy to 8080
- **API Endpoint**: `/api/variable-picker/start`
- **CORS**: Enabled for all origins

## Troubleshooting

### If search still doesn't work:

1. **Check backend is running**: 
   ```bash
   curl http://localhost:8080/api/health
   ```

2. **Test Variable Picker API directly**:
   ```bash
   python3 test_variable_picker_backend.py
   ```

3. **Check browser console** for any errors (F12 → Console tab)

4. **Check network tab** to see if API calls are being made

### Common Issues:

- **Port 8080 already in use**: Kill the process using the port or change the port in main.py
- **Module not found errors**: Make sure you're in the project root directory
- **CORS errors**: Should not occur as CORS is configured to allow all origins

## Development vs Production

- In development: Both frontend and backend run locally
- In production: Both are deployed to Google App Engine

The current setup uses mock data if embeddings are not loaded, so search should work even without the full dataset.