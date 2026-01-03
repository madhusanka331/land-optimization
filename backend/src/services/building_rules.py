"""
Sri Lankan Building Rules and Regulations
Based on Urban Development Authority (UDA) standards for residential buildings

This module implements:
- Setback requirements
- Coverage limits
- Minimum room sizes
- Building height restrictions
- Other UDA residential building regulations
"""

from typing import List, Dict, Tuple, Optional
from src.models.schemas import LandInputSchema, RoomSchema
from src.config.settings import settings


class SriLankanBuildingRules:
    """
    Sri Lankan Urban Development Authority (UDA) Building Regulations

    References:
    - UDA Building Regulations (Residential)
    - National Building Research Organization (NBRO) Guidelines
    - Local Authority Building By-laws
    """

    # ==================== MINIMUM ROOM SIZES ====================
    # All measurements in square meters (sqm)

    MIN_BEDROOM_AREA = 9.3      # ~100 sq ft - Single bedroom minimum
    MIN_MASTER_BEDROOM = 11.1   # ~120 sq ft - Master bedroom recommended
    MIN_TOILET_AREA = 2.8       # ~30 sq ft - Standard toilet/bathroom
    MIN_BATHROOM_AREA = 3.7     # ~40 sq ft - Full bathroom with shower
    MIN_KITCHEN_AREA = 5.6      # ~60 sq ft - Minimum kitchen
    MIN_LIVING_AREA = 11.1      # ~120 sq ft - Living room
    MIN_DINING_AREA = 9.3       # ~100 sq ft - Dining room
    MIN_PANTRY_AREA = 2.8       # ~30 sq ft - Pantry/utility room

    # ==================== SETBACK REQUIREMENTS ====================
    # Distance from plot boundaries (meters)

    FRONT_SETBACK = 3.0         # Front boundary (road side)
    SIDE_SETBACK = 1.5          # Side boundaries (left/right)
    BACK_SETBACK = 1.5          # Rear boundary

    # Setback variations based on land size
    LARGE_LAND_FRONT_SETBACK = 4.5   # For lands > 500 sqm
    LARGE_LAND_SIDE_SETBACK = 2.0    # For lands > 500 sqm

    # ==================== COVERAGE LIMITS ====================

    MAX_COVERAGE_PERCENT = 65.0     # Maximum 65% of land can be covered
    MIN_OPEN_SPACE_PERCENT = 35.0   # Minimum 35% must remain open
    RECOMMENDED_COVERAGE = 50.0     # Recommended for better ventilation

    # ==================== DIMENSION RESTRICTIONS ====================

    MIN_ROOM_WIDTH = 2.4        # Minimum width for any habitable room
    MIN_ROOM_LENGTH = 2.7       # Minimum length for bedroom
    MIN_CEILING_HEIGHT = 2.7    # Minimum ceiling height (meters)
    MIN_CORRIDOR_WIDTH = 0.9    # Minimum passage width
    MIN_DOOR_WIDTH = 0.75       # Minimum door width
    MIN_WINDOW_AREA_RATIO = 0.1 # Windows should be 10% of floor area

    # ==================== HEIGHT RESTRICTIONS ====================

    MAX_BUILDING_HEIGHT = 15.0      # Maximum height (meters) for residential
    MAX_FLOORS_RESIDENTIAL = 4      # Maximum number of floors
    FLOOR_TO_FLOOR_HEIGHT = 3.0     # Typical floor-to-floor height

    # ==================== PARKING REQUIREMENTS ====================

    PARKING_SPACE_LENGTH = 5.0      # Meters
    PARKING_SPACE_WIDTH = 2.5       # Meters
    MIN_PARKING_AREA = 12.5         # 5m x 2.5m

    # ==================== VENTILATION & LIGHT ====================

    MIN_VENTILATION_PERCENTAGE = 5.0    # 5% of floor area
    MIN_NATURAL_LIGHT_PERCENTAGE = 10.0  # 10% of floor area

    @classmethod
    def get_setback_requirements(cls, land_area: float) -> Dict[str, float]:
        """
        Get applicable setback requirements based on land size

        Args:
            land_area: Total land area in square meters

        Returns:
            Dictionary with setback distances for each side
        """
        # Use larger setbacks for larger lands
        if land_area is not None and land_area > 500:
            return {
                'front': cls.LARGE_LAND_FRONT_SETBACK,
                'back': cls.BACK_SETBACK,
                'left': cls.LARGE_LAND_SIDE_SETBACK,
                'right': cls.LARGE_LAND_SIDE_SETBACK
            }
        else:
            return {
                'front': cls.FRONT_SETBACK,
                'back': cls.BACK_SETBACK,
                'left': cls.SIDE_SETBACK,
                'right': cls.SIDE_SETBACK
            }

    @classmethod
    def get_buildable_area(cls, land_length: float, land_width: float,
                          land_area: float) -> Dict[str, float]:
        """
        Calculate buildable area after applying setbacks

        Args:
            land_length: Length of land plot (meters)
            land_width: Width of land plot (meters)
            land_area: Total land area (sqm)

        Returns:
            Dictionary with buildable dimensions and offsets
        """
        setbacks = cls.get_setback_requirements(land_area)

        # Calculate buildable dimensions
        buildable_length = land_length - setbacks['front'] - setbacks['back']
        buildable_width = land_width - setbacks['left'] - setbacks['right']
        buildable_area = max(0, buildable_length * buildable_width)

        return {
            'length': max(0, buildable_length),
            'width': max(0, buildable_width),
            'area': buildable_area,
            'offset_x': setbacks['left'],
            'offset_y': setbacks['front'],
            'setbacks': setbacks
        }

    @classmethod
    def calculate_min_required_area(cls, land_input: LandInputSchema) -> Dict[str, float]:
        """
        Calculate minimum total area needed for all requirements

        Args:
            land_input: User's land input with requirements

        Returns:
            Dictionary with area breakdown and total
        """
        breakdown = {
            'bedrooms': 0.0,
            'toilets': 0.0,
            'kitchen': 0.0,
            'living': 0.0,
            'dining': 0.0,
            'circulation': 0.0,
            'total': 0.0
        }

        # Calculate bedroom area
        if land_input.bedrooms > 0:
            # First bedroom (master) larger, others minimum
            breakdown['bedrooms'] = cls.MIN_MASTER_BEDROOM
            if land_input.bedrooms > 1:
                breakdown['bedrooms'] += (land_input.bedrooms - 1) * cls.MIN_BEDROOM_AREA

        # Calculate toilet/bathroom area
        breakdown['toilets'] = land_input.toilets * cls.MIN_TOILET_AREA

        # Kitchen
        if land_input.kitchen > 0:
            breakdown['kitchen'] = cls.MIN_KITCHEN_AREA * land_input.kitchen

        # Living room
        if land_input.living_room > 0:
            breakdown['living'] = cls.MIN_LIVING_AREA

        # Dining room
        if land_input.dining_room > 0:
            breakdown['dining'] = cls.MIN_DINING_AREA

        # Circulation space (corridors, staircases, etc.)
        # Typically 15-20% of usable area
        usable_area = sum(breakdown.values())
        breakdown['circulation'] = usable_area * 0.18

        # Total required
        breakdown['total'] = sum(breakdown.values())

        return breakdown

    @classmethod
    def validate_feasibility(cls, land_input: LandInputSchema) -> Dict:
        """
        Check if requirements can physically fit in the land

        Args:
            land_input: User's land input

        Returns:
            Dictionary with feasibility status and details
        """
        # Get buildable area after setbacks
        total_area = land_input.total_area or (land_input.length * land_input.width if land_input.length and land_input.width else None)

        # Ensure total_area is not None
        if total_area is None:
            return {
                'is_feasible': False,
                'buildable_area': 0,
                'required_area': 0,
                'max_allowed_built_area': 0,
                'remaining_area': 0,
                'coverage_if_built': 0,
                'area_breakdown': {},
                'setbacks': {},
                'errors': ['Cannot calculate land area - length and width are required'],
                'warnings': []
            }

        buildable = cls.get_buildable_area(
            land_input.length,
            land_input.width,
            total_area
        )

        # Get minimum required area
        required = cls.calculate_min_required_area(land_input)

        # Maximum allowed built area (coverage limit)
        max_allowed_built_area = total_area * (cls.MAX_COVERAGE_PERCENT / 100)

        # Check feasibility conditions
        has_buildable_space = buildable['area'] > 0
        fits_in_buildable = required['total'] <= buildable['area']
        within_coverage = required['total'] <= max_allowed_built_area

        is_feasible = has_buildable_space and fits_in_buildable and within_coverage

        # Generate detailed response
        errors = []
        warnings = []

        if not has_buildable_space:
            errors.append(
                f"Land too small. After setbacks ({buildable['setbacks']}), "
                f"no buildable area remains."
            )

        if not fits_in_buildable and has_buildable_space:
            shortage = required['total'] - buildable['area']
            errors.append(
                f"Insufficient buildable area. Need {required['total']:.1f}m² "
                f"but only {buildable['area']:.1f}m² available after setbacks. "
                f"Shortage: {shortage:.1f}m²"
            )

        if not within_coverage:
            errors.append(
                f"Required area {required['total']:.1f}m² exceeds maximum "
                f"allowed coverage of {max_allowed_built_area:.1f}m² ({cls.MAX_COVERAGE_PERCENT}%)"
            )

        # Warnings (not blocking but important)
        if is_feasible:
            coverage_if_built = (required['total'] / total_area) * 100

            if coverage_if_built < 30:
                warnings.append(
                    f"Low coverage ({coverage_if_built:.1f}%) - space may be underutilized"
                )
            elif coverage_if_built > 60:
                warnings.append(
                    f"High coverage ({coverage_if_built:.1f}%) - limited open space"
                )

            # Check room count vs land size
            total_rooms = (land_input.bedrooms + land_input.toilets +
                          land_input.kitchen + land_input.living_room +
                          land_input.dining_room)
            rooms_per_100sqm = (total_rooms / total_area) * 100

            if rooms_per_100sqm > 5:
                warnings.append(
                    f"Many rooms ({total_rooms}) for land size - may feel cramped"
                )

        return {
            'is_feasible': is_feasible,
            'buildable_area': buildable['area'],
            'required_area': required['total'],
            'max_allowed_built_area': max_allowed_built_area,
            'remaining_area': max(0, buildable['area'] - required['total']),
            'coverage_if_built': (required['total'] / total_area) * 100 if total_area > 0 else 0,
            'area_breakdown': required,
            'setbacks': buildable['setbacks'],
            'errors': errors,
            'warnings': warnings
        }

    @classmethod
    def validate_room(cls, room: RoomSchema) -> Tuple[bool, List[str]]:
        """
        Validate individual room against regulations

        Args:
            room: Room to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Map room types to minimum areas
        min_area_map = {
            'bedroom': cls.MIN_BEDROOM_AREA,
            'master_bedroom': cls.MIN_MASTER_BEDROOM,
            'toilet': cls.MIN_TOILET_AREA,
            'bathroom': cls.MIN_BATHROOM_AREA,
            'kitchen': cls.MIN_KITCHEN_AREA,
            'living': cls.MIN_LIVING_AREA,
            'dining': cls.MIN_DINING_AREA,
            'pantry': cls.MIN_PANTRY_AREA
        }

        # Check minimum area
        if room.type in min_area_map:
            min_area = min_area_map[room.type]
            if room.area < min_area:
                errors.append(
                    f"{room.type.capitalize()} area {room.area:.2f}m² is below "
                    f"minimum required {min_area:.2f}m²"
                )

        # Check minimum width for habitable rooms
        if room.type in ['bedroom', 'master_bedroom', 'living', 'dining']:
            if room.width < cls.MIN_ROOM_WIDTH:
                errors.append(
                    f"{room.type.capitalize()} width {room.width:.2f}m is below "
                    f"minimum {cls.MIN_ROOM_WIDTH}m"
                )
            if room.height < cls.MIN_ROOM_LENGTH:
                errors.append(
                    f"{room.type.capitalize()} length {room.height:.2f}m is below "
                    f"minimum {cls.MIN_ROOM_LENGTH}m"
                )

        return len(errors) == 0, errors

    @classmethod
    def validate_layout(cls, land_input: LandInputSchema,
                       rooms: List[RoomSchema]) -> Dict:
        """
        Validate complete layout against all regulations

        Args:
            land_input: Original land input
            rooms: List of all rooms in layout

        Returns:
            Dictionary with validation results
        """
        all_errors = []
        warnings = []

        # 1. Validate each room individually
        for i, room in enumerate(rooms):
            is_valid, errors = cls.validate_room(room)
            if not is_valid:
                all_errors.extend([f"Room {i+1} ({room.type}): {err}" for err in errors])

        # 2. Check total coverage
        # Calculate total_area if not provided
        total_area = land_input.total_area or (land_input.length * land_input.width if land_input.length and land_input.width else None)

        if total_area is None or total_area == 0:
            all_errors.append("Cannot validate layout - land area is not defined")
            return {
                'is_valid': False,
                'errors': all_errors,
                'warnings': warnings
            }

        total_built_area = sum(room.area for room in rooms)
        coverage_percent = (total_built_area / total_area) * 100

        if coverage_percent > cls.MAX_COVERAGE_PERCENT:
            all_errors.append(
                f"Total coverage {coverage_percent:.1f}% exceeds maximum "
                f"{cls.MAX_COVERAGE_PERCENT}%"
            )
        elif coverage_percent > cls.RECOMMENDED_COVERAGE:
            warnings.append(
                f"Coverage {coverage_percent:.1f}% exceeds recommended "
                f"{cls.RECOMMENDED_COVERAGE}% - may limit outdoor space"
            )

        # 3. Check setback compliance
        buildable = cls.get_buildable_area(
            land_input.length,
            land_input.width,
            land_input.total_area
        )

        for i, room in enumerate(rooms):
            # Left boundary
            if room.x < buildable['offset_x']:
                all_errors.append(
                    f"Room {i+1} ({room.type}) violates left setback "
                    f"(x={room.x:.2f}m, required={buildable['offset_x']:.2f}m)"
                )

            # Front boundary
            if room.y < buildable['offset_y']:
                all_errors.append(
                    f"Room {i+1} ({room.type}) violates front setback "
                    f"(y={room.y:.2f}m, required={buildable['offset_y']:.2f}m)"
                )

            # Right boundary
            right_edge = room.x + room.width
            max_right = land_input.width - buildable['setbacks']['right']
            if right_edge > max_right:
                all_errors.append(
                    f"Room {i+1} ({room.type}) violates right setback "
                    f"(extends to {right_edge:.2f}m, max allowed={max_right:.2f}m)"
                )

            # Back boundary
            back_edge = room.y + room.height
            max_back = land_input.length - buildable['setbacks']['back']
            if back_edge > max_back:
                all_errors.append(
                    f"Room {i+1} ({room.type}) violates back setback "
                    f"(extends to {back_edge:.2f}m, max allowed={max_back:.2f}m)"
                )

        # 4. Check room count requirements
        room_counts = {}
        for room in rooms:
            room_counts[room.type] = room_counts.get(room.type, 0) + 1

        # Bedrooms
        expected_bedrooms = land_input.bedrooms
        actual_bedrooms = room_counts.get('bedroom', 0) + room_counts.get('master_bedroom', 0)
        if actual_bedrooms != expected_bedrooms:
            all_errors.append(
                f"Bedroom count mismatch: required {expected_bedrooms}, "
                f"got {actual_bedrooms}"
            )

        # Toilets
        if room_counts.get('toilet', 0) + room_counts.get('bathroom', 0) != land_input.toilets:
            all_errors.append(
                f"Toilet count mismatch: required {land_input.toilets}, "
                f"got {room_counts.get('toilet', 0)}"
            )

        # 5. Check for room overlaps
        overlaps = cls._check_overlaps(rooms)
        if overlaps:
            all_errors.extend(overlaps)

        # 6. Coverage warnings
        if coverage_percent < 30:
            warnings.append(
                f"Low coverage {coverage_percent:.1f}% - consider adding more rooms"
            )

        return {
            'valid': len(all_errors) == 0,
            'errors': all_errors,
            'warnings': warnings,
            'coverage_percent': coverage_percent,
            'total_built_area': total_built_area,
            'buildable_area': buildable['area'],
            'room_counts': room_counts
        }

    @classmethod
    def _check_overlaps(cls, rooms: List[RoomSchema]) -> List[str]:
        """Check if any rooms overlap"""
        overlaps = []

        for i in range(len(rooms)):
            for j in range(i + 1, len(rooms)):
                if cls._rooms_overlap(rooms[i], rooms[j]):
                    overlaps.append(
                        f"Room {i+1} ({rooms[i].type}) overlaps with "
                        f"Room {j+1} ({rooms[j].type})"
                    )

        return overlaps

    @staticmethod
    def _rooms_overlap(room1: RoomSchema, room2: RoomSchema,
                       tolerance: float = 0.01) -> bool:
        """
        Check if two rooms overlap

        Args:
            room1: First room
            room2: Second room
            tolerance: Small tolerance for floating point errors (meters)

        Returns:
            True if rooms overlap
        """
        # Rooms don't overlap if one is completely to the left/right/above/below the other
        return not (
            room1.x + room1.width - tolerance <= room2.x or
            room2.x + room2.width - tolerance <= room1.x or
            room1.y + room1.height - tolerance <= room2.y or
            room2.y + room2.height - tolerance <= room1.y
        )

    @classmethod
    def get_min_land_size(cls, bedrooms: int, toilets: int) -> float:
        """
        Estimate minimum land size needed for basic requirements

        Args:
            bedrooms: Number of bedrooms
            toilets: Number of toilets

        Returns:
            Minimum land area in square meters
        """
        # Basic built area
        built_area = (bedrooms * cls.MIN_BEDROOM_AREA +
                     toilets * cls.MIN_TOILET_AREA +
                     cls.MIN_KITCHEN_AREA +
                     cls.MIN_LIVING_AREA)

        # Add circulation (20%)
        built_area *= 1.2

        # Account for coverage limit (can only use 65% of land)
        min_land = built_area / (cls.MAX_COVERAGE_PERCENT / 100)

        return min_land
