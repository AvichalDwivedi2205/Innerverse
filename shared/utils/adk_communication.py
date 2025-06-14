import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class MessageType(Enum):
    """Google ADK agent communication message types"""
    USER_STATE_UPDATE = "user_state_update"
    THERAPY_SESSION_REQUEST = "therapy_session_request"
    EXERCISE_RECOMMENDATION = "exercise_recommendation"
    CRISIS_ALERT = "crisis_alert"
    PROGRESS_REPORT = "progress_report"
    SCHEDULING_REQUEST = "scheduling_request"
    AGENT_COORDINATION = "agent_coordination"

class Priority(Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ADKMessage:
    """Standardized Google ADK agent communication message"""
    message_id: str
    message_type: MessageType
    sender_agent: str
    recipient_agent: str
    priority: Priority
    timestamp: datetime
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    requires_response: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Google ADK transmission"""
        return {
            'message_id': self.message_id,
            'message_type': self.message_type.value,
            'sender_agent': self.sender_agent,
            'recipient_agent': self.recipient_agent,
            'priority': self.priority.value,
            'timestamp': self.timestamp.isoformat(),
            'payload': self.payload,
            'correlation_id': self.correlation_id,
            'requires_response': self.requires_response
        }

class ADKCommunicationHelper:
    """Helper class for Google ADK agent communication"""
    
    def __init__(self):
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.active_conversations: Dict[str, List[ADKMessage]] = {}
    
    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """Register handler for specific message type"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    async def send_message(self, message: ADKMessage) -> bool:
        """Send message through Google ADK communication layer"""
        try:
            # Log message for debugging
            logging.info(f"Sending ADK message: {message.message_type.value} from {message.sender_agent} to {message.recipient_agent}")
            
            # Store in conversation history
            conversation_key = f"{message.sender_agent}_{message.recipient_agent}"
            if conversation_key not in self.active_conversations:
                self.active_conversations[conversation_key] = []
            self.active_conversations[conversation_key].append(message)
            
            # In production, this would integrate with Google ADK's messaging system
            # For now, we'll simulate the communication
            await self._simulate_adk_transmission(message)
            
            return True
            
        except Exception as e:
            logging.error(f"Error sending ADK message: {e}")
            return False
    
    async def _simulate_adk_transmission(self, message: ADKMessage):
        """Simulate Google ADK message transmission"""
        # Simulate network delay based on priority
        delay_map = {
            Priority.CRITICAL: 0.1,
            Priority.HIGH: 0.2,
            Priority.NORMAL: 0.5,
            Priority.LOW: 1.0
        }
        
        await asyncio.sleep(delay_map.get(message.priority, 0.5))
        
        # Trigger message handlers
        if message.message_type in self.message_handlers:
            for handler in self.message_handlers[message.message_type]:
                try:
                    await handler(message)
                except Exception as e:
                    logging.error(f"Error in message handler: {e}")
    
    def create_crisis_alert(self, user_id: str, crisis_indicators: List[str], sender_agent: str) -> ADKMessage:
        """Create crisis alert message"""
        return ADKMessage(
            message_id=f"crisis_{user_id}_{datetime.now().timestamp()}",
            message_type=MessageType.CRISIS_ALERT,
            sender_agent=sender_agent,
            recipient_agent="therapy_agent",
            priority=Priority.CRITICAL,
            timestamp=datetime.now(),
            payload={
                'user_id': user_id,
                'crisis_indicators': crisis_indicators,
                'immediate_intervention_required': True,
                'emergency_contacts_notified': False
            },
            requires_response=True
        )
    
    def create_progress_report_request(self, user_id: str, sender_agent: str) -> ADKMessage:
        """Create progress report request message"""
        return ADKMessage(
            message_id=f"progress_{user_id}_{datetime.now().timestamp()}",
            message_type=MessageType.PROGRESS_REPORT,
            sender_agent=sender_agent,
            recipient_agent="mental_orchestration_agent",
            priority=Priority.NORMAL,
            timestamp=datetime.now(),
            payload={
                'user_id': user_id,
                'report_type': 'comprehensive',
                'time_period_days': 30
            },
            requires_response=True
        )
    
    def create_exercise_recommendation_request(self, user_id: str, mental_state: Dict[str, Any], sender_agent: str) -> ADKMessage:
        """Create exercise recommendation request"""
        return ADKMessage(
            message_id=f"exercise_rec_{user_id}_{datetime.now().timestamp()}",
            message_type=MessageType.EXERCISE_RECOMMENDATION,
            sender_agent=sender_agent,
            recipient_agent="mental_exercise_agent",
            priority=Priority.HIGH,
            timestamp=datetime.now(),
            payload={
                'user_id': user_id,
                'current_mental_state': mental_state,
                'urgency_level': 'moderate',
                'preferred_duration': 10
            },
            requires_response=True
        )

# Global ADK communication helper
adk_comm = ADKCommunicationHelper()
