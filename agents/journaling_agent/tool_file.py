import asyncio
import logging
import base64
from typing import Dict, Any, Optional, List
import io
from datetime import datetime

from google.cloud import speech
from google.cloud.speech import RecognitionConfig, RecognitionAudio
from google.genai import Client as GenAIClient

from config.api_keys import get_api_key
from config.firebase_config import firebase_config
from vector_db.embeddings.gemini_embeddings import gemini_embeddings
from vector_db.utils.vector_operations import vector_ops
from vector_db.schemas.mental_health_schemas import VectorType

class SpeechToTextTool:
    """Google Speech-to-Text integration for voice journaling"""
    
    def __init__(self):
        self.api_key = get_api_key('google_speech')
        self.client = None
        
        if self.api_key:
            try:
                self.client = speech.SpeechClient()
                logging.info("Google Speech-to-Text client initialized")
            except Exception as e:
                logging.error(f"Failed to initialize Speech-to-Text client: {e}")
                self.client = None
        else:
            logging.warning("Google Speech API key not found")
    
    async def transcribe_audio(self, audio_data: bytes, language_code: str = 'en-US', **kwargs) -> Dict[str, Any]:
        """Transcribe audio data to text"""
        if not self.client:
            return await self._mock_transcription(audio_data)
        
        try:
            # Configure recognition settings optimized for journaling
            config = RecognitionConfig(
                encoding=RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code=language_code,
                enable_automatic_punctuation=kwargs.get('enable_automatic_punctuation', True),
                enable_word_time_offsets=True,
                model=kwargs.get('model', 'latest_long'),
                use_enhanced=True,
                # Optimize for emotional content
                speech_contexts=[
                    speech.SpeechContext(
                        phrases=[
                            "I feel", "I'm feeling", "today was", "I'm struggling",
                            "anxiety", "depression", "stress", "overwhelmed",
                            "grateful", "happy", "sad", "angry", "frustrated"
                        ]
                    )
                ]
            )
            
            audio = RecognitionAudio(content=audio_data)
            
            # Perform transcription
            response = await asyncio.to_thread(
                self.client.recognize,
                config=config,
                audio=audio
            )
            
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                
                # Extract word-level timing for advanced analysis
                word_info = []
                if hasattr(response.results[0].alternatives[0], 'words'):
                    for word in response.results[0].alternatives[0].words:
                        word_info.append({
                            'word': word.word,
                            'start_time': word.start_time.total_seconds(),
                            'end_time': word.end_time.total_seconds()
                        })
                
                return {
                    'transcript': transcript,
                    'confidence': confidence,
                    'word_info': word_info,
                    'language_code': language_code,
                    'processing_time': datetime.now().isoformat()
                }
            else:
                return {
                    'transcript': '',
                    'confidence': 0.0,
                    'error': 'No speech detected'
                }
                
        except Exception as e:
            logging.error(f"Error in speech transcription: {e}")
            return await self._mock_transcription(audio_data)
    
    async def _mock_transcription(self, audio_data: bytes) -> Dict[str, Any]:
        """Mock transcription for demonstration purposes"""
        # Simulate processing delay
        await asyncio.sleep(2.0)
        
        mock_transcripts = [
            "I'm feeling really anxious today about work. There's so much pressure and I don't know if I can handle it all.",
            "Today was actually a good day. I managed to get through my to-do list and even had time to go for a walk.",
            "I'm struggling with some negative thoughts lately. Everything feels overwhelming and I'm not sure what to do.",
            "I'm grateful for my friends and family. They've been so supportive during this difficult time.",
            "Work has been stressful but I'm trying to use the breathing techniques I learned to manage my anxiety."
        ]
        
        import random
        selected_transcript = random.choice(mock_transcripts)
        
        return {
            'transcript': selected_transcript,
            'confidence': 0.85,
            'word_info': [],
            'language_code': 'en-US',
            'processing_time': datetime.now().isoformat(),
            'mock': True
        }

class FirebaseStorageTool:
    """Firebase Firestore integration for journal data storage"""
    
    def __init__(self):
        self.db = firebase_config.get_firestore_client()
    
    async def store_journal_entry(self, user_id: str, entry_data: Dict[str, Any]) -> str:
        """Store journal entry in Firestore"""
        try:
            doc_ref = self.db.collection('journal_entries').document()
            
            journal_doc = {
                'user_id': user_id,
                'entry_id': doc_ref.id,
                'text': entry_data.get('text', ''),
                'transcription': entry_data.get('transcription', ''),
                'entry_type': entry_data.get('type', 'text'),
                'timestamp': datetime.now(),
                'metadata': entry_data.get('metadata', {}),
                'processed': False
            }
            
            await asyncio.to_thread(doc_ref.set, journal_doc)
            
            logging.info(f"Journal entry stored: {doc_ref.id}")
            return doc_ref.id
            
        except Exception as e:
            logging.error(f"Error storing journal entry: {e}")
            raise
    
    async def get_user_journal_entries(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent journal entries for user"""
        try:
            query = (self.db.collection('journal_entries')
                    .where('user_id', '==', user_id)
                    .order_by('timestamp', direction='DESCENDING')
                    .limit(limit))
            
            docs = await asyncio.to_thread(query.get)
            
            entries = []
            for doc in docs:
                entry = doc.to_dict()
                entry['id'] = doc.id
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logging.error(f"Error retrieving journal entries: {e}")
            return []
    
    async def update_entry_processing_status(self, entry_id: str, processing_data: Dict[str, Any]):
        """Update journal entry with processing results"""
        try:
            doc_ref = self.db.collection('journal_entries').document(entry_id)
            
            update_data = {
                'processed': True,
                'processing_timestamp': datetime.now(),
                'sentiment_analysis': processing_data.get('sentiment_analysis', {}),
                'mental_state': processing_data.get('mental_state', {}),
                'vector_id': processing_data.get('vector_id', '')
            }
            
            await asyncio.to_thread(doc_ref.update, update_data)
            
        except Exception as e:
            logging.error(f"Error updating entry processing status: {e}")

class VectorDatabaseTool:
    """Pinecone vector database operations for journal entries"""
    
    def __init__(self):
        self.vector_ops = vector_ops
        self.embeddings = gemini_embeddings
    
    async def store_journal_vector(self, user_id: str, text: str, metadata: Dict[str, Any]) -> str:
        """Store journal entry as vector in Pinecone"""
        try:
            # Generate embedding
            embedding = await self.embeddings.generate_mental_health_embedding(
                text, 
                title=f"Journal entry - {datetime.now().strftime('%Y-%m-%d')}"
            )
            
            # Create vector ID
            vector_id = f"journal_{user_id}_{datetime.now().timestamp()}"
            
            # Prepare vector data
            vector_data = [(
                vector_id,
                embedding,
                {
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'entry_type': 'journal',
                    **metadata
                }
            )]
            
            # Store in Pinecone
            success = self.vector_ops.pinecone_config.upsert_vectors(
                'journal-entries', 
                vector_data
            )
            
            if success:
                logging.info(f"Journal vector stored: {vector_id}")
                return vector_id
            else:
                raise Exception("Failed to store vector in Pinecone")
                
        except Exception as e:
            logging.error(f"Error storing journal vector: {e}")
            raise
    
    async def semantic_search_journals(self, user_id: str, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search on user's journal entries"""
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.generate_mental_health_embedding(query_text)
            
            # Perform semantic search
            results = await self.vector_ops.semantic_search(
                query_vector=query_embedding,
                vector_type=VectorType.JOURNAL_ENTRY,
                user_id=user_id,
                top_k=top_k
            )
            
            return results
            
        except Exception as e:
            logging.error(f"Error in semantic search: {e}")
            return []
    
    async def get_emotional_patterns(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze emotional patterns from journal vectors"""
        try:
            # Get clustering analysis
            clustering_result = await self.vector_ops.cluster_mental_health_vectors(
                vector_type=VectorType.JOURNAL_ENTRY,
                user_id=user_id,
                time_window_days=days,
                num_clusters=5
            )
            
            return clustering_result
            
        except Exception as e:
            logging.error(f"Error analyzing emotional patterns: {e}")
            return {}

class GeminiAnalysisTool:
    """Gemini 2.5 Pro integration for advanced journal analysis"""
    
    def __init__(self):
        self.client = GenAIClient(api_key=get_api_key('gemini_2_5_pro'))
    
    async def analyze_emotional_state(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze emotional state using Gemini 2.5 Pro"""
        try:
            analysis_prompt = f"""
            Analyze the emotional state and mental health indicators in this journal entry:
            
            "{text}"
            
            Context: {context if context else 'No additional context'}
            
            Provide a detailed analysis including:
            1. Primary emotions (with intensity 0-1)
            2. Secondary emotions
            3. Mood score (-1 to 1, where -1 is very negative, 1 is very positive)
            4. Stress level (0-1)
            5. Anxiety indicators (0-1)
            6. Depression indicators (0-1)
            7. Energy level (0-1)
            8. Identified triggers
            9. Coping mechanisms mentioned
            10. Crisis risk assessment (low/moderate/high/critical)
            11. Therapeutic recommendations
            
            Return as structured JSON format.
            """
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model='gemini-2.5-pro',
                contents=analysis_prompt
            )
            
            # Parse response (would need proper JSON parsing in production)
            analysis_text = response.text
            
            # For demo, return structured data
            return {
                'analysis_text': analysis_text,
                'mood_score': self._extract_mood_score(analysis_text),
                'emotions': self._extract_emotions(analysis_text),
                'risk_level': self._extract_risk_level(analysis_text),
                'recommendations': self._extract_recommendations(analysis_text),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error in Gemini analysis: {e}")
            return {}
    
    def _extract_mood_score(self, analysis_text: str) -> float:
        """Extract mood score from analysis text"""
        # Simplified extraction - would use proper parsing in production
        if 'very positive' in analysis_text.lower():
            return 0.8
        elif 'positive' in analysis_text.lower():
            return 0.4
        elif 'negative' in analysis_text.lower():
            return -0.4
        elif 'very negative' in analysis_text.lower():
            return -0.8
        else:
            return 0.0
    
    def _extract_emotions(self, analysis_text: str) -> Dict[str, float]:
        """Extract emotions from analysis text"""
        # Simplified extraction
        emotions = {}
        emotion_keywords = {
            'anxiety': ['anxious', 'worried', 'nervous'],
            'depression': ['sad', 'hopeless', 'empty'],
            'anger': ['angry', 'frustrated', 'irritated'],
            'joy': ['happy', 'joyful', 'excited'],
            'stress': ['stressed', 'overwhelmed', 'pressure']
        }
        
        for emotion, keywords in emotion_keywords.items():
            intensity = 0.0
            for keyword in keywords:
                if keyword in analysis_text.lower():
                    intensity = max(intensity, 0.7)  # Simplified scoring
            emotions[emotion] = intensity
        
        return emotions
    
    def _extract_risk_level(self, analysis_text: str) -> str:
        """Extract risk level from analysis"""
        text_lower = analysis_text.lower()
        if 'critical' in text_lower or 'crisis' in text_lower:
            return 'critical'
        elif 'high' in text_lower:
            return 'high'
        elif 'moderate' in text_lower:
            return 'moderate'
        else:
            return 'low'
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Extract recommendations from analysis"""
        # Simplified extraction
        recommendations = []
        if 'breathing' in analysis_text.lower():
            recommendations.append('Practice breathing exercises')
        if 'mindfulness' in analysis_text.lower():
            recommendations.append('Try mindfulness meditation')
        if 'therapy' in analysis_text.lower():
            recommendations.append('Consider therapy session')
        if 'exercise' in analysis_text.lower():
            recommendations.append('Engage in physical exercise')
        
        return recommendations

# Initialize tool instances
speech_to_text_tool = SpeechToTextTool()
firebase_storage_tool = FirebaseStorageTool()
vector_database_tool = VectorDatabaseTool()
gemini_analysis_tool = GeminiAnalysisTool()
