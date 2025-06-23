# Multi-service Dockerfile for Innerverse Production Deployment
FROM python:3.9-slim

# Install Node.js for MCP server
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Google Calendar MCP server globally
RUN npm install -g @cocal/google-calendar-mcp

# Copy application code
COPY . .

# Create directories for user credentials (multi-tenant ready)
RUN mkdir -p /tmp/oauth_creds
RUN chmod 755 /tmp/oauth_creds

# Set environment variables for production
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV GOOGLE_GENAI_USE_VERTEXAI=True

# Expose port (Cloud Run will set PORT env var)
EXPOSE $PORT

# Create production startup script
COPY production_start.py .

# Start all services
CMD ["python", "production_start.py"] 