import base64
from io import BytesIO
from gtts import gTTS
import requests
import json

def speech_to_text(audio_file):
    """
    SIMPLIFIED VOICE PROCESSING
    Since speech_recognition has dependency issues, we'll use a different approach.
    In production, you could use:
    - Google Cloud Speech-to-Text API (free tier available)
    - Azure Speech Services (free tier available)  
    - Mozilla DeepSpeech (open source)
    - Or implement a custom solution
    
    For now, we'll return a placeholder and focus on Text-to-Speech which works reliably.
    """
    try:
        # For demonstration purposes, we'll simulate speech recognition
        # In a real application, you would integrate with a proper speech-to-text service
        
        # You can implement actual speech recognition by:
        # 1. Using Google Cloud Speech-to-Text (free tier available)
        # 2. Using Azure Cognitive Services Speech-to-Text (free tier available)
        # 3. Using Mozilla DeepSpeech (open source)
        
        # Placeholder implementation
        return "[Voice answer recorded - speech-to-text would convert this to text]"
        
    except Exception as e:
        return f"[Voice processing would happen here. Error: {str(e)}]"

def text_to_speech(text):
    """
    Convert text to speech using free gTTS (Google Text-to-Speech)
    This works reliably and doesn't have dependency issues
    """
    try:
        if not text or len(text.strip()) == 0:
            raise ValueError("No text provided for speech synthesis")
        
        # Limit text length to avoid very long processing
        if len(text) > 500:
            text = text[:500] + "..."
        
        print(f"🔊 Generating speech for: {text[:100]}...")
        
        # Create gTTS object with better parameters
        tts = gTTS(
            text=text, 
            lang='en', 
            slow=False,
            lang_check=True
        )
        
        # Save to bytes buffer
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # Convert to base64 for JSON response
        audio_base64 = base64.b64encode(audio_buffer.read()).decode('utf-8')
        
        print("🔊 Speech generated successfully")
        return audio_base64
        
    except Exception as e:
        print(f"🔊 TTS Error: {e}")
        raise Exception(f"Text-to-speech conversion failed: {str(e)}")

def get_voice_capabilities():
    """
    Return available voice capabilities
    """
    return {
        'text_to_speech': True,
        'speech_to_text': False,  # Disabled due to dependency issues
        'reason': 'Speech-to-text requires additional setup due to library dependencies',
        'alternative': 'Use text input mode for now, or implement cloud-based speech-to-text'
    }

# Test function
if __name__ == '__main__':
    print("🎯 Voice Processor Test")
    capabilities = get_voice_capabilities()
    print("Capabilities:", capabilities)
    
    # Test text-to-speech
    try:
        test_text = "Hello! This is a test of the text to speech system for your interview practice app."
        audio_data = text_to_speech(test_text)
        print("✅ Text-to-speech test: SUCCESS")
        print(f"🔊 Audio data length: {len(audio_data)} characters")
    except Exception as e:
        print(f"❌ Text-to-speech test: FAILED - {e}")