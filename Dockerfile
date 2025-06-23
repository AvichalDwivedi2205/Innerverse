# Multi-service Dockerfile for Innerverse Production Deployment
FROM python:3.11-slim

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
ENV GOOGLE_GENAI_USE_VERTEXAI=False
ENV OAUTH_TEST_MODE=true
# GOOGLE_API_KEY will be set via Cloud Run environment variables - NEVER hardcode here! 

# Expose multiple ports for all services
EXPOSE 8080
EXPOSE 8081
EXPOSE 8082

# Copy main application file
COPY app.py .

# Start the production services
CMD ["python", "production_start.py"] 