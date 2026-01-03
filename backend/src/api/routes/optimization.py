"""
Optimization API endpoints.
Provides REST API for land optimization, validation, and visualization.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path as FilePath
from loguru import logger

from ...models.schemas import (
    OptimizationRequestSchema,
    OptimizationResponseSchema,
    ValidationResponseSchema,
    LandInputSchema,
)
from ...services.validation_service import ValidationService
from ...services.genetic_optimizer import GeneticOptimizer
from ...services.visualization_service import VisualizationService
from ..database import get_db
from ..crud import optimization_crud


router = APIRouter(prefix="/optimization", tags=["Optimization"])

# Initialize services
validation_service = ValidationService()
visualization_service = VisualizationService()


@router.post(
    "/calculate-buildable-area",
    summary="Calculate buildable area from land dimensions",
    description="Calculate buildable area and check if rooms will fit"
)
async def calculate_buildable_area(
    land_input: LandInputSchema
) -> dict:
    """
    Calculate buildable area from land dimensions.

    Takes land dimensions and room requirements, returns:
    - Total land area
    - Buildable area (after setbacks)
    - Required space for rooms
    - Whether rooms will fit
    - Setback details
    """
    try:
        from ...services.building_rules import SriLankanBuildingRules
        from ...services.room_optimizer import RoomOptimizer

        # Calculate buildable area
        buildable = SriLankanBuildingRules.get_buildable_area(
            land_input.length,
            land_input.width,
            land_input.total_area
        )

        # Calculate required space for rooms
        room_optimizer = RoomOptimizer(land_input)
        optimized_land_input, messages = room_optimizer.optimize_room_count()

        # Calculate total required space
        total_required = 0

        # Master bedroom
        total_required += 14.4

        # Regular bedrooms
        total_required += (optimized_land_input.bedrooms - 1) * 10.8

        # Toilets
        total_required += optimized_land_input.toilets * 4.4

        # Kitchen, living, dining
        if optimized_land_input.kitchen:
            total_required += 10.8
        if optimized_land_input.living_room:
            total_required += 14.4
        if optimized_land_input.dining_room:
            total_required += 10.8

        # Calculate usable area (75% of buildable)
        usable_area = buildable['area'] * 0.75

        # Check if it fits
        will_fit = total_required <= usable_area

        return {
            "land": {
                "length": land_input.length,
                "width": land_input.width,
                "total_area": land_input.length * land_input.width,
            },
            "setbacks": {
                "front": buildable['setbacks']['front'],
                "rear": buildable['setbacks']['back'],
                "left": buildable['setbacks']['left'],
                "right": buildable['setbacks']['right'],
            },
            "buildable_area": {
                "length": buildable['length'],
                "width": buildable['width'],
                "total_sqm": buildable['area'],
                "usable_sqm": round(usable_area, 2),
                "offset_x": buildable['offset_x'],
                "offset_y": buildable['offset_y'],
            },
            "room_requirements": {
                "requested": {
                    "bedrooms": land_input.bedrooms,
                    "toilets": land_input.toilets,
                    "kitchen": land_input.kitchen,
                    "living_room": land_input.living_room,
                    "dining_room": land_input.dining_room,
                },
                "optimized": {
                    "bedrooms": optimized_land_input.bedrooms,
                    "toilets": optimized_land_input.toilets,
                    "kitchen": optimized_land_input.kitchen,
                    "living_room": optimized_land_input.living_room,
                    "dining_room": optimized_land_input.dining_room,
                },
                "total_required_sqm": round(total_required, 2),
            },
            "feasibility": {
                "will_fit": will_fit,
                "space_remaining": round(usable_area - total_required, 2) if will_fit else round(total_required - usable_area, 2),
                "status": "OK - Rooms will fit" if will_fit else "WARNING - Not enough space",
                "messages": messages,
            }
        }

    except Exception as e:
        import traceback
        logger.error(f"Buildable area calculation error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/validate",
    response_model=ValidationResponseSchema,
    summary="Validate land input parameters",
    description="Validates land dimensions and requirements before optimization"
)
async def validate_land_input(
    land_input: LandInputSchema
) -> ValidationResponseSchema:
    """
    Validate land input parameters.

    Checks:
    - Dimension constraints
    - Feasibility of requirements
    - Building regulation compliance
    - Provides warnings and suggestions
    """
    try:
        validation_result = validation_service.validate_input(land_input)

        return ValidationResponseSchema(
            valid=validation_result['valid'],
            errors=validation_result['errors'],
            warnings=validation_result['warnings'],
            feasibility=validation_result.get('feasibility', {}),
        )

    except Exception as e:
        import traceback
        logger.error(f"Validation error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/optimize",
    response_model=OptimizationResponseSchema,
    summary="Optimize house layout",
    description="Runs genetic algorithm to generate optimal house layout"
)
async def optimize_layout(
    request: OptimizationRequestSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    save_to_db: bool = Query(True, description="Save optimization result to database"),
) -> OptimizationResponseSchema:
    """
    Optimize house layout using genetic algorithm.

    Process:
    1. Validates input parameters
    2. Runs GA optimization
    3. Generates floor plan visualization
    4. Saves results to database (optional)

    Returns optimized layout with scores and visualization.
    """
    try:
        import time
        start_time = time.time()

        land_input = request.land_input

        # Validate input first
        logger.info(f"Validating input for optimization: {land_input.length}x{land_input.width}m")
        validation_result = validation_service.validate_before_optimization(land_input)

        if not validation_result['valid']:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Input validation failed",
                    "errors": validation_result['errors'],
                    "warnings": validation_result['warnings']
                }
            )

        # Create optimizer with custom parameters if provided
        logger.info("Creating genetic optimizer...")
        optimizer = GeneticOptimizer(
            land_input=land_input,
            generations=request.generations,
            population_size=request.population_size,
            mutation_rate=request.mutation_rate,
            crossover_rate=request.crossover_rate,
        )

        # Run optimization
        logger.info("Running optimization...")
        layout_output = optimizer.optimize()

        # Generate TWO visualizations
        logger.info("Generating visualizations...")

        # OUTPUT 1: Land plot with buildable area
        logger.info("Generating land plot with buildable area...")
        land_plot_path = visualization_service.generate_land_plot(
            land_input=land_input,
        )
        land_plot_filename = FilePath(land_plot_path).name

        # OUTPUT 2: Floor plan within buildable area
        logger.info("Generating floor plan within buildable area...")
        floor_plan_path = visualization_service.generate_floor_plan(
            land_input=land_input,
            layout=layout_output,
            show_dimensions=True,
            show_labels=True,
            show_setbacks=True,
        )
        floor_plan_filename = FilePath(floor_plan_path).name

        # Save to database if requested
        optimization_id = None
        if save_to_db:
            logger.info("Saving optimization result to database...")
            db_record = optimization_crud.create_optimization_record(
                db=db,
                land_input=land_input,
                layout_output=layout_output,
                project_id=request.project_id,
            )
            optimization_id = db_record.id

        # Calculate execution time
        execution_time = time.time() - start_time

        # Create response with TWO visualization URLs
        response = OptimizationResponseSchema(
            success=True,
            message="Optimization completed successfully - 2 outputs generated",
            layout=layout_output,
            land_plot_url=f"/api/v1/optimization/visualization/{land_plot_filename}",
            floor_plan_url=f"/api/v1/optimization/visualization/{floor_plan_filename}",
            visualization_url=f"/api/v1/optimization/visualization/{floor_plan_filename}",  # Deprecated, kept for backward compatibility
            execution_time_seconds=execution_time,
            optimization_id=optimization_id,
            warnings=layout_output.optimization_messages if layout_output.optimization_messages else None,
        )

        logger.info(
            f"Optimization complete: Fitness={layout_output.fitness_score:.2f}, "
            f"ID={optimization_id}"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Optimization error: {e}\n{tb}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/visualization/{filename}",
    response_class=FileResponse,
    summary="Get visualization image",
    description="Retrieve generated floor plan image"
)
async def get_visualization(
    filename: str = Path(..., description="Visualization filename")
) -> FileResponse:
    """
    Get floor plan visualization image.

    Returns PNG image file.
    """
    try:
        file_path = visualization_service.output_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Visualization not found")

        return FileResponse(
            path=str(file_path),
            media_type="image/png",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving visualization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/history",
    summary="Get optimization history",
    description="Retrieve past optimization results"
)
async def get_optimization_history(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
) -> List[dict]:
    """
    Get recent optimization history.

    Returns list of past optimizations with scores and parameters.
    """
    try:
        optimizations = optimization_crud.get_recent_optimizations(
            db=db,
            limit=limit,
            project_id=project_id
        )

        return [
            {
                "id": opt.id,
                "land_dimensions": f"{opt.land_length}x{opt.land_width}",
                "land_area": opt.total_area,
                "bedrooms": opt.bedrooms,
                "toilets": opt.toilets,
                "fitness_score": opt.fitness_score,
                "efficiency_score": opt.efficiency_score,
                "created_at": opt.created_at.isoformat(),
                "project_id": opt.project_id,
            }
            for opt in optimizations
        ]

    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/history/{optimization_id}",
    summary="Get optimization by ID",
    description="Retrieve specific optimization result"
)
async def get_optimization_detail(
    optimization_id: int = Path(..., description="Optimization ID"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get detailed optimization result by ID.

    Returns complete layout data, scores, and parameters.
    """
    try:
        optimization = optimization_crud.get_optimization_by_id(db, optimization_id)

        if not optimization:
            raise HTTPException(status_code=404, detail="Optimization not found")

        return {
            "id": optimization.id,
            "land_input": {
                "length": optimization.land_length,
                "width": optimization.land_width,
                "area": optimization.total_area,
                "bedrooms": optimization.bedrooms,
                "toilets": optimization.toilets,
                "living_room": optimization.living_room,
                "dining_room": optimization.dining_room,
                "garden_area": optimization.garden_area,
                "front_direction": optimization.front_direction,
                "road_side": optimization.road_side,
            },
            "layout_data": optimization.layout_data,
            "scores": {
                "fitness": optimization.fitness_score,
                "efficiency": optimization.efficiency_score,
                "sunlight": optimization.sunlight_score,
                "privacy": optimization.privacy_score,
                "regulation_compliance": optimization.regulation_compliance,
            },
            "metadata": {
                "generations": optimization.generations,
                "execution_time": optimization.execution_time,
                "created_at": optimization.created_at.isoformat(),
            },
            "project_id": optimization.project_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching optimization detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/best",
    summary="Get best optimizations",
    description="Retrieve top-rated optimization results"
)
async def get_best_optimizations(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of records"),
    min_fitness: float = Query(70.0, ge=0, le=100, description="Minimum fitness score"),
) -> List[dict]:
    """
    Get best optimization results.

    Returns optimizations sorted by fitness score.
    """
    try:
        optimizations = optimization_crud.get_best_optimizations(
            db=db,
            limit=limit,
            min_fitness=min_fitness
        )

        return [
            {
                "id": opt.id,
                "land_dimensions": f"{opt.land_length}x{opt.land_width}",
                "bedrooms": opt.bedrooms,
                "fitness_score": opt.fitness_score,
                "efficiency_score": opt.efficiency_score,
                "created_at": opt.created_at.isoformat(),
            }
            for opt in optimizations
        ]

    except Exception as e:
        logger.error(f"Error fetching best optimizations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/history/{optimization_id}",
    summary="Delete optimization",
    description="Delete optimization result from database"
)
async def delete_optimization(
    optimization_id: int = Path(..., description="Optimization ID"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Delete an optimization record.

    Returns success status.
    """
    try:
        deleted = optimization_crud.delete_optimization(db, optimization_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Optimization not found")

        return {"success": True, "message": f"Optimization {optimization_id} deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/search",
    summary="Search optimizations",
    description="Search optimization results with filters"
)
async def search_optimizations(
    db: Session = Depends(get_db),
    bedrooms: Optional[int] = Query(None, ge=0, le=10, description="Number of bedrooms"),
    min_area: Optional[float] = Query(None, ge=0, description="Minimum land area"),
    max_area: Optional[float] = Query(None, ge=0, description="Maximum land area"),
    min_fitness: Optional[float] = Query(None, ge=0, le=100, description="Minimum fitness score"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
) -> List[dict]:
    """
    Search optimizations with filters.

    Supports filtering by bedrooms, land area, and fitness score.
    """
    try:
        optimizations = optimization_crud.search_optimizations(
            db=db,
            bedrooms=bedrooms,
            min_area=min_area,
            max_area=max_area,
            min_fitness=min_fitness,
            limit=limit
        )

        return [
            {
                "id": opt.id,
                "land_dimensions": f"{opt.land_length}x{opt.land_width}",
                "land_area": opt.total_area,
                "bedrooms": opt.bedrooms,
                "fitness_score": opt.fitness_score,
                "created_at": opt.created_at.isoformat(),
            }
            for opt in optimizations
        ]

    except Exception as e:
        logger.error(f"Error searching optimizations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
