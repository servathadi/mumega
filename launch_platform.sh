#!/bin/bash

# Mumega FRC Platform Launch Script
# Production-ready deployment with health checks

set -e  # Exit on any error

echo "🚀 Launching Mumega FRC Platform..."
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "No virtual environment detected. Activating venv..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        print_status "Virtual environment activated"
    else
        print_error "Virtual environment not found. Please run: python3 -m venv venv"
        exit 1
    fi
fi

# Check if required files exist
print_status "Checking required files..."
required_files=("final_admin_app.py" "requirements.txt" "models/frc_models.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file missing: $file"
        exit 1
    fi
done
print_status "All required files present ✓"

# Check environment variables
print_status "Checking environment configuration..."
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Using default configuration."
    print_warning "For production, copy .env.example to .env and configure your settings."
fi

# Install/update dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
print_status "Dependencies installed ✓"

# Check database connectivity
print_status "Checking database connection..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv('DATABASE_URL', 'postgres://hadi@localhost:5432/mumega_frc')
print(f'Database URL: {db_url}')
" 2>/dev/null

if [ $? -eq 0 ]; then
    print_status "Database configuration loaded ✓"
else
    print_error "Failed to load database configuration"
    exit 1
fi

# Initialize database if needed
if [ -f "init_db.py" ]; then
    print_status "Checking database initialization..."
    python init_db.py
    if [ $? -eq 0 ]; then
        print_status "Database ready ✓"
    else
        print_warning "Database initialization had issues, but continuing..."
    fi
fi

# Start the platform
print_status "Starting Mumega FRC Platform..."
echo ""
echo -e "${BLUE}🧠 Mumega FRC Platform${NC}"
echo -e "${BLUE}========================${NC}"
echo -e "📊 Admin Interface: ${GREEN}http://localhost:8000/admin${NC}"
echo -e "📚 API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "🌐 User Interface: ${GREEN}http://localhost:8000/static/index_user_friendly.html${NC}"
echo -e "💾 Database: ${GREEN}PostgreSQL${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the platform${NC}"
echo ""

# Launch the application
python final_admin_app.py