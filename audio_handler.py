"""
Audio Handler Module
Manages speech recognition (STT) and text-to-speech (TTS) functionality
"""

import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import os
import tempfile
from typing import Optional, Tuple
import time


class AudioHandler:
    """Handle audio input/output for interview system"""
    
    def __init__(self, use_gtts: bool = False):
        """
        Initialize audio handler
        
        Args:
            use_gtts: Use Google TTS instead of pyttsx3
        """
        self.recognizer = sr.Recognizer()
        self.use_gtts = use_gtts
        
        # Initialize TTS engine
        if not use_gtts:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)  # Speed of speech
                self.tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            except Exception as e:
                print(f"Error initializing pyttsx3: {e}")
                print("Falling back to gTTS")
                self.use_gtts = True
    
    def speak(self, text: str) -> bool:
        """
        Convert text to speech and play it
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.use_gtts:
                return self._speak_gtts(text)
            else:
                return self._speak_pyttsx3(text)
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            return False
    
    def _speak_pyttsx3(self, text: str) -> bool:
        """Speak using pyttsx3 (offline)"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            print(f"pyttsx3 error: {e}")
            return False
    
    def _speak_gtts(self, text: str) -> bool:
        """Speak using Google TTS (online)"""
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
                tts.save(temp_file)
            
            # Play the audio file (platform-dependent)
            if os.name == 'posix':  # Linux/Mac
                os.system(f'mpg123 -q {temp_file} 2>/dev/null || afplay {temp_file} 2>/dev/null')
            else:  # Windows
                os.system(f'start {temp_file}')
            
            time.sleep(0.5)
            
            # Clean up
            try:
                os.remove(temp_file)
            except:
                pass
            
            return True
        except Exception as e:
            print(f"gTTS error: {e}")
            return False
    
    def listen(self, timeout: int = 120, phrase_time_limit: int = 120) -> Tuple[Optional[str], dict]:
        """
        Listen to microphone and convert speech to text
        
        Args:
            timeout: Maximum time to wait for phrase start
            phrase_time_limit: Maximum time for phrase
            
        Returns:
            Tuple of (transcribed text or None, audio analysis dict)
        """
        audio_analysis = {
            'duration': 0,
            'confidence': 0,
            'error': None
        }
        
        try:
            with sr.Microphone() as source:
                print("🎤 Listening... (speak now)")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Record audio
                start_time = time.time()
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                audio_analysis['duration'] = time.time() - start_time
                
                print("🔄 Processing your response...")
                
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                audio_analysis['confidence'] = 0.85  # Google doesn't provide confidence
                
                return text, audio_analysis
                
        except sr.WaitTimeoutError:
            audio_analysis['error'] = 'timeout'
            print("⏱️ No speech detected within timeout period")
            return None, audio_analysis
            
        except sr.UnknownValueError:
            audio_analysis['error'] = 'unclear'
            print("❌ Could not understand the audio")
            return None, audio_analysis
            
        except sr.RequestError as e:
            audio_analysis['error'] = 'service_error'
            print(f"❌ Could not request results from speech recognition service: {e}")
            return None, audio_analysis
            
        except Exception as e:
            audio_analysis['error'] = str(e)
            print(f"❌ Error during speech recognition: {e}")
            return None, audio_analysis
    
    def analyze_voice_features(self, audio_data, text: str) -> dict:
        """
        Analyze voice features from audio
        
        Args:
            audio_data: Audio data from speech recognition
            text: Transcribed text
            
        Returns:
            Dictionary with voice analysis metrics
        """
        # Basic analysis based on transcribed text
        analysis = {
            'word_count': len(text.split()),
            'speaking_rate': 0,  # Words per minute
            'volume_level': 'medium',  # Would need audio processing for actual value
            'clarity_score': 0.7  # Default placeholder
        }
        
        # Estimate speaking rate if we have duration
        # This is a simplified version - would need actual audio processing for accuracy
        if hasattr(audio_data, 'duration'):
            duration_minutes = audio_data.duration / 60
            if duration_minutes > 0:
                analysis['speaking_rate'] = analysis['word_count'] / duration_minutes
        
        # Assess clarity based on word count and sentence structure
        if analysis['word_count'] > 30:
            analysis['clarity_score'] = 0.8
        if analysis['word_count'] > 50:
            analysis['clarity_score'] = 0.85
        
        return analysis
    
    def test_audio_setup(self) -> dict:
        """
        Test audio input/output setup
        
        Returns:
            Dictionary with test results
        """
        results = {
            'microphone': False,
            'speakers': False,
            'speech_recognition': False
        }
        
        # Test speakers
        print("\nTesting speakers...")
        try:
            self.speak("Testing audio output. Can you hear this?")
            results['speakers'] = True
            print("✅ Speakers working")
        except Exception as e:
            print(f"❌ Speaker test failed: {e}")
        
        # Test microphone
        print("\nTesting microphone...")
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                results['microphone'] = True
                print("✅ Microphone detected")
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
        
        # Test speech recognition
        if results['microphone']:
            print("\nTesting speech recognition...")
            print("Please say: 'This is a test'")
            try:
                text, _ = self.listen(timeout=10, phrase_time_limit=10)
                if text:
                    results['speech_recognition'] = True
                    print(f"✅ Recognized: {text}")
            except Exception as e:
                print(f"❌ Speech recognition test failed: {e}")
        
        return results


if __name__ == "__main__":
    # Test the audio handler
    print("Audio Handler Module - Test Mode")
    print("=" * 50)
    
    handler = AudioHandler()
    
    # Run audio setup test
    test_results = handler.test_audio_setup()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    for component, status in test_results.items():
        status_symbol = "✅" if status else "❌"
        print(f"{status_symbol} {component.replace('_', ' ').title()}: {'Working' if status else 'Failed'}")