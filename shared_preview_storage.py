#!/usr/bin/env python3
"""
Shared preview storage system for Mental Health Dashboard.
This module provides a centralized storage that can be used by both the ADK agent and preview server.
"""

import json
import uuid
import time
import threading
import os
import tempfile
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SharedPreviewStorage:
    """Thread-safe file-based storage for temporary HTML previews that can be shared across processes"""
    
    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            # Use a temporary directory that persists across processes
            self.storage_dir = Path(tempfile.gettempdir()) / "mental_health_previews"
        else:
            self.storage_dir = Path(storage_dir)
        
        # Create storage directory if it doesn't exist
        self.storage_dir.mkdir(exist_ok=True, parents=True)
        
        self._lock = threading.Lock()
        self._cleanup_interval = 300  # 5 minutes
        self._max_age = 3600  # 1 hour
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
        logger.info(f"SharedPreviewStorage initialized at: {self.storage_dir}")
    
    def store_preview(self, html_content: str, title: str = "Mental Health Dashboard") -> str:
        """Store HTML content and return unique preview ID"""
        preview_id = str(uuid.uuid4())[:8]  # Short UUID
        expiry_time = time.time() + self._max_age
        
        preview_data = {
            'html': html_content,
            'title': title,
            'created': time.time(),
            'expires': expiry_time,
            'views': 0
        }
        
        # Save to file
        preview_file = self.storage_dir / f"{preview_id}.json"
        
        with self._lock:
            try:
                with open(preview_file, 'w', encoding='utf-8') as f:
                    json.dump(preview_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Stored preview {preview_id} at {preview_file}")
            except Exception as e:
                logger.error(f"Error storing preview {preview_id}: {e}")
                raise
        
        return preview_id
    
    def get_preview(self, preview_id: str) -> Optional[str]:
        """Retrieve HTML content by preview ID"""
        preview_file = self.storage_dir / f"{preview_id}.json"
        
        if not preview_file.exists():
            logger.warning(f"Preview file not found: {preview_file}")
            return None
        
        with self._lock:
            try:
                with open(preview_file, 'r', encoding='utf-8') as f:
                    preview_data = json.load(f)
                
                # Check if expired
                if time.time() > preview_data['expires']:
                    logger.info(f"Preview {preview_id} has expired, removing")
                    preview_file.unlink(missing_ok=True)
                    return None
                
                # Increment view count and save back
                preview_data['views'] += 1
                with open(preview_file, 'w', encoding='utf-8') as f:
                    json.dump(preview_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Retrieved preview {preview_id} (view #{preview_data['views']})")
                return preview_data['html']
                
            except Exception as e:
                logger.error(f"Error retrieving preview {preview_id}: {e}")
                return None
    
    def _cleanup_expired(self):
        """Remove expired previews"""
        current_time = time.time()
        expired_count = 0
        
        with self._lock:
            try:
                for preview_file in self.storage_dir.glob("*.json"):
                    try:
                        with open(preview_file, 'r', encoding='utf-8') as f:
                            preview_data = json.load(f)
                        
                        if current_time > preview_data['expires']:
                            preview_file.unlink()
                            expired_count += 1
                            logger.debug(f"Cleaned up expired preview: {preview_file.stem}")
                    
                    except Exception as e:
                        logger.warning(f"Error checking preview file {preview_file}: {e}")
                        # Remove corrupted files
                        preview_file.unlink(missing_ok=True)
                        expired_count += 1
            
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
        
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired/corrupted previews")
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_loop():
            while True:
                time.sleep(self._cleanup_interval)
                self._cleanup_expired()
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        logger.info("Cleanup thread started")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        with self._lock:
            try:
                preview_files = list(self.storage_dir.glob("*.json"))
                total_previews = len(preview_files)
                total_views = 0
                oldest_preview = time.time()
                total_size = 0
                
                for preview_file in preview_files:
                    try:
                        with open(preview_file, 'r', encoding='utf-8') as f:
                            preview_data = json.load(f)
                        total_views += preview_data.get('views', 0)
                        oldest_preview = min(oldest_preview, preview_data.get('created', time.time()))
                        total_size += preview_file.stat().st_size
                    except:
                        continue
                
                return {
                    'total_previews': total_previews,
                    'total_views': total_views,
                    'oldest_preview': oldest_preview if total_previews > 0 else 0,
                    'storage_size_mb': total_size / (1024 * 1024),
                    'storage_dir': str(self.storage_dir)
                }
            
            except Exception as e:
                logger.error(f"Error getting stats: {e}")
                return {
                    'total_previews': 0,
                    'total_views': 0,
                    'oldest_preview': 0,
                    'storage_size_mb': 0.0,
                    'storage_dir': str(self.storage_dir),
                    'error': str(e)
                }
    
    def list_previews(self) -> list:
        """List all available preview IDs"""
        try:
            preview_files = list(self.storage_dir.glob("*.json"))
            preview_ids = []
            
            for preview_file in preview_files:
                try:
                    with open(preview_file, 'r', encoding='utf-8') as f:
                        preview_data = json.load(f)
                    
                    # Check if not expired
                    if time.time() <= preview_data['expires']:
                        preview_ids.append({
                            'id': preview_file.stem,
                            'title': preview_data.get('title', 'Unknown'),
                            'created': preview_data.get('created', 0),
                            'views': preview_data.get('views', 0)
                        })
                except:
                    continue
            
            return sorted(preview_ids, key=lambda x: x['created'], reverse=True)
        
        except Exception as e:
            logger.error(f"Error listing previews: {e}")
            return []

# Global shared storage instance
shared_storage = SharedPreviewStorage()

def get_shared_storage() -> SharedPreviewStorage:
    """Get the global shared storage instance"""
    return shared_storage

if __name__ == "__main__":
    # Test the shared storage
    storage = get_shared_storage()
    
    # Test storing a preview
    test_html = """
    <html>
    <head><title>Test Preview</title></head>
    <body>
        <h1>Test Mental Health Dashboard</h1>
        <p>This is a test preview for Avichal Dwivedi</p>
        <p>Timestamp: {}</p>
    </body>
    </html>
    """.format(time.time())
    
    preview_id = storage.store_preview(test_html, "Test Dashboard")
    print(f"✅ Stored test preview with ID: {preview_id}")
    
    # Test retrieving the preview
    retrieved_html = storage.get_preview(preview_id)
    if retrieved_html:
        print("✅ Successfully retrieved preview")
        print(f"📝 Preview length: {len(retrieved_html)} characters")
    else:
        print("❌ Failed to retrieve preview")
    
    # Get stats
    stats = storage.get_stats()
    print(f"📊 Storage stats: {stats}")
    
    # List previews
    previews = storage.list_previews()
    print(f"📋 Available previews: {len(previews)}")
    for preview in previews:
        print(f"  - {preview['id']}: {preview['title']} (views: {preview['views']})") 