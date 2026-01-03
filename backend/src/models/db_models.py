"""
SQLAlchemy database models for persistent storage
Defines tables for optimization history and user projects
"""

from sqlalchemy import (
    Column, Integer, Float, String, JSON, DateTime,
    Boolean, Text, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

# Base class for all models
Base = declarative_base()


class OptimizationHistory(Base):
    """
    Stores complete history of all optimization requests and results
    Each record represents one optimization run
    """
    __tablename__ = "optimization_history"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Input Parameters - Land Details
    land_length = Column(Float, nullable=False, comment="Land length in meters")
    land_width = Column(Float, nullable=False, comment="Land width in meters")
    total_area = Column(Float, nullable=False, comment="Total land area in sqm")
    land_shape = Column(String(20), default="rectangular", comment="Land shape")

    # Input Parameters - Requirements
    bedrooms = Column(Integer, nullable=False, comment="Number of bedrooms")
    toilets = Column(Integer, nullable=False, comment="Number of toilets")
    kitchen = Column(Integer, default=1, comment="Number of kitchens")
    living_room = Column(Integer, default=1, comment="Living room count")
    dining_room = Column(Integer, default=0, comment="Dining room count")
    garden_area = Column(Float, default=0.0, comment="Garden area in sqm")
    parking_spaces = Column(Integer, default=0, comment="Parking spaces")
    balcony = Column(Boolean, default=False, comment="Balcony included")

    # Input Parameters - Direction
    front_direction = Column(String(20), nullable=False, comment="Front facing direction")
    road_side = Column(String(20), nullable=False, comment="Road access side")

    # AI Parameters
    generations = Column(Integer, default=100, comment="GA generations used")
    population_size = Column(Integer, default=50, comment="GA population size")
    mutation_rate = Column(Float, default=0.1, comment="GA mutation rate")

    # Output Results - Complete Layout
    layout_data = Column(JSON, nullable=False, comment="Complete layout as JSON")

    # Output Results - Scores
    fitness_score = Column(Float, index=True, comment="Overall fitness score")
    efficiency_score = Column(Float, comment="Space efficiency score")
    sunlight_score = Column(Float, comment="Sunlight optimization score")
    privacy_score = Column(Float, comment="Privacy score")
    circulation_score = Column(Float, comment="Circulation efficiency score")
    regulation_compliance = Column(Float, comment="Regulation compliance score")

    # Output Results - Metrics
    total_built_area = Column(Float, comment="Total built area in sqm")
    coverage_percentage = Column(Float, comment="Land coverage percentage")
    total_rooms = Column(Integer, comment="Total number of rooms")

    # Execution Metadata
    execution_time = Column(Float, comment="Execution time in seconds")
    visualization_path = Column(String(500), nullable=True, comment="Path to floor plan image")

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When optimization was created"
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Last update time"
    )

    # User/Project Association (optional)
    user_id = Column(String(100), nullable=True, index=True, comment="User identifier")
    project_id = Column(Integer, ForeignKey("user_projects.id"), nullable=True, comment="Associated project")

    # Status
    is_active = Column(Boolean, default=True, comment="Record is active")
    is_favorite = Column(Boolean, default=False, comment="Marked as favorite")

    # Relationships
    project = relationship("UserProject", back_populates="optimizations")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_created_at', 'created_at'),
        Index('idx_fitness_score', 'fitness_score'),
        Index('idx_user_id_created', 'user_id', 'created_at'),
        Index('idx_project_id', 'project_id'),
    )

    def __repr__(self):
        return (
            f"<OptimizationHistory(id={self.id}, "
            f"area={self.total_area}, "
            f"rooms={self.bedrooms}bed/{self.toilets}bath, "
            f"score={self.fitness_score:.2f})>"
        )

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "land_dimensions": {
                "length": self.land_length,
                "width": self.land_width,
                "area": self.total_area,
                "shape": self.land_shape
            },
            "requirements": {
                "bedrooms": self.bedrooms,
                "toilets": self.toilets,
                "kitchen": self.kitchen,
                "living_room": self.living_room,
                "dining_room": self.dining_room,
                "garden_area": self.garden_area
            },
            "scores": {
                "fitness": self.fitness_score,
                "efficiency": self.efficiency_score,
                "sunlight": self.sunlight_score,
                "privacy": self.privacy_score,
                "regulation_compliance": self.regulation_compliance
            },
            "layout": self.layout_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class UserProject(Base):
    """
    User projects to organize multiple optimizations
    Allows users to group related optimization attempts
    """
    __tablename__ = "user_projects"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Project Details
    project_name = Column(String(200), nullable=False, comment="Project name")
    description = Column(Text, nullable=True, comment="Project description")

    # User Information
    user_id = Column(String(100), nullable=True, index=True, comment="Owner user ID")
    user_email = Column(String(255), nullable=True, comment="Owner email")

    # Project Metadata
    location = Column(String(200), nullable=True, comment="Physical location/address")
    client_name = Column(String(200), nullable=True, comment="Client name")

    # Latest Optimization Reference
    latest_optimization_id = Column(Integer, nullable=True, comment="ID of latest optimization")

    # Statistics (denormalized for performance)
    total_optimizations = Column(Integer, default=0, comment="Total optimization runs")
    best_fitness_score = Column(Float, nullable=True, comment="Best fitness score achieved")

    # Status
    is_active = Column(Boolean, default=True, nullable=False, comment="Project is active")
    is_archived = Column(Boolean, default=False, comment="Project is archived")

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Project creation time"
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Last update time"
    )

    # Relationships
    optimizations = relationship(
        "OptimizationHistory",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_created_at_project', 'created_at'),
        Index('idx_is_active', 'is_active'),
    )

    def __repr__(self):
        return (
            f"<UserProject(id={self.id}, "
            f"name='{self.project_name}', "
            f"optimizations={self.total_optimizations})>"
        )

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "project_name": self.project_name,
            "description": self.description,
            "location": self.location,
            "total_optimizations": self.total_optimizations,
            "best_fitness_score": self.best_fitness_score,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class SystemConfig(Base):
    """
    System configuration and settings storage
    Allows runtime configuration without redeploying
    """
    __tablename__ = "system_config"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Configuration
    config_key = Column(String(100), unique=True, nullable=False, index=True, comment="Configuration key")
    config_value = Column(Text, nullable=True, comment="Configuration value (JSON or string)")
    value_type = Column(String(20), default="string", comment="Value type (string, int, float, json, bool)")

    # Metadata
    description = Column(Text, nullable=True, comment="Configuration description")
    category = Column(String(50), nullable=True, index=True, comment="Configuration category")

    # Status
    is_active = Column(Boolean, default=True, comment="Config is active")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SystemConfig(key='{self.config_key}', value='{self.config_value}')>"


class OptimizationTemplate(Base):
    """
    Predefined templates for common land optimization scenarios
    Quick start templates (small house, family home, etc.)
    """
    __tablename__ = "optimization_templates"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Template Info
    template_name = Column(String(100), unique=True, nullable=False, comment="Template name")
    description = Column(Text, nullable=True, comment="Template description")
    category = Column(String(50), nullable=True, index=True, comment="Template category")

    # Template Configuration (stored as JSON)
    template_config = Column(JSON, nullable=False, comment="Template configuration")

    # Metadata
    min_land_area = Column(Float, nullable=True, comment="Minimum land area required")
    max_land_area = Column(Float, nullable=True, comment="Maximum land area recommended")

    # Usage Statistics
    usage_count = Column(Integer, default=0, comment="Number of times used")
    average_fitness = Column(Float, nullable=True, comment="Average fitness score")

    # Status
    is_active = Column(Boolean, default=True, comment="Template is active")
    is_default = Column(Boolean, default=False, comment="Is default template")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_category_active', 'category', 'is_active'),
    )

    def __repr__(self):
        return f"<OptimizationTemplate(name='{self.template_name}', used={self.usage_count})>"
