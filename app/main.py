"""
Trident Energy Global Risk Manager API
FastAPI application for querying the risk management database
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
from datetime import datetime

from .database import get_db_connection
from .models import (
    User, UserCreate, UserResponse,
    Risk, RiskResponse,
    Country, Role,
    ActionPlan, Control, Comment
)

# Create FastAPI app
app = FastAPI(
    title="Trident Energy Risk Manager API",
    description="API para consulta do sistema de gestão de riscos da Trident Energy",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# ROOT ENDPOINT
# ============================================

@app.get("/")
def root():
    """Root endpoint - API health check"""
    return {
        "status": "online",
        "message": "Trident Energy Risk Manager API",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================
# USERS ENDPOINTS
# ============================================

@app.get("/api/users", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    role_id: Optional[int] = None,
    country_id: Optional[int] = None,
    is_active: Optional[bool] = True
):
    """
    Get all users with optional filters
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **role_id**: Filter by role ID
    - **country_id**: Filter by country ID
    - **is_active**: Filter by active status
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            u.id,
            u.full_name,
            u.email,
            u.role_id,
            r.name as role_name,
            r.view_scope,
            u.country_id,
            c.name as country_name,
            c.code as country_code,
            u.is_admin,
            u.is_active,
            u.last_login,
            u.created_at
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        LEFT JOIN countries c ON u.country_id = c.id
        WHERE 1=1
    """
    params = []
    
    if role_id is not None:
        query += " AND u.role_id = %s"
        params.append(role_id)
    
    if country_id is not None:
        query += " AND u.country_id = %s"
        params.append(country_id)
    
    if is_active is not None:
        query += " AND u.is_active = %s"
        params.append(1 if is_active else 0)
    
    query += " ORDER BY u.full_name LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    cursor.execute(query, params)
    users = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return users


@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """Get a specific user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            u.id,
            u.full_name,
            u.email,
            u.role_id,
            r.name as role_name,
            r.view_scope,
            u.country_id,
            c.name as country_name,
            c.code as country_code,
            u.is_admin,
            u.is_active,
            u.last_login,
            u.created_at
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        LEFT JOIN countries c ON u.country_id = c.id
        WHERE u.id = %s
    """
    
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@app.get("/api/users/count")
def get_users_count():
    """Get total count of users"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as total FROM users")
    result = cursor.fetchone()
    
    cursor.execute("""
        SELECT r.name, COUNT(u.id) as count 
        FROM users u 
        JOIN roles r ON u.role_id = r.id 
        GROUP BY r.id, r.name
    """)
    by_role = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return {
        "total": result["total"],
        "by_role": by_role
    }


# ============================================
# ROLES ENDPOINTS
# ============================================

@app.get("/api/roles", response_model=List[Role])
def get_roles():
    """Get all roles"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, name, description, view_scope, 
               can_edit_any_risk, can_delete_risks, has_admin_privileges
        FROM roles
        ORDER BY id
    """)
    roles = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return roles


# ============================================
# COUNTRIES ENDPOINTS
# ============================================

@app.get("/api/countries", response_model=List[Country])
def get_countries():
    """Get all countries"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, code, name FROM countries ORDER BY name")
    countries = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return countries


# ============================================
# RISKS ENDPOINTS
# ============================================

@app.get("/api/risks", response_model=List[RiskResponse])
def get_risks(
    skip: int = 0,
    limit: int = 100,
    country_id: Optional[int] = None,
    status_id: Optional[int] = None,
    classification: Optional[str] = None
):
    """
    Get all risks with optional filters
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **country_id**: Filter by country ID
    - **status_id**: Filter by status ID
    - **classification**: Filter by residual classification (Low, Moderate, Significant)
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            r.id,
            r.risk_code,
            r.title,
            r.description,
            r.country_id,
            c.name as country_name,
            c.code as country_code,
            rr.name as risk_register,
            rf.name as function_area,
            rc.name as category,
            r.owner_id,
            u.full_name as owner_name,
            rs.name as status,
            rt.name as trend,
            r.inherent_impact,
            r.inherent_likelihood,
            r.inherent_score,
            r.inherent_classification,
            r.residual_impact,
            r.residual_likelihood,
            r.residual_score,
            r.residual_classification,
            r.last_review_date,
            r.created_at
        FROM risks r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN risk_registers rr ON r.risk_register_id = rr.id
        LEFT JOIN risk_functions rf ON r.function_id = rf.id
        LEFT JOIN risk_categories rc ON r.category_id = rc.id
        LEFT JOIN users u ON r.owner_id = u.id
        LEFT JOIN risk_statuses rs ON r.status_id = rs.id
        LEFT JOIN risk_trends rt ON r.trend_id = rt.id
        WHERE 1=1
    """
    params = []
    
    if country_id is not None:
        query += " AND r.country_id = %s"
        params.append(country_id)
    
    if status_id is not None:
        query += " AND r.status_id = %s"
        params.append(status_id)
    
    if classification is not None:
        query += " AND r.residual_classification = %s"
        params.append(classification)
    
    query += " ORDER BY r.residual_score DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    cursor.execute(query, params)
    risks = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return risks


@app.get("/api/risks/{risk_id}")
def get_risk(risk_id: int):
    """Get a specific risk by ID with all details"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get risk details
    query = """
        SELECT 
            r.*,
            c.name as country_name,
            c.code as country_code,
            rr.name as risk_register,
            rf.name as function_area,
            rc.name as category,
            pr.name as principal_risk,
            u.full_name as owner_name,
            rs.name as status,
            rt.name as trend,
            cr.name as controls_rating
        FROM risks r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN risk_registers rr ON r.risk_register_id = rr.id
        LEFT JOIN risk_functions rf ON r.function_id = rf.id
        LEFT JOIN risk_categories rc ON r.category_id = rc.id
        LEFT JOIN principal_risks pr ON r.principal_risk_id = pr.id
        LEFT JOIN users u ON r.owner_id = u.id
        LEFT JOIN risk_statuses rs ON r.status_id = rs.id
        LEFT JOIN risk_trends rt ON r.trend_id = rt.id
        LEFT JOIN control_ratings cr ON r.controls_rating_id = cr.id
        WHERE r.id = %s
    """
    
    cursor.execute(query, (risk_id,))
    risk = cursor.fetchone()
    
    if not risk:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Risk not found")
    
    # Get controls
    cursor.execute("""
        SELECT id, title, description, control_type, effectiveness_score
        FROM controls WHERE risk_id = %s
    """, (risk_id,))
    controls = cursor.fetchall()
    
    # Get action plans
    cursor.execute("""
        SELECT ap.id, ap.title, ap.description, ap.due_date, ap.status, ap.priority,
               u.full_name as responsible_name
        FROM action_plans ap
        LEFT JOIN users u ON ap.responsible_id = u.id
        WHERE ap.risk_id = %s
    """, (risk_id,))
    action_plans = cursor.fetchall()
    
    # Get comments
    cursor.execute("""
        SELECT cm.id, cm.comment_text, cm.created_at, u.full_name as user_name
        FROM comments cm
        LEFT JOIN users u ON cm.user_id = u.id
        WHERE cm.risk_id = %s AND cm.is_internal = 0
        ORDER BY cm.created_at DESC
    """, (risk_id,))
    comments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    risk["controls"] = controls
    risk["action_plans"] = action_plans
    risk["comments"] = comments
    
    return risk


@app.get("/api/risks/summary/by-country")
def get_risks_by_country():
    """Get risk summary by country"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            c.code as country_code,
            c.name as country_name,
            COUNT(r.id) as total_risks,
            SUM(CASE WHEN r.residual_classification = 'Significant' THEN 1 ELSE 0 END) as significant,
            SUM(CASE WHEN r.residual_classification = 'Moderate' THEN 1 ELSE 0 END) as moderate,
            SUM(CASE WHEN r.residual_classification = 'Low' THEN 1 ELSE 0 END) as low,
            ROUND(AVG(r.residual_score), 1) as avg_residual_score
        FROM risks r
        JOIN countries c ON r.country_id = c.id
        GROUP BY c.id, c.code, c.name
        ORDER BY total_risks DESC
    """)
    summary = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return summary


@app.get("/api/risks/summary/heatmap")
def get_risk_heatmap():
    """Get risk heatmap data (impact vs likelihood matrix)"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            residual_impact as impact,
            residual_likelihood as likelihood,
            COUNT(*) as count
        FROM risks
        WHERE status_id != 4
        GROUP BY residual_impact, residual_likelihood
    """)
    heatmap = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return heatmap


# ============================================
# ACTION PLANS ENDPOINTS
# ============================================

@app.get("/api/action-plans")
def get_action_plans(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
):
    """Get all action plans with optional status filter"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            ap.id,
            ap.title,
            ap.description,
            ap.due_date,
            ap.status,
            ap.priority,
            ap.completion_date,
            r.risk_code,
            r.title as risk_title,
            u.full_name as responsible_name
        FROM action_plans ap
        JOIN risks r ON ap.risk_id = r.id
        JOIN users u ON ap.responsible_id = u.id
        WHERE 1=1
    """
    params = []
    
    if status is not None:
        query += " AND ap.status = %s"
        params.append(status)
    
    query += " ORDER BY ap.due_date LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    cursor.execute(query, params)
    plans = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return plans


# ============================================
# DASHBOARD ENDPOINTS
# ============================================

@app.get("/api/dashboard/summary")
def get_dashboard_summary():
    """Get dashboard summary statistics"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Total risks
    cursor.execute("SELECT COUNT(*) as total FROM risks WHERE status_id != 4")
    total_risks = cursor.fetchone()["total"]
    
    # Risks by classification
    cursor.execute("""
        SELECT residual_classification, COUNT(*) as count
        FROM risks WHERE status_id != 4
        GROUP BY residual_classification
    """)
    by_classification = {row["residual_classification"]: row["count"] for row in cursor.fetchall()}
    
    # Average residual score
    cursor.execute("SELECT ROUND(AVG(residual_score), 1) as avg FROM risks WHERE status_id != 4")
    avg_score = cursor.fetchone()["avg"]
    
    # Open action plans
    cursor.execute("SELECT COUNT(*) as total FROM action_plans WHERE status IN ('Open', 'In Progress')")
    open_actions = cursor.fetchone()["total"]
    
    # Overdue action plans
    cursor.execute("""
        SELECT COUNT(*) as total FROM action_plans 
        WHERE status IN ('Open', 'In Progress') AND due_date < CURDATE()
    """)
    overdue_actions = cursor.fetchone()["total"]
    
    # Total users
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE is_active = 1")
    total_users = cursor.fetchone()["total"]
    
    cursor.close()
    conn.close()
    
    return {
        "total_risks": total_risks,
        "risks_by_classification": by_classification,
        "average_residual_score": avg_score,
        "open_action_plans": open_actions,
        "overdue_action_plans": overdue_actions,
        "total_active_users": total_users
    }
