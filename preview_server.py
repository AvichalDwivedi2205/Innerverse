#!/usr/bin/env python3
"""
Simple HTTP server to handle preview URLs for mental health dashboard visualizations.
This server works alongside the ADK web interface to serve generated HTML previews.
"""

import http.server
import socketserver
import urllib.parse
import logging
import threading
import time
from typing import Optional

# Import the shared preview storage
try:
    from shared_preview_storage import get_shared_storage
    preview_storage = get_shared_storage()
    print("✅ Using shared preview storage")
except ImportError:
    print("❌ Warning: Could not import shared storage. Creating mock storage.")
    
    class MockPreviewStorage:
        def get_preview(self, preview_id: str) -> Optional[str]:
            return f"""
            <html>
            <head><title>Preview Not Available</title></head>
            <body>
                <h1>Preview System Not Available</h1>
                <p>Preview ID: {preview_id}</p>
                <p>The preview system could not be loaded. Please check your installation.</p>
            </body>
            </html>
            """
        
        def get_stats(self):
            return {"error": "Mock storage in use"}
    
    preview_storage = MockPreviewStorage()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PreviewHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler for preview URLs"""
    
    def do_GET(self):
        """Handle GET requests for preview URLs"""
        
        # Parse the URL
        parsed_url = urllib.parse.urlparse(self.path)
        path_parts = parsed_url.path.strip('/').split('/')
        
        # Check if this is a preview request
        if len(path_parts) >= 2 and path_parts[0] == 'preview':
            preview_id = path_parts[1]
            self.serve_preview(preview_id)
        elif parsed_url.path == '/':
            self.serve_index()
        elif parsed_url.path == '/health':
            self.serve_health_check()
        elif parsed_url.path == '/stats':
            self.serve_stats()
        else:
            self.send_error(404, "Not Found")
    
    def serve_preview(self, preview_id: str):
        """Serve a specific preview by ID"""
        try:
            html_content = preview_storage.get_preview(preview_id)
            
            if html_content:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
                logger.info(f"✅ Served preview: {preview_id}")
            else:
                self.serve_preview_not_found(preview_id)
                
        except Exception as e:
            logger.error(f"❌ Error serving preview {preview_id}: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def serve_preview_not_found(self, preview_id: str):
        """Serve a 404 page for missing previews"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Preview Not Found</title>
            <style>
                body {{
                    font-family: 'Segoe UI', system-ui, sans-serif;
                    margin: 0;
                    padding: 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }}
                h1 {{ color: #e74c3c; margin-bottom: 20px; }}
                p {{ color: #555; line-height: 1.6; }}
                .preview-id {{ 
                    background: #f8f9fa; 
                    padding: 10px; 
                    border-radius: 5px; 
                    font-family: monospace; 
                    margin: 20px 0;
                }}
                .back-btn {{
                    background: #667eea;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    text-decoration: none;
                    display: inline-block;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 Preview Not Found</h1>
                <p>The requested preview could not be found or has expired.</p>
                <div class="preview-id">Preview ID: {preview_id}</div>
                <p>Previews expire after 1 hour for security reasons.</p>
                <a href="/" class="back-btn">← Back to Home</a>
            </div>
        </body>
        </html>
        """
        
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
        logger.warning(f"⚠️ Preview not found: {preview_id}")
    
    def serve_index(self):
        """Serve the index page"""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mental Health Preview Server</title>
            <style>
                body {
                    font-family: 'Segoe UI', system-ui, sans-serif;
                    margin: 0;
                    padding: 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: white;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    text-align: center;
                }
                h1 { font-size: 3rem; margin-bottom: 20px; }
                p { font-size: 1.2rem; opacity: 0.9; }
                .info-box {
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 15px;
                    margin: 30px 0;
                    backdrop-filter: blur(10px);
                }
                .endpoint {
                    background: rgba(255,255,255,0.2);
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                    font-family: monospace;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧠 Mental Health Preview Server</h1>
                <p>Production-ready preview system for mental health dashboard visualizations</p>
                
                <div class="info-box">
                    <h2>📊 Available Endpoints</h2>
                    <div class="endpoint">/preview/{id} - View dashboard preview</div>
                    <div class="endpoint">/health - Health check</div>
                    <div class="endpoint">/stats - Storage statistics</div>
                </div>
                
                <div class="info-box">
                    <h2>🚀 How to Use</h2>
                    <p>1. Use the ADK Mental Orchestrator Agent</p>
                    <p>2. Ask for "dashboard preview" or "create preview"</p>
                    <p>3. Click the generated preview URL</p>
                    <p>4. View your interactive dashboard!</p>
                </div>
                
                <div class="info-box">
                    <h2>🔗 ADK Web Interface</h2>
                    <p><a href="http://localhost:8002" style="color: #fff; text-decoration: underline;">http://localhost:8002</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def serve_health_check(self):
        """Serve health check endpoint"""
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "server": "Mental Health Preview Server",
            "version": "1.0.0"
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(str(health_data).encode('utf-8'))
    
    def serve_stats(self):
        """Serve storage statistics"""
        try:
            stats = preview_storage.get_stats()
            stats_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Preview Server Stats</title>
                <style>
                    body {{ font-family: monospace; padding: 20px; background: #f5f5f5; }}
                    .stat {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h1>📊 Preview Server Statistics</h1>
                <div class="stat">Total Previews: {stats.get('total_previews', 0)}</div>
                <div class="stat">Total Views: {stats.get('total_views', 0)}</div>
                <div class="stat">Storage Size: {stats.get('storage_size_mb', 0):.2f} MB</div>
                <div class="stat">Oldest Preview: {stats.get('oldest_preview', 0)}</div>
                <div class="stat">Server Uptime: {time.time():.0f}s</div>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(stats_html.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error getting stats: {e}")
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def start_preview_server(port: int = 8003, host: str = "localhost"):
    """Start the preview server"""
    
    try:
        with socketserver.TCPServer((host, port), PreviewHTTPRequestHandler) as httpd:
            logger.info(f"🚀 Mental Health Preview Server starting on http://{host}:{port}")
            logger.info(f"📊 Preview URLs: http://{host}:{port}/preview/{{id}}")
            logger.info(f"🔗 ADK Interface: http://localhost:8002")
            logger.info(f"📈 Stats: http://{host}:{port}/stats")
            logger.info("Press Ctrl+C to stop the server")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")

def start_preview_server_thread(port: int = 8003, host: str = "localhost"):
    """Start the preview server in a background thread"""
    
    def server_thread():
        start_preview_server(port, host)
    
    thread = threading.Thread(target=server_thread, daemon=True)
    thread.start()
    logger.info(f"🧵 Preview server thread started on http://{host}:{port}")
    return thread

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    port = 8003
    host = "localhost"
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    # Start the server
    start_preview_server(port, host) 