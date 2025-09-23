#!/bin/bash

# Development script for Customer Lifecycle AI
echo "🚀 Starting Customer Lifecycle AI Development Environment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  Port $1 is already in use${NC}"
        return 1
    else
        return 0
    fi
}

# Function to kill processes on ports
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up processes...${NC}"
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Trap to cleanup on script exit
trap cleanup EXIT

# Check if required directories exist
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Backend directory not found${NC}"
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Frontend directory not found${NC}"
    exit 1
fi

# Check if backend dependencies are installed
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  Backend .env file not found${NC}"
    echo -e "${BLUE}ℹ️  Creating basic .env file...${NC}"
    cat > backend/.env << EOF
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
AI_FALLBACK_ENABLED=true
EOF
fi

# Check if frontend node_modules exist
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies not installed${NC}"
    echo -e "${BLUE}ℹ️  Installing frontend dependencies...${NC}"
    cd frontend && npm install && cd ..
fi

# Check if backend virtual environment exists
echo -e "${BLUE}ℹ️  Checking backend dependencies...${NC}"
cd backend
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Using system Python...${NC}"
}

# Install backend dependencies if needed
pip install -r requirements.txt > /dev/null 2>&1

# Initialize database if needed
if [ ! -f "sprint_board.db" ]; then
    echo -e "${BLUE}ℹ️  Initializing database...${NC}"
    python init_sprint_db.py
fi

cd ..

# Check ports
echo -e "${BLUE}ℹ️  Checking ports...${NC}"
if ! check_port 8000; then
    echo -e "${RED}❌ Backend port 8000 is in use. Please free it first.${NC}"
    exit 1
fi

if ! check_port 3000; then
    echo -e "${RED}❌ Frontend port 3000 is in use. Please free it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All checks passed!${NC}"
echo ""
echo -e "${BLUE}🔧 Starting services...${NC}"

# Start backend
echo -e "${BLUE}📡 Starting Backend (FastAPI)...${NC}"
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
fi
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo -e "${BLUE}🎨 Starting Frontend (React)...${NC}"
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait for services to start
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 5

# Check if services are running
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Backend running on http://localhost:8000${NC}"
    echo -e "${GREEN}📚 API Documentation: http://localhost:8000/docs${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
fi

if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Frontend running on http://localhost:3000${NC}"
else
    echo -e "${RED}❌ Frontend failed to start${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Development environment is ready!${NC}"
echo -e "${BLUE}📊 Sprint Board: http://localhost:3000/sprint-board${NC}"
echo -e "${BLUE}📈 Dashboard: http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for user to stop
wait
