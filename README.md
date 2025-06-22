# Innerverse - Personal Empowerment AI System

An AI-powered personal development platform that helps users shift from victim consciousness to creator consciousness through intelligent agents for journaling, therapy, nutrition, and scheduling.

## Features

### 🧠 Mental Orchestrator Agent
- Analyzes internal patterns from journal entries and therapy sessions
- Creates visual mind maps of personal insights
- Generates empowering recommendations for personal growth
- Tracks progress toward self-awareness and empowerment

### 📝 Journaling Agent
- Intelligent daily journaling with empowerment-focused prompts
- Reflection question generation based on personal patterns
- Mood tracking and insights
- Vector embeddings for pattern analysis

### 🗣️ Therapy Agent
- Structured therapy sessions with empowerment focus
- Clinical note generation for session continuity
- Risk assessment and progress tracking
- Integration with mental orchestrator for holistic insights

### 🍎 Nutrition Agent
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
├── mental_orchestrator_agent/  # Pattern analysis and insights
├── nutrition_agent/        # Meal planning and nutrition
└── scheduling_agent/       # Calendar and time management
```

### Core Services
- **Pinecone Integration**: Vector embeddings for pattern recognition
- **Firebase/Firestore**: Data persistence and user management
- **Google Calendar MCP**: Smart scheduling capabilities
- **Vertex AI**: Advanced AI model integration

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
2. **Scheduling**: Use scheduling agent to plan your day
3. **Nutrition Planning**: Get meal recommendations from nutrition agent
4. **Therapy Sessions**: Weekly structured sessions with therapy agent
5. **Insights Review**: Check mental orchestrator for pattern analysis

### Agent Interactions
- All agents feed data to the mental orchestrator for holistic analysis
- Reflection questions are generated based on cross-agent insights
- Progress tracking spans across all personal development areas

## Development

### Key Components
- **ADK Framework**: Google's Agent Development Kit for LLM agents
- **MCP Integration**: Model Context Protocol for tool integration
- **Vector Embeddings**: Semantic analysis for pattern recognition
- **Multi-Agent Coordination**: Sophisticated agent interaction system

### Data Flow
1. User interactions generate data across agents
2. Data is processed and stored with vector embeddings
3. Mental orchestrator analyzes patterns across all data sources
4. Insights and recommendations are generated for user empowerment

## Support

For issues or questions:
1. Check your environment variables and credentials
2. Verify API key permissions and quotas
3. Ensure all required services are properly configured
4. Check logs for detailed error information

## License

This project is proprietary software for personal empowerment and development.

---

**Transform your life through AI-powered self-awareness and empowerment.** 🚀 