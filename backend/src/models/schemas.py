"""
Pydantic models for API request/response validation
These schemas define the structure of data exchanged via the API
"""

from pydantic import BaseModel, Field, field_validator, computed_field
from typing import List, Optional, Literal
from enum import Enum
from datetime import datetime


# Enums for validation
class DirectionEnum(str, Enum):
    """Cardinal and intercardinal directions"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    NORTHEAST = "northeast"
    NORTHWEST = "northwest"
    SOUTHEAST = "southeast"
    SOUTHWEST = "southwest"


class LandShapeEnum(str, Enum):
    """Possible land shapes"""
    RECTANGULAR = "rectangular"
    SQUARE = "square"
    IRREGULAR = "irregular"


# Input Schemas
class LandInputSchema(BaseModel):
    """
    User input schema for land optimization request
    Validates all user-provided land details and requirements
    """

    # Land Dimensions
    length: float = Field(
        ...,
        gt=0,
        le=1000,
        description="Land length in meters",
        examples=[15.0]
    )
    width: float = Field(
        ...,
        gt=0,
        le=1000,
        description="Land width in meters",
        examples=[10.0]
    )
    total_area: Optional[float] = Field(
        None,
        description="Total area in square meters (auto-calculated if not provided)"
    )
    shape: LandShapeEnum = Field(
        default=LandShapeEnum.RECTANGULAR,
        description="Shape of the land plot"
    )

    # Room Requirements
    bedrooms: int = Field(
        ...,
        ge=0,
        le=10,
        description="Number of bedrooms required",
        examples=[3]
    )
    toilets: int = Field(
        ...,
        ge=1,
        le=5,
        description="Number of toilets/bathrooms required",
        examples=[2]
    )
    kitchen: int = Field(
        default=1,
        ge=0,
        le=2,
        description="Number of kitchens (0, 1, or 2)"
    )
    living_room: int = Field(
        default=1,
        ge=0,
        le=1,
        description="Living room required (0 or 1)"
    )
    dining_room: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Dining room required (0 or 1)"
    )
    garden_area: float = Field(
        default=0.0,
        ge=0,
        le=1000,
        description="Required garden area in square meters"
    )

    # Direction and Orientation
    front_direction: DirectionEnum = Field(
        ...,
        description="Direction the front of the land faces",
        examples=["north"]
    )
    road_side: DirectionEnum = Field(
        ...,
        description="Which side of the land has road access",
        examples=["north"]
    )

    # Optional Preferences
    parking_spaces: int = Field(
        default=0,
        ge=0,
        le=5,
        description="Number of parking spaces required"
    )
    balcony: bool = Field(
        default=False,
        description="Whether to include a balcony"
    )

    @field_validator('total_area', mode='before')
    @classmethod
    def calculate_total_area(cls, v, info):
        """Auto-calculate total area if not provided"""
        if v is None:
            data = info.data
            if 'length' in data and 'width' in data:
                return data['length'] * data['width']
        return v

    @field_validator('width')
    @classmethod
    def validate_width(cls, v, info):
        """Ensure width is reasonable"""
        data = info.data
        if 'length' in data and data['length'] is not None and v is not None:
            # Aspect ratio should not be too extreme
            aspect_ratio = max(data['length'], v) / min(data['length'], v)
            if aspect_ratio > 10:
                raise ValueError(
                    f"Land aspect ratio too extreme ({aspect_ratio:.1f}:1). "
                    "Maximum allowed is 10:1"
                )
        return v

    model_config = {
        "populate_by_name": True,  # Allow both field name and alias
        "json_schema_extra": {
            "examples": [
                {
                    "length": 15.0,
                    "width": 10.0,
                    "bedrooms": 3,
                    "toilets": 2,
                    "kitchen": 1,
                    "living_room": 1,
                    "dining_room": 1,
                    "garden_area": 20.0,
                    "front_direction": "north",
                    "road_side": "north",
                    "parking_spaces": 1,
                    "balcony": False
                }
            ]
        }
    }


# Output Schemas
class RoomSchema(BaseModel):
    """
    Individual room in the optimized layout
    Contains position, dimensions, and area information
    """

    type: str = Field(
        ...,
        description="Room type (bedroom, toilet, kitchen, living, dining, etc.)"
    )
    x: float = Field(
        ...,
        ge=0,
        description="X position in meters from left edge"
    )
    y: float = Field(
        ...,
        ge=0,
        description="Y position in meters from bottom edge"
    )
    width: float = Field(
        ...,
        gt=0,
        description="Room width in meters"
    )
    height: float = Field(
        ...,
        gt=0,
        description="Room height/length in meters"
    )
    area: float = Field(
        ...,
        gt=0,
        description="Room area in square meters"
    )

    @computed_field
    @property
    def center_x(self) -> float:
        """Calculate room center X coordinate"""
        return self.x + self.width / 2

    @computed_field
    @property
    def center_y(self) -> float:
        """Calculate room center Y coordinate"""
        return self.y + self.height / 2

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "bedroom",
                    "x": 1.5,
                    "y": 3.0,
                    "width": 3.5,
                    "height": 4.0,
                    "area": 14.0
                }
            ]
        }
    }


class LayoutOutputSchema(BaseModel):
    """
    Complete optimized layout output
    Contains all rooms and optimization scores
    """

    rooms: List[RoomSchema] = Field(
        ...,
        description="List of all rooms in the optimized layout"
    )

    # Optimization Scores
    fitness_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall fitness score (0-100, higher is better)"
    )
    efficiency_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Space utilization efficiency percentage"
    )
    sunlight_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Sunlight optimization score"
    )
    privacy_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Privacy optimization score"
    )
    circulation_score: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Circulation/movement efficiency score"
    )
    regulation_compliance: float = Field(
        ...,
        ge=0,
        le=100,
        description="Building regulation compliance score"
    )

    # Area Metrics
    total_built_area: float = Field(
        ...,
        ge=0,
        description="Total built area in square meters"
    )
    coverage_percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of land covered by buildings"
    )

    # Metadata
    generation_time_seconds: Optional[float] = Field(
        None,
        description="Time taken to generate this layout"
    )
    optimization_messages: Optional[List[str]] = Field(
        default_factory=list,
        description="Messages about room optimization (e.g., room count adjustments)"
    )

    # Architectural Elements (walls, doors, fixtures, corridors)
    architectural_elements: Optional[dict] = Field(
        None,
        description="Dictionary containing walls, doors, fixtures, and corridors for architectural visualization"
    )

    @computed_field
    @property
    def total_rooms(self) -> int:
        """Total number of rooms"""
        return len(self.rooms)

    @computed_field
    @property
    def room_breakdown(self) -> dict:
        """Breakdown of rooms by type"""
        breakdown = {}
        for room in self.rooms:
            breakdown[room.type] = breakdown.get(room.type, 0) + 1
        return breakdown

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "rooms": [
                        {
                            "type": "bedroom",
                            "x": 1.5,
                            "y": 3.0,
                            "width": 3.5,
                            "height": 4.0,
                            "area": 14.0
                        }
                    ],
                    "fitness_score": 87.5,
                    "efficiency_score": 75.3,
                    "sunlight_score": 85.0,
                    "privacy_score": 90.0,
                    "circulation_score": 80.0,
                    "regulation_compliance": 100.0,
                    "total_built_area": 80.0,
                    "coverage_percentage": 53.3,
                    "generation_time_seconds": 12.5
                }
            ]
        }
    }


# Request/Response Schemas
class OptimizationRequestSchema(BaseModel):
    """
    Complete optimization request
    Contains land input and optional GA parameters
    """

    land_input: LandInputSchema = Field(
        ...,
        description="Land details and requirements"
    )

    # Genetic Algorithm Parameters (optional overrides)
    generations: Optional[int] = Field(
        default=None,
        ge=10,
        le=500,
        description="Number of GA generations (uses config default if not specified)"
    )
    population_size: Optional[int] = Field(
        default=None,
        ge=10,
        le=200,
        description="GA population size (uses config default if not specified)"
    )
    mutation_rate: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="GA mutation rate (0.0-1.0, uses config default if not specified)"
    )
    crossover_rate: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="GA crossover rate (0.0-1.0, uses config default if not specified)"
    )

    # Optional project tracking
    project_id: Optional[int] = Field(
        default=None,
        description="Optional project ID to associate this optimization with a project"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "land_input": {
                        "length": 15.0,
                        "width": 10.0,
                        "bedrooms": 3,
                        "toilets": 2,
                        "kitchen": 1,
                        "living_room": 1,
                        "dining_room": 1,
                        "garden_area": 20.0,
                        "front_direction": "north",
                        "road_side": "north"
                    },
                    "generations": 100,
                    "population_size": 50,
                    "mutation_rate": 0.1,
                    "crossover_rate": 0.8
                }
            ]
        }
    }


class OptimizationResponseSchema(BaseModel):
    """
    API response for optimization request
    Contains status, layout, and metadata
    """

    success: bool = Field(
        ...,
        description="Whether optimization succeeded"
    )
    message: str = Field(
        ...,
        description="Status message or error description"
    )
    layout: Optional[LayoutOutputSchema] = Field(
        None,
        description="Optimized layout (null if failed)"
    )
    land_plot_url: Optional[str] = Field(
        None,
        description="URL to download land plot visualization (OUTPUT 1)"
    )
    floor_plan_url: Optional[str] = Field(
        None,
        description="URL to download floor plan visualization (OUTPUT 2)"
    )
    # Deprecated - use land_plot_url and floor_plan_url instead
    visualization_url: Optional[str] = Field(
        None,
        description="[DEPRECATED] URL to download floor plan visualization - use floor_plan_url instead"
    )
    execution_time_seconds: float = Field(
        ...,
        ge=0,
        description="Total execution time in seconds"
    )
    optimization_id: Optional[int] = Field(
        None,
        description="Database ID of saved optimization record (if save_to_db was true)"
    )

    # Optional error details
    errors: Optional[List[str]] = Field(
        None,
        description="List of errors if optimization failed"
    )
    warnings: Optional[List[str]] = Field(
        None,
        description="List of warnings (non-fatal issues)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Optimization completed successfully",
                    "layout": {
                        "rooms": [],
                        "fitness_score": 87.5,
                        "efficiency_score": 75.3,
                        "sunlight_score": 85.0,
                        "privacy_score": 90.0,
                        "regulation_compliance": 100.0,
                        "total_built_area": 80.0,
                        "coverage_percentage": 53.3
                    },
                    "visualization_url": "/api/v1/optimization/visualization/floor_plan_20240101_120000.png",
                    "execution_time_seconds": 12.5,
                    "optimization_id": 123,
                    "errors": None,
                    "warnings": None
                }
            ]
        }
    }


class ValidationResponseSchema(BaseModel):
    """Response for input validation endpoint"""

    valid: bool = Field(
        ...,
        description="Whether input is valid"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="List of validation errors"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of warnings"
    )
    feasibility: Optional[dict] = Field(
        None,
        description="Feasibility analysis details"
    )


class HealthCheckSchema(BaseModel):
    """Health check response"""

    status: Literal["healthy", "unhealthy"] = Field(
        ...,
        description="Service health status"
    )
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Current server time"
    )
