#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================================================"
echo -e "${BLUE}🛑 LLM Trading Competition - Shutdown Script${NC}"
echo "================================================================================"

# Function to check if a service is running
check_service() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Function to stop a service by port
stop_by_port() {
    local port=$1
    local name=$2

    if check_service $port; then
        echo -e "${YELLOW}Stopping $name (port $port)...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 1

        if check_service $port; then
            echo -e "${RED}❌ Failed to stop $name${NC}"
            return 1
        else
            echo -e "${GREEN}✅ $name stopped${NC}"
            return 0
        fi
    else
        echo -e "${YELLOW}⏭️  $name is not running${NC}"
        return 0
    fi
}

# Stop backend
stop_by_port 8000 "Backend"

# Stop frontend
stop_by_port 3000 "Frontend"

# Clean up PID files
rm -f .backend.pid .frontend.pid 2>/dev/null

# Clean up log files (optional)
if [ -f "backend.log" ] || [ -f "frontend.log" ]; then
    read -p "Delete log files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f backend.log frontend.log
        echo -e "${GREEN}✅ Log files deleted${NC}"
    fi
fi

echo ""
echo "================================================================================"
echo -e "${GREEN}✅ ALL SERVICES STOPPED${NC}"
echo "================================================================================"
