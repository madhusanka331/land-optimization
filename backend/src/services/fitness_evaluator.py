"""
Fitness Evaluator - Core AI Logic for Genetic Algorithm
Evaluates house layouts based on multi-objective optimization criteria.

Multi-objective fitness function with weights:
- Space Efficiency: 25%
- Sunlight Optimization: 20%
- Privacy: 15%
- Circulation Efficiency: 15%
- Building Regulation Compliance: 25%
"""

import math
from typing import List, Dict, Tuple, Any
from loguru import logger

from ..models.schemas import LandInputSchema, RoomSchema, DirectionEnum
from .building_rules import SriLankanBuildingRules


class FitnessEvaluator:
    """
    Evaluates fitness of house layouts for genetic algorithm optimization.

    Chromosome Encoding:
    Each room is encoded as: [x_ratio, y_ratio, width_ratio, height_ratio]
    - Ratios are 0-1 values relative to buildable area
    - Total chromosome length = num_rooms * 4
    """

    # Fitness weights (must sum to 1.0)
    WEIGHT_SPACE = 0.20          # Reduced to make room for connectivity
    WEIGHT_SUNLIGHT = 0.15       # Reduced to make room for connectivity
    WEIGHT_PRIVACY = 0.10        # Reduced to make room for connectivity
    WEIGHT_CIRCULATION = 0.15    # Unchanged
    WEIGHT_CONNECTIVITY = 0.20   # NEW: Ensures rooms have access (doors)
    WEIGHT_REGULATIONS = 0.20    # Reduced to make room for connectivity

    # Room type priorities for placement
    ROOM_PRIORITIES = {
        'bedroom': 10,
        'master_bedroom': 12,
        'toilet': 8,
        'kitchen': 9,
        'living': 11,
        'dining': 7,
        'garden': 5,
    }

    def __init__(self, land_input: LandInputSchema):
        """
        Initialize fitness evaluator with land parameters.

        Args:
            land_input: Land dimensions and requirements
        """
        self.land_input = land_input

        # Calculate total_area if not provided
        total_area = land_input.total_area or (land_input.length * land_input.width if land_input.length and land_input.width else None)

        # Calculate buildable area (after setbacks)
        self.buildable = SriLankanBuildingRules.get_buildable_area(
            land_input.length,
            land_input.width,
            total_area
        )

        # Define required rooms based on input
        self.required_rooms = self._define_required_rooms()

        # Calculate expected chromosome length
        self.chromosome_length = len(self.required_rooms) * 4

        logger.info(
            f"Fitness evaluator initialized: "
            f"{len(self.required_rooms)} rooms, "
            f"buildable area: {self.buildable['area']:.2f} sqm"
        )

    def _define_required_rooms(self) -> List[Dict[str, Any]]:
        """
        Define required rooms based on user input.

        Returns:
            List of room definitions with type and minimum area
        """
        rooms = []

        # Bedrooms
        for i in range(self.land_input.bedrooms):
            room_type = 'master_bedroom' if i == 0 else 'bedroom'
            min_area = SriLankanBuildingRules.MIN_BEDROOM_AREA
            rooms.append({
                'type': room_type,
                'min_area': min_area,
                'priority': self.ROOM_PRIORITIES.get(room_type, 5)
            })

        # Toilets
        for i in range(self.land_input.toilets):
            rooms.append({
                'type': 'toilet',
                'min_area': SriLankanBuildingRules.MIN_TOILET_AREA,
                'priority': self.ROOM_PRIORITIES['toilet']
            })

        # Kitchen (always required)
        rooms.append({
            'type': 'kitchen',
            'min_area': SriLankanBuildingRules.MIN_KITCHEN_AREA,
            'priority': self.ROOM_PRIORITIES['kitchen']
        })

        # Living room (optional)
        if self.land_input.living_room > 0:
            rooms.append({
                'type': 'living',
                'min_area': SriLankanBuildingRules.MIN_LIVING_AREA,
                'priority': self.ROOM_PRIORITIES['living']
            })

        # Dining room (optional)
        if self.land_input.dining_room > 0:
            rooms.append({
                'type': 'dining',
                'min_area': SriLankanBuildingRules.MIN_DINING_AREA,
                'priority': self.ROOM_PRIORITIES['dining']
            })

        # Garden (optional)
        if self.land_input.garden_area > 0:
            rooms.append({
                'type': 'garden',
                'min_area': self.land_input.garden_area,
                'priority': self.ROOM_PRIORITIES['garden']
            })

        return rooms

    def decode_chromosome(self, chromosome: List[float]) -> List[RoomSchema]:
        """
        Decode chromosome into actual room positions and sizes.

        Chromosome format: [x1, y1, w1, h1, x2, y2, w2, h2, ...]
        Each value is 0-1 representing ratio of buildable area.

        Args:
            chromosome: Flat list of genes (length = num_rooms * 4)

        Returns:
            List of RoomSchema objects with actual coordinates
        """
        if len(chromosome) != self.chromosome_length:
            logger.warning(
                f"Chromosome length mismatch: expected {self.chromosome_length}, "
                f"got {len(chromosome)}"
            )
            # Pad or truncate
            if len(chromosome) < self.chromosome_length:
                chromosome = list(chromosome) + [0.5] * (self.chromosome_length - len(chromosome))
            else:
                chromosome = chromosome[:self.chromosome_length]

        rooms = []
        buildable_width = self.buildable['width']
        buildable_length = self.buildable['length']
        offset_x = self.buildable['offset_x']
        offset_y = self.buildable['offset_y']

        for i, room_def in enumerate(self.required_rooms):
            # Extract genes for this room
            idx = i * 4
            x_ratio = max(0.0, min(1.0, chromosome[idx]))
            y_ratio = max(0.0, min(1.0, chromosome[idx + 1]))
            w_ratio = max(0.05, min(0.5, chromosome[idx + 2]))  # Min 5%, max 50%
            h_ratio = max(0.05, min(0.5, chromosome[idx + 3]))

            # Calculate actual dimensions
            width = w_ratio * buildable_width
            height = h_ratio * buildable_length

            # Ensure minimum area is met
            min_area = room_def['min_area']
            current_area = width * height
            if current_area < min_area:
                # Scale up to meet minimum area
                scale = math.sqrt(min_area / current_area)
                width *= scale
                height *= scale

            # Calculate position (ensure room fits within buildable area)
            max_x = max(0, buildable_width - width)
            max_y = max(0, buildable_length - height)
            x = offset_x + (x_ratio * max_x)
            y = offset_y + (y_ratio * max_y)

            # Create room schema
            room = RoomSchema(
                type=room_def['type'],
                x=x,
                y=y,
                width=width,
                height=height,
                area=width * height
            )
            rooms.append(room)

        return rooms

    def evaluate_fitness(
        self,
        ga_instance: Any,
        solution: Any,
        solution_idx: int
    ) -> float:
        """
        Main fitness function called by PyGAD.

        Args:
            ga_instance: PyGAD GA instance
            solution: Chromosome (gene values)
            solution_idx: Index in population (unused)

        Returns:
            Fitness score (0-100, higher is better)
        """
        try:
            # Decode chromosome to rooms
            rooms = self.decode_chromosome(solution)

            # Calculate individual objective scores
            space_score = self._evaluate_space_efficiency(rooms)
            sunlight_score = self._evaluate_sunlight(rooms)
            privacy_score = self._evaluate_privacy(rooms)
            circulation_score = self._evaluate_circulation(rooms)
            connectivity_score = self._evaluate_connectivity(rooms)
            regulation_score = self._evaluate_regulations(rooms)

            # Weighted combination
            fitness = (
                self.WEIGHT_SPACE * space_score +
                self.WEIGHT_SUNLIGHT * sunlight_score +
                self.WEIGHT_PRIVACY * privacy_score +
                self.WEIGHT_CIRCULATION * circulation_score +
                self.WEIGHT_CONNECTIVITY * connectivity_score +
                self.WEIGHT_REGULATIONS * regulation_score
            )

            # CRITICAL: Apply overlap penalty to FINAL fitness (not just space score)
            # This ensures overlapping layouts are COMPLETELY REJECTED
            overlap_penalty = self._calculate_overlap_penalty(rooms)
            if overlap_penalty > 0:
                # ANY overlap makes solution completely unfit - ZERO FITNESS
                fitness = 0.0  # Complete rejection - was 0.01 (1%)
                logger.warning(f"OVERLAP DETECTED! Layout REJECTED. Penalty: {overlap_penalty:.1f}, Fitness = 0.0")

            # Ensure fitness is in valid range
            fitness = max(0.0, min(100.0, fitness))

            return fitness

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error(f"Fitness evaluation error: {e}\n{tb}")
            return 0.0  # Invalid solution

    def _evaluate_space_efficiency(self, rooms: List[RoomSchema]) -> float:
        """
        Evaluate how efficiently the layout uses available space.

        Criteria:
        - Total room area vs buildable area (target: 60-80%)
        - Minimize wasted space
        - Avoid room overlaps
        - Compact arrangement

        Returns:
            Score 0-100
        """
        score = 100.0

        total_room_area = sum(room.area for room in rooms)
        buildable_area = self.buildable['area']

        # Coverage ratio (target: 60-80%)
        coverage_ratio = total_room_area / buildable_area if buildable_area > 0 else 0

        if coverage_ratio < 0.4:
            # Too sparse - penalize
            score -= (0.4 - coverage_ratio) * 100
        elif coverage_ratio > 0.8:
            # Too dense - penalize
            score -= (coverage_ratio - 0.8) * 150
        else:
            # Good range - reward
            if 0.6 <= coverage_ratio <= 0.75:
                score += 20  # Optimal range bonus

        # Note: Overlap penalty now applied to final fitness, not here

        # Bonus for compact arrangement
        compactness = self._calculate_compactness(rooms)
        score += compactness * 10

        return max(0.0, min(100.0, score))

    def _evaluate_sunlight(self, rooms: List[RoomSchema]) -> float:
        """
        Evaluate sunlight optimization based on room placement.

        Criteria:
        - Bedrooms and living areas should face favorable directions
        - Service areas (toilets, kitchen) can face less favorable directions
        - Consider front direction for optimal sunlight

        Returns:
            Score 0-100
        """
        score = 70.0  # Base score

        front_dir = self.land_input.front_direction

        # Define favorable positions based on front direction
        # In Sri Lanka, north and east are typically favorable for sunlight
        favorable_zones = self._get_sunlight_zones(front_dir)

        for room in rooms:
            room_center_x = room.center_x
            room_center_y = room.center_y

            # Check if room is in favorable zone
            is_favorable = self._is_in_favorable_zone(
                room_center_x,
                room_center_y,
                favorable_zones
            )

            # Reward/penalize based on room type
            if room.type in ['bedroom', 'master_bedroom', 'living']:
                if is_favorable:
                    score += 5
                else:
                    score -= 3
            elif room.type == 'garden':
                if is_favorable:
                    score += 8  # Garden benefits most from sunlight

        return max(0.0, min(100.0, score))

    def _evaluate_privacy(self, rooms: List[RoomSchema]) -> float:
        """
        Evaluate privacy considerations.

        Criteria:
        - Bedrooms should not be near entrances
        - Toilets should be accessible but private
        - Living areas can be near entrance

        Returns:
            Score 0-100
        """
        score = 80.0  # Base score

        # Identify entrance area (based on road side)
        entrance_zone = self._get_entrance_zone()

        for room in rooms:
            distance_from_entrance = self._calculate_distance_from_zone(
                room.center_x,
                room.center_y,
                entrance_zone
            )

            # Normalize distance (0-1)
            max_distance = math.sqrt(
                self.buildable['width']**2 + self.buildable['length']**2
            )
            norm_distance = distance_from_entrance / max_distance if max_distance > 0 else 0

            if room.type in ['bedroom', 'master_bedroom']:
                # Bedrooms should be far from entrance
                if norm_distance > 0.5:
                    score += 5
                else:
                    score -= 10
            elif room.type == 'toilet':
                # Toilets should be moderately private
                if 0.3 < norm_distance < 0.7:
                    score += 3
            elif room.type == 'living':
                # Living can be near entrance
                if norm_distance < 0.4:
                    score += 4

        return max(0.0, min(100.0, score))

    def _evaluate_circulation(self, rooms: List[RoomSchema]) -> float:
        """
        Evaluate circulation efficiency (ease of movement between rooms).

        Criteria:
        - Logical flow from entrance to different areas
        - Minimize unnecessary distances
        - Good adjacency relationships

        Returns:
            Score 0-100
        """
        score = 75.0  # Base score

        # Check adjacency preferences
        adjacency_bonus = 0

        # Find room pairs
        kitchen_room = next((r for r in rooms if r.type == 'kitchen'), None)
        dining_room = next((r for r in rooms if r.type == 'dining'), None)
        living_room = next((r for r in rooms if r.type == 'living'), None)

        # Kitchen-Dining adjacency
        if kitchen_room and dining_room:
            distance = self._calculate_distance(
                kitchen_room.center_x, kitchen_room.center_y,
                dining_room.center_x, dining_room.center_y
            )
            if distance < 5:  # Close proximity (< 5 meters)
                adjacency_bonus += 10

        # Living-Dining adjacency
        if living_room and dining_room:
            distance = self._calculate_distance(
                living_room.center_x, living_room.center_y,
                dining_room.center_x, dining_room.center_y
            )
            if distance < 6:
                adjacency_bonus += 8

        score += adjacency_bonus

        # Penalty for very scattered layout
        scatter_penalty = self._calculate_scatter_penalty(rooms)
        score -= scatter_penalty

        return max(0.0, min(100.0, score))

    def _evaluate_connectivity(self, rooms: List[RoomSchema]) -> float:
        """
        Evaluate room connectivity (ensures all rooms can have doors/access).

        Criteria:
        - Rooms should be adjacent to other rooms or corridors
        - No isolated rooms (critical for door placement)
        - Compact groupings preferred

        Returns:
            Score 0-100
        """
        if not rooms:
            return 0.0

        score = 100.0
        adjacency_tolerance = 0.5  # meters - rooms within this distance are considered adjacent

        # Check each room for adjacency to at least one other room
        isolated_rooms = 0
        connected_rooms = 0

        for room in rooms:
            is_connected = False

            # Check if this room is adjacent to ANY other room
            for other_room in rooms:
                if other_room == room:
                    continue

                # Check horizontal adjacency (side by side)
                horizontal_gap = min(
                    abs((room.x + room.width) - other_room.x),  # room to left
                    abs(room.x - (other_room.x + other_room.width))  # room to right
                )

                # Check vertical adjacency (stacked)
                vertical_gap = min(
                    abs((room.y + room.height) - other_room.y),  # room above
                    abs(room.y - (other_room.y + other_room.height))  # room below
                )

                # Check if there's overlap in the perpendicular direction
                if horizontal_gap < adjacency_tolerance:
                    # Potentially adjacent horizontally - check for vertical overlap
                    y_overlap_start = max(room.y, other_room.y)
                    y_overlap_end = min(room.y + room.height, other_room.y + other_room.height)
                    if y_overlap_end > y_overlap_start:
                        is_connected = True
                        break

                if vertical_gap < adjacency_tolerance:
                    # Potentially adjacent vertically - check for horizontal overlap
                    x_overlap_start = max(room.x, other_room.x)
                    x_overlap_end = min(room.x + room.width, other_room.x + other_room.width)
                    if x_overlap_end > x_overlap_start:
                        is_connected = True
                        break

            if is_connected:
                connected_rooms += 1
            else:
                isolated_rooms += 1

        # Calculate connectivity percentage
        total_rooms = len(rooms)
        connectivity_percentage = (connected_rooms / total_rooms) * 100 if total_rooms > 0 else 0

        # Score based on connectivity:
        # - 100% connected = full score (100)
        # - 75% connected = good score (80)
        # - 50% connected = moderate score (50)
        # - 25% connected = poor score (25)
        # - 0% connected = minimum score (0)

        score = connectivity_percentage

        # Extra penalty for isolated rooms (these can't have doors!)
        # Each isolated room is a critical failure for door placement
        if isolated_rooms > 0:
            penalty_per_isolated = 20  # Heavy penalty per isolated room
            score -= (isolated_rooms * penalty_per_isolated)

        # Bonus for fully connected layouts
        if isolated_rooms == 0 and connected_rooms == total_rooms:
            score += 10  # Bonus for perfect connectivity

        return max(0.0, min(100.0, score))

    def _evaluate_regulations(self, rooms: List[RoomSchema]) -> float:
        """
        Evaluate compliance with building regulations.

        Criteria:
        - Minimum room sizes
        - Setback requirements
        - Coverage limits
        - No overlaps

        Returns:
            Score 0-100
        """
        score = 100.0

        # Validate layout against building rules
        validation_result = SriLankanBuildingRules.validate_layout(
            self.land_input,
            rooms
        )

        if not validation_result['valid']:
            # Deduct points for each violation
            for error in validation_result['errors']:
                if 'minimum area' in error.lower():
                    score -= 15
                elif 'overlap' in error.lower():
                    score -= 25  # Heavy penalty for overlaps
                elif 'setback' in error.lower():
                    score -= 20
                elif 'coverage' in error.lower():
                    score -= 10
                else:
                    score -= 5

        # Minor penalty for warnings
        score -= len(validation_result.get('warnings', [])) * 2

        return max(0.0, min(100.0, score))

    # Helper methods

    def _calculate_overlap_penalty(self, rooms: List[RoomSchema]) -> float:
        """Calculate penalty for overlapping rooms - MAXIMUM SEVERITY."""
        penalty = 0.0
        overlap_count = 0

        for i, room1 in enumerate(rooms):
            for room2 in rooms[i+1:]:
                overlap_area = self._calculate_overlap_area(room1, room2)
                if overlap_area > 0:
                    overlap_count += 1
                    # MAXIMUM PENALTY: Any overlap is completely unacceptable
                    # 10,000 points per sqm of overlap (was 500)
                    penalty += overlap_area * 10000
                    # Additional massive flat penalty for each overlap
                    penalty += 50000  # was 1000

        if overlap_count > 0:
            logger.debug(f"Found {overlap_count} overlaps, total penalty: {penalty:.1f}")

        return penalty

    def _calculate_overlap_area(self, room1: RoomSchema, room2: RoomSchema) -> float:
        """Calculate overlapping area between two rooms."""
        # Calculate intersection rectangle
        x_left = max(room1.x, room2.x)
        y_top = max(room1.y, room2.y)
        x_right = min(room1.x + room1.width, room2.x + room2.width)
        y_bottom = min(room1.y + room1.height, room2.y + room2.height)

        if x_right > x_left and y_bottom > y_top:
            return (x_right - x_left) * (y_bottom - y_top)
        return 0.0

    def _calculate_compactness(self, rooms: List[RoomSchema]) -> float:
        """
        Calculate how compact the room arrangement is (0-1).
        Compact = rooms are close together, not scattered.
        """
        if len(rooms) < 2:
            return 1.0

        # Calculate centroid of all rooms
        centroid_x = sum(r.center_x for r in rooms) / len(rooms)
        centroid_y = sum(r.center_y for r in rooms) / len(rooms)

        # Calculate average distance from centroid
        avg_distance = sum(
            self._calculate_distance(r.center_x, r.center_y, centroid_x, centroid_y)
            for r in rooms
        ) / len(rooms)

        # Normalize (assume max distance is half the buildable diagonal)
        max_distance = math.sqrt(
            self.buildable['width']**2 + self.buildable['length']**2
        ) / 2

        compactness = 1.0 - (avg_distance / max_distance) if max_distance > 0 else 1.0
        return max(0.0, min(1.0, compactness))

    def _calculate_scatter_penalty(self, rooms: List[RoomSchema]) -> float:
        """Calculate penalty for scattered room arrangement."""
        compactness = self._calculate_compactness(rooms)
        # Penalty increases as compactness decreases
        return (1.0 - compactness) * 20

    def _get_sunlight_zones(self, front_direction: DirectionEnum) -> Dict[str, Any]:
        """Get favorable sunlight zones based on front direction."""
        # Simplified: favorable zones are typically north and east
        buildable_width = self.buildable['width']
        buildable_length = self.buildable['length']
        offset_x = self.buildable['offset_x']
        offset_y = self.buildable['offset_y']

        # Define zones based on front direction
        # This is a simplified model
        return {
            'favorable_x_min': offset_x,
            'favorable_x_max': offset_x + buildable_width * 0.6,
            'favorable_y_min': offset_y,
            'favorable_y_max': offset_y + buildable_length * 0.5,
        }

    def _is_in_favorable_zone(
        self,
        x: float,
        y: float,
        zones: Dict[str, Any]
    ) -> bool:
        """Check if point is in favorable sunlight zone."""
        return (
            zones['favorable_x_min'] <= x <= zones['favorable_x_max'] and
            zones['favorable_y_min'] <= y <= zones['favorable_y_max']
        )

    def _get_entrance_zone(self) -> Dict[str, float]:
        """Get entrance zone based on road side."""
        road_side = self.land_input.road_side
        offset_x = self.buildable['offset_x']
        offset_y = self.buildable['offset_y']
        width = self.buildable['width']
        length = self.buildable['length']

        # Entrance is typically on road side
        if road_side == DirectionEnum.NORTH:
            return {'x': offset_x + width/2, 'y': offset_y}
        elif road_side == DirectionEnum.SOUTH:
            return {'x': offset_x + width/2, 'y': offset_y + length}
        elif road_side == DirectionEnum.EAST:
            return {'x': offset_x + width, 'y': offset_y + length/2}
        else:  # WEST
            return {'x': offset_x, 'y': offset_y + length/2}

    def _calculate_distance_from_zone(
        self,
        x: float,
        y: float,
        zone: Dict[str, float]
    ) -> float:
        """Calculate distance from point to zone (entrance)."""
        return self._calculate_distance(x, y, zone['x'], zone['y'])

    def _calculate_distance(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float
    ) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def get_detailed_scores(self, chromosome: List[float]) -> Dict[str, float]:
        """
        Get detailed breakdown of all fitness scores.
        Useful for debugging and displaying to users.

        Args:
            chromosome: Gene values

        Returns:
            Dictionary with all individual scores and total fitness
        """
        rooms = self.decode_chromosome(chromosome)

        scores = {
            'space_efficiency': self._evaluate_space_efficiency(rooms),
            'sunlight_score': self._evaluate_sunlight(rooms),
            'privacy_score': self._evaluate_privacy(rooms),
            'circulation_score': self._evaluate_circulation(rooms),
            'connectivity_score': self._evaluate_connectivity(rooms),
            'regulation_compliance': self._evaluate_regulations(rooms),
        }

        # Calculate weighted total
        scores['fitness_score'] = (
            self.WEIGHT_SPACE * scores['space_efficiency'] +
            self.WEIGHT_SUNLIGHT * scores['sunlight_score'] +
            self.WEIGHT_PRIVACY * scores['privacy_score'] +
            self.WEIGHT_CIRCULATION * scores['circulation_score'] +
            self.WEIGHT_CONNECTIVITY * scores['connectivity_score'] +
            self.WEIGHT_REGULATIONS * scores['regulation_compliance']
        )

        scores['rooms'] = [room.model_dump() for room in rooms]

        return scores
