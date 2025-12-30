"""
Edge TTS Server for IELTS Speaking Test
Deploy to Railway, Render, or any Python hosting

Usage:
    pip install -r requirements.txt
    python server.py
"""

from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import edge_tts
import asyncio
import io
import os

app = Flask(__name__)
CORS(app)  # Allow requests from your frontend

# Available voices for IELTS examiner
VOICES = {
    'female_british': 'en-GB-SoniaNeural',      # Primary: British female examiner
    'female_british_alt': 'en-GB-LibbyNeural',  # Alternative British female
    'male_british': 'en-GB-RyanNeural',         # British male examiner
    'female_australian': 'en-AU-NatashaNeural', # Australian accent
    'female_american': 'en-US-JennyNeural',     # American accent
}

# Default voice
DEFAULT_VOICE = 'en-GB-SoniaNeural'


async def generate_speech(text: str, voice: str) -> bytes:
    """Generate speech audio from text using Edge TTS"""
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    
    return audio_data


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'edge-tts-server',
        'voices': list(VOICES.keys())
    })


@app.route('/voices', methods=['GET'])
def list_voices():
    """List available voices"""
    return jsonify({
        'voices': VOICES,
        'default': DEFAULT_VOICE
    })


@app.route('/tts', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech
    
    Request JSON:
    {
        "text": "Hello, welcome to the speaking test",
        "voice": "female_british" (optional, defaults to female_british)
    }
    
    Returns: MP3 audio file
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing "text" field'}), 400
        
        text = data['text']
        
        # Get voice (support both short names and full voice IDs)
        voice_key = data.get('voice', 'female_british')
        voice = VOICES.get(voice_key, voice_key)
        
        # Validate voice exists in our list or is a valid Edge TTS voice
        if not voice.startswith('en-'):
            voice = DEFAULT_VOICE
        
        # Generate audio
        audio_data = asyncio.run(generate_speech(text, voice))
        
        # Return as MP3
        return Response(
            audio_data,
            mimetype='audio/mpeg',
            headers={
                'Content-Disposition': 'inline; filename="speech.mp3"',
                'Cache-Control': 'no-cache'
            }
        )
    
    except Exception as e:
        print(f"TTS Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/tts/stream', methods=['POST'])
def text_to_speech_stream():
    """
    Stream text to speech (for longer texts)
    Returns chunked audio data
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing "text" field'}), 400
        
        text = data['text']
        voice_key = data.get('voice', 'female_british')
        voice = VOICES.get(voice_key, voice_key)
        
        if not voice.startswith('en-'):
            voice = DEFAULT_VOICE
        
        def generate():
            async def stream_audio():
                communicate = edge_tts.Communicate(text, voice)
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        yield chunk["data"]
            
            # Run async generator in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async_gen = stream_audio()
            try:
                while True:
                    chunk = loop.run_until_complete(async_gen.__anext__())
                    yield chunk
            except StopAsyncIteration:
                pass
            finally:
                loop.close()
        
        return Response(
            generate(),
            mimetype='audio/mpeg',
            headers={
                'Content-Disposition': 'inline; filename="speech.mp3"',
                'Transfer-Encoding': 'chunked'
            }
        )
    
    except Exception as e:
        print(f"TTS Stream Error: {e}")
        return jsonify({'error': str(e)}), 500


# Simple GET endpoint for testing
@app.route('/tts/test', methods=['GET'])
def test_tts():
    """Test endpoint - generates a sample audio"""
    text = request.args.get('text', 'Hello, this is a test of the Edge TTS system.')
    voice = request.args.get('voice', DEFAULT_VOICE)
    
    try:
        audio_data = asyncio.run(generate_speech(text, voice))
        return Response(
            audio_data,
            mimetype='audio/mpeg'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print(f"🎙️ Edge TTS Server starting on port {port}")
    print(f"📋 Available voices: {list(VOICES.keys())}")
    print(f"🔗 Test URL: http://localhost:{port}/tts/test")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
