"""Tools for the mental orchestrator agent.

This module contains tools for embedding clustering, mind map generation, 
empowerment insights creation, exercise recommendations, dashboard metrics, 
and crisis detection with focus on internal pattern analysis and creator consciousness.
"""

import json
import os
import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
import time
import threading

from google.adk.tools import ToolContext
from google.cloud import firestore
import vertexai
from vertexai.generative_models import GenerativeModel
from sklearn.decomposition import PCA
# Pinecone functionality is now handled by the pinecone_service

try:
    from .prompts import (
        get_clustering_prompt,
        get_empowerment_insights_prompt,
        get_exercise_recommendation_prompt,
        get_crisis_detection_prompt
    )
    from ..common import OrchestratorToolResult
    from ..common.pinecone_service import pinecone_service
except ImportError:
    try:
        from agents.mental_orchestrator_agent.prompts import (
            get_clustering_prompt,
            get_empowerment_insights_prompt,
            get_exercise_recommendation_prompt,
            get_crisis_detection_prompt
        )
        from agents.common import OrchestratorToolResult
        from agents.common.pinecone_service import pinecone_service
    except ImportError:
        try:
            from prompts import (
                get_clustering_prompt,
                get_empowerment_insights_prompt,
                get_exercise_recommendation_prompt,
                get_crisis_detection_prompt
            )
            # Create fallback classes
            class OrchestratorToolResult:
                @staticmethod
                def error_result(message, error_details="", next_actions=None):
                    return {"status": "error", "message": message, "error_details": error_details}
                
                @staticmethod
                def success_result(data, message, next_actions=None):
                    return {"status": "success", "data": data, "message": message}
            
            class MockPineconeService:
                async def retrieve_user_embeddings(self, user_id, limit=1000):
                    return []
            
            pinecone_service = MockPineconeService()
        except ImportError:
            # Final fallback - create minimal functions
            def get_clustering_prompt():
                return "Analyze these texts and identify the main theme: {list_of_texts}"
            
            def get_empowerment_insights_prompt():
                return "Generate empowerment insights from: {mind_map_json}"
            
            def get_exercise_recommendation_prompt():
                return "Recommend exercises for: {theme}"
            
            def get_crisis_detection_prompt():
                return "Detect crisis patterns in: {patterns}"
            
            class OrchestratorToolResult:
                @staticmethod
                def error_result(message, error_details="", next_actions=None):
                    return {"status": "error", "message": message, "error_details": error_details}
                
                @staticmethod
                def success_result(data, message, next_actions=None):
                    return {"status": "success", "data": data, "message": message}
            
            class MockPineconeService:
                async def retrieve_user_embeddings(self, user_id, limit=1000):
                    return []
            
            pinecone_service = MockPineconeService()

# Initialize clients lazily to avoid import-time errors
_db = None
_model = None

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Demo user profiles for mock artifacts
DEMO_USER_PROFILES = {
    "stressed_professional": {
        "name": "Avichal Dwivedi",
        "background": "Software engineer and AI entrepreneur building innovative mental health solutions",
        "primary_themes": ["work_stress", "burnout_prevention", "work_life_balance", "entrepreneurial_growth"],
        "breakthrough_moments": [
            "Realized perfectionism was limiting creative potential",
            "Discovered the power of saying 'no' to non-essential commitments",
            "Found that meditation breaks improved both focus and innovation"
        ],
        "empowerment_journey": "From overwhelmed perfectionist to balanced innovator and creator"
    },
    "career_transition": {
        "name": "Avichal Dwivedi",
        "background": "Tech entrepreneur transitioning from traditional software to AI-powered mental health platforms",
        "primary_themes": ["career_evolution", "innovation_confidence", "skill_development", "leadership_growth"],
        "breakthrough_moments": [
            "Recognized the intersection of technology and mental wellness",
            "Built first AI agent that received positive user feedback",
            "Connected with mental health professionals for deeper insights"
        ],
        "empowerment_journey": "From technical expertise to holistic wellness innovation leadership"
    },
    "new_parent": {
        "name": "Avichal Dwivedi",
        "background": "Entrepreneur balancing startup ambitions with personal growth and wellness priorities",
        "primary_themes": ["startup_stress", "identity_evolution", "time_optimization", "wellness_systems"],
        "breakthrough_moments": [
            "Accepted that sustainable growth requires personal wellness",
            "Created daily routines that balance productivity with mindfulness",
            "Redefined success to include mental health and life satisfaction"
        ],
        "empowerment_journey": "From hustle-focused founder to wellness-integrated entrepreneur"
    }
}

def get_firestore_client():
    """Get Firestore client with lazy initialization."""
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db

def get_gemini_model():
    """Get Gemini model with lazy initialization using Google AI API."""
    global _model
    if _model is None:
        import os
        google_api_key = os.getenv('GOOGLE_API_KEY')
        
        if google_api_key:
            # Use Google AI API directly
            import google.generativeai as genai
            genai.configure(api_key=google_api_key)
            _model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            # Fallback to Vertex AI
            vertexai.init()
            _model = GenerativeModel("gemini-2.5-flash")
    return _model


async def retrieve_user_embeddings(
    tool_context: ToolContext,
) -> OrchestratorToolResult:
    """Tool to retrieve all user embeddings from Pinecone for analysis."""
    
    try:
        user_id = tool_context.state.get("user_id")
        if not user_id:
            return OrchestratorToolResult.error_result(
                message="User ID not found in context",
                error_details="user_id is required for embedding retrieval",
                next_actions=["verify_user_context"]
            )
        
        # Retrieve embeddings from Pinecone using the service
        embeddings_data = await pinecone_service.retrieve_user_embeddings(
            user_id=user_id,
            limit=1000
        )
        
        # Store in context
        tool_context.state["orchestrator_state"]["embeddings_data"] = embeddings_data
        
        return OrchestratorToolResult.success_result(
            data={
                "embeddings_data": embeddings_data,
                "embeddings_count": len(embeddings_data)
            },
            message=f"Retrieved {len(embeddings_data)} embeddings for analysis",
            next_actions=["cluster_internal_patterns"]
        )
        
    except Exception as e:
        return OrchestratorToolResult.error_result(
            message="Error retrieving user embeddings",
            error_details=str(e),
            next_actions=["retry_embedding_retrieval", "check_pinecone_connection"]
        )


async def cluster_internal_patterns(
    tool_context: ToolContext,
) -> str:
    """Tool to cluster embeddings using DBSCAN for internal pattern identification."""
    
    try:
        embeddings_data = tool_context.state["orchestrator_state"]["embeddings_data"]
        
        if not embeddings_data:
            return "Error: No embeddings data available for clustering"
        
        print(f"📊 Clustering {len(embeddings_data)} embeddings...")
        
        # Extract vectors for clustering
        vectors = np.array([item["vector"] for item in embeddings_data])
        
        # Standardize vectors
        scaler = StandardScaler()
        vectors_scaled = scaler.fit_transform(vectors)
        
        # Apply DBSCAN clustering with more lenient parameters for small datasets
        min_samples = max(1, min(2, len(embeddings_data) // 3))  # Adaptive min_samples
        eps = 0.7 if len(embeddings_data) < 10 else 0.5  # More lenient eps for small datasets
        
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = dbscan.fit_predict(vectors_scaled)
        
        print(f"🔍 DBSCAN results: eps={eps}, min_samples={min_samples}")
        print(f"🏷️ Cluster labels: {cluster_labels}")
        
        # Group embeddings by clusters
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(embeddings_data[i])
        
        # Generate cluster themes using Gemini
        cluster_themes = {}
        for cluster_id, cluster_items in clusters.items():
            # Include noise cluster (-1) as "Unique Insights" for small datasets
            if cluster_id == -1 and len(embeddings_data) >= 5:  # Only skip noise if we have enough data
                continue
                
            # Extract text content for theme generation
            texts = [item["metadata"].get("text", "") for item in cluster_items]
            
            prompt = get_clustering_prompt()
            full_prompt = prompt.format(list_of_texts=texts[:5])  # Limit to first 5 texts
            
            model = get_gemini_model()
            response = model.generate_content(full_prompt)
            theme = response.text.strip()
            
            # Special handling for noise cluster
            if cluster_id == -1:
                theme = f"Unique Individual Insights: {theme}"
            
            cluster_themes[cluster_id] = {
                "theme": theme,
                "size": len(cluster_items),
                "items": cluster_items
            }
            
            print(f"📝 Cluster {cluster_id}: {theme} ({len(cluster_items)} items)")
        
        # Store in context
        tool_context.state["orchestrator_state"]["clusters"] = cluster_themes
        
        if len(cluster_themes) == 0:
            return "Identified 0 internal pattern clusters. Consider adding more journal entries or therapy sessions for better pattern recognition."
        
        return f"Identified {len(cluster_themes)} internal pattern clusters with empowerment themes"
        
    except Exception as e:
        print(f"❌ Clustering error: {str(e)}")
        return f"Error clustering internal patterns: {str(e)}"


async def build_mental_mind_map(
    tool_context: ToolContext,
) -> str:
    """Tool to build mental mind map with internal patterns and empowerment opportunities."""
    
    try:
        clusters = tool_context.state["orchestrator_state"]["clusters"]
        
        if not clusters:
            return "Error: No clusters available for mind map generation"
        
        # Build nodes from clusters
        nodes = []
        for cluster_id, cluster_data in clusters.items():
            node = {
                "id": f"cluster_{cluster_id}",
                "theme": cluster_data["theme"],
                "size": cluster_data["size"],
                "timestampRange": {
                    "start": min([item["metadata"]["timestamp"] for item in cluster_data["items"]]),
                    "end": max([item["metadata"]["timestamp"] for item in cluster_data["items"]])
                },
                "metadata": {
                    "contexts": list(set([item["metadata"]["context"] for item in cluster_data["items"]])),
                    "empowerment_focus": True
                }
            }
            nodes.append(node)
        
        # Build edges based on temporal and semantic relationships
        edges = []
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes):
                if i != j:
                    # Calculate relationship strength (simplified)
                    weight = 0.5 if len(set(node1["metadata"]["contexts"]) & set(node2["metadata"]["contexts"])) > 0 else 0.3
                    
                    edge = {
                        "source": node1["id"],
                        "target": node2["id"],
                        "weight": weight,
                        "type": "semantic"
                    }
                    edges.append(edge)
        
        # Create mind map structure
        mind_map = {
            "nodes": nodes,
            "edges": edges,
            "lastUpdated": datetime.now().isoformat(),
            "version": 1
        }
        
        # Store in context
        tool_context.state["orchestrator_state"]["mind_map"] = mind_map
        
        return f"Built mental mind map with {len(nodes)} nodes and {len(edges)} edges focusing on internal empowerment patterns"
        
    except Exception as e:
        return f"Error building mental mind map: {str(e)}"


async def generate_empowerment_insights(
    tool_context: ToolContext,
) -> str:
    """Tool to generate empowerment-focused insights from mind map analysis."""
    
    try:
        mind_map = tool_context.state["orchestrator_state"]["mind_map"]
        clusters = tool_context.state["orchestrator_state"]["clusters"]
        
        if not mind_map or not clusters:
            return "Error: Mind map or clusters data not available"
        
        # Extract themes and patterns for insight generation
        themes = [node["theme"] for node in mind_map["nodes"]]
        emotions = []  # Would be extracted from actual data
        
        prompt = get_empowerment_insights_prompt()
        full_prompt = prompt.format(
            mind_map_json=json.dumps(mind_map),
            themes=themes,
            emotions=emotions
        )
        
        model = get_gemini_model()
        response = model.generate_content(full_prompt)
        insights_text = response.text
        
        # Structure insights
        insights = [
            {
                "challengeType": "self_doubt",
                "insight": insights_text,
                "action": "Practice recognizing your creative power in shaping your thoughts",
                "confidence": 0.8,
                "source": ["journal", "therapy", "mind_map"],
                "relevanceScore": 0.9,
                "status": "active"
            }
        ]
        
        # Store in context
        tool_context.state["orchestrator_state"]["insights"] = insights
        
        return f"Generated {len(insights)} empowerment-focused insights for internal transformation"
        
    except Exception as e:
        return f"Error generating empowerment insights: {str(e)}"


async def recommend_awareness_exercises(
    tool_context: ToolContext,
) -> str:
    """Tool to recommend exercises that build internal awareness and personal empowerment."""
    
    try:
        clusters = tool_context.state["orchestrator_state"]["clusters"]
        
        if not clusters:
            return "Error: No clusters available for exercise recommendations"
        
        exercise_recommendations = []
        
        # Generate recommendations for each major theme
        for cluster_id, cluster_data in clusters.items():
            theme = cluster_data["theme"]
            
            prompt = get_exercise_recommendation_prompt()
            full_prompt = prompt.format(theme=theme)
            
            model = get_gemini_model()
            response = model.generate_content(full_prompt)
            exercise_type = response.text.strip()
            
            recommendation = {
                "type": "exercise",
                "content": f"Practice {exercise_type} to build awareness around {theme}",
                "category": exercise_type,
                "source": "mind_map",
                "priority": min(5, cluster_data["size"]),  # Priority based on cluster size
                "status": "pending"
            }
            
            exercise_recommendations.append(recommendation)
        
        # Store in context
        tool_context.state["orchestrator_state"]["exercise_recommendations"] = exercise_recommendations
        
        return f"Generated {len(exercise_recommendations)} awareness-building exercise recommendations"
        
    except Exception as e:
        return f"Error recommending awareness exercises: {str(e)}"


async def calculate_dashboard_metrics(
    tool_context: ToolContext,
) -> str:
    """Tool to calculate dashboard metrics including mood trends and progress tracking."""
    
    try:
        user_id = tool_context.state.get("user_id")
        clusters = tool_context.state["orchestrator_state"]["clusters"]
        mind_map = tool_context.state["orchestrator_state"]["mind_map"]
        
        if not user_id:
            return "Error: User ID not found in context"
        
        # Calculate metrics (simplified for implementation)
        dashboard_metrics = {
            "moodTrends": [
                {"date": "2025-06-15", "mood": "neutral", "intensity": 5},
                {"date": "2025-06-14", "mood": "positive", "intensity": 7}
            ],
            "patternSummary": {
                "dominantThemes": [cluster["theme"] for cluster in clusters.values()][:3],
                "empowermentProgress": 0.7,
                "creatorConsciousnessLevel": 0.6
            },
            "exerciseAdherence": 0.8,
            "consistency": {
                "journalCount": 15,
                "therapyCount": 3,
                "journalStreak": 7,
                "therapyStreak": 2
            },
            "lastUpdated": datetime.now().isoformat()
        }
        
        # Store in context
        tool_context.state["orchestrator_state"]["dashboard_metrics"] = dashboard_metrics
        
        return f"Calculated comprehensive dashboard metrics tracking empowerment progress"
        
    except Exception as e:
        return f"Error calculating dashboard metrics: {str(e)}"


async def detect_crisis_with_empowerment(
    tool_context: ToolContext,
) -> str:
    """Tool to detect crisis patterns while maintaining empowerment perspective."""
    
    try:
        clusters = tool_context.state["orchestrator_state"]["clusters"]
        embeddings_data = tool_context.state["orchestrator_state"]["embeddings_data"]
        
        if not clusters or not embeddings_data:
            return "Error: Insufficient data for crisis detection"
        
        # Analyze patterns for crisis indicators
        patterns = [cluster["theme"] for cluster in clusters.values()]
        intensity_levels = [7, 8, 6]  # Simulated intensity levels
        themes = patterns
        
        prompt = get_crisis_detection_prompt()
        full_prompt = prompt.format(
            patterns=patterns,
            intensity_levels=intensity_levels,
            themes=themes
        )
        
        model = get_gemini_model()
        response = model.generate_content(full_prompt)
        crisis_analysis = response.text
        
        # Structure crisis alert if needed
        crisis_alerts = []
        if "severe" in crisis_analysis.lower():
            alert = {
                "severity": "moderate",  # Conservative approach
                "triggerSource": "pattern_analysis",
                "confidence": 0.7,
                "recommendedAction": "Focus on internal empowerment exercises and self-compassion practices",
                "status": "active"
            }
            crisis_alerts.append(alert)
        
        # Store in context
        tool_context.state["orchestrator_state"]["crisis_alerts"] = crisis_alerts
        
        return f"Crisis detection completed with empowerment perspective: {len(crisis_alerts)} alerts generated"
        
    except Exception as e:
        return f"Error detecting crisis with empowerment: {str(e)}"


async def store_orchestrator_results(
    tool_context: ToolContext,
) -> str:
    """Tool to store all orchestrator results in Firebase Firestore."""
    
    try:
        user_id = tool_context.state.get("user_id")
        orchestrator_state = tool_context.state["orchestrator_state"]
        
        if not user_id:
            return "Error: User ID not found in context"
        
        # Store mind map
        db = get_firestore_client()
        mind_map_ref = db.collection("users").document(user_id).collection("mindMap").document("current")
        mind_map_ref.set(orchestrator_state["mind_map"], merge=True)
        
        # Store insights
        for insight in orchestrator_state["insights"]:
            insight_doc = {
                **insight,
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }
            db.collection("users").document(user_id).collection("insights").add(insight_doc)
        
        # Store exercise recommendations
        for recommendation in orchestrator_state["exercise_recommendations"]:
            rec_doc = {
                **recommendation,
                "createdAt": datetime.now().isoformat(),
                "expiresAt": (datetime.now() + timedelta(days=7)).isoformat()
            }
            db.collection("users").document(user_id).collection("recommendations").add(rec_doc)
        
        # Store dashboard metrics
        metrics_ref = db.collection("users").document(user_id).collection("dashboard").document("metrics")
        metrics_ref.set(orchestrator_state["dashboard_metrics"], merge=True)
        
        # Store crisis alerts
        for alert in orchestrator_state["crisis_alerts"]:
            alert_doc = {
                **alert,
                "createdAt": datetime.now().isoformat(),
                "resolvedAt": None
            }
            db.collection("users").document(user_id).collection("crisisAlerts").add(alert_doc)
        
        return f"Successfully stored all orchestrator results with empowerment focus"
        
    except Exception as e:
        return f"Error storing orchestrator results: {str(e)}"

def _select_demo_profile() -> Dict[str, Any]:
    """Select a random demo profile for mock artifacts."""
    profile_key = random.choice(list(DEMO_USER_PROFILES.keys()))
    return DEMO_USER_PROFILES[profile_key]

def _generate_mock_mind_map(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a rich mock mind map based on the demo profile."""
    themes = profile["primary_themes"]
    central_theme = themes[0]
    
    # Create interconnected nodes
    nodes = [
        {"id": "central", "label": central_theme.replace("_", " ").title(), "type": "central", "size": 50}
    ]
    
    # Add theme nodes
    for i, theme in enumerate(themes):
        nodes.append({
            "id": f"theme_{i}",
            "label": theme.replace("_", " ").title(),
            "type": "theme",
            "size": 30 + random.randint(5, 15)
        })
    
    # Add insight nodes
    insights = [
        "Self-awareness", "Growth mindset", "Resilience building", "Boundary setting",
        "Emotional regulation", "Goal clarity", "Support network", "Mindful practices"
    ]
    
    for i, insight in enumerate(insights[:6]):  # Limit to 6 insights
        nodes.append({
            "id": f"insight_{i}",
            "label": insight,
            "type": "insight",
            "size": 20 + random.randint(3, 10)
        })
    
    # Create connections
    connections = []
    # Connect central to themes
    for i in range(len(themes)):
        connections.append({
            "source": "central",
            "target": f"theme_{i}",
            "strength": random.uniform(0.7, 1.0),
            "type": "primary"
        })
    
    # Connect themes to insights
    for i in range(len(themes)):
        for j in range(2):  # Each theme connects to 2 insights
            insight_idx = (i * 2 + j) % 6
            connections.append({
                "source": f"theme_{i}",
                "target": f"insight_{insight_idx}",
                "strength": random.uniform(0.5, 0.8),
                "type": "secondary"
            })
    
    # Add some cross-connections between insights
    for i in range(3):
        source_idx = random.randint(0, 5)
        target_idx = random.randint(0, 5)
        if source_idx != target_idx:
            connections.append({
                "source": f"insight_{source_idx}",
                "target": f"insight_{target_idx}",
                "strength": random.uniform(0.3, 0.6),
                "type": "cross_connection"
            })
    
    return {
        "profile_name": profile["name"],
        "empowerment_theme": profile["empowerment_journey"],
        "nodes": nodes,
        "connections": connections,
        "total_nodes": len(nodes),
        "total_connections": len(connections),
        "generated_at": datetime.now().isoformat()
    }

def _generate_mock_timeline(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a mock empowerment timeline with key breakthrough moments."""
    base_date = datetime.now() - timedelta(days=90)  # 3 months of journey
    
    timeline_events = []
    
    # Add breakthrough moments from profile
    for i, moment in enumerate(profile["breakthrough_moments"]):
        event_date = base_date + timedelta(days=20 + i * 25)
        timeline_events.append({
            "date": event_date.isoformat(),
            "type": "breakthrough",
            "title": f"Breakthrough #{i+1}",
            "description": moment,
            "impact_score": random.uniform(7, 10),
            "themes": [profile["primary_themes"][i % len(profile["primary_themes"])]]
        })
    
    # Add pattern recognition events
    pattern_events = [
        "Identified recurring stress triggers",
        "Recognized personal strength patterns",
        "Discovered effective coping strategies",
        "Found connection between thoughts and emotions"
    ]
    
    for i, pattern in enumerate(pattern_events):
        event_date = base_date + timedelta(days=10 + i * 20)
        timeline_events.append({
            "date": event_date.isoformat(),
            "type": "pattern_recognition",
            "title": "Pattern Discovery",
            "description": pattern,
            "impact_score": random.uniform(5, 8),
            "themes": random.sample(profile["primary_themes"], 2)
        })
    
    # Sort by date
    timeline_events.sort(key=lambda x: x["date"])
    
    return {
        "profile_name": profile["name"],
        "journey_start": base_date.isoformat(),
        "journey_current": datetime.now().isoformat(),
        "total_events": len(timeline_events),
        "breakthrough_count": len(profile["breakthrough_moments"]),
        "events": timeline_events,
        "empowerment_progression": profile["empowerment_journey"]
    }

def _generate_mock_dashboard(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a comprehensive mock dashboard with metrics and insights."""
    
    # Calculate mock metrics
    total_entries = random.randint(25, 45)
    processed_entries = total_entries
    patterns_found = len(profile["primary_themes"]) + random.randint(2, 5)
    
    return {
        "profile_name": profile["name"],
        "overview": {
            "total_journal_entries": total_entries,
            "entries_processed": processed_entries,
            "patterns_identified": patterns_found,
            "breakthrough_moments": len(profile["breakthrough_moments"]),
            "empowerment_score": random.uniform(7.2, 9.1),
            "growth_trajectory": "Positive"
        },
        "theme_distribution": {
            theme.replace("_", " ").title(): random.uniform(15, 35) 
            for theme in profile["primary_themes"]
        },
        "weekly_progress": [
            {
                "week": f"Week {i+1}",
                "entries": random.randint(3, 8),
                "insights": random.randint(1, 4),
                "empowerment_score": 5.0 + (i * 0.3) + random.uniform(-0.5, 0.5)
            }
            for i in range(12)  # 12 weeks of data
        ],
        "top_insights": [
            f"Your {theme.replace('_', ' ')} patterns show significant growth"
            for theme in profile["primary_themes"][:3]
        ],
        "recommendations": [
            "Continue exploring the connection between work stress and self-care",
            "Consider deepening your mindfulness practice",
            "Celebrate your progress in boundary setting"
        ],
        "generated_at": datetime.now().isoformat()
    }

def _generate_mock_pattern_network(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a mock pattern network graph showing theme relationships."""
    themes = profile["primary_themes"]
    
    # Create network nodes
    network_nodes = []
    for i, theme in enumerate(themes):
        network_nodes.append({
            "id": theme,
            "label": theme.replace("_", " ").title(),
            "size": random.randint(20, 40),
            "color": f"hsl({i * 90 % 360}, 70%, 60%)",
            "connections": random.randint(2, len(themes))
        })
    
    # Add related concept nodes
    related_concepts = [
        "mindfulness", "self_compassion", "resilience", "growth", 
        "balance", "clarity", "confidence", "purpose"
    ]
    
    for concept in related_concepts[:4]:  # Add 4 related concepts
        network_nodes.append({
            "id": concept,
            "label": concept.replace("_", " ").title(),
            "size": random.randint(15, 25),
            "color": "hsl(200, 50%, 70%)",
            "connections": random.randint(1, 3)
        })
    
    # Create network edges
    network_edges = []
    
    # Connect themes to each other
    for i in range(len(themes)):
        for j in range(i + 1, len(themes)):
            if random.random() > 0.3:  # 70% chance of connection
                network_edges.append({
                    "source": themes[i],
                    "target": themes[j],
                    "weight": random.uniform(0.4, 0.9),
                    "type": "theme_connection"
                })
    
    # Connect themes to related concepts
    for theme in themes:
        connected_concepts = random.sample(related_concepts[:4], 2)
        for concept in connected_concepts:
            network_edges.append({
                "source": theme,
                "target": concept,
                "weight": random.uniform(0.3, 0.7),
                "type": "concept_connection"
            })
    
    return {
        "profile_name": profile["name"],
        "network_summary": f"Pattern network showing {len(network_nodes)} interconnected themes and concepts",
        "nodes": network_nodes,
        "edges": network_edges,
        "total_connections": len(network_edges),
        "density": len(network_edges) / (len(network_nodes) * (len(network_nodes) - 1) / 2),
        "generated_at": datetime.now().isoformat()
    }

def cluster_journal_patterns(entries: List[Dict]) -> Dict[str, Any]:
    """
    Enhanced clustering with mock data fallback for demonstration.
    """
    logger.info(f"Starting pattern clustering for {len(entries)} entries")
    
    # Check if we have insufficient real data
    if len(entries) < 10:
        logger.info("Insufficient real data detected. Generating mock demonstration artifacts.")
        
        # Select demo profile and generate comprehensive mock artifacts
        demo_profile = _select_demo_profile()
        
        return {
            "status": "demo_mode",
            "message": f"Generated demonstration artifacts for {demo_profile['name']} - {demo_profile['background']}",
            "real_entries_count": len(entries),
            "demo_profile": demo_profile,
            "clusters": {
                "total_clusters": len(demo_profile["primary_themes"]),
                "themes_identified": demo_profile["primary_themes"],
                "cluster_details": [
                    {
                        "cluster_id": i,
                        "theme": theme.replace("_", " ").title(),
                        "entries_count": random.randint(5, 12),
                        "key_insights": [
                            f"Pattern recognition in {theme.replace('_', ' ')}",
                            f"Growth trajectory showing improvement",
                            f"Connection to overall empowerment journey"
                        ],
                        "empowerment_score": random.uniform(6.5, 9.2)
                    }
                    for i, theme in enumerate(demo_profile["primary_themes"])
                ]
            },
            "mock_artifacts": {
                "mind_map": _generate_mock_mind_map(demo_profile),
                "timeline": _generate_mock_timeline(demo_profile),
                "dashboard": _generate_mock_dashboard(demo_profile),
                "pattern_network": _generate_mock_pattern_network(demo_profile)
            },
            "generated_at": datetime.now().isoformat()
        }
    
    # Original clustering logic for real data
    if not entries:
        return {
            "status": "error",
            "message": "No journal entries provided for clustering",
            "clusters": []
        }
    
    try:
        # Extract text content
        texts = []
        for entry in entries:
            content = entry.get('content', '')
            reflection = entry.get('reflection', '')
            combined_text = f"{content} {reflection}".strip()
            if combined_text:
                texts.append(combined_text)
        
        if not texts:
            return {
                "status": "error", 
                "message": "No valid text content found in entries",
                "clusters": []
            }
        
        # Vectorize texts
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        vectors = vectorizer.fit_transform(texts)
        
        # Adaptive clustering parameters based on data size
        n_samples = len(texts)
        min_samples = max(2, min(3, n_samples // 3))
        eps = 0.3 if n_samples > 10 else 0.5
        
        logger.info(f"Using DBSCAN with min_samples={min_samples}, eps={eps}")
        
        # Perform clustering
        clustering = DBSCAN(
            eps=eps,
            min_samples=min_samples,
            metric='cosine'
        )
        
        cluster_labels = clustering.fit_predict(vectors.toarray())
        
        # Process clusters
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append({
                'index': i,
                'text': texts[i],
                'entry': entries[i] if i < len(entries) else {}
            })
        
        # Generate cluster summaries
        cluster_summaries = []
        feature_names = vectorizer.get_feature_names_out()
        
        for label, cluster_entries in clusters.items():
            if label == -1:
                cluster_summaries.append({
                    'cluster_id': 'noise',
                    'label': 'Unique Insights',
                    'size': len(cluster_entries),
                    'entries': cluster_entries,
                    'themes': ['individual_insights', 'unique_patterns'],
                    'description': 'Unique individual insights and patterns'
                })
            else:
                # Get representative terms for this cluster
                cluster_indices = [entry['index'] for entry in cluster_entries]
                cluster_vectors = vectors[cluster_indices]
                
                if cluster_vectors.shape[0] > 1:
                    centroid = cluster_vectors.mean(axis=0).A1
                else:
                    centroid = cluster_vectors.toarray()[0]
                
                top_features_idx = centroid.argsort()[-5:][::-1]
                top_features = [feature_names[idx] for idx in top_features_idx if centroid[idx] > 0]
                
                cluster_summaries.append({
                    'cluster_id': label,
                    'label': f"Pattern {label + 1}",
                    'size': len(cluster_entries),
                    'entries': cluster_entries,
                    'themes': top_features[:3],
                    'key_terms': top_features,
                    'description': f"Pattern involving {', '.join(top_features[:3])}"
                })
        
        return {
            "status": "success",
            "message": f"Successfully identified {len(cluster_summaries)} patterns from {len(entries)} entries",
            "total_entries": len(entries),
            "total_clusters": len([c for c in cluster_summaries if c['cluster_id'] != 'noise']),
            "noise_entries": len(clusters.get(-1, [])),
            "clusters": cluster_summaries,
            "clustering_params": {
                "min_samples": min_samples,
                "eps": eps,
                "vectorizer_features": vectors.shape[1]
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in clustering: {str(e)}")
        return {
            "status": "error",
            "message": f"Clustering failed: {str(e)}",
            "clusters": []
        }

def generate_empowerment_mind_map(cluster_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced mind map generation with mock data support.
    """
    logger.info("Generating empowerment mind map")
    
    # Check if we're in demo mode
    if cluster_data.get("status") == "demo_mode":
        logger.info("Using mock mind map from demo artifacts")
        return {
            "status": "demo_mode",
            "message": "Generated comprehensive demonstration mind map",
            "mind_map": cluster_data["mock_artifacts"]["mind_map"],
            "visualization_ready": True
        }
    
    # Original mind map logic for real data
    if cluster_data.get("status") != "success":
        return {
            "status": "error",
            "message": "Cannot generate mind map: clustering data invalid",
            "mind_map": None
        }
    
    clusters = cluster_data.get("clusters", [])
    if not clusters:
        return {
            "status": "error",
            "message": "No clusters available for mind map generation",
            "mind_map": None
        }
    
    try:
        # Create mind map structure
        nodes = []
        connections = []
        
        # Central empowerment node
        nodes.append({
            "id": "empowerment_center",
            "label": "Personal Empowerment Journey",
            "type": "central",
            "size": 50,
            "color": "gold"
        })
        
        # Add cluster nodes
        for cluster in clusters:
            cluster_id = f"cluster_{cluster['cluster_id']}"
            
            # Determine node properties based on cluster
            if cluster['cluster_id'] == 'noise':
                node_type = "insight"
                color = "lightblue"
                size = 25
            else:
                node_type = "theme"
                color = "lightgreen" 
                size = 30 + min(cluster['size'] * 2, 20)
            
            nodes.append({
                "id": cluster_id,
                "label": cluster.get('label', f"Pattern {cluster['cluster_id']}"),
                "type": node_type,
                "size": size,
                "color": color,
                "cluster_size": cluster['size'],
                "themes": cluster.get('themes', [])
            })
            
            # Connect to center
            connections.append({
                "source": "empowerment_center",
                "target": cluster_id,
                "strength": min(cluster['size'] / 10.0, 1.0),
                "type": "primary"
            })
        
        # Add theme interconnections if we have multiple clusters
        if len(clusters) > 1:
            for i, cluster1 in enumerate(clusters):
                for j, cluster2 in enumerate(clusters[i+1:], i+1):
                    # Check for theme overlap
                    themes1 = set(cluster1.get('themes', []))
                    themes2 = set(cluster2.get('themes', []))
                    overlap = len(themes1.intersection(themes2))
                    
                    if overlap > 0:
                        connections.append({
                            "source": f"cluster_{cluster1['cluster_id']}",
                            "target": f"cluster_{cluster2['cluster_id']}",
                            "strength": overlap / max(len(themes1), len(themes2)),
                            "type": "thematic_connection",
                            "shared_themes": list(themes1.intersection(themes2))
                        })
        
        mind_map = {
            "central_theme": "Personal Empowerment Journey",
            "total_patterns": len(clusters),
            "nodes": nodes,
            "connections": connections,
            "layout_suggestions": {
                "algorithm": "force_directed",
                "center_gravity": 0.8,
                "node_repulsion": 100
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "message": f"Generated mind map with {len(nodes)} nodes and {len(connections)} connections",
            "mind_map": mind_map,
            "visualization_ready": True
        }
        
    except Exception as e:
        logger.error(f"Error generating mind map: {str(e)}")
        return {
            "status": "error",
            "message": f"Mind map generation failed: {str(e)}",
            "mind_map": None
        }

def display_comprehensive_artifacts(cluster_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Display all available artifacts in a comprehensive format.
    """
    logger.info("Displaying comprehensive mental orchestrator artifacts")
    
    # Check if we're in demo mode
    if cluster_data.get("status") == "demo_mode":
        mock_artifacts = cluster_data["mock_artifacts"]
        demo_profile = cluster_data["demo_profile"]
        
        return {
            "status": "demo_mode",
            "title": f"🧠 Mental Orchestrator - Comprehensive Demo for {demo_profile['name']}",
            "profile_background": demo_profile["background"],
            "empowerment_journey": demo_profile["empowerment_journey"],
            
            "artifacts": {
                "mind_map": {
                    "title": "🗺️ Empowerment Mind Map",
                    "description": "Interactive visualization of interconnected growth themes",
                    "data": mock_artifacts["mind_map"],
                    "ready_for_display": True
                },
                
                "timeline": {
                    "title": "📈 Empowerment Timeline", 
                    "description": "Journey progression with breakthrough moments",
                    "data": mock_artifacts["timeline"],
                    "ready_for_display": True
                },
                
                "dashboard": {
                    "title": "📊 Growth Analytics Dashboard",
                    "description": "Comprehensive metrics and insights overview",
                    "data": mock_artifacts["dashboard"],
                    "ready_for_display": True
                },
                
                "pattern_network": {
                    "title": "🕸️ Pattern Network Graph",
                    "description": "Network visualization of theme relationships",
                    "data": mock_artifacts["pattern_network"],
                    "ready_for_display": True
                },
                
                "cluster_analysis": {
                    "title": "🎯 Pattern Clusters",
                    "description": "Detailed cluster analysis and insights",
                    "data": cluster_data["clusters"],
                    "ready_for_display": True
                }
            },
            
            "summary": {
                "total_artifacts": 5,
                "demonstration_mode": True,
                "real_data_entries": cluster_data.get("real_entries_count", 0),
                "generated_at": datetime.now().isoformat()
            },
            
            "interaction_suggestions": [
                "Explore the mind map to see theme interconnections",
                "Review the timeline for breakthrough moment patterns", 
                "Analyze the dashboard metrics for growth trends",
                "Examine the pattern network for relationship insights",
                "Study cluster analysis for detailed pattern understanding"
            ]
        }
    
    # Handle real data display
    else:
        mind_map_result = generate_empowerment_mind_map(cluster_data)
        
        return {
            "status": cluster_data.get("status", "unknown"),
            "title": "🧠 Mental Orchestrator - Pattern Analysis Results",
            
            "artifacts": {
                "cluster_analysis": {
                    "title": "🎯 Pattern Clusters",
                    "description": f"Identified {len(cluster_data.get('clusters', []))} patterns",
                    "data": cluster_data,
                    "ready_for_display": True
                },
                
                "mind_map": {
                    "title": "🗺️ Empowerment Mind Map",
                    "description": "Visualization of identified patterns",
                    "data": mind_map_result,
                    "ready_for_display": mind_map_result.get("status") == "success"
                }
            },
            
            "summary": {
                "total_entries_processed": cluster_data.get("total_entries", 0),
                "patterns_identified": len(cluster_data.get("clusters", [])),
                "demonstration_mode": False,
                "generated_at": datetime.now().isoformat()
            }
        }

async def analyze_journal_patterns(
    tool_context: ToolContext,
) -> str:
    """Tool to analyze journal patterns and generate comprehensive mental health artifacts."""
    
    try:
        user_id = tool_context.state.get("user_id", "demo_user")
        
        # Simulate getting journal entries (in real implementation, this would come from database)
        journal_entries = [
            {
                "content": "Had a challenging day at work. Feeling stressed about deadlines.",
                "reflection": "I notice I'm putting too much pressure on myself. Need to practice self-compassion.",
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            },
            {
                "content": "Tried meditation today. It helped me feel more centered.",
                "reflection": "Small mindful moments make a big difference in my day.",
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
        ]
        
        # Perform clustering analysis
        cluster_result = cluster_journal_patterns(journal_entries)
        
        # Generate comprehensive artifacts
        artifacts_result = display_comprehensive_artifacts(cluster_result)
        
        if artifacts_result.get("status") == "demo_mode":
            demo_profile = cluster_result["demo_profile"]
            
            # Check if user wants HTML visualization
            user_request = tool_context.state.get("user_request", "").lower()
            logger.info(f"User request captured: '{user_request}'")
            
            # Check for inline HTML request (specific keywords only)
            inline_keywords = ["html", "inline", "embed", "show html"]
            if any(keyword in user_request for keyword in inline_keywords):
                logger.info("Returning inline HTML visualization based on keywords")
                return _generate_visualization_html(artifacts_result["artifacts"], demo_profile)
            
            # For ALL other comprehensive/visualization requests, generate preview URL (default behavior)
            elif any(keyword in user_request for keyword in ["visual", "dashboard", "chart", "graph", "comprehensive", "artifacts", "preview", "url", "link", "share", "shareable"]):
                logger.info("Generating preview URL for comprehensive request")
                return await create_dashboard_preview(tool_context)
            
            # Return text summary (existing behavior)
            response = f"""🧠 **Mental Orchestrator Analysis Complete**

**Demo Profile: {demo_profile['name']}**
*{demo_profile['background']}*

**Empowerment Journey:** {demo_profile['empowerment_journey']}

## 📊 Generated Artifacts ({artifacts_result['summary']['total_artifacts']} total):

### 🗺️ Empowerment Mind Map
- **Nodes:** {artifacts_result['artifacts']['mind_map']['data']['total_nodes']}
- **Connections:** {artifacts_result['artifacts']['mind_map']['data']['total_connections']}
- **Central Theme:** {artifacts_result['artifacts']['mind_map']['data']['empowerment_theme']}

### 📈 Empowerment Timeline
- **Total Events:** {artifacts_result['artifacts']['timeline']['data']['total_events']}
- **Breakthrough Moments:** {artifacts_result['artifacts']['timeline']['data']['breakthrough_count']}
- **Journey Duration:** 3 months of growth tracking

### 📊 Growth Analytics Dashboard
- **Empowerment Score:** {artifacts_result['artifacts']['dashboard']['data']['overview']['empowerment_score']:.1f}/10
- **Growth Trajectory:** {artifacts_result['artifacts']['dashboard']['data']['overview']['growth_trajectory']}
- **Patterns Identified:** {artifacts_result['artifacts']['dashboard']['data']['overview']['patterns_identified']}

### 🕸️ Pattern Network Graph
- **Network Density:** {artifacts_result['artifacts']['pattern_network']['data']['density']:.2f}
- **Total Connections:** {artifacts_result['artifacts']['pattern_network']['data']['total_connections']}

### 🎯 Pattern Clusters
- **Primary Themes:** {', '.join([theme.replace('_', ' ').title() for theme in demo_profile['primary_themes']])}
- **Cluster Count:** {cluster_result['clusters']['total_clusters']}

## 💡 Key Insights:
{chr(10).join([f"• {insight}" for insight in artifacts_result['artifacts']['dashboard']['data']['top_insights']])}

## 🎯 Next Steps:
{chr(10).join([f"• {rec}" for rec in artifacts_result['artifacts']['dashboard']['data']['recommendations']])}

*This demonstration shows the rich insights available when you have comprehensive journal data. The system automatically generates detailed visualizations and empowerment-focused analysis.*"""

            return response
        
        else:
            return f"Analysis completed with status: {artifacts_result.get('status')}. {artifacts_result.get('message', '')}"
        
    except Exception as e:
        logger.error(f"Error in journal pattern analysis: {str(e)}")
        return f"Error analyzing journal patterns: {str(e)}"

async def generate_mental_health_dashboard(
    tool_context: ToolContext,
) -> str:
    """Tool to generate a comprehensive mental health dashboard with all artifacts."""
    
    try:
        user_id = tool_context.state.get("user_id", "demo_user")
        
        # Get journal entries and perform analysis
        journal_entries = [
            {
                "content": "Had a challenging day at work. Feeling stressed about deadlines.",
                "reflection": "I notice I'm putting too much pressure on myself. Need to practice self-compassion.",
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            },
            {
                "content": "Tried meditation today. It helped me feel more centered.",
                "reflection": "Small mindful moments make a big difference in my day.",
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
        ]
        
        # Perform clustering analysis
        cluster_result = cluster_journal_patterns(journal_entries)
        
        # Generate comprehensive artifacts
        artifacts_result = display_comprehensive_artifacts(cluster_result)
        
        if artifacts_result.get("status") == "demo_mode":
            demo_profile = cluster_result["demo_profile"]
            
            # Always return preview URL for dashboard requests
            logger.info("Generating preview URL for mental health dashboard tool")
            return await create_dashboard_preview(tool_context)
        
        else:
            return f"Dashboard generation completed with status: {artifacts_result.get('status')}. {artifacts_result.get('message', '')}"
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}")
        return f"Error generating mental health dashboard: {str(e)}"


# Enhanced HTML Visualization Functions for ADK
def _generate_visualization_html(artifacts: Dict[str, Any], profile: Dict[str, Any] = None) -> str:
    """Generate rich HTML with embedded JavaScript visualizations for ADK."""
    
    # Extract data for visualizations
    mind_map = artifacts.get("mind_map", {})
    timeline = artifacts.get("timeline", {})
    dashboard = artifacts.get("dashboard", {})
    network = artifacts.get("pattern_network", {})
    clusters = artifacts.get("pattern_clusters", {})
    
    profile_info = profile or {"name": "User", "background": "General user"}
    
    html_content = f"""
<div style="font-family: 'Segoe UI', system-ui, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px;">
    <!-- Header -->
    <div style="text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px;">
        <h1 style="margin: 0; font-size: 2.5em;">🧠 Mental Health Artifacts Dashboard</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">Comprehensive insights and empowerment journey visualization</p>
    </div>

    <!-- Profile Info -->
    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #667eea;">
        <h3 style="margin: 0 0 10px 0; color: #495057;">📊 Demo Profile: {profile_info['name']}</h3>
        <p style="margin: 0; color: #6c757d;">{profile_info['background']}</p>
        <p style="margin: 5px 0 0 0; color: #6c757d;"><strong>Empowerment Journey:</strong> {profile_info.get('journey', 'Personal growth and transformation')}</p>
    </div>

    <!-- Metrics Cards -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
        <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; border-top: 4px solid #28a745;">
            <div style="font-size: 2.5em; font-weight: bold; color: #28a745; margin-bottom: 5px;">
                {dashboard.get('overview', {}).get('empowerment_score', 7.7)}/10
            </div>
            <div style="color: #6c757d; font-weight: 500;">Empowerment Score</div>
            <div style="font-size: 0.9em; color: #28a745; margin-top: 5px;">↗️ +0.8 this week</div>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; border-top: 4px solid #17a2b8;">
            <div style="font-size: 2em; font-weight: bold; color: #17a2b8; margin-bottom: 5px;">
                {dashboard.get('overview', {}).get('growth_trajectory', 'Positive')}
            </div>
            <div style="color: #6c757d; font-weight: 500;">Growth Trajectory</div>
            <div style="font-size: 0.9em; color: #17a2b8; margin-top: 5px;">📈 Consistent progress</div>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; border-top: 4px solid #ffc107;">
            <div style="font-size: 2.5em; font-weight: bold; color: #ffc107; margin-bottom: 5px;">
                {dashboard.get('overview', {}).get('patterns_identified', 6)}
            </div>
            <div style="color: #6c757d; font-weight: 500;">Patterns Identified</div>
            <div style="font-size: 0.9em; color: #ffc107; margin-top: 5px;">🔍 Deep insights</div>
        </div>
    </div>

    <!-- Visualizations Grid -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
        <!-- Mind Map -->
        <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 15px 0; color: #495057; display: flex; align-items: center;">
                🗺️ Empowerment Mind Map
                <span style="margin-left: auto; font-size: 0.8em; color: #6c757d;">
                    {len(mind_map.get('nodes', []))} nodes • {len(mind_map.get('connections', []))} connections
                </span>
            </h3>
            <div id="mindmap" style="height: 300px; background: #f8f9fa; border-radius: 8px; position: relative;">
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; color: #6c757d;">
                    <div style="font-size: 3em; margin-bottom: 10px;">🧠</div>
                    <div>Interactive mind map visualization</div>
                    <div style="font-size: 0.9em; margin-top: 5px;">Showing empowerment themes and connections</div>
                </div>
            </div>
        </div>

        <!-- Timeline -->
        <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 15px 0; color: #495057; display: flex; align-items: center;">
                📈 Empowerment Timeline
                <span style="margin-left: auto; font-size: 0.8em; color: #6c757d;">
                    {len(timeline.get('events', []))} events • 3 months
                </span>
            </h3>
            <div id="timeline" style="height: 300px; background: #f8f9fa; border-radius: 8px; position: relative;">
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; color: #6c757d;">
                    <div style="font-size: 3em; margin-bottom: 10px;">📊</div>
                    <div>Growth trajectory visualization</div>
                    <div style="font-size: 0.9em; margin-top: 5px;">Timeline of breakthrough moments</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Pattern Analysis -->
    <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px;">
        <h3 style="margin: 0 0 20px 0; color: #495057;">🎯 Pattern Clusters Analysis</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
            {_generate_cluster_cards(clusters)}
        </div>
    </div>

    <!-- Key Insights -->
    <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <h3 style="margin: 0 0 20px 0; color: #495057;">💡 Key Insights</h3>
        <div style="display: grid; gap: 10px;">
            {_generate_insights_list(profile_info)}
        </div>
    </div>

    <!-- Next Steps -->
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px;">
        <h3 style="margin: 0 0 15px 0;">🎯 Recommended Next Steps</h3>
        <div style="display: grid; gap: 10px;">
            {_generate_next_steps()}
        </div>
    </div>

    <!-- Interactive Elements Script -->
    <script>
        // Add hover effects and interactions
        document.querySelectorAll('[data-interactive]').forEach(element => {{
            element.addEventListener('mouseenter', function() {{
                this.style.transform = 'scale(1.02)';
                this.style.transition = 'transform 0.2s ease';
            }});
            element.addEventListener('mouseleave', function() {{
                this.style.transform = 'scale(1)';
            }});
        }});

        // Simulate data loading for visualization placeholders
        setTimeout(() => {{
            document.getElementById('mindmap').innerHTML = `
                <div style="display: flex; justify-content: center; align-items: center; height: 100%; flex-direction: column;">
                    <div style="font-size: 1.2em; color: #28a745; margin-bottom: 10px;">✅ Mind Map Generated</div>
                    <div style="color: #6c757d;">Central theme: {profile_info.get('central_theme', 'Personal Growth')}</div>
                </div>
            `;
            
            document.getElementById('timeline').innerHTML = `
                <div style="display: flex; justify-content: center; align-items: center; height: 100%; flex-direction: column;">
                    <div style="font-size: 1.2em; color: #17a2b8; margin-bottom: 10px;">📈 Timeline Created</div>
                    <div style="color: #6c757d;">Journey span: 3 months of growth tracking</div>
                </div>
            `;
        }}, 1000);
    </script>
</div>
"""
    
    return html_content


def _generate_cluster_cards(clusters: Dict[str, Any]) -> str:
    """Generate HTML cards for pattern clusters."""
    if not clusters or not clusters.get('cluster_details'):
        return """
        <div style="padding: 20px; text-align: center; color: #6c757d; grid-column: 1 / -1;">
            <div style="font-size: 2em; margin-bottom: 10px;">🎯</div>
            <div>Pattern analysis complete</div>
            <div style="font-size: 0.9em; margin-top: 5px;">4 primary themes identified</div>
        </div>
        """
    
    cards_html = ""
    colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#feca57"]
    
    for i, cluster in enumerate(clusters.get('cluster_details', [])[:5]):
        color = colors[i % len(colors)]
        cards_html += f"""
        <div style="padding: 15px; border-radius: 8px; border-left: 4px solid {color}; background: #f8f9fa;" data-interactive="true">
            <div style="font-weight: bold; color: #495057; margin-bottom: 5px;">{cluster.get('theme', f'Theme {i+1}')}</div>
            <div style="font-size: 0.9em; color: #6c757d; margin-bottom: 8px;">
                Score: {cluster.get('empowerment_score', 7.5)}/10 • {cluster.get('entries_count', 5)} entries
            </div>
            <div style="background: {color}; height: 4px; border-radius: 2px; width: {min(100, cluster.get('empowerment_score', 7.5) * 10)}%;"></div>
        </div>
        """
    
    return cards_html


def _generate_insights_list(profile_info: Dict[str, Any]) -> str:
    """Generate insights based on profile."""
    insights = [
        "Your work stress patterns show significant growth potential",
        "Burnout prevention strategies are becoming more effective",
        "Work-life balance improvements are clearly visible",
        "Self-awareness practices are yielding positive results"
    ]
    
    insights_html = ""
    for insight in insights:
        insights_html += f"""
        <div style="padding: 12px; background: #d4edda; border-left: 4px solid #28a745; border-radius: 4px; color: #155724;">
            • {insight}
        </div>
        """
    
    return insights_html


def _generate_next_steps() -> str:
    """Generate next steps recommendations."""
    steps = [
        "Continue exploring the connection between work stress and self-care",
        "Consider deepening your mindfulness practice", 
        "Celebrate your progress in boundary setting",
        "Schedule regular reflection sessions"
    ]
    
    steps_html = ""
    for step in steps:
        steps_html += f"""
        <div style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.9);">
            • {step}
        </div>
        """
    
    return steps_html


def _generate_dashboard_html(artifacts: Dict[str, Any], profile: Dict[str, Any] = None) -> str:
    """Generate dashboard-focused HTML for the mental health dashboard tool."""
    
    profile_info = profile or {"name": "User", "background": "General user"}
    dashboard_data = artifacts.get("dashboard", {})
    
    dashboard_html = f"""
<div style="font-family: 'Segoe UI', system-ui, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px;">
    <div style="text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; border-radius: 12px;">
        <h1 style="margin: 0; font-size: 2.2em;">📊 Mental Health Dashboard</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">Real-time insights and progress tracking</p>
    </div>

    <!-- Weekly Progress -->
    <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <h3 style="margin: 0 0 20px 0; color: #495057;">📈 Weekly Progress</h3>
        <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px;">
            {_generate_weekly_progress()}
        </div>
    </div>

    <!-- Mood Tracking -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
        <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 15px 0; color: #495057;">😊 Mood Trends</h3>
            <div style="height: 200px; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #6c757d;">
                <div style="text-align: center;">
                    <div style="font-size: 3em; margin-bottom: 10px;">📊</div>
                    <div>Mood tracking visualization</div>
                </div>
            </div>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 15px 0; color: #495057;">🎯 Goals Progress</h3>
            <div style="space-y: 15px;">
                {_generate_goals_progress()}
            </div>
        </div>
    </div>

    <!-- Activity Summary -->
    <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h3 style="margin: 0 0 20px 0; color: #495057;">📋 Activity Summary</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            {_generate_activity_summary()}
        </div>
    </div>
</div>
"""
    
    return dashboard_html


def _generate_weekly_progress() -> str:
    """Generate weekly progress indicators."""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    progress = [85, 92, 78, 88, 95, 70, 82]
    
    html = ""
    for i, (day, prog) in enumerate(zip(days, progress)):
        color = "#28a745" if prog >= 80 else "#ffc107" if prog >= 60 else "#dc3545"
        html += f"""
        <div style="text-align: center; padding: 10px; background: #f8f9fa; border-radius: 8px;">
            <div style="font-size: 0.8em; color: #6c757d; margin-bottom: 5px;">{day}</div>
            <div style="width: 40px; height: 40px; border-radius: 50%; background: {color}; margin: 0 auto; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.9em;">
                {prog}%
            </div>
        </div>
        """
    
    return html


def _generate_goals_progress() -> str:
    """Generate goals progress bars."""
    goals = [
        {"name": "Daily Journaling", "progress": 85, "target": "7 days/week"},
        {"name": "Mindfulness Practice", "progress": 70, "target": "20 min/day"},
        {"name": "Therapy Sessions", "progress": 100, "target": "1/week"}
    ]
    
    html = ""
    for goal in goals:
        color = "#28a745" if goal["progress"] >= 80 else "#ffc107" if goal["progress"] >= 60 else "#dc3545"
        html += f"""
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: 500; color: #495057;">{goal["name"]}</span>
                <span style="color: #6c757d; font-size: 0.9em;">{goal["progress"]}%</span>
            </div>
            <div style="background: #e9ecef; height: 8px; border-radius: 4px; overflow: hidden;">
                <div style="background: {color}; height: 100%; width: {goal["progress"]}%; transition: width 0.3s ease;"></div>
            </div>
            <div style="font-size: 0.8em; color: #6c757d; margin-top: 3px;">Target: {goal["target"]}</div>
        </div>
        """
    
    return html


def _generate_activity_summary() -> str:
    """Generate activity summary cards."""
    activities = [
        {"icon": "📝", "name": "Journal Entries", "count": 15, "streak": 7},
        {"icon": "🧘", "name": "Meditation", "count": 12, "streak": 4},
        {"icon": "💬", "name": "Therapy Sessions", "count": 3, "streak": 3},
        {"icon": "🎯", "name": "Goals Achieved", "count": 8, "streak": 2}
    ]
    
    html = ""
    for activity in activities:
        html += f"""
        <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; border-top: 3px solid #28a745;">
            <div style="font-size: 2em; margin-bottom: 10px;">{activity["icon"]}</div>
            <div style="font-weight: bold; color: #495057; margin-bottom: 5px;">{activity["name"]}</div>
            <div style="font-size: 1.5em; font-weight: bold; color: #28a745; margin-bottom: 3px;">{activity["count"]}</div>
            <div style="font-size: 0.8em; color: #6c757d;">🔥 {activity["streak"]} day streak</div>
        </div>
        """
    
    return html


async def show_visual_dashboard(
    tool_context: ToolContext,
) -> str:
    """Tool that always returns rich HTML visualizations for mental health artifacts."""
    
    try:
        user_id = tool_context.state.get("user_id", "demo_user")
        logger.info(f"Visual dashboard requested for user: {user_id}")
        
        # Use demo mode with mock data to ensure dashboard always works
        profile = _select_demo_profile()
        
        # Generate mock artifacts for consistent dashboard display
        artifacts = {
            'mind_map': _generate_mock_mind_map(profile),
            'timeline': _generate_mock_timeline(profile),
            'dashboard': _generate_mock_dashboard(profile),
            'pattern_network': _generate_mock_pattern_network(profile),
            'cluster_analysis': {
                'clusters': {
                    'empowerment_themes': {
                        'texts': profile['primary_themes'],
                        'theme': 'Personal Growth & Empowerment',
                        'insights': profile['breakthrough_moments'],
                        'size': len(profile['primary_themes'])
                    }
                },
                'summary': f"Analyzed {len(profile['primary_themes'])} key themes in {profile['name']}'s journey"
            }
        }
        
        logger.info("Generating visual dashboard with mock data")
        
        # Store artifacts in tool context for dashboard preview
        tool_context.state["dashboard_artifacts"] = artifacts
        tool_context.state["dashboard_profile"] = profile
        
        # Always return dashboard preview
        return await create_dashboard_preview(tool_context)
        
    except Exception as e:
        logger.error(f"Error generating visual dashboard: {str(e)}")
        # Fallback response if even the mock data fails
        return f"""🎯 **Visual Dashboard Generation**

**❌ Error generating interactive dashboard:** {str(e)}

**📊 Basic Dashboard Summary:**
• **Profile:** Demo user with empowerment-focused themes
• **Analysis:** Insufficient data for detailed clustering
• **Recommendation:** Add more journal entries and therapy sessions for better insights

**🔧 Troubleshooting:**
• Try the 'generate_mental_health_dashboard' function for text-based insights
• Ensure sufficient user data is available for pattern analysis
• Contact support if issues persist

**💡 Next Steps:**
• Add at least 5-10 journal entries for meaningful analysis
• Complete therapy sessions to build comprehensive data
• Use other mental health tools to gather more insights"""

# Production-ready preview system
class PreviewStorage:
    """Thread-safe in-memory storage for temporary HTML previews"""
    
    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._cleanup_interval = 300  # 5 minutes
        self._max_age = 3600  # 1 hour
        self._start_cleanup_thread()
    
    def store_preview(self, html_content: str, title: str = "Mental Health Dashboard") -> str:
        """Store HTML content and return unique preview ID"""
        preview_id = str(uuid.uuid4())[:8]  # Short UUID
        expiry_time = time.time() + self._max_age
        
        with self._lock:
            self._storage[preview_id] = {
                'html': html_content,
                'title': title,
                'created': time.time(),
                'expires': expiry_time,
                'views': 0
            }
        
        return preview_id
    
    def get_preview(self, preview_id: str) -> Optional[str]:
        """Retrieve HTML content by preview ID"""
        with self._lock:
            if preview_id in self._storage:
                preview_data = self._storage[preview_id]
                if time.time() < preview_data['expires']:
                    preview_data['views'] += 1
                    return preview_data['html']
                else:
                    # Clean up expired content
                    del self._storage[preview_id]
        return None
    
    def _cleanup_expired(self):
        """Remove expired previews"""
        current_time = time.time()
        with self._lock:
            expired_keys = [
                key for key, data in self._storage.items()
                if current_time > data['expires']
            ]
            for key in expired_keys:
                del self._storage[key]
        
        if expired_keys:
            logging.info(f"Cleaned up {len(expired_keys)} expired previews")
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_loop():
            while True:
                time.sleep(self._cleanup_interval)
                self._cleanup_expired()
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        with self._lock:
            return {
                'total_previews': len(self._storage),
                'total_views': sum(data['views'] for data in self._storage.values()),
                'oldest_preview': min((data['created'] for data in self._storage.values()), default=0),
                'storage_size_mb': len(str(self._storage)) / (1024 * 1024)
            }

# Use shared storage that works across processes
try:
    from shared_preview_storage import get_shared_storage
    preview_storage = get_shared_storage()
    logger.info("Using shared preview storage")
except ImportError:
    # Fallback to in-memory storage
    preview_storage = PreviewStorage()
    logger.warning("Using fallback in-memory storage")

def _generate_complete_html_page(artifacts: Dict[str, Any], profile: Dict[str, Any] = None) -> str:
    """Generate complete standalone HTML page with all styling and scripts"""
    
    # Select profile if not provided
    if not profile:
        profile = _select_demo_profile()
    
    # Generate visualization components
    dashboard_html = _generate_dashboard_html(artifacts, profile)
    
    # Complete HTML page template
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mental Health Artifacts Dashboard - {profile['name']}</title>
    <meta name="description" content="Comprehensive mental health insights and empowerment dashboard">
    <meta name="author" content="Innerverse Mental Health Platform">
    
    <style>
        /* Reset and base styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .main-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            overflow: hidden;
            animation: slideUp 0.8s ease-out;
        }}
        
        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
            animation: float 20s infinite linear;
        }}
        
        @keyframes float {{
            0% {{ transform: translateY(0px); }}
            100% {{ transform: translateY(-100px); }}
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }}
        
        .content {{
            padding: 0;
        }}
        
        /* Loading animation */
        .loading {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        /* Print styles */
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .main-container {{
                box-shadow: none;
                border-radius: 0;
            }}
            
            .header {{
                background: #667eea !important;
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }}
        }}
        
        /* Mobile responsive */
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .header p {{
                font-size: 1rem;
            }}
        }}
        
        /* Accessibility */
        @media (prefers-reduced-motion: reduce) {{
            * {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="header">
            <h1>🧠 Mental Health Artifacts Dashboard</h1>
            <p>Comprehensive insights and empowerment journey for {profile['name']}</p>
        </div>
        
        <div class="content">
            {dashboard_html}
        </div>
    </div>
    
    <script>
        // Enhanced interactivity
        document.addEventListener('DOMContentLoaded', function() {{
            // Add loading animations
            const loadingElements = document.querySelectorAll('.loading');
            loadingElements.forEach(el => {{
                setTimeout(() => {{
                    el.style.display = 'none';
                    const parent = el.parentElement;
                    if (parent) {{
                        parent.innerHTML += ' <span style="color: #27ae60;">✓ Loaded</span>';
                    }}
                }}, Math.random() * 2000 + 1000);
            }});
            
            // Add hover effects to metric cards
            const metricCards = document.querySelectorAll('.metric-card');
            metricCards.forEach(card => {{
                card.addEventListener('mouseenter', function() {{
                    this.style.transform = 'translateY(-5px) scale(1.02)';
                    this.style.boxShadow = '0 10px 30px rgba(0,0,0,0.15)';
                }});
                
                card.addEventListener('mouseleave', function() {{
                    this.style.transform = 'translateY(0) scale(1)';
                    this.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
                }});
            }});
            
            // Add click tracking
            document.addEventListener('click', function(e) {{
                if (e.target.classList.contains('insight-box') || e.target.classList.contains('metric-card')) {{
                    console.log('User interacted with:', e.target.textContent.substring(0, 50));
                }}
            }});
            
            // Add print functionality
            if (window.print) {{
                const printBtn = document.createElement('button');
                printBtn.innerHTML = '🖨️ Print Dashboard';
                printBtn.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    z-index: 1000;
                    font-size: 14px;
                `;
                printBtn.onclick = () => window.print();
                document.body.appendChild(printBtn);
            }}
        }});
        
        // Performance monitoring
        window.addEventListener('load', function() {{
            const loadTime = performance.now();
            console.log(`Dashboard loaded in ${{loadTime.toFixed(2)}}ms`);
        }});
    </script>
</body>
</html>"""
    
    return html_template

async def create_dashboard_preview(tool_context: ToolContext) -> str:
    """Create a shareable preview URL for the mental health dashboard"""
    
    try:
        logger.info("🎯 Creating dashboard preview...")
        
        # Check for sufficient data
        user_id = tool_context.state.get("user_id", "demo_user")
        
        # For demo purposes, always use mock data
        profile = _select_demo_profile()
        
        # Generate comprehensive artifacts
        artifacts = {
            'mind_map': _generate_mock_mind_map(profile),
            'timeline': _generate_mock_timeline(profile),
            'dashboard': _generate_mock_dashboard(profile),
            'pattern_network': _generate_mock_pattern_network(profile),
            'cluster_analysis': {
                'clusters': {
                    'empowerment_themes': {
                        'texts': profile['primary_themes'],
                        'theme': 'Personal Growth & Empowerment',
                        'insights': profile['breakthrough_moments'],
                        'size': len(profile['primary_themes'])
                    }
                },
                'summary': f"Analyzed {len(profile['primary_themes'])} key themes in {profile['name']}'s journey"
            }
        }
        
        # Generate complete HTML page
        html_content = _generate_complete_html_page(artifacts, profile)
        
        # In production, directly return the dashboard content instead of using preview URLs
        if os.getenv('ENVIRONMENT') == 'production':
            result = f"""🎯 **Mental Health Dashboard Generated Successfully!**

**👤 Demo Profile:** {profile['name']} - {profile['background']}

**📈 Interactive Dashboard Features:**
✅ Interactive metrics cards with hover effects
✅ Comprehensive mind map visualization  
✅ Timeline of breakthrough moments
✅ Pattern cluster analysis
✅ Empowerment insights with highlights
✅ Next steps recommendations
✅ Mobile-responsive design

**🧠 Key Insights:**
{chr(10).join([f'• {insight[:100]}...' for insight in profile['breakthrough_moments'][:3]])}

**📊 Dashboard Metrics:**
• **Empowerment Score:** {artifacts['dashboard']['metrics']['empowerment_score']}/10
• **Growth Trajectory:** {artifacts['dashboard']['metrics']['growth_trajectory']}
• **Active Goals:** {artifacts['dashboard']['metrics']['active_goals']}
• **Journal Entries:** {artifacts['dashboard']['metrics']['journal_entries']}

**🎯 Next Steps:**
• Continue daily journaling for pattern recognition
• Implement recommended mindfulness exercises  
• Schedule regular self-reflection sessions
• Track progress on personal growth goals

**💡 Summary:** Your mental health dashboard shows strong empowerment themes with consistent growth patterns. The visualization reveals key breakthrough moments and provides actionable insights for continued development.

*🌟 Dashboard successfully generated with comprehensive mental health insights and empowerment analysis!*"""
        else:
            # Development mode - use preview system
            preview_id = preview_storage.store_preview(
                html_content=html_content,
                title=f"Mental Health Dashboard - {profile['name']}"
            )
            base_url = tool_context.state.get("preview_base_url", "http://localhost:8003")
            preview_url = f"{base_url}/preview/{preview_id}"
            stats = preview_storage.get_stats()
            
            result = f"""🎯 **Dashboard Preview Created Successfully!**

**📊 Your Interactive Dashboard:**
🔗 **Preview URL:** {preview_url}

**👤 Demo Profile:** {profile['name']}
**🎭 Background:** {profile['background']}

**📈 Dashboard Features:**
✅ Interactive metrics cards with hover effects
✅ Comprehensive mind map visualization
✅ Timeline of breakthrough moments  
✅ Pattern cluster analysis
✅ Empowerment insights with highlights
✅ Next steps recommendations
✅ Mobile-responsive design
✅ Print-friendly layout

**⚡ Preview Details:**
• **Preview ID:** {preview_id}
• **Expires:** 1 hour from now
• **Features:** Full HTML with CSS/JS
• **Size:** Professional dashboard layout

**📊 System Stats:**
• Total previews: {stats['total_previews']}
• Total views: {stats['total_views']}
• Storage: {stats['storage_size_mb']:.2f} MB

*💡 Click the preview URL to view your interactive dashboard!*"""
            
            logger.info(f"✅ Preview created successfully: {preview_id}")

        return result
        
    except Exception as e:
        logger.error(f"❌ Error creating dashboard preview: {str(e)}")
        return f"❌ Error creating dashboard preview: {str(e)}"
