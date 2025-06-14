import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class TextProcessor:
    """Advanced text processing utilities for mental health content"""
    
    # Mental health related keywords and patterns
    CRISIS_KEYWORDS = [
        'suicide', 'kill myself', 'end it all', 'not worth living', 'better off dead',
        'self harm', 'cut myself', 'hurt myself', 'overdose', 'can\'t go on'
    ]
    
    EMOTIONAL_KEYWORDS = {
        'anxiety': ['anxious', 'worried', 'nervous', 'panic', 'fear', 'scared'],
        'depression': ['sad', 'hopeless', 'empty', 'worthless', 'depressed', 'down'],
        'anger': ['angry', 'furious', 'rage', 'mad', 'irritated', 'frustrated'],
        'joy': ['happy', 'joyful', 'excited', 'elated', 'cheerful', 'content'],
        'stress': ['stressed', 'overwhelmed', 'pressure', 'tension', 'burden']
    }
    
    COPING_MECHANISMS = [
        'meditation', 'breathing', 'exercise', 'walk', 'music', 'friends',
        'therapy', 'journal', 'sleep', 'bath', 'nature', 'prayer'
    ]
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text for processing"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text
    
    @staticmethod
    def extract_emotions(text: str) -> Dict[str, float]:
        """Extract emotional indicators from text"""
        text_lower = text.lower()
        emotions = {}
        
        for emotion, keywords in TextProcessor.EMOTIONAL_KEYWORDS.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            # Normalize by text length
            emotions[emotion] = count / max(len(text.split()), 1)
        
        return emotions
    
    @staticmethod
    def detect_crisis_indicators(text: str) -> Tuple[bool, List[str]]:
        """Detect crisis indicators in text"""
        text_lower = text.lower()
        detected_indicators = []
        
        for keyword in TextProcessor.CRISIS_KEYWORDS:
            if keyword in text_lower:
                detected_indicators.append(keyword)
        
        is_crisis = len(detected_indicators) > 0
        return is_crisis, detected_indicators
    
    @staticmethod
    def extract_coping_mechanisms(text: str) -> List[str]:
        """Extract mentioned coping mechanisms from text"""
        text_lower = text.lower()
        found_coping = []
        
        for mechanism in TextProcessor.COPING_MECHANISMS:
            if mechanism in text_lower:
                found_coping.append(mechanism)
        
        return found_coping
    
    @staticmethod
    def extract_triggers(text: str) -> List[str]:
        """Extract potential triggers from text using pattern matching"""
        triggers = []
        text_lower = text.lower()
        
        # Common trigger patterns
        trigger_patterns = [
            r'because of (\w+)',
            r'triggered by (\w+)',
            r'after (\w+)',
            r'when (\w+)',
            r'(\w+) made me feel'
        ]
        
        for pattern in trigger_patterns:
            matches = re.findall(pattern, text_lower)
            triggers.extend(matches)
        
        return list(set(triggers))  # Remove duplicates
    
    @staticmethod
    def calculate_sentiment_score(text: str) -> float:
        """Calculate basic sentiment score (-1 to 1)"""
        positive_words = ['good', 'great', 'happy', 'better', 'improved', 'positive', 'hopeful']
        negative_words = ['bad', 'terrible', 'sad', 'worse', 'negative', 'hopeless', 'awful']
        
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_emotional_words = positive_count + negative_count
        if total_emotional_words == 0:
            return 0.0
        
        return (positive_count - negative_count) / total_emotional_words
    
    @staticmethod
    def prepare_for_embedding(text: str, context: Dict[str, Any] = None) -> str:
        """Prepare text for optimal embedding generation"""
        cleaned_text = TextProcessor.clean_text(text)
        
        if context:
            # Add context information for better embeddings
            context_parts = []
            
            if 'mood' in context:
                context_parts.append(f"Mood: {context['mood']}")
            
            if 'session_type' in context:
                context_parts.append(f"Session: {context['session_type']}")
            
            if 'framework' in context:
                context_parts.append(f"Framework: {context['framework']}")
            
            if context_parts:
                cleaned_text = " | ".join(context_parts) + " | " + cleaned_text
        
        return cleaned_text

class SentimentAnalyzer:
    """Advanced sentiment analysis for mental health content"""
    
    @staticmethod
    def analyze_journal_entry(entry_text: str) -> Dict[str, Any]:
        """Comprehensive analysis of journal entry"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'text_length': len(entry_text),
            'word_count': len(entry_text.split()),
            'emotions': TextProcessor.extract_emotions(entry_text),
            'sentiment_score': TextProcessor.calculate_sentiment_score(entry_text),
            'coping_mechanisms': TextProcessor.extract_coping_mechanisms(entry_text),
            'triggers': TextProcessor.extract_triggers(entry_text)
        }
        
        # Crisis detection
        is_crisis, crisis_indicators = TextProcessor.detect_crisis_indicators(entry_text)
        analysis['crisis_detected'] = is_crisis
        analysis['crisis_indicators'] = crisis_indicators
        
        # Overall mood assessment
        dominant_emotion = max(analysis['emotions'].items(), key=lambda x: x[1])
        analysis['dominant_emotion'] = dominant_emotion[0]
        analysis['emotional_intensity'] = dominant_emotion[1]
        
        return analysis
    
    @staticmethod
    def analyze_therapy_session(session_text: str, framework: str) -> Dict[str, Any]:
        """Analyze therapy session content"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'framework': framework,
            'text_length': len(session_text),
            'therapeutic_progress_indicators': [],
            'insights_extracted': [],
            'homework_suggestions': []
        }
        
        # Framework-specific analysis
        if framework.upper() == 'CBT':
            analysis['cognitive_patterns'] = TextProcessor.extract_triggers(session_text)
            analysis['behavioral_changes'] = TextProcessor.extract_coping_mechanisms(session_text)
        
        elif framework.upper() == 'DBT':
            analysis['emotional_regulation'] = TextProcessor.extract_emotions(session_text)
            analysis['distress_tolerance'] = TextProcessor.extract_coping_mechanisms(session_text)
        
        elif framework.upper() == 'ACT':
            analysis['acceptance_indicators'] = []
            analysis['values_alignment'] = []
        
        return analysis
