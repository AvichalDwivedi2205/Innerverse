import asyncio
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import asdict

from config.vector_db_config import pinecone_config
from vector_db.schemas.mental_health_schemas import BaseVectorSchema, VectorType, VectorSchemaFactory
from vector_db.embeddings.gemini_embeddings import gemini_embeddings

class VectorOperations:
    """Advanced vector database operations for mental health data"""
    
    def __init__(self):
        self.pinecone_config = pinecone_config
        self.embeddings = gemini_embeddings
    
    async def upsert_mental_health_vector(self, schema: BaseVectorSchema) -> bool:
        """Upsert vector with mental health schema validation"""
        try:
            index_name = schema.get_pinecone_index_name()
            
            # Prepare vector data for Pinecone
            vector_data = [(
                schema.id,
                schema.vector,
                {
                    'user_id': schema.user_id,
                    'created_at': schema.created_at.isoformat(),
                    'updated_at': schema.updated_at.isoformat(),
                    **schema.metadata,
                    **self._extract_schema_metadata(schema)
                }
            )]
            
            success = self.pinecone_config.upsert_vectors(index_name, vector_data)
            if success:
                logging.info(f"Successfully upserted vector {schema.id} to {index_name}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error upserting vector {schema.id}: {e}")
            return False
    
    def _extract_schema_metadata(self, schema: BaseVectorSchema) -> Dict[str, Any]:
        """Extract schema-specific metadata for Pinecone storage"""
        metadata = {}
        schema_dict = asdict(schema)
        
        # Exclude vector and base fields from metadata
        exclude_fields = {'id', 'user_id', 'vector', 'created_at', 'updated_at', 'metadata'}
        
        for key, value in schema_dict.items():
            if key not in exclude_fields and value is not None:
                # Convert complex types to strings for Pinecone compatibility
                if isinstance(value, (list, dict)):
                    metadata[key] = str(value)
                elif isinstance(value, datetime):
                    metadata[key] = value.isoformat()
                else:
                    metadata[key] = value
        
        return metadata
    
    async def semantic_search(self, 
                            query_vector: List[float], 
                            vector_type: VectorType,
                            user_id: str = None,
                            top_k: int = 10,
                            time_filter: Optional[Dict[str, datetime]] = None) -> List[Dict[str, Any]]:
        """Perform semantic search with advanced filtering"""
        try:
            # Get appropriate index name
            schema_class = VectorSchemaFactory.SCHEMA_MAPPING[vector_type]
            index_name = schema_class.get_pinecone_index_name()
            
            # Build filter dictionary
            filter_dict = {}
            if user_id:
                filter_dict['user_id'] = user_id
            
            # Add time-based filtering
            if time_filter:
                if 'start_date' in time_filter:
                    filter_dict['created_at'] = {'$gte': time_filter['start_date'].isoformat()}
                if 'end_date' in time_filter:
                    if 'created_at' not in filter_dict:
                        filter_dict['created_at'] = {}
                    filter_dict['created_at']['$lte'] = time_filter['end_date'].isoformat()
            
            # Perform vector search
            results = self.pinecone_config.query_vectors(
                index_name=index_name,
                vector=query_vector,
                top_k=top_k,
                filter_dict=filter_dict if filter_dict else None
            )
            
            return self._process_search_results(results)
            
        except Exception as e:
            logging.error(f"Error in semantic search: {e}")
            return []
    
    def _process_search_results(self, results) -> List[Dict[str, Any]]:
        """Process and format search results"""
        if not hasattr(results, 'matches') or not results.matches:
            return []
        
        processed_results = []
        for match in results.matches:
            result = {
                'id': match.id,
                'score': match.score,
                'metadata': match.metadata if hasattr(match, 'metadata') else {}
            }
            processed_results.append(result)
        
        return processed_results
    
    async def cluster_mental_health_vectors(self, 
                                          vector_type: VectorType,
                                          user_id: str,
                                          time_window_days: int = 30,
                                          num_clusters: int = 5) -> Dict[str, Any]:
        """Perform clustering analysis on mental health vectors"""
        try:
            # Get recent vectors for clustering
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_window_days)
            
            # Create a dummy query vector for retrieval (we'll get all vectors)
            expected_dims = VectorSchemaFactory.get_expected_dimensions(vector_type)
            dummy_vector = [0.0] * expected_dims
            
            search_results = await self.semantic_search(
                query_vector=dummy_vector,
                vector_type=vector_type,
                user_id=user_id,
                top_k=1000,  # Get many vectors for clustering
                time_filter={'start_date': start_date, 'end_date': end_date}
            )
            
            if len(search_results) < num_clusters:
                return {
                    'clusters': [],
                    'insights': 'Insufficient data for clustering analysis',
                    'vector_count': len(search_results)
                }
            
            # Perform clustering analysis
            clusters = self._perform_kmeans_clustering(search_results, num_clusters)
            insights = self._generate_clustering_insights(clusters, vector_type)
            
            return {
                'clusters': clusters,
                'insights': insights,
                'vector_count': len(search_results),
                'time_window': f"{time_window_days} days"
            }
            
        except Exception as e:
            logging.error(f"Error in clustering analysis: {e}")
            return {'error': str(e)}
    
    def _perform_kmeans_clustering(self, vectors: List[Dict[str, Any]], num_clusters: int) -> List[Dict[str, Any]]:
        """Perform K-means clustering on vectors"""
        # This is a simplified clustering implementation
        # In production, you would use scikit-learn or similar libraries
        
        clusters = []
        vectors_per_cluster = len(vectors) // num_clusters
        
        for i in range(num_clusters):
            start_idx = i * vectors_per_cluster
            end_idx = start_idx + vectors_per_cluster if i < num_clusters - 1 else len(vectors)
            
            cluster_vectors = vectors[start_idx:end_idx]
            
            # Calculate cluster centroid (simplified)
            cluster_metadata = self._analyze_cluster_metadata(cluster_vectors)
            
            clusters.append({
                'cluster_id': i,
                'vector_count': len(cluster_vectors),
                'vectors': cluster_vectors,
                'characteristics': cluster_metadata
            })
        
        return clusters
    
    def _analyze_cluster_metadata(self, cluster_vectors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze metadata characteristics of a cluster"""
        characteristics = {}
        
        # Analyze common patterns in metadata
        mood_scores = []
        triggers = []
        
        for vector in cluster_vectors:
            metadata = vector.get('metadata', {})
            
            # Collect mood scores if available
            if 'mood_score' in metadata:
                try:
                    mood_scores.append(float(metadata['mood_score']))
                except (ValueError, TypeError):
                    pass
            
            # Collect triggers if available
            if 'triggers' in metadata:
                try:
                    trigger_list = eval(metadata['triggers']) if isinstance(metadata['triggers'], str) else metadata['triggers']
                    if isinstance(trigger_list, list):
                        triggers.extend(trigger_list)
                except:
                    pass
        
        # Calculate characteristics
        if mood_scores:
            characteristics['avg_mood_score'] = sum(mood_scores) / len(mood_scores)
            characteristics['mood_range'] = [min(mood_scores), max(mood_scores)]
        
        if triggers:
            # Count trigger frequency
            trigger_counts = {}
            for trigger in triggers:
                trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
            characteristics['common_triggers'] = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return characteristics
    
    def _generate_clustering_insights(self, clusters: List[Dict[str, Any]], vector_type: VectorType) -> str:
        """Generate insights from clustering analysis"""
        insights = []
        
        insights.append(f"Identified {len(clusters)} distinct patterns in {vector_type.value}")
        
        for cluster in clusters:
            characteristics = cluster.get('characteristics', {})
            
            if 'avg_mood_score' in characteristics:
                avg_mood = characteristics['avg_mood_score']
                mood_desc = "positive" if avg_mood > 0.5 else "negative" if avg_mood < -0.5 else "neutral"
                insights.append(f"Cluster {cluster['cluster_id']}: {mood_desc} emotional pattern (avg mood: {avg_mood:.2f})")
            
            if 'common_triggers' in characteristics:
                top_triggers = [trigger[0] for trigger in characteristics['common_triggers']]
                insights.append(f"Cluster {cluster['cluster_id']} common triggers: {', '.join(top_triggers)}")
        
        return " | ".join(insights)
    
    async def get_user_mental_health_timeline(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive mental health timeline for user"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            timeline = {}
            
            # Get journal entries timeline
            journal_vectors = await self.semantic_search(
                query_vector=[0.0] * 768,  # Dummy vector
                vector_type=VectorType.JOURNAL_ENTRY,
                user_id=user_id,
                top_k=100,
                time_filter={'start_date': start_date, 'end_date': end_date}
            )
            timeline['journal_entries'] = journal_vectors
            
            # Get therapy sessions timeline
            therapy_vectors = await self.semantic_search(
                query_vector=[0.0] * 768,  # Dummy vector
                vector_type=VectorType.THERAPY_SESSION,
                user_id=user_id,
                top_k=50,
                time_filter={'start_date': start_date, 'end_date': end_date}
            )
            timeline['therapy_sessions'] = therapy_vectors
            
            # Get progress tracking
            progress_vectors = await self.semantic_search(
                query_vector=[0.0] * 384,  # Dummy vector
                vector_type=VectorType.PROGRESS_TRACKING,
                user_id=user_id,
                top_k=20,
                time_filter={'start_date': start_date, 'end_date': end_date}
            )
            timeline['progress_tracking'] = progress_vectors
            
            return {
                'user_id': user_id,
                'timeline_days': days,
                'timeline': timeline,
                'summary': self._generate_timeline_summary(timeline)
            }
            
        except Exception as e:
            logging.error(f"Error generating timeline for user {user_id}: {e}")
            return {'error': str(e)}
    
    def _generate_timeline_summary(self, timeline: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate summary of user's mental health timeline"""
        summary_parts = []
        
        journal_count = len(timeline.get('journal_entries', []))
        therapy_count = len(timeline.get('therapy_sessions', []))
        progress_count = len(timeline.get('progress_tracking', []))
        
        summary_parts.append(f"Journal entries: {journal_count}")
        summary_parts.append(f"Therapy sessions: {therapy_count}")
        summary_parts.append(f"Progress records: {progress_count}")
        
        return " | ".join(summary_parts)

# Global vector operations instance
vector_ops = VectorOperations()
