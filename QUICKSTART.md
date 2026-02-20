# Quick Start Guide

Get your Research Agent up and running in minutes!

## Local Development

### 1. Backend Setup

```bash
# Navigate to agent directory
cd agent

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the API server
python start_server.py
# Or: python -m uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 3. Test It Out!

1. Open `http://localhost:3000` in your browser
2. Enter a research topic (e.g., "AI in healthcare")
3. Click "Research"
4. Wait for results!

## CLI Mode

If you prefer the command line:

```bash
cd agent
python main.py
```

Then enter research topics when prompted.

## Getting Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file

## Troubleshooting

### Backend won't start
- Check that `GEMINI_API_KEY` is set in `.env`
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.9+ required)

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Check browser console for CORS errors

### Import errors
- Make sure you're in the correct directory
- Verify all Python packages are installed
- Try: `pip install -r requirements.txt --upgrade`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Explore the code to understand how it works!
