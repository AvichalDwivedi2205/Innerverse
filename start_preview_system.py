#!/usr/bin/env python3
"""
Startup script for the Mental Health Preview System.
This script starts the preview server and provides testing instructions.
"""

import os
import sys
import time
import threading
import subprocess
from preview_server import start_preview_server_thread

def print_banner():
    """Print startup banner"""
    print("""
🧠 ═══════════════════════════════════════════════════════════════
   MENTAL HEALTH PREVIEW SYSTEM - PRODUCTION READY
   ═══════════════════════════════════════════════════════════════

   🚀 Starting comprehensive dashboard preview system...
   
""")

def print_instructions():
    """Print testing instructions"""
    print("""
📋 TESTING INSTRUCTIONS:
   ═══════════════════════════════════════════════════════════════

   1️⃣  PREVIEW SERVER: ✅ Already started on http://localhost:8003
   
   2️⃣  ADK WEB INTERFACE: 
       Open a NEW terminal and run:
       → adk web
       
   3️⃣  BROWSER:
       → Go to http://localhost:8002
       → Select "mental_orchestrator_agent"
       
   4️⃣  TEST COMMANDS (copy and paste):
       
       🎯 PREVIEW URL GENERATION:
       "Create a dashboard preview for my mental health insights"
       
       📊 INLINE HTML VISUALIZATION:
       "Show me comprehensive mental health artifacts and visualizations"
       
       📈 DASHBOARD VIEW:
       "Generate my mental health dashboard with charts"
       
   5️⃣  EXPECTED RESULTS:
       → Preview commands generate clickable URLs
       → URLs open full interactive dashboards
       → HTML commands show rich visualizations inline
       → All include demo data with realistic insights

   ═══════════════════════════════════════════════════════════════
   
   🔗 USEFUL LINKS:
   • Preview Server: http://localhost:8003
   • ADK Interface: http://localhost:8002  
   • Server Stats: http://localhost:8003/stats
   • Health Check: http://localhost:8003/health
   
   ═══════════════════════════════════════════════════════════════
""")

def check_adk_running():
    """Check if ADK web interface is running"""
    try:
        import requests
        response = requests.get("http://localhost:8002", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    """Main startup function"""
    print_banner()
    
    # Start preview server in background thread
    print("🚀 Starting preview server on http://localhost:8003...")
    server_thread = start_preview_server_thread(port=8003, host="localhost")
    
    # Give server time to start
    time.sleep(2)
    
    print("✅ Preview server started successfully!")
    print("📊 Preview URLs will be: http://localhost:8003/preview/{id}")
    
    # Check if ADK is running
    if check_adk_running():
        print("✅ ADK web interface detected on http://localhost:8002")
    else:
        print("⚠️  ADK web interface not detected. Please run 'adk web' in another terminal.")
    
    print_instructions()
    
    try:
        print("🔄 Preview server running... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down preview system...")
        print("✅ Preview system stopped. Thank you!")

if __name__ == "__main__":
    main() 