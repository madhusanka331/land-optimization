"""
CRUD operations for optimization history.
Handles database operations for saving and retrieving optimization results.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from loguru import logger

from ...models.db_models import OptimizationHistory, UserProject
from ...models.schemas import (
    LandInputSchema,
    LayoutOutputSchema,
    OptimizationRequestSchema,
)


def create_optimization_record(
    db: Session,
    land_input: LandInputSchema,
    layout_output: LayoutOutputSchema,
    project_id: Optional[int] = None,
) -> OptimizationHistory:
    """
    Save an optimization result to the database.

    Args:
        db: Database session
        land_input: Input parameters
        layout_output: Optimization result
        project_id: Optional project ID to associate with

    Returns:
        Created OptimizationHistory record
    """
    # Convert layout output to JSON-serializable dict
    layout_data = layout_output.model_dump()

    # Create record
    optimization = OptimizationHistory(
        # Input parameters
        land_length=land_input.length,
        land_width=land_input.width,
        total_area=land_input.total_area or (land_input.length * land_input.width),
        bedrooms=land_input.bedrooms,
        toilets=land_input.toilets,
        living_room=land_input.living_room,
        dining_room=land_input.dining_room,
        kitchen=land_input.kitchen,
        garden_area=land_input.garden_area,
        front_direction=land_input.front_direction.value,
        road_side=land_input.road_side.value,
        land_shape=land_input.shape.value if land_input.shape else None,

        # Output results
        layout_data=layout_data,
        fitness_score=layout_output.fitness_score,
        efficiency_score=layout_output.efficiency_score,
        sunlight_score=layout_output.sunlight_score,
        privacy_score=layout_output.privacy_score,
        regulation_compliance=layout_output.regulation_compliance,
        generations=layout_output.generation_count if hasattr(layout_output, 'generation_count') else None,
        execution_time=layout_output.optimization_time if hasattr(layout_output, 'optimization_time') else None,

        # Project association
        project_id=project_id,
    )

    db.add(optimization)
    db.commit()
    db.refresh(optimization)

    logger.info(f"Saved optimization record: ID={optimization.id}, Fitness={optimization.fitness_score:.2f}")

    return optimization


def get_optimization_by_id(
    db: Session,
    optimization_id: int
) -> Optional[OptimizationHistory]:
    """
    Get optimization record by ID.

    Args:
        db: Database session
        optimization_id: Record ID

    Returns:
        OptimizationHistory record or None
    """
    return db.query(OptimizationHistory).filter(
        OptimizationHistory.id == optimization_id
    ).first()


def get_recent_optimizations(
    db: Session,
    limit: int = 10,
    project_id: Optional[int] = None
) -> List[OptimizationHistory]:
    """
    Get recent optimization records.

    Args:
        db: Database session
        limit: Maximum number of records
        project_id: Optional project filter

    Returns:
        List of OptimizationHistory records
    """
    query = db.query(OptimizationHistory)

    if project_id:
        query = query.filter(OptimizationHistory.project_id == project_id)

    return query.order_by(
        desc(OptimizationHistory.created_at)
    ).limit(limit).all()


def get_best_optimizations(
    db: Session,
    limit: int = 10,
    min_fitness: float = 70.0
) -> List[OptimizationHistory]:
    """
    Get best optimization results.

    Args:
        db: Database session
        limit: Maximum number of records
        min_fitness: Minimum fitness score threshold

    Returns:
        List of best OptimizationHistory records
    """
    return db.query(OptimizationHistory).filter(
        OptimizationHistory.fitness_score >= min_fitness
    ).order_by(
        desc(OptimizationHistory.fitness_score)
    ).limit(limit).all()


def search_optimizations(
    db: Session,
    bedrooms: Optional[int] = None,
    min_area: Optional[float] = None,
    max_area: Optional[float] = None,
    min_fitness: Optional[float] = None,
    limit: int = 50
) -> List[OptimizationHistory]:
    """
    Search optimization records with filters.

    Args:
        db: Database session
        bedrooms: Filter by bedroom count
        min_area: Minimum land area
        max_area: Maximum land area
        min_fitness: Minimum fitness score
        limit: Maximum number of records

    Returns:
        List of matching OptimizationHistory records
    """
    query = db.query(OptimizationHistory)

    if bedrooms is not None:
        query = query.filter(OptimizationHistory.bedrooms == bedrooms)

    if min_area is not None:
        query = query.filter(OptimizationHistory.total_area >= min_area)

    if max_area is not None:
        query = query.filter(OptimizationHistory.total_area <= max_area)

    if min_fitness is not None:
        query = query.filter(OptimizationHistory.fitness_score >= min_fitness)

    return query.order_by(
        desc(OptimizationHistory.created_at)
    ).limit(limit).all()


def delete_optimization(
    db: Session,
    optimization_id: int
) -> bool:
    """
    Delete an optimization record.

    Args:
        db: Database session
        optimization_id: Record ID

    Returns:
        True if deleted, False if not found
    """
    optimization = get_optimization_by_id(db, optimization_id)

    if optimization:
        db.delete(optimization)
        db.commit()
        logger.info(f"Deleted optimization record: ID={optimization_id}")
        return True

    return False


# Project CRUD operations

def create_project(
    db: Session,
    name: str,
    description: Optional[str] = None,
    user_email: Optional[str] = None
) -> UserProject:
    """
    Create a new project.

    Args:
        db: Database session
        name: Project name
        description: Project description
        user_email: User email

    Returns:
        Created UserProject record
    """
    project = UserProject(
        name=name,
        description=description,
        user_email=user_email,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    logger.info(f"Created project: ID={project.id}, Name={project.name}")

    return project


def get_project_by_id(
    db: Session,
    project_id: int
) -> Optional[UserProject]:
    """
    Get project by ID.

    Args:
        db: Database session
        project_id: Project ID

    Returns:
        UserProject record or None
    """
    return db.query(UserProject).filter(
        UserProject.id == project_id
    ).first()


def get_all_projects(
    db: Session,
    limit: int = 100
) -> List[UserProject]:
    """
    Get all projects.

    Args:
        db: Database session
        limit: Maximum number of records

    Returns:
        List of UserProject records
    """
    return db.query(UserProject).order_by(
        desc(UserProject.created_at)
    ).limit(limit).all()


def update_project(
    db: Session,
    project_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Optional[UserProject]:
    """
    Update project details.

    Args:
        db: Database session
        project_id: Project ID
        name: New name
        description: New description

    Returns:
        Updated UserProject record or None
    """
    project = get_project_by_id(db, project_id)

    if project:
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description

        project.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(project)

        logger.info(f"Updated project: ID={project_id}")

    return project


def delete_project(
    db: Session,
    project_id: int
) -> bool:
    """
    Delete a project and all associated optimizations.

    Args:
        db: Database session
        project_id: Project ID

    Returns:
        True if deleted, False if not found
    """
    project = get_project_by_id(db, project_id)

    if project:
        db.delete(project)
        db.commit()
        logger.info(f"Deleted project: ID={project_id}")
        return True

    return False
