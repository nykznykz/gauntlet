#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================================================"
echo -e "${BLUE}🚀 LLM Trading Competition - Startup Script${NC}"
echo "================================================================================"

# Check if we're in the right directory
if [ ! -f "backend/app/main.py" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Function to check if a service is running
check_service() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Function to check if PostgreSQL is running
check_postgres() {
    # Check if Docker container is healthy
    if docker ps --filter "name=postgres" --filter "health=healthy" --format "{{.Names}}" | grep -q postgres 2>/dev/null; then
        return 0
    fi
    # Fallback to pg_isready if not using Docker
    if command -v pg_isready >/dev/null 2>&1; then
        if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Function to check if Redis is running
check_redis() {
    # Check if Docker container is healthy
    if docker ps --filter "name=redis" --filter "health=healthy" --format "{{.Names}}" | grep -q redis 2>/dev/null; then
        return 0
    fi
    # Fallback to redis-cli if not using Docker
    if command -v redis-cli >/dev/null 2>&1; then
        if redis-cli ping >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Check prerequisites
echo ""
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check PostgreSQL
if check_postgres; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL is not running${NC}"

    # Check if docker-compose.yml exists in backend
    if [ -f "backend/docker-compose.yml" ]; then
        echo "   Starting PostgreSQL and Redis via Docker Compose..."
        cd backend
        docker-compose up postgres redis -d
        cd ..

        # Wait for services to be ready
        echo -n "   Waiting for services to start"
        for i in {1..30}; do
            if check_postgres && check_redis; then
                echo ""
                echo -e "${GREEN}✅ PostgreSQL and Redis started via Docker${NC}"
                break
            fi
            echo -n "."
            sleep 1
        done

        if ! check_postgres; then
            echo ""
            echo -e "${RED}❌ Failed to start PostgreSQL via Docker${NC}"
            echo "   Please start manually:"
            echo "   - macOS: brew services start postgresql"
            echo "   - Linux: sudo systemctl start postgresql"
            exit 1
        fi
    else
        echo -e "${RED}   docker-compose.yml not found in backend/${NC}"
        echo "   Please start PostgreSQL manually:"
        echo "   - macOS: brew services start postgresql"
        echo "   - Linux: sudo systemctl start postgresql"
        exit 1
    fi
fi

# Check Redis
if check_redis; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠️  Redis is not running${NC}"

    # Check if docker-compose.yml exists in backend
    if [ -f "backend/docker-compose.yml" ]; then
        echo "   Starting Redis via Docker Compose..."
        cd backend
        docker-compose up redis -d
        cd ..

        # Wait for Redis to be ready
        echo -n "   Waiting for Redis to start"
        for i in {1..15}; do
            if check_redis; then
                echo ""
                echo -e "${GREEN}✅ Redis started via Docker${NC}"
                break
            fi
            echo -n "."
            sleep 1
        done

        if ! check_redis; then
            echo ""
            echo -e "${RED}❌ Failed to start Redis via Docker${NC}"
            echo "   Please start manually:"
            echo "   - macOS: brew services start redis"
            echo "   - Linux: sudo systemctl start redis"
            exit 1
        fi
    else
        echo -e "${RED}   docker-compose.yml not found in backend/${NC}"
        echo "   Please start Redis manually:"
        echo "   - macOS: brew services start redis"
        echo "   - Linux: sudo systemctl start redis"
        exit 1
    fi
fi

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}⚠️  Backend virtual environment not found${NC}"
    echo "   Creating virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Check if frontend node_modules exist
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies not found${NC}"
    echo "   Installing dependencies..."
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# Ask if user wants to reset/initialize competition
echo ""
echo -e "${YELLOW}🎮 Competition Setup${NC}"
read -p "Do you want to reset and initialize the competition? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Running initialization script...${NC}"
    cd backend
    ./venv/bin/python scripts/init_competition.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Competition initialized${NC}"
    else
        echo -e "${RED}❌ Initialization failed${NC}"
        exit 1
    fi
    cd ..
fi

# Check if backend is already running
echo ""
echo -e "${YELLOW}🔧 Starting services...${NC}"

if check_service 8000; then
    echo -e "${YELLOW}⚠️  Backend already running on port 8000${NC}"
    read -p "Kill existing process and restart? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✅ Stopped existing backend${NC}"
        sleep 1
    else
        echo -e "${YELLOW}⏭️  Skipping backend startup${NC}"
        BACKEND_STARTED="skip"
    fi
fi

# Start backend
if [ "$BACKEND_STARTED" != "skip" ]; then
    echo -e "${BLUE}Starting backend...${NC}"
    cd backend
    ./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..

    # Wait for backend to start
    echo -n "   Waiting for backend to start"
    for i in {1..30}; do
        if check_service 8000; then
            echo ""
            echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
            echo "   API: http://localhost:8000/docs"
            break
        fi
        echo -n "."
        sleep 1
    done

    if ! check_service 8000; then
        echo ""
        echo -e "${RED}❌ Backend failed to start${NC}"
        echo "   Check backend.log for errors"
        exit 1
    fi
fi

# Check if frontend is already running
if check_service 3000; then
    echo -e "${YELLOW}⚠️  Frontend already running on port 3000${NC}"
    read -p "Kill existing process and restart? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:3000 | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✅ Stopped existing frontend${NC}"
        sleep 1
    else
        echo -e "${YELLOW}⏭️  Skipping frontend startup${NC}"
        FRONTEND_STARTED="skip"
    fi
fi

# Start frontend
if [ "$FRONTEND_STARTED" != "skip" ]; then
    echo -e "${BLUE}Starting frontend...${NC}"
    cd frontend
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..

    # Wait for frontend to start
    echo -n "   Waiting for frontend to start"
    for i in {1..30}; do
        if check_service 3000; then
            echo ""
            echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
            echo "   Dashboard: http://localhost:3000"
            break
        fi
        echo -n "."
        sleep 1
    done

    if ! check_service 3000; then
        echo ""
        echo -e "${RED}❌ Frontend failed to start${NC}"
        echo "   Check frontend.log for errors"
        exit 1
    fi
fi

# Save PIDs for stop script
echo "$BACKEND_PID" > .backend.pid 2>/dev/null
echo "$FRONTEND_PID" > .frontend.pid 2>/dev/null

# Final summary
echo ""
echo "================================================================================"
echo -e "${GREEN}✅ ALL SERVICES STARTED SUCCESSFULLY!${NC}"
echo "================================================================================"
echo ""
echo -e "${BLUE}🌐 Access URLs:${NC}"
echo "   Frontend:  http://localhost:3000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo "   Backend:   tail -f backend.log"
echo "   Frontend:  tail -f frontend.log"
echo ""
echo -e "${BLUE}🛑 Stop Services:${NC}"
echo "   Run: ./stop.sh"
echo ""
echo -e "${YELLOW}💡 The scheduler will invoke LLMs every 60 minutes automatically${NC}"
echo "================================================================================"
