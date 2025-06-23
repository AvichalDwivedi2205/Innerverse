#!/usr/bin/env python3
"""
Production startup script for Innerverse - All-in-One Container
Manages ADK Web Interface, Preview Server, and MCP connections
"""

import os
import sys
import time
import asyncio
import threading
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionServices:
    def __init__(self):
        self.port = int(os.environ.get('PORT', 8080))
        self.preview_port = self.port + 1  # Use PORT+1 for preview server
        self.services = []
        
    def start_preview_server(self):
        """Start preview server in background thread"""
        try:
            from preview_server import start_preview_server_thread
            logger.info(f"🚀 Starting preview server on port {self.preview_port}")
            
            # Start preview server thread
            preview_thread = start_preview_server_thread(
                port=self.preview_port,
                host="0.0.0.0"
            )
            self.services.append(("preview_server", preview_thread))
            
            logger.info(f"✅ Preview server started on port {self.preview_port}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start preview server: {e}")
            
    def setup_environment(self):
        """Setup production environment variables"""
        
        # Ensure required environment variables
        required_env = {
            'GOOGLE_CLOUD_PROJECT': os.environ.get('GOOGLE_CLOUD_PROJECT'),
            'GOOGLE_GENAI_USE_VERTEXAI': 'True',
            'ENVIRONMENT': 'production',
            'USER_TIMEZONE': os.environ.get('USER_TIMEZONE', 'America/New_York')
        }
        
        for key, value in required_env.items():
            if value:
                os.environ[key] = str(value)
                logger.info(f"✅ Environment: {key} = {value}")
            else:
                logger.warning(f"⚠️  Missing environment variable: {key}")
    
    def start_adk_web(self):
        """Start ADK web interface as main process"""
        try:
            logger.info(f"🚀 Starting ADK web interface on port {self.port}")
            
            # Build ADK command
            cmd = [
                "adk", "web", "agents/",
                "--port", str(self.port),
                "--host", "0.0.0.0"
            ]
            
            logger.info(f"🔧 ADK Command: {' '.join(cmd)}")
            
            # Start ADK (this will block as main process)
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ ADK web interface failed: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Unexpected error starting ADK: {e}")
            sys.exit(1)
    
    def health_check(self):
        """Simple health check endpoint"""
        try:
            import http.server
            import socketserver
            
            class HealthHandler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/health':
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {
                            "status": "healthy",
                            "services": ["adk_web", "preview_server", "mcp_ready"],
                            "timestamp": time.time()
                        }
                        self.wfile.write(str(response).encode())
                    else:
                        self.send_error(404)
            
            # Start health check server on a different port
            health_port = self.port + 2
            with socketserver.TCPServer(("", health_port), HealthHandler) as httpd:
                logger.info(f"🏥 Health check available on port {health_port}")
                threading.Thread(target=httpd.serve_forever, daemon=True).start()
                
        except Exception as e:
            logger.warning(f"⚠️  Health check setup failed: {e}")
    
    def verify_mcp_availability(self):
        """Verify MCP server is available"""
        try:
            # Check if npm and MCP server are available
            result = subprocess.run(
                ["npm", "list", "-g", "@cocal/google-calendar-mcp"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Google Calendar MCP server is available")
                return True
            else:
                logger.warning("⚠️  MCP server check failed, but proceeding")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️  MCP verification failed: {e}")
            return False
    
    def start_all_services(self):
        """Start all services in production mode"""
        logger.info("🚀 Starting Innerverse Production Services")
        
        # Setup environment
        self.setup_environment()
        
        # Verify MCP availability
        self.verify_mcp_availability()
        
        # Start preview server in background
        self.start_preview_server()
        
        # Setup health check
        self.health_check()
        
        # Give background services time to start
        time.sleep(3)
        
        logger.info("🎯 All background services started, launching ADK web interface...")
        
        # Start ADK web interface (main blocking process)
        self.start_adk_web()

def main():
    """Main production startup"""
    try:
        # Print startup banner
        print("""
🧠 ═══════════════════════════════════════════════════════════════
   INNERVERSE - PRODUCTION DEPLOYMENT
   ═══════════════════════════════════════════════════════════════
   🚀 Multi-Agent AI System for Personal Empowerment
   ═══════════════════════════════════════════════════════════════
        """)
        
        # Start all services
        services = ProductionServices()
        services.start_all_services()
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown signal received")
    except Exception as e:
        logger.error(f"❌ Production startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 