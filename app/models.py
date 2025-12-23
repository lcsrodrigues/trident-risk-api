"""
Pydantic models for Trident Energy Risk Manager API
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date


# ============================================
# USER MODELS
# ============================================

class UserBase(BaseModel):
    full_name: str
    email: str
    role_id: int
    country_id: Optional[int] = None
    is_admin: bool = False
    is_active: bool = True


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role_id: int
    role_name: Optional[str] = None
    view_scope: Optional[str] = None
    country_id: Optional[int] = None
    country_name: Optional[str] = None
    country_code: Optional[str] = None
    is_admin: bool
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# ROLE MODELS
# ============================================

class Role(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    view_scope: str
    can_edit_any_risk: bool = False
    can_delete_risks: bool = False
    has_admin_privileges: bool = False

    class Config:
        from_attributes = True


# ============================================
# COUNTRY MODELS
# ============================================

class Country(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True


# ============================================
# RISK MODELS
# ============================================

class RiskBase(BaseModel):
    risk_code: Optional[str] = None
    title: str
    description: Optional[str] = None
    country_id: int
    risk_register_id: int
    function_id: int
    category_id: int
    principal_risk_id: Optional[int] = None
    owner_id: int
    status_id: int = 1
    trend_id: Optional[int] = None
    inherent_impact: int
    inherent_likelihood: int
    controls_rating_id: Optional[int] = None
    residual_impact: int
    residual_likelihood: int


class Risk(RiskBase):
    id: int
    inherent_score: Optional[int] = None
    residual_score: Optional[int] = None
    inherent_classification: Optional[str] = None
    residual_classification: Optional[str] = None
    last_review_date: Optional[date] = None
    last_reviewer_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RiskResponse(BaseModel):
    id: int
    risk_code: Optional[str] = None
    title: str
    description: Optional[str] = None
    country_id: int
    country_name: Optional[str] = None
    country_code: Optional[str] = None
    risk_register: Optional[str] = None
    function_area: Optional[str] = None
    category: Optional[str] = None
    owner_id: int
    owner_name: Optional[str] = None
    status: Optional[str] = None
    trend: Optional[str] = None
    inherent_impact: int
    inherent_likelihood: int
    inherent_score: Optional[int] = None
    inherent_classification: Optional[str] = None
    residual_impact: int
    residual_likelihood: int
    residual_score: Optional[int] = None
    residual_classification: Optional[str] = None
    last_review_date: Optional[date] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# CONTROL MODELS
# ============================================

class Control(BaseModel):
    id: int
    risk_id: int
    title: str
    description: Optional[str] = None
    control_type: str = "preventive"
    rating_id: Optional[int] = None
    effectiveness_score: Optional[int] = None
    is_active: bool = True

    class Config:
        from_attributes = True


# ============================================
# ACTION PLAN MODELS
# ============================================

class ActionPlan(BaseModel):
    id: int
    risk_id: int
    title: str
    description: Optional[str] = None
    responsible_id: int
    due_date: Optional[date] = None
    status: str = "Open"
    priority: str = "Medium"
    completion_date: Optional[date] = None

    class Config:
        from_attributes = True


# ============================================
# COMMENT MODELS
# ============================================

class Comment(BaseModel):
    id: int
    risk_id: int
    user_id: int
    comment_text: str
    is_internal: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
