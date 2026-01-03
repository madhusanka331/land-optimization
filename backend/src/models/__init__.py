"""
Models package - exports all Pydantic schemas and SQLAlchemy models
"""

# Pydantic Schemas (API validation)
from .schemas import (
    # Enums
    DirectionEnum,
    LandShapeEnum,

    # Input Schemas
    LandInputSchema,

    # Output Schemas
    RoomSchema,
    LayoutOutputSchema,

    # Request/Response Schemas
    OptimizationRequestSchema,
    OptimizationResponseSchema,
    ValidationResponseSchema,
    HealthCheckSchema,
)

# SQLAlchemy Models (Database ORM)
from .db_models import (
    Base,
    OptimizationHistory,
    UserProject,
    SystemConfig,
    OptimizationTemplate,
)

__all__ = [
    # Enums
    "DirectionEnum",
    "LandShapeEnum",

    # Pydantic Schemas
    "LandInputSchema",
    "RoomSchema",
    "LayoutOutputSchema",
    "OptimizationRequestSchema",
    "OptimizationResponseSchema",
    "ValidationResponseSchema",
    "HealthCheckSchema",

    # SQLAlchemy Models
    "Base",
    "OptimizationHistory",
    "UserProject",
    "SystemConfig",
    "OptimizationTemplate",
]
