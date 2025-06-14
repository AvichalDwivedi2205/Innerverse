import asyncio
import logging
import io
import base64
from typing import Dict, Any, Optional, List
import requests
from datetime import datetime

from config.api_keys import get_api_key, get_headers_for_service

class ElevenLabsVoiceSynthesis:
    """ElevenLabs voice synthesis for wellness platform"""
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    # Voice configurations for different wellness contexts
    VOICE_PROFILES = {
        'therapy': {
            'voice_id': 'pNInz6obpgDQGcFmaJgB',  # Adam - calm, professional
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {
                'stability': 0.8,
                'similarity_boost': 0.7,
                'style': 0.3,
                'use_speaker_boost': True
            }
        },
        'mental_exercise': {
            'voice_id': 'EXAVITQu4vr4xnSDxMaL',  # Bella - soothing, guided
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {
                'stability': 0.9,
                'similarity_boost': 0.6,
                'style': 0.2,
                'use_speaker_boost': True
            }
        },
        'nutrition': {
            'voice_id': 'TxGEqnHWrfWFTfGW9XjX',  # Josh - friendly, informative
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {
                'stability': 0.7,
                'similarity_boost': 0.8,
                'style': 0.4,
                'use_speaker_boost': True
            }
        },
        'fitness': {
            'voice_id': 'pqHfZKP75CvOlQylNhV4',  # Bill - energetic, motivational
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {
                'stability': 0.6,
                'similarity_boost': 0.9,
                'style': 0.6,
                'use_speaker_boost': True
            }
        }
    }
    
    def __init__(self):
        self.api_key = get_api_key('elevenlabs')
        self.headers = get_headers_for_service('elevenlabs')
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        if not self.api_key:
            logging.warning("ElevenLabs API key not found. Voice synthesis will be disabled.")
    
    async def synthesize_therapy_session_audio(self, text: str, session_context: Dict[str, Any]) -> Optional[bytes]:
        """Generate voice audio for therapy sessions with appropriate tone"""
        try:
            # Enhance text with therapeutic context
            enhanced_text = self._enhance_therapy_text(text, session_context)
            
            return await self._synthesize_voice(
                text=enhanced_text,
                voice_profile='therapy',
                context=session_context
            )
            
        except Exception as e:
            logging.error(f"Error synthesizing therapy session audio: {e}")
            return None
    
    def _enhance_therapy_text(self, text: str, context: Dict[str, Any]) -> str:
        """Enhance therapy text with SSML for better emotional delivery"""
        framework = context.get('therapeutic_framework', 'CBT')
        mood_score = context.get('user_mood_score', 0.0)
        
        # Add SSML tags based on therapeutic context
        if framework == 'mindfulness':
            # Slower, more meditative pace
            enhanced_text = f'<speak><prosody rate="slow" pitch="-2st">{text}</prosody></speak>'
        elif mood_score < -0.5:
            # More gentle and supportive tone for low mood
            enhanced_text = f'<speak><prosody rate="medium" pitch="-1st" volume="soft">{text}</prosody></speak>'
        elif framework == 'CBT':
            # Clear, structured delivery for CBT
            enhanced_text = f'<speak><prosody rate="medium" pitch="medium">{text}</prosody></speak>'
        else:
            enhanced_text = text
        
        return enhanced_text
    
    async def synthesize_mental_exercise_audio(self, exercise_text: str, exercise_type: str) -> Optional[bytes]:
        """Generate guided audio for mental health exercises"""
        try:
            # Enhance text based on exercise type
            enhanced_text = self._enhance_exercise_text(exercise_text, exercise_type)
            
            return await self._synthesize_voice(
                text=enhanced_text,
                voice_profile='mental_exercise',
                context={'exercise_type': exercise_type}
            )
            
        except Exception as e:
            logging.error(f"Error synthesizing mental exercise audio: {e}")
            return None
    
    def _enhance_exercise_text(self, text: str, exercise_type: str) -> str:
        """Enhance exercise text with appropriate pacing and tone"""
        if exercise_type == 'mindfulness':
            # Very slow, meditative pace with pauses
            enhanced_text = f'<speak><prosody rate="x-slow" pitch="-3st">{text.replace(".", ".<break time=\"2s\"/>")}</prosody></speak>'
        elif exercise_type == 'breathing':
            # Rhythmic pacing for breathing exercises
            enhanced_text = f'<speak><prosody rate="slow" pitch="-2st">{text.replace("inhale", "<emphasis level=\"moderate\">inhale</emphasis>").replace("exhale", "<emphasis level=\"moderate\">exhale</emphasis>")}</prosody></speak>'
        elif exercise_type == 'CBT':
            # Clear, instructional tone
            enhanced_text = f'<speak><prosody rate="medium" pitch="medium">{text}</prosody></speak>'
        else:
            enhanced_text = text
        
        return enhanced_text
    
    async def synthesize_nutrition_consultation_audio(self, text: str, consultation_context: Dict[str, Any]) -> Optional[bytes]:
        """Generate voice audio for nutrition consultations"""
        try:
            return await self._synthesize_voice(
                text=text,
                voice_profile='nutrition',
                context=consultation_context
            )
            
        except Exception as e:
            logging.error(f"Error synthesizing nutrition consultation audio: {e}")
            return None
    
    async def synthesize_fitness_coaching_audio(self, text: str, workout_context: Dict[str, Any]) -> Optional[bytes]:
        """Generate motivational voice audio for fitness coaching"""
        try:
            # Add motivational enhancement
            enhanced_text = self._enhance_fitness_text(text, workout_context)
            
            return await self._synthesize_voice(
                text=enhanced_text,
                voice_profile='fitness',
                context=workout_context
            )
            
        except Exception as e:
            logging.error(f"Error synthesizing fitness coaching audio: {e}")
            return None
    
    def _enhance_fitness_text(self, text: str, context: Dict[str, Any]) -> str:
        """Enhance fitness text with motivational tone"""
        workout_type = context.get('workout_type', 'general')
        
        if workout_type == 'high_intensity':
            # High energy, fast pace
            enhanced_text = f'<speak><prosody rate="fast" pitch="+2st" volume="loud">{text}</prosody></speak>'
        elif workout_type == 'strength':
            # Strong, encouraging tone
            enhanced_text = f'<speak><prosody rate="medium" pitch="+1st">{text}</prosody></speak>'
        elif workout_type == 'yoga':
            # Calm, flowing pace
            enhanced_text = f'<speak><prosody rate="slow" pitch="-1st">{text}</prosody></speak>'
        else:
            enhanced_text = text
        
        return enhanced_text
    
    async def _synthesize_voice(self, text: str, voice_profile: str, context: Dict[str, Any] = None) -> Optional[bytes]:
        """Internal method to synthesize voice using ElevenLabs API"""
        if not self.api_key:
            logging.warning("ElevenLabs API key not available")
            return None
        
        profile = self.VOICE_PROFILES.get(voice_profile, self.VOICE_PROFILES['therapy'])
        
        url = f"{self.BASE_URL}/text-to-speech/{profile['voice_id']}"
        
        payload = {
            "text": text,
            "model_id": profile['model_id'],
            "voice_settings": profile['voice_settings']
        }
        
        try:
            response = await asyncio.to_thread(
                self.session.post,
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logging.info(f"Successfully synthesized {voice_profile} audio")
                return response.content
            else:
                logging.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error calling ElevenLabs API: {e}")
            return None
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices from ElevenLabs"""
        if not self.api_key:
            return []
        
        url = f"{self.BASE_URL}/voices"
        
        try:
            response = await asyncio.to_thread(self.session.get, url)
            
            if response.status_code == 200:
                voices_data = response.json()
                return voices_data.get('voices', [])
            else:
                logging.error(f"Error fetching voices: {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"Error fetching available voices: {e}")
            return []

# Global ElevenLabs instance
elevenlabs_voice = ElevenLabsVoiceSynthesis()
