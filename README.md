# IELTS TTS Server

Simple Edge TTS server for high-quality text-to-speech in the IELTS Speaking test.

## Features

- **Free** - Uses Microsoft Edge TTS (no API costs!)
- **High Quality** - Neural voices identical to Azure TTS
- **Fast** - ~300ms latency for short phrases
- **British Accents** - Perfect for IELTS examiner simulation

## Quick Deploy

### Option 1: Railway (Recommended - $5/month, very easy)

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repo and the `tts-server` folder
4. Railway auto-detects Python and deploys!
5. Copy your URL (e.g., `https://your-app.railway.app`)

### Option 2: Render (Free tier available)

1. Go to [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repo
4. Set:
   - **Root Directory**: `tts-server`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn server:app --bind 0.0.0.0:$PORT`
5. Click "Create Web Service"
6. Copy your URL (e.g., `https://your-app.onrender.com`)

### Option 3: Run Locally (For testing)

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python server.py

# Test it
curl "http://localhost:5000/tts/test?text=Hello"
```

## API Endpoints

### POST /tts
Generate speech from text.

```javascript
// Request
fetch('https://your-server.com/tts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Hello, welcome to the speaking test.',
    voice: 'female_british'  // optional
  })
})
.then(res => res.blob())
.then(blob => {
  const audio = new Audio(URL.createObjectURL(blob));
  audio.play();
});
```

### GET /tts/test
Quick test endpoint.

```
https://your-server.com/tts/test?text=Hello&voice=en-GB-SoniaNeural
```

### GET /voices
List available voices.

### GET /health
Health check.

## Available Voices

| Key | Voice ID | Description |
|-----|----------|-------------|
| `female_british` | en-GB-SoniaNeural | British female (default) |
| `female_british_alt` | en-GB-LibbyNeural | British female (alternative) |
| `male_british` | en-GB-RyanNeural | British male |
| `female_australian` | en-AU-NatashaNeural | Australian female |
| `female_american` | en-US-JennyNeural | American female |

## Configure in Your App

After deploying, update your IELTS app's config:

```javascript
// In your frontend code
const TTS_SERVER_URL = 'https://your-server.railway.app';  // Your deployed URL
```

Or set in VoiceSystem.js:
```javascript
VoiceSystem.serverUrl = 'https://your-server.railway.app';
```

## Cost

| Platform | Cost | Notes |
|----------|------|-------|
| Railway | $5/month | Very reliable, easy setup |
| Render | Free tier | 750 hrs/month, may sleep |
| DigitalOcean | $4/month | Full control |

The TTS itself is **FREE** - you only pay for hosting!
