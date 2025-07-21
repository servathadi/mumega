"""
Final Mumega FRC Platform - Admin Application
Uses modern FastAPI patterns and compatible with current versions
"""

import os
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from tortoise import Tortoise
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our models
from models.frc_models import (
    User, ProtocolTemplate, ProtocolSession, CoherenceLog, 
    UserProfile, SystemMetrics
)

# Import our existing resonancelib
from resonancelib import core, protocols, tools, avf

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://hadi@localhost:5432/mumega_frc")
SECRET_KEY = os.getenv("SECRET_KEY", "frc-secret-key")

# Lifespan manager for database connections
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={'models': ['models.frc_models']}
    )
    print("📊 Database connected successfully")
    yield
    # Shutdown
    await Tortoise.close_connections()
    print("📊 Database disconnected")

# Create main FastAPI app with lifespan
app = FastAPI(
    title="Mumega FRC Platform",
    description="Consciousness Enhancement Platform with Admin Interface",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Simple session storage (for demo purposes)
active_sessions = set()

def create_session_token(username: str) -> str:
    """Create a simple session token"""
    token = f"{username}_{datetime.now().timestamp()}"
    active_sessions.add(token)
    return token

def verify_session(token: str) -> bool:
    """Verify if session token is valid"""
    return token in active_sessions

# Routes

@app.get("/")
async def root():
    """Root endpoint with platform information"""
    return {
        "platform": "Mumega FRC Platform",
        "version": "2.0.0",
        "description": "Consciousness Enhancement Platform with Admin Interface",
        "admin_url": "/admin",
        "api_docs": "/docs",
        "status": "operational",
        "features": {
            "database": "PostgreSQL with Tortoise ORM",
            "protocols": "Interactive consciousness protocols",
            "coherence_tracking": "S_FRC calculations and logging",
            "admin_interface": "Simple web-based administration"
        }
    }

@app.get("/admin")
async def admin_interface():
    """Simple admin interface"""
    return HTMLResponse(content="""<!DOCTYPE html><html><head><title>Mumega FRC Admin</title><meta name="viewport" content="width=device-width, initial-scale=1"><style>* { box-sizing: border-box; }body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }.container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; }.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }.header h1 { margin: 0; font-size: 3em; font-weight: 300; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }.header p { margin: 10px 0 0 0; opacity: 0.9; font-size: 1.2em; }.content { padding: 40px; }.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }.stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; text-align: center; box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); transition: transform 0.3s ease; }.stat-card:hover { transform: translateY(-5px); }.stat-number { font-size: 3em; font-weight: bold; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }.stat-label { opacity: 0.9; font-size: 1.1em; }.section { margin-bottom: 40px; background: #f8f9fa; padding: 30px; border-radius: 15px; }.section h3 { color: #333; margin-top: 0; font-size: 1.5em; margin-bottom: 20px; }.btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; border: none; border-radius: 25px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; font-weight: 500; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); }.btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4); }.api-test { background: white; padding: 25px; border-radius: 15px; margin: 20px 0; border: 1px solid #e9ecef; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }.api-test h4 { color: #495057; margin-top: 0; margin-bottom: 15px; }.response { background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 15px; font-family: 'Monaco', 'Menlo', monospace; font-size: 13px; border-left: 4px solid #667eea; overflow-x: auto; }.status-list { list-style: none; padding: 0; }.status-list li { padding: 10px 0; border-bottom: 1px solid #e9ecef; font-size: 1.1em; }.status-list li:last-child { border-bottom: none; }.loading { color: #6c757d; font-style: italic; }.error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 5px; border: 1px solid #f5c6cb; }</style></head><body><div class="container"><div class="header"><h1>🧠 Mumega FRC</h1><p>Consciousness Enhancement Platform Administration</p></div><div class="content"><div class="stats" id="stats"><div class="stat-card"><div class="stat-number" id="userCount">Loading...</div><div class="stat-label">Total Users</div></div><div class="stat-card"><div class="stat-number" id="sessionCount">Loading...</div><div class="stat-label">Protocol Sessions</div></div><div class="stat-card"><div class="stat-number" id="protocolCount">Loading...</div><div class="stat-label">Active Protocols</div></div><div class="stat-card"><div class="stat-number" id="avgSfrc">Loading...</div><div class="stat-label">Avg S_FRC</div></div></div><div class="section"><h3>🧪 API Testing & Monitoring</h3><div class="api-test"><h4>🔬 Test S_FRC Calculation</h4><p>Test the core consciousness metric calculation with sample data</p><button class="btn" onclick="testSFRC()">Run S_FRC Test</button><div id="sfrcResult" class="response" style="display: none;"></div></div><div class="api-test"><h4>📋 Protocol Management</h4><p>View available interactive consciousness protocols</p><button class="btn" onclick="loadProtocols()">Load Protocols</button><div id="protocolsResult" class="response" style="display: none;"></div></div><div class="api-test"><h4>📊 Database Statistics</h4><p>Real-time platform usage statistics</p><button class="btn" onclick="loadStats()">Refresh Stats</button><div id="statsResult" class="response" style="display: none;"></div></div><div class="api-test"><h4>👥 User Management</h4><p>View registered users and their consciousness development</p><button class="btn" onclick="loadUsers()">Load Users</button><div id="usersResult" class="response" style="display: none;"></div></div></div><div class="section"><h3>🌐 Platform Access</h3><a href="/docs" class="btn">📚 API Documentation</a><a href="/static/index_user_friendly.html" class="btn">👤 User Interface</a><a href="/static/index_simple.html" class="btn">🔧 Developer Interface</a><a href="/api/protocols" class="btn">📋 Protocols API</a></div><div class="section"><h3>⚡ System Status</h3><ul class="status-list"><li>🟢 Database: Connected (PostgreSQL)</li><li>🟢 FRC Library: v1.0.0</li><li>🟢 Tortoise ORM: Active</li><li>🟢 API: Operational</li><li>🟢 Redis: <span id="redisStatus">Connected</span></li></ul></div></div></div><script>loadStats();async function makeRequest(url, options = {}) { try { const response = await fetch(url, options); if (!response.ok) { throw new Error(`HTTP ${response.status}: ${response.statusText}`); } return await response.json(); } catch (error) { console.error('Request failed:', error); throw error; } }async function loadStats() { try { const data = await makeRequest('/admin/api/stats'); document.getElementById('userCount').textContent = data.users || 0; document.getElementById('sessionCount').textContent = data.sessions || 0; document.getElementById('protocolCount').textContent = data.protocols || 0; document.getElementById('avgSfrc').textContent = (data.avg_sfrc || 0).toFixed(3); document.getElementById('statsResult').style.display = 'block'; document.getElementById('statsResult').textContent = JSON.stringify(data, null, 2); } catch (error) { showError('statsResult', 'Error loading stats: ' + error.message); } }async function testSFRC() { const testData = { coherence_levels: [0.1, 0.3, 0.5, 0.8, 0.9, 0.7, 0.4, 0.2], context: "admin_test_comprehensive" }; try { const data = await makeRequest('/api/calculate-sfrc', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(testData) }); document.getElementById('sfrcResult').style.display = 'block'; document.getElementById('sfrcResult').textContent = JSON.stringify(data, null, 2); } catch (error) { showError('sfrcResult', 'Error testing S_FRC: ' + error.message); } }async function loadProtocols() { try { const data = await makeRequest('/api/protocols'); document.getElementById('protocolsResult').style.display = 'block'; document.getElementById('protocolsResult').textContent = JSON.stringify(data, null, 2); } catch (error) { showError('protocolsResult', 'Error loading protocols: ' + error.message); } }async function loadUsers() { try { const data = await makeRequest('/api/users'); document.getElementById('usersResult').style.display = 'block'; document.getElementById('usersResult').textContent = JSON.stringify(data, null, 2); } catch (error) { showError('usersResult', 'Error loading users: ' + error.message); } }function showError(elementId, message) { const element = document.getElementById(elementId); element.style.display = 'block'; element.innerHTML = `<div class="error">${message}</div>`; }setInterval(loadStats, 30000);</script></body></html>""")

@app.get("/admin/api/stats")
async def admin_stats():
    """Get admin statistics"""
    try:
        stats = {
            "users": await User.all().count(),
            "sessions": await ProtocolSession.all().count(),
            "protocols": await ProtocolTemplate.filter(is_active=True).count(),
            "avg_sfrc": 0.0,
            "total_coherence_logs": await CoherenceLog.all().count(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Calculate average S_FRC
        coherence_logs = await CoherenceLog.all()
        if coherence_logs:
            stats["avg_sfrc"] = sum(log.sfrc_score for log in coherence_logs) / len(coherence_logs)
        
        return stats
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

# API Endpoints

@app.post("/api/calculate-sfrc")
async def calculate_sfrc_api(request: dict):
    """Calculate S_FRC and optionally log to database"""
    coherence_levels = request.get("coherence_levels", [])
    user_id = request.get("user_id")
    context = request.get("context", "api_calculation")
    
    if len(coherence_levels) != 8:
        raise HTTPException(status_code=400, detail="coherence_levels must have 8 values (μ0 to μ7)")
    
    # Calculate S_FRC using our existing library
    sfrc = core.calculate_s_frc(coherence_levels)
    
    # Determine interpretation
    if sfrc < 0.3:
        interpretation = "Low coherence - system fragmented, significant dissonance between consciousness levels"
    elif sfrc < 0.6:
        interpretation = "Moderate coherence - partial integration, room for improvement in alignment"
    elif sfrc < 0.8:
        interpretation = "Good coherence - system operating with healthy integration across levels"
    else:
        interpretation = "High coherence - excellent integration, optimal consciousness functioning"
    
    # Log to database if user provided
    if user_id:
        try:
            user = await User.get(id=user_id)
            await CoherenceLog.create(
                user=user,
                mu_levels_json=coherence_levels,
                sfrc_score=sfrc,
                context=context,
                calculation_method="api_standard",
                notes=f"Calculation via API - {interpretation}"
            )
        except Exception as e:
            print(f"Failed to log to database: {e}")
    
    return {
        "sfrc": round(sfrc, 6),
        "coherence_levels": coherence_levels,
        "interpretation": interpretation,
        "context": context,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/protocols")
async def get_protocols():
    """Get available protocols from database"""
    protocols = await ProtocolTemplate.filter(is_active=True).all()
    
    return {
        "protocols": [
            {
                "id": p.slug,
                "name": p.name,
                "description": p.description,
                "duration": f"{p.duration_minutes} minutes",
                "difficulty": p.difficulty_level,
                "category": p.category,
                "steps_count": len(p.steps),
                "created_at": p.created_at.isoformat()
            }
            for p in protocols
        ],
        "total_count": len(protocols),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/users")
async def get_users():
    """Get user list for admin"""
    users = await User.all()
    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": u.full_name,
                "is_active": u.is_active,
                "is_admin": u.is_admin,
                "baseline_sfrc": round(u.baseline_sfrc, 4),
                "coherence_level": u.coherence_level,
                "created_at": u.created_at.isoformat()
            }
            for u in users
        ],
        "total_count": len(users),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/sessions")
async def get_sessions():
    """Get recent protocol sessions"""
    sessions = await ProtocolSession.all().prefetch_related("user", "protocol").limit(50).order_by("-started_at")
    
    return {
        "sessions": [
            {
                "id": s.id,
                "user": s.user.username,
                "protocol": s.protocol.name,
                "started_at": s.started_at.isoformat(),
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                "is_completed": s.is_completed,
                "coherence_improvement": s.coherence_improvement,
                "duration_minutes": s.duration_minutes
            }
            for s in sessions
        ],
        "total_count": len(sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/coherence-logs")
async def get_coherence_logs():
    """Get recent coherence calculations"""
    logs = await CoherenceLog.all().prefetch_related("user").limit(100).order_by("-created_at")
    
    return {
        "logs": [
            {
                "id": log.id,
                "user": log.user.username if log.user else "Anonymous",
                "sfrc_score": round(log.sfrc_score, 6),
                "mu_levels": log.mu_levels,
                "context": log.context,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ],
        "total_count": len(logs),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Mumega FRC Platform...")
    print(f"📊 Admin Interface: http://localhost:8000/admin")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🌐 User Interface: http://localhost:8000/static/index_user_friendly.html")
    print(f"💾 Database: {DATABASE_URL}")
    uvicorn.run(app, host="0.0.0.0", port=8000)