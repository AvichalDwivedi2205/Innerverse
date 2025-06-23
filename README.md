# Innerverse - Personal Empowerment AI System

An AI-powered personal development platform that helps users shift from victim consciousness to creator consciousness through intelligent agents for journaling, therapy, nutrition, and scheduling with advanced pattern recognition and automatic mental orchestration.

## Features

### 🧠 Mental Orchestrator Agent
- **DBSCAN Clustering Algorithm**: Advanced pattern recognition using DBSCAN to identify behavioral trends and emotional patterns
- **Automatic Triggering**: Automatically activated after therapy and journaling sessions via Vertex AI semantic embeddings
- **Pinecone Vector Storage**: All session data processed through Vertex AI embeddings and stored in Pinecone for pattern analysis
- **Exercise Recommendations**: AI-powered selection from 4 specialized exercises based on identified patterns:
  - Mindfulness & Breathing Exercises
  - Cognitive Restructuring Activities  
  - Emotional Regulation Techniques
  - Behavioral Activation Exercises
- Creates visual mind maps of personal insights
- Generates empowering recommendations for personal growth
- Tracks progress toward self-awareness and empowerment

### 📝 Journaling Agent
- **Automatic Mental Orchestration**: Every journal entry triggers mental orchestrator analysis
- **Vertex AI Embeddings**: Journal transcripts processed through Vertex AI semantic embeddings model
- **Pinecone Integration**: Embeddings automatically stored in Pinecone for pattern recognition
- Intelligent daily journaling with empowerment-focused prompts
- Reflection question generation based on personal patterns
- Mood tracking and insights
- Vector embeddings for pattern analysis

### 🗣️ Therapy Agent
- **Automatic Mental Orchestration**: Every therapy session triggers mental orchestrator analysis
- **Vertex AI Embeddings**: Therapy transcripts processed through Vertex AI semantic embeddings model
- **Pinecone Integration**: Session embeddings automatically stored for cross-session pattern analysis
- Structured therapy sessions with empowerment focus
- Clinical note generation for session continuity
- Risk assessment and progress tracking
- Integration with mental orchestrator for holistic insights

### 🍎 Nutrition Agent
- **Google Vision API Integration**: Advanced food image analysis and recognition
- **Visual Meal Planning**: Upload food photos for instant nutritional analysis
- **Image-Based Recommendations**: AI-powered meal suggestions based on visual food analysis
- AI-powered meal planning with dietary preferences
- Budget-conscious meal optimization
- Nutritional analysis and recommendations
- Ingredient substitution engine

### 📅 Scheduling Agent
- Smart calendar management with Google Calendar integration
- Natural language date/time processing
- Timezone-aware scheduling
- Conflict resolution and availability checking

## Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Platform account
- Firebase project
- Pinecone account (for vector embeddings)
- Google Calendar API credentials
- Google Vision API access

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Innerverse
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup:**
   - Copy `env-example.txt` to `.env`
   - Configure your API keys and credentials:
     ```
     GOOGLE_API_KEY=your_google_api_key
     GOOGLE_CLOUD_PROJECT=your_project_id
     PINECONE_API_KEY=your_pinecone_key
     PINECONE_INDEX_NAME=innerverse
     USER_TIMEZONE=America/New_York
     DEV_USER_ID=your_user_id
     ```

5. **Set up credentials:**
   - Place your `google-oauth-credentials.json` in the project root
   - Place your `service-account-key.json` in the project root

### Running the Application

Start the ADK web interface:
```bash
python run_adk_web.py
```

The application will be available at `http://localhost:8080`

## Architecture

### Agent Structure
```
agents/
├── common/                 # Shared services and utilities
├── journaling_agent/       # Daily journaling and reflection
├── therapy_agent/          # Structured therapy sessions
├── mental_orchestrator_agent/  # DBSCAN pattern analysis and insights
├── nutrition_agent/        # Vision API meal planning and nutrition
└── scheduling_agent/       # Calendar and time management
```

### Core Services
- **Pinecone Integration**: Vector embeddings for pattern recognition with automatic storage
- **Vertex AI Embeddings**: Semantic embeddings model for transcript processing
- **DBSCAN Clustering**: Advanced pattern recognition algorithm for trend analysis
- **Google Vision API**: Food image analysis and recognition
- **Firebase/Firestore**: Data persistence and user management
- **Google Calendar MCP**: Smart scheduling capabilities

### Automatic Mental Orchestration Flow
1. **Therapy/Journal Session** → User completes session
2. **Vertex AI Processing** → Transcript processed through semantic embeddings
3. **Pinecone Storage** → Embeddings automatically stored with metadata
4. **DBSCAN Analysis** → Mental orchestrator triggered to analyze patterns
5. **Exercise Recommendation** → AI selects 1 of 4 specialized exercises
6. **Insight Generation** → Empowerment-focused insights delivered to user

## Configuration

### Environment Variables
- `USER_TIMEZONE`: Your timezone (e.g., "America/New_York")
- `GOOGLE_API_KEY`: Google AI API key
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `PINECONE_API_KEY`: Pinecone vector database key
- `PINECONE_INDEX_NAME`: Pinecone index name (default: "innerverse")
- `DEV_USER_ID`: Your user identifier

### Model Configuration
Each agent supports model customization through environment variables:
- `JOURNALING_AGENT_MODEL`
- `THERAPY_AGENT_MODEL`
- `ORCHESTRATOR_AGENT_MODEL`
- `NUTRITION_AGENT_MODEL`
- `SCHEDULING_AGENT_MODEL`

## Usage

### Daily Workflow
1. **Morning Journaling**: Start with journaling agent for daily reflection
   - Automatic Vertex AI embedding processing
   - Automatic mental orchestration triggering
   - DBSCAN pattern analysis
2. **Scheduling**: Use scheduling agent to plan your day
3. **Nutrition Planning**: Upload food photos for Vision API analysis
4. **Therapy Sessions**: Weekly structured sessions with therapy agent
   - Automatic transcript embedding processing
   - Automatic mental orchestration triggering
5. **Insights Review**: Check mental orchestrator for DBSCAN-powered pattern analysis
6. **Exercise Recommendations**: Receive personalized exercise from 4 categories

### Agent Interactions
- **Automatic Orchestration**: Mental orchestrator automatically triggered after therapy/journaling
- **Vertex AI Pipeline**: All transcripts processed through semantic embeddings
- **Pinecone Storage**: Embeddings stored automatically for pattern recognition
- **DBSCAN Clustering**: Advanced algorithm identifies behavioral and emotional trends
- **Exercise Selection**: AI recommends 1 of 4 specialized exercises based on patterns

## Development

### Key Components
- **ADK Framework**: Google's Agent Development Kit for LLM agents
- **MCP Integration**: Model Context Protocol for tool integration
- **Vertex AI Embeddings**: Semantic analysis for transcript processing
- **DBSCAN Algorithm**: Clustering algorithm for pattern recognition
- **Google Vision API**: Food image analysis and recognition
- **Multi-Agent Coordination**: Sophisticated agent interaction system

### Data Flow
1. User interactions generate data across agents (therapy/journaling)
2. Transcripts automatically processed through Vertex AI semantic embeddings
3. Embeddings stored in Pinecone with session metadata
4. Mental orchestrator automatically triggered for DBSCAN analysis
5. Patterns analyzed and 1 of 4 exercises recommended
6. Insights and recommendations generated for user empowerment

## Support

For issues or questions:
1. Check your environment variables and credentials
2. Verify API key permissions and quotas (including Vision API)
3. Ensure all required services are properly configured
4. Check logs for detailed error information

## License

This project is proprietary software for personal empowerment and development.

---

**Transform your life through AI-powered self-awareness and empowerment with advanced pattern recognition.** 🚀 