# 🧠 Mental Health Preview System - Testing Guide

## 🚀 Production-Ready Dashboard Visualization System

This guide explains how to test the new **production-ready preview system** that generates shareable URLs for mental health dashboard visualizations.

## 📋 System Overview

The preview system consists of:

1. **Preview Server** (`preview_server.py`) - Serves HTML dashboards on port 8003
2. **Preview Tool** (`create_dashboard_preview`) - Generates preview URLs in the Mental Orchestrator Agent
3. **Storage System** - Thread-safe in-memory storage with automatic cleanup
4. **Complete HTML Generation** - Standalone pages with CSS, JavaScript, and interactivity

## 🔧 Quick Start

### Option 1: Automated Startup (Recommended)

```bash
# Start the complete system
python start_preview_system.py
```

### Option 2: Manual Startup

```bash
# Terminal 1: Start preview server
python preview_server.py

# Terminal 2: Start ADK web interface
adk web
```

## 🧪 Testing Instructions

### 1. Open ADK Web Interface

1. Go to http://localhost:8002
2. Select **"mental_orchestrator_agent"** from the dropdown
3. Wait for the agent to load

### 2. Test Commands

Copy and paste these commands into the ADK chat:

#### 🎯 Preview URL Generation (Production Feature)
```
Create a dashboard preview for my mental health insights
```

**Expected Result:**
- Generates a clickable URL like `http://localhost:8003/image.pngpreview/abc12345`
- URL opens a complete interactive dashboard in a new tab
- Includes demo profile data with realistic mental health insights

#### 📊 Inline HTML Visualization
```
Show me comprehensive mental health artifacts and visualizations
```

**Expected Result:**
- Rich HTML displayed directly in the ADK interface
- Interactive metrics cards, mind maps, and insights
- Responsive design with professional styling

#### 📈 Dashboard View
```
Generate my mental health dashboard with charts
```

**Expected Result:**
- Comprehensive dashboard with metrics and visualizations
- Color-coded progress indicators
- Timeline and pattern analysis

### 3. Verify Preview URLs

1. Click on any generated preview URL
2. Should open in a new browser tab
3. Verify the dashboard includes:
   - ✅ Professional header with gradient background
   - ✅ Interactive metrics cards (hover effects)
   - ✅ Mind map visualization section
   - ✅ Timeline with breakthrough moments
   - ✅ Pattern cluster analysis
   - ✅ Key insights with highlights
   - ✅ Next steps recommendations
   - ✅ Print button (top-right corner)
   - ✅ Mobile-responsive design

## 🔍 System Endpoints

### Preview Server (Port 8003)

- **Home**: http://localhost:8003/
- **Preview**: http://localhost:8003/preview/{id}
- **Stats**: http://localhost:8003/stats
- **Health**: http://localhost:8003/health

### ADK Interface (Port 8002)

- **Web UI**: http://localhost:8002

## 📊 Demo Data

The system includes 3 realistic demo profiles:

1. **Alex Chen** - Stressed professional dealing with work-life balance
2. **Maria Rodriguez** - Career transition with imposter syndrome
3. **Jordan Kim** - New parent balancing family and career

Each profile includes:
- Realistic background and challenges
- Primary empowerment themes
- Breakthrough moments
- Comprehensive journey insights

## 🛠️ Advanced Testing

### Test Preview Expiration

```bash
# Check preview stats
curl http://localhost:8003/stats

# Test health endpoint
curl http://localhost:8003/health
```

### Test Error Handling

1. Try accessing an invalid preview URL: http://localhost:8003/preview/invalid
2. Should show a professional 404 page with styling

### Test Concurrent Usage

1. Generate multiple previews simultaneously
2. Verify each gets a unique URL
3. Check that all previews work independently

## 🐛 Troubleshooting

### Preview Server Won't Start

```bash
# Check if port 8003 is in use
netstat -tulpn | grep 8003

# Kill existing process if needed
pkill -f preview_server.py
```

### ADK Agent Not Loading

```bash
# Verify ADK installation
adk --version

# Check agent imports
python -c "from agents.mental_orchestrator_agent.tools import create_dashboard_preview; print('✅ Import successful')"
```

### Preview URLs Not Working

1. Verify preview server is running: http://localhost:8003/
2. Check server logs for errors
3. Verify the agent is generating valid preview IDs

### HTML Not Rendering

1. Check browser developer console for JavaScript errors
2. Verify CSS is loading properly
3. Test with different browsers (Chrome, Firefox, Safari)

## 🚀 Production Deployment

This system is designed for production deployment:

### Docker Deployment

```dockerfile
# Add to your Dockerfile
EXPOSE 8003
CMD ["python", "preview_server.py", "8003", "0.0.0.0"]
```

### Google Cloud Run

```bash
# Deploy with both ADK and preview server
gcloud run deploy mental-health-app \
  --source . \
  --port 8003 \
  --allow-unauthenticated
```

### Environment Variables

```bash
# Optional configuration
export PREVIEW_SERVER_PORT=8003
export PREVIEW_SERVER_HOST=0.0.0.0
export PREVIEW_MAX_AGE=3600  # 1 hour
export PREVIEW_CLEANUP_INTERVAL=300  # 5 minutes
```

## 📈 Performance Metrics

The system includes built-in monitoring:

- **Storage Statistics**: Total previews, views, storage size
- **Performance Logging**: Load times, request tracking
- **Automatic Cleanup**: Expired preview removal
- **Thread Safety**: Concurrent request handling

## ✅ Success Criteria

A successful test should demonstrate:

1. ✅ Preview URLs generate successfully
2. ✅ URLs open interactive dashboards
3. ✅ Dashboards include all visual elements
4. ✅ Hover effects and interactivity work
5. ✅ Mobile responsiveness functions
6. ✅ Print functionality available
7. ✅ Error handling graceful
8. ✅ Concurrent usage supported

## 🎯 Next Steps

After successful testing, you can:

1. **Deploy to Production**: Use the Docker/Cloud Run instructions
2. **Customize Styling**: Modify the HTML templates in `tools.py`
3. **Add Real Data**: Connect to actual user journal/therapy data
4. **Extend Features**: Add more visualization types
5. **Monitor Usage**: Track preview generation and usage patterns

---

**🎉 Congratulations!** You now have a production-ready mental health dashboard preview system that generates shareable URLs for rich, interactive visualizations! 