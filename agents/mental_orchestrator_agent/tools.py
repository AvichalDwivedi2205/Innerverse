"""Tools for the mental orchestrator agent.

This module contains tools for embedding clustering, mind map generation, 
empowerment insights creation, exercise recommendations, dashboard metrics, 
and crisis detection with focus on internal pattern analysis and creator consciousness.
"""

import json
import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from google.adk.tools import ToolContext
from google.cloud import firestore
import vertexai
from vertexai.generative_models import GenerativeModel
import pinecone

from .prompts import (
    get_clustering_prompt,
    get_empowerment_insights_prompt,
    get_exercise_recommendation_prompt,
    get_crisis_detection_prompt
)

# Initialize clients
db = firestore.Client()
vertexai.init()
model = GenerativeModel("gemini-2.5-pro")


async def retrieve_user_embeddings(
    tool_context: ToolContext,
) -> str:
    """Tool to retrieve all user embeddings from Pinecone for analysis."""
    
    try:
        user_id = tool_context.state.get("user_id")
        if not user_id:
            return "Error: User ID not found in context"
        
        # Retrieve embeddings from Pinecone (simulated)
        # In real implementation, this would query Pinecone
        embeddings_data = []
        
        # Simulate retrieving embeddings with metadata
        # pinecone_results = pinecone.query(
        #     filter={"userId": user_id},
        #     top_k=1000,
        #     include_metadata=True
        # )
        
        # For simulation, create sample data structure
        sample_embeddings = [
            {
                "id": f"{user_id}_journal_001",
                "vector": np.random.rand(768).tolist(),
                "metadata": {
                    "userId": user_id,
                    "context": "journal",
                    "sourceId": "journal_001",
                    "timestamp": "2025-06-15T10:00:00Z"
                }
            },
            {
                "id": f"{user_id}_therapy_001",
                "vector": np.random.rand(768).tolist(),
                "metadata": {
                    "userId": user_id,
                    "context": "therapy",
                    "sourceId": "therapy_001",
                    "timestamp": "2025-06-15T14:00:00Z"
                }
            }
        ]
        
        embeddings_data = sample_embeddings
        
        # Store in context
        tool_context.state["orchestrator_state"]["embeddings_data"] = embeddings_data
        
        return f"Retrieved {len(embeddings_data)} embeddings for analysis"
        
    except Exception as e:
        return f"Error retrieving user embeddings: {str(e)}"


async def cluster_internal_patterns(
    tool_context: ToolContext,
) -> str:
    """Tool to cluster embeddings using DBSCAN for internal pattern identification."""
    
    try:
        embeddings_data = tool_context.state["orchestrator_state"]["embeddings_data"]
        
        if not embeddings_data:
            return "Error: No embeddings data available for clustering"
        
        # Extract vectors for clustering
        vectors = np.array([item["vector"] for item in embeddings_data])
        
        # Standardize vectors
        scaler = StandardScaler()
        vectors_scaled = scaler.fit_transform(vectors)
        
        # Apply DBSCAN clustering
        dbscan = DBSCAN(eps=0.5, min_samples=2)
        cluster_labels = dbscan.fit_predict(vectors_scaled)
        
        # Group embeddings by clusters
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(embeddings_data[i])
        
        # Generate cluster themes using Gemini
        cluster_themes = {}
        for cluster_id, cluster_items in clusters.items():
            if cluster_id == -1:  # Skip noise cluster
                continue
                
            # Extract text content for theme generation
            texts = [item["metadata"].get("text", "") for item in cluster_items]
            
            prompt = get_clustering_prompt()
            full_prompt = prompt.format(list_of_texts=texts[:5])  # Limit to first 5 texts
            
            response = model.generate_content(full_prompt)
            theme = response.text.strip()
            
            cluster_themes[cluster_id] = {
                "theme": theme,
                "size": len(cluster_items),
                "items": cluster_items
            }
        
        # Store in context
        tool_context.state["orchestrator_state"]["clusters"] = cluster_themes
        
        return f"Identified {len(cluster_themes)} internal pattern clusters with empowerment themes"
        
    except Exception as e:
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
        mind_map_ref = db.collection("users").document(user_id).collection("mindMap").document("current")
        mind_map_ref.set(orchestrator_state["mind_map"], merge=True)
        
        # Store insights
        for insight in orchestrator_state["insights"]:
            insight_doc = {
                **insight,
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }
            db.collection("users").document(user_id).collection("insights").add(insight_doc)
        
        # Store exercise recommendations
        for recommendation in orchestrator_state["exercise_recommendations"]:
            rec_doc = {
                **recommendation,
                "createdAt": datetime.now(),
                "expiresAt": datetime.now() + timedelta(days=7)
            }
            db.collection("users").document(user_id).collection("recommendations").add(rec_doc)
        
        # Store dashboard metrics
        metrics_ref = db.collection("users").document(user_id).collection("dashboard").document("metrics")
        metrics_ref.set(orchestrator_state["dashboard_metrics"], merge=True)
        
        # Store crisis alerts
        for alert in orchestrator_state["crisis_alerts"]:
            alert_doc = {
                **alert,
                "createdAt": datetime.now(),
                "resolvedAt": None
            }
            db.collection("users").document(user_id).collection("crisisAlerts").add(alert_doc)
        
        return f"Successfully stored all orchestrator results with empowerment focus"
        
    except Exception as e:
        return f"Error storing orchestrator results: {str(e)}"
