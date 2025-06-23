# 🚀 INNERVERSE - PRODUCTION DEPLOYMENT GUIDE

**⏰ URGENT: For Tomorrow's Submission**

## 📋 Quick Deployment Checklist

### 1. **OAuth Setup (5 minutes)**

#### A. **Keep Test Mode** (Recommended for submission)
- ✅ **Fast**: No verification needed
- ✅ **Works immediately**: Up to 100 test users
- ⚠️ Shows "unverified app" warning (acceptable for demo)

#### B. **Production OAuth** (1-7 days - NOT for tomorrow)
- ❌ **Slow**: Requires Google verification
- ❌ **Risky**: Might not be approved in time

**For tomorrow: STICK WITH TEST MODE**

### 2. **Environment Variables Setup (2 minutes)**

```bash
# Required for deployment
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"

# Optional (has defaults)
export SERVICE_NAME="innerverse-ai"
export APP_NAME="innerverse"
```

### 3. **OAuth Credentials File**

Ensure `google-oauth-credentials.json` is in your project root:
```bash
ls -la google-oauth-credentials.json
# Should exist and contain your OAuth client credentials
```

### 4. **Deploy (5 minutes)**

```bash
# One command deployment!
./deploy.sh
```

## 🔧 **How All Services Work Together**

### **Single Container Architecture**
```
Cloud Run Container:
├── ADK Web Interface (Main UI) - Port 8080
├── Preview Server (Dashboards) - Port 8081  
├── MCP Server (Calendar) - Background Process
└── Health Check - Port 8082
```

### **Service Communication**
1. **User** → ADK Web UI (port 8080)
2. **ADK Agents** → MCP Server (for calendar)
3. **Mental Orchestrator** → Preview Server (for dashboards)
4. **All Services** → Shared memory & environment

## 🌐 **Production URLs**

After deployment:
- **Main App**: `https://innerverse-ai-[hash].a.run.app`
- **Health Check**: `https://innerverse-ai-[hash].a.run.app/health`
- **Preview System**: `https://innerverse-ai-[hash].a.run.app:8081/preview/{id}`

## 🧪 **Testing After Deployment**

### 1. **Basic Health Check**
```bash
curl https://your-app-url.run.app/health
```

### 2. **Test Scheduling Agent**
1. Open app URL in browser
2. Select "google_calendar_scheduling_agent"
3. Type: "List my calendars"
4. **First time**: Will show OAuth consent screen
5. **Grant permissions**: Allow calendar access
6. **Test command**: "Schedule a meeting tomorrow at 2pm"

### 3. **Test Preview System**
1. Select "mental_orchestrator_agent"
2. Type: "Create a dashboard preview"
3. Should generate clickable preview URL
4. Click URL → Opens interactive dashboard

## ⚠️ **Multi-User Authentication**

### **How It Works Now**
- Each user gets separate session (by session_id)
- OAuth tokens are managed per session
- First user per session needs to authenticate
- Subsequent users in same session share authentication

### **For Production (Phase 2)**
- User-specific OAuth token storage
- Proper session management
- Individual authentication flows

## 🚨 **Troubleshooting**

### **MCP Server Issues**
```bash
# Check MCP availability
npm list -g @cocal/google-calendar-mcp

# If missing, install:
npm install -g @cocal/google-calendar-mcp
```

### **Authentication Timeouts**
- Delete old token files: `rm token.json`
- Re-authenticate through OAuth flow
- Check OAuth credentials file exists

### **Preview Server Issues**
- Check logs: `gcloud logs tail innerverse-ai`
- Verify port configuration
- Test health endpoint

## 📱 **Submission Strategy**

### **For Tomorrow's Demo**
1. **Deploy in test mode** ✅
2. **Add demo users** to OAuth consent screen
3. **Test all agent functionalities**
4. **Create sample dashboards** for preview
5. **Document any OAuth warnings** as "production ready pending approval"

### **Post-Submission (Next Week)**
1. Submit OAuth verification
2. Implement proper multi-tenant authentication
3. Add user management system
4. Scale infrastructure

## 🎯 **Success Criteria**

✅ **All agents working**
✅ **Calendar integration functional**  
✅ **Dashboard previews generating**
✅ **Multi-user sessions supported**
✅ **Production deployment live**

**You're ready for tomorrow! 🚀**

---

### **Quick Deploy Command**
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
./deploy.sh
```

**That's it! Your AI system will be live in ~10 minutes.** 