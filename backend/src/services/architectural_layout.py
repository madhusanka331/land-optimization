"""
Architectural Floor Plan Generator
Creates complete house layouts with corridors, walls, doors, and fixtures.
Generates REAL architectural floor plans, not just floating rooms.
"""

from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np
from loguru import logger

from ..models.schemas import LandInputSchema, RoomSchema


@dataclass
class Wall:
    """Represents a wall in the floor plan."""
    x1: float
    y1: float
    x2: float
    y2: float
    thickness: float = 0.15  # meters (typically 6 inches = 0.15m)
    is_exterior: bool = False


@dataclass
class Door:
    """Represents a door with swing arc."""
    x: float
    y: float
    width: float = 0.9  # meters (standard door width)
    orientation: str = "horizontal"  # or "vertical"
    swing_direction: str = "right"  # or "left"


@dataclass
class Window:
    """Represents a window for VENTILATION and natural light - ESSENTIAL for real houses!"""
    x: float
    y: float
    width: float = 1.2  # meters (standard window width)
    orientation: str = "horizontal"  # or "vertical" (which wall it's on)


@dataclass
class Fixture:
    """Represents a fixture (toilet, sink, stove, etc.)."""
    x: float
    y: float
    type: str  # "toilet", "sink", "stove", "refrigerator"
    width: float
    height: float


@dataclass
class Corridor:
    """Represents a corridor/hallway."""
    x: float
    y: float
    width: float
    height: float
    orientation: str  # "horizontal" or "vertical"


class ArchitecturalLayoutGenerator:
    """
    Generates complete architectural floor plans with:
    - Building perimeter (exterior walls)
    - Interior walls    - Corridors for connectivity
    - Doors and fixtures
    - Vastu-compliant room placement
    """

    # Vastu directions for room placement
    VASTU_PLACEMENT = {
        'kitchen': 'southeast',          # Agni (fire) corner
        'master_bedroom': 'southwest',   # Most stable, auspicious
        'living': 'northeast',           # Best for social activities
        'dining': 'west',                # Good for dining
        'toilet': 'northwest',           # Vayu (air) corner
        'bedroom': 'south',              # Good for rest
    }

    # Minimum corridor width (meters)
    MIN_CORRIDOR_WIDTH = 1.2  # meters (4 feet)

    # Wall thickness
    WALL_THICKNESS = 0.15  # meters (6 inches)

    def __init__(self, buildable: Dict[str, float], land_input: LandInputSchema):
        """
        Initialize architectural layout generator.

        Args:
            buildable: Buildable area dictionary
            land_input: Land input with room requirements
        """
        self.buildable = buildable
        self.land_input = land_input

        # Extract buildable dimensions
        self.width = buildable['width']
        self.height = buildable['length']
        self.offset_x = buildable['offset_x']
        self.offset_y = buildable['offset_y']

        # Initialize containers
        self.rooms: List[RoomSchema] = []
        self.walls: List[Wall] = []
        self.doors: List[Door] = []
        self.windows: List[Window] = []  # CRITICAL: Windows for ventilation!
        self.corridors: List[Corridor] = []
        self.fixtures: List[Fixture] = []

    def generate_layout(self) -> Dict[str, Any]:
        """
        Generate complete architectural floor plan.
        Creates REALISTIC RESIDENTIAL layouts without mandatory central corridors.
        Rooms flow into each other naturally like a real house.

        Returns:
            Dictionary with rooms, walls, doors, corridors, fixtures
        """
        logger.info("Generating realistic residential floor plan...")

        # Step 1: Create building perimeter (exterior walls)
        self._create_exterior_walls()

        # Step 2: Get room requirements BEFORE clearing
        public_rooms, private_rooms = self._group_rooms_by_zone()

        # Step 3: CLEAR GA-generated rooms to avoid overlaps!
        # Create fresh rooms with proper sizes and NO overlaps
        logger.debug(f"Clearing {len(self.rooms)} GA-generated rooms to create natural layout...")
        self.rooms.clear()

        # Step 4: Place public rooms (living, dining, kitchen) adjacently - open flow
        self._place_public_rooms_adjacent(public_rooms)

        # Step 4: Place private rooms (bedrooms, bathrooms) in separate area
        self._place_private_rooms_adjacent(private_rooms)

        # Step 5: Add small hallway ONLY if needed to connect zones
        self._add_connecting_hallway_if_needed()

        # Step 6: Generate interior walls between rooms
        self._generate_interior_walls()

        # Step 7: Place doors between adjacent rooms (not to corridor)
        self._place_doors_between_rooms()

        # Step 8: Add WINDOWS for ventilation - ESSENTIAL for real houses!
        self._place_windows()

        # Step 9: Add fixtures (toilet, sink, stove)
        self._add_fixtures()

        logger.info(f"Layout complete: {len(self.rooms)} rooms, {len(self.corridors)} hallways, "
                   f"{len(self.walls)} walls, {len(self.doors)} doors, {len(self.windows)} windows")

        return {
            'rooms': self.rooms,
            'walls': self.walls,
            'doors': self.doors,
            'windows': self.windows,
            'corridors': self.corridors,
            'fixtures': self.fixtures,
        }

    def _create_exterior_walls(self):
        """Create thick exterior walls around building perimeter."""
        logger.debug("Creating exterior walls...")

        # Top wall
        self.walls.append(Wall(
            x1=self.offset_x,
            y1=self.offset_y,
            x2=self.offset_x + self.width,
            y2=self.offset_y,
            is_exterior=True
        ))

        # Bottom wall
        self.walls.append(Wall(
            x1=self.offset_x,
            y1=self.offset_y + self.height,
            x2=self.offset_x + self.width,
            y2=self.offset_y + self.height,
            is_exterior=True
        ))

        # Left wall
        self.walls.append(Wall(
            x1=self.offset_x,
            y1=self.offset_y,
            x2=self.offset_x,
            y2=self.offset_y + self.height,
            is_exterior=True
        ))

        # Right wall
        self.walls.append(Wall(
            x1=self.offset_x + self.width,
            y1=self.offset_y,
            x2=self.offset_x + self.width,
            y2=self.offset_y + self.height,
            is_exterior=True
        ))

    def _group_rooms_by_zone(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Group rooms into public (living, dining, kitchen) and private (bedrooms, bathrooms) zones.

        Returns:
            Tuple of (public_rooms, private_rooms)
        """
        public_rooms = []
        private_rooms = []

        # Get all required rooms
        all_rooms = self._get_required_rooms()

        for room in all_rooms:
            room_type = room['type']
            if room_type in ['living', 'dining', 'kitchen']:
                public_rooms.append(room)
            else:  # bedrooms, bathrooms
                private_rooms.append(room)

        logger.debug(f"Grouped rooms: {len(public_rooms)} public, {len(private_rooms)} private")
        return public_rooms, private_rooms

    def _place_public_rooms_adjacent(self, public_rooms: List[Dict]):
        """
        Create NATURAL house layout with OPEN CONCEPT like reference images!
        - Entry porch at front
        - Living/Dining/Kitchen = ONE LARGE OPEN SPACE
        - Car parking on side
        """
        if not public_rooms:
            return

        logger.debug(f"Creating NATURAL open concept layout like real houses...")

        # NATURAL HOUSE LAYOUT (like reference images):
        # 1. Entry Porch (2.5m x 1.5m) at front center
        # 2. Car Parking (3.5m x 5m) on left side
        # 3. OPEN CONCEPT main area (living/dining/kitchen combined) - ONE BIG SPACE

        buildable_width = self.width
        buildable_height = self.height

        # 1. ENTRY PORCH (front entrance - essential!)
        porch_width = min(2.5, buildable_width * 0.25)
        porch_height = 1.5
        porch_x = self.offset_x + (buildable_width - porch_width) / 2  # Center it

        self._create_room(
            room_type='living',  # Entry is part of living area
            x=porch_x,
            y=self.offset_y,
            width=porch_width,
            height=porch_height
        )

        # 2. CAR PARKING (left side)
        parking_width = min(3.5, buildable_width * 0.3)
        parking_height = min(5.0, buildable_height * 0.4)

        self._add_car_parking(
            x=self.offset_x,
            y=self.offset_y + porch_height + 0.2,
            width=parking_width,
            height=parking_height
        )

        # 3. PUBLIC ROOMS (Kitchen, Living, Dining) side-by-side
        # Create as separate rooms but adjacent for natural flow
        public_x = self.offset_x
        public_y = self.offset_y + porch_height + 0.2
        public_width = buildable_width
        public_height = buildable_height * 0.45  # Front 45% of house

        # Divide width among public rooms
        room_width = public_width / len(public_rooms)

        for i, room_data in enumerate(public_rooms):
            room_type = room_data['type']

            self._create_room(
                room_type=room_type,  # Use actual type: kitchen, living, or dining
                x=public_x + (i * room_width),
                y=public_y,
                width=room_width * 0.95,
                height=public_height
            )

    def _place_rooms_horizontal_flow(self, rooms: List[Dict], start_x: float, start_y: float,
                                     total_width: float, total_height: float):
        """Place rooms in horizontal flow (side by side)."""
        num_rooms = len(rooms)
        if num_rooms == 0:
            return

        room_width = total_width / num_rooms

        for i, room_data in enumerate(rooms):
            room_x = start_x + (i * room_width)
            room_width_actual = room_width * 0.95  # Small gap for walls

            self._create_room(
                room_type=room_data['type'],
                x=room_x,
                y=start_y,
                width=room_width_actual,
                height=total_height * 0.95
            )

    def _place_rooms_vertical_flow(self, rooms: List[Dict], start_x: float, start_y: float,
                                   total_width: float, total_height: float):
        """Place rooms in vertical flow (stacked)."""
        num_rooms = len(rooms)
        if num_rooms == 0:
            return

        room_height = total_height / num_rooms

        for i, room_data in enumerate(rooms):
            room_y = start_y + (i * room_height)
            room_height_actual = room_height * 0.95  # Small gap for walls

            self._create_room(
                room_type=room_data['type'],
                x=start_x,
                y=room_y,
                width=total_width * 0.95,
                height=room_height_actual
            )

    def _place_private_rooms_adjacent(self, private_rooms: List[Dict]):
        """
        Create NATURAL bedroom area with hallway like real houses!
        - Small hallway leading to bedrooms
        - Bedrooms with attached small bathrooms
        - Natural, organic layout
        """
        if not private_rooms:
            return

        logger.debug(f"Creating natural bedroom area with hallway...")

        buildable_width = self.width
        buildable_height = self.height
        private_zone_height = buildable_height * 0.50
        private_zone_y = self.offset_y + (buildable_height * 0.50)

        # Separate bedrooms and toilets
        bedrooms = [r for r in private_rooms if 'bedroom' in r['type']]
        toilets = [r for r in private_rooms if r['type'] == 'toilet']

        # NATURAL LAYOUT (like reference images):
        # 1. Small hallway (1m wide) along one side
        # 2. Bedrooms off the hallway
        # 3. Small bathrooms (2m x 2m) attached to bedrooms

        hallway_width = 1.2  # Narrow hallway
        bedroom_area_width = buildable_width - hallway_width

        # Place bedrooms with attached bathrooms
        num_bedrooms = len(bedrooms)
        bedroom_width = bedroom_area_width if num_bedrooms == 1 else bedroom_area_width / num_bedrooms

        current_x = self.offset_x + hallway_width

        # Place bedrooms - give them proper size
        for i, bedroom_data in enumerate(bedrooms):
            # Bedroom gets most of the width
            bed_w = bedroom_width - 2.2  # Reserve 2.2m for attached bathroom

            # Create bedroom
            self._create_room(
                room_type=bedroom_data['type'],
                x=current_x,
                y=private_zone_y,
                width=bed_w,
                height=private_zone_height * 0.95
            )

            current_x += bed_w

        # Place ALL toilets consistently small (2m x 2.2m)
        toilet_x = self.offset_x + hallway_width
        toilet_y = private_zone_y

        for i, toilet_data in enumerate(toilets):
            # ALL toilets are EXACTLY 2m x 2.2m - consistently small!
            self._create_room(
                room_type='toilet',
                x=toilet_x,
                y=toilet_y,
                width=2.0,
                height=2.2
            )

            # Stack toilets vertically if multiple
            toilet_y += 2.4  # Small gap between toilets

    def _create_room(self, room_type: str, x: float, y: float, width: float, height: float):
        """Helper to create a room with given dimensions."""
        room = RoomSchema(
            type=room_type,
            x=x,
            y=y,
            width=width,
            height=height,
            area=width * height
        )
        self.rooms.append(room)
        logger.debug(f"Created {room_type} at ({x:.1f}, {y:.1f}) size {width:.1f}x{height:.1f}")

    def _add_car_parking(self, x: float, y: float, width: float, height: float):
        """Add car parking area (appears as a special room type)."""
        parking = RoomSchema(
            type='parking',
            x=x,
            y=y,
            width=width,
            height=height,
            area=width * height
        )
        self.rooms.append(parking)
        logger.debug(f"Created car parking at ({x:.1f}, {y:.1f}) size {width:.1f}x{height:.1f} ({width*height:.1f} sqm)")

    def _add_connecting_hallway_if_needed(self):
        """
        Add a small hallway ONLY if needed to connect public and private zones.
        Real houses minimize hallway space - only add if zones are not adjacent.
        """
        if not self.rooms:
            return

        # Check if public and private zones are already adjacent
        # If yes, no hallway needed (rooms will have doors between them)
        # For now, we'll skip adding hallway as rooms are placed adjacently

        logger.debug("Skipping hallway - rooms are adjacent and will have direct doors")
        # Note: If needed in future, add a small connecting hallway here

    def _place_doors_between_rooms(self):
        """
        Place doors between adjacent rooms (not to corridor).
        Creates natural flow: Living → Dining → Kitchen, and Bedroom → Bathroom.
        """
        logger.debug("Placing doors between adjacent rooms...")

        # Clear any existing doors
        self.doors = []

        # For each room, check for adjacent rooms and add doors
        for i, room in enumerate(self.rooms):
            # Check adjacency with other rooms
            for j, other_room in enumerate(self.rooms):
                if i >= j:  # Skip self and already-checked pairs
                    continue

                door = self._find_door_between_adjacent_rooms(room, other_room)
                if door:
                    self.doors.append(door)
                    logger.debug(f"Door between {room.type} and {other_room.type}")

        logger.info(f"Placed {len(self.doors)} doors between adjacent rooms")

    def _find_door_between_adjacent_rooms(self, room1: RoomSchema, room2: RoomSchema) -> Optional[Door]:
        """
        Find optimal door position between two adjacent rooms.

        Returns:
            Door object if rooms are adjacent, None otherwise
        """
        tolerance = 0.5  # meters - rooms within 0.5m are considered adjacent

        # Check if rooms share a horizontal edge (stacked vertically)
        if abs(room1.x - room2.x) < tolerance and abs((room1.x + room1.width) - (room2.x + room2.width)) < tolerance:
            # Rooms are horizontally aligned, check vertical adjacency
            if abs(room1.y + room1.height - room2.y) < tolerance:
                # room1 is above room2
                door_x = room1.x + room1.width / 2 - 0.45  # Center the door
                door_y = room1.y + room1.height
                return Door(x=door_x, y=door_y, orientation="horizontal")
            elif abs(room2.y + room2.height - room1.y) < tolerance:
                # room2 is above room1
                door_x = room2.x + room2.width / 2 - 0.45
                door_y = room2.y + room2.height
                return Door(x=door_x, y=door_y, orientation="horizontal")

        # Check if rooms share a vertical edge (side by side)
        if abs(room1.y - room2.y) < tolerance and abs((room1.y + room1.height) - (room2.y + room2.height)) < tolerance:
            # Rooms are vertically aligned, check horizontal adjacency
            if abs(room1.x + room1.width - room2.x) < tolerance:
                # room1 is left of room2
                door_x = room1.x + room1.width
                door_y = room1.y + room1.height / 2 - 0.45  # Center the door
                return Door(x=door_x, y=door_y, orientation="vertical")
            elif abs(room2.x + room2.width - room1.x) < tolerance:
                # room2 is left of room1
                door_x = room2.x + room2.width
                door_y = room2.y + room2.height / 2 - 0.45
                return Door(x=door_x, y=door_y, orientation="vertical")

        return None

    def _place_windows(self):
        """
        Place windows on exterior walls for VENTILATION and natural light.
        CRITICAL for realistic house floor plans!
        Every habitable room needs windows!
        """
        logger.debug("Placing windows for ventilation...")

        self.windows = []

        # Building exterior boundaries
        min_x = self.offset_x
        max_x = self.offset_x + self.width
        min_y = self.offset_y
        max_y = self.offset_y + self.height

        tolerance = 0.5  # meters

        for room in self.rooms:
            # Skip parking - it doesn't need windows
            if room.type == 'parking':
                continue

            room_windows = []

            # Check which exterior walls this room touches
            # Left wall (west)
            if abs(room.x - min_x) < tolerance:
                window_x = room.x
                window_y = room.y + room.height / 2 - 0.6  # Center on wall
                room_windows.append(Window(x=window_x, y=window_y, width=1.2, orientation="vertical"))

            # Right wall (east)
            if abs(room.x + room.width - max_x) < tolerance:
                window_x = room.x + room.width
                window_y = room.y + room.height / 2 - 0.6
                room_windows.append(Window(x=window_x, y=window_y, width=1.2, orientation="vertical"))

            # Top wall (north)
            if abs(room.y + room.height - max_y) < tolerance:
                window_x = room.x + room.width / 2 - 0.6  # Center on wall
                window_y = room.y + room.height
                room_windows.append(Window(x=window_x, y=window_y, width=1.2, orientation="horizontal"))

            # Bottom wall (south)
            if abs(room.y - min_y) < tolerance:
                window_x = room.x + room.width / 2 - 0.6
                window_y = room.y
                room_windows.append(Window(x=window_x, y=window_y, width=1.2, orientation="horizontal"))

            # Add windows for this room
            if room_windows:
                # For habitable rooms, use all windows; for toilets, use just one
                if room.type == 'toilet':
                    self.windows.append(room_windows[0])  # Just one small window
                else:
                    self.windows.extend(room_windows)  # All windows for ventilation

                logger.debug(f"Added {len(room_windows) if room.type != 'toilet' else 1} window(s) to {room.type}")

        logger.info(f"Placed {len(self.windows)} windows for ventilation")

    def _allocate_corridor_space(self) -> Dict[str, Any]:
        """
        Allocate 10-15% of buildable area for corridors/hallways.

        Returns:
            Dictionary with corridor layout plan
        """
        total_area = self.width * self.height
        corridor_area = total_area * 0.12  # 12% for corridors

        logger.debug(f"Allocating {corridor_area:.1f} sqm ({12}%) for corridors")

        # Create a central corridor layout
        # For most houses, a central hallway works best
        if self.width > self.height:
            # Wide house - horizontal corridor
            corridor_width = self.MIN_CORRIDOR_WIDTH
            corridor_length = self.width * 0.8

            corridor = Corridor(
                x=self.offset_x + (self.width - corridor_length) / 2,
                y=self.offset_y + self.height / 2 - corridor_width / 2,
                width=corridor_length,
                height=corridor_width,
                orientation="horizontal"
            )
        else:
            # Tall house - vertical corridor
            corridor_width = self.MIN_CORRIDOR_WIDTH
            corridor_height = self.height * 0.8

            corridor = Corridor(
                x=self.offset_x + self.width / 2 - corridor_width / 2,
                y=self.offset_y + (self.height - corridor_height) / 2,
                width=corridor_width,
                height=corridor_height,
                orientation="vertical"
            )

        self.corridors.append(corridor)

        return {
            'main_corridor': corridor,
            'total_corridor_area': corridor_area,
        }

    def _partition_space_into_rooms(self, corridor_allocation: Dict[str, Any]):
        """
        Partition space into rooms using Vastu principles.

        Args:
            corridor_allocation: Corridor layout information
        """
        logger.debug("Partitioning space into rooms with Vastu compliance...")

        main_corridor = corridor_allocation['main_corridor']

        # Get list of required rooms
        rooms_needed = self._get_required_rooms()

        # Divide buildable area into zones based on Vastu and corridor
        zones = self._create_vastu_zones(main_corridor)

        # Place rooms in appropriate zones
        self._place_rooms_in_zones(rooms_needed, zones, main_corridor)

    def _get_required_rooms(self) -> List[Dict[str, Any]]:
        """Get list of required rooms from land input."""
        rooms = []

        # Bedrooms
        if self.land_input.bedrooms >= 1:
            rooms.append({'type': 'master_bedroom', 'min_area': 14.0})
            for i in range(self.land_input.bedrooms - 1):
                rooms.append({'type': 'bedroom', 'min_area': 12.0})

        # Toilets
        for i in range(self.land_input.toilets):
            rooms.append({'type': 'toilet', 'min_area': 4.0})

        # Kitchen (always required)
        rooms.append({'type': 'kitchen', 'min_area': 7.0})

        # Living room
        if self.land_input.living_room > 0:
            rooms.append({'type': 'living', 'min_area': 13.0})

        # Dining room
        if self.land_input.dining_room > 0:
            rooms.append({'type': 'dining', 'min_area': 11.0})

        return rooms

    def _create_vastu_zones(self, corridor: Corridor) -> Dict[str, Dict]:
        """
        Create Vastu-compliant zones for room placement around the corridor.

        Divides space into zones based on corridor orientation and Vastu directions.

        Args:
            corridor: The main corridor

        Returns:
            Dictionary mapping Vastu directions to available zones
        """
        zones = {}

        if corridor.orientation == "horizontal":
            # Horizontal corridor divides space into top and bottom zones
            # Top zones (north)
            top_height = corridor.y - self.offset_y
            if top_height > 0:
                # Northeast (top-left)
                zones['northeast'] = {
                    'x': self.offset_x,
                    'y': self.offset_y,
                    'width': self.width / 2,
                    'height': top_height,
                    'adjacent_to_corridor': True
                }
                # Northwest (top-right)
                zones['northwest'] = {
                    'x': self.offset_x + self.width / 2,
                    'y': self.offset_y,
                    'width': self.width / 2,
                    'height': top_height,
                    'adjacent_to_corridor': True
                }

            # Bottom zones (south)
            bottom_y = corridor.y + corridor.height
            bottom_height = (self.offset_y + self.height) - bottom_y
            if bottom_height > 0:
                # Southeast (bottom-left)
                zones['southeast'] = {
                    'x': self.offset_x,
                    'y': bottom_y,
                    'width': self.width / 2,
                    'height': bottom_height,
                    'adjacent_to_corridor': True
                }
                # Southwest (bottom-right)
                zones['southwest'] = {
                    'x': self.offset_x + self.width / 2,
                    'y': bottom_y,
                    'width': self.width / 2,
                    'height': bottom_height,
                    'adjacent_to_corridor': True
                }

        else:  # vertical corridor
            # Vertical corridor divides space into left and right zones
            # Left zones (west)
            left_width = corridor.x - self.offset_x
            if left_width > 0:
                # Northwest (left-top)
                zones['northwest'] = {
                    'x': self.offset_x,
                    'y': self.offset_y,
                    'width': left_width,
                    'height': self.height / 2,
                    'adjacent_to_corridor': True
                }
                # Southwest (left-bottom)
                zones['southwest'] = {
                    'x': self.offset_x,
                    'y': self.offset_y + self.height / 2,
                    'width': left_width,
                    'height': self.height / 2,
                    'adjacent_to_corridor': True
                }

            # Right zones (east)
            right_x = corridor.x + corridor.width
            right_width = (self.offset_x + self.width) - right_x
            if right_width > 0:
                # Northeast (right-top)
                zones['northeast'] = {
                    'x': right_x,
                    'y': self.offset_y,
                    'width': right_width,
                    'height': self.height / 2,
                    'adjacent_to_corridor': True
                }
                # Southeast (right-bottom)
                zones['southeast'] = {
                    'x': right_x,
                    'y': self.offset_y + self.height / 2,
                    'width': right_width,
                    'height': self.height / 2,
                    'adjacent_to_corridor': True
                }

        logger.debug(f"Created {len(zones)} Vastu zones around corridor")
        return zones

    def _place_rooms_in_zones(self, rooms_needed: List[Dict], zones: Dict, corridor: Corridor):
        """
        Place rooms in Vastu-appropriate zones.

        Args:
            rooms_needed: List of room requirements
            zones: Available Vastu zones
            corridor: Main corridor for access
        """
        logger.debug(f"Placing {len(rooms_needed)} rooms in {len(zones)} zones...")

        # Group rooms by their Vastu direction
        room_groups = {}
        for room in rooms_needed:
            vastu_dir = self.VASTU_PLACEMENT.get(room['type'], 'northeast')
            if vastu_dir not in room_groups:
                room_groups[vastu_dir] = []
            room_groups[vastu_dir].append(room)

        # Place each group of rooms in their designated zone
        for vastu_dir, rooms_in_zone in room_groups.items():
            if vastu_dir not in zones:
                # Fallback to any available zone
                vastu_dir = list(zones.keys())[0] if zones else None
                if not vastu_dir:
                    logger.warning(f"No zones available for {len(rooms_in_zone)} rooms")
                    continue

            zone = zones[vastu_dir]
            self._pack_rooms_in_zone(rooms_in_zone, zone, corridor)

        logger.info(f"Placed {len(self.rooms)} rooms in zones")

    def _pack_rooms_in_zone(self, rooms_to_place: List[Dict], zone: Dict, corridor: Corridor):
        """
        Pack multiple rooms into a single zone using intelligent layout.

        Args:
            rooms_to_place: Rooms to place in this zone
            zone: Zone boundaries and properties
            corridor: Main corridor for access
        """
        zone_x = zone['x']
        zone_y = zone['y']
        zone_width = zone['width']
        zone_height = zone['height']

        num_rooms = len(rooms_to_place)
        if num_rooms == 0:
            return

        # Calculate total required area
        total_min_area = sum(room['min_area'] for room in rooms_to_place)
        zone_area = zone_width * zone_height

        # Check if rooms fit in zone
        if total_min_area > zone_area * 0.85:  # 85% max utilization
            logger.warning(f"Zone area ({zone_area:.1f}m²) may be tight for {num_rooms} rooms ({total_min_area:.1f}m² needed)")

        # Determine layout pattern (1 room, 2 rooms horizontal/vertical, or grid)
        if num_rooms == 1:
            # Single room - use most of zone
            room = rooms_to_place[0]
            self._place_single_room(room, zone_x, zone_y, zone_width, zone_height, corridor)

        elif num_rooms == 2:
            # Two rooms - split zone
            if zone_width >= zone_height:
                # Split horizontally (side by side)
                for i, room in enumerate(rooms_to_place):
                    room_x = zone_x + (i * zone_width / 2)
                    room_width = zone_width / 2
                    self._place_single_room(room, room_x, zone_y, room_width * 0.95, zone_height * 0.95, corridor)
            else:
                # Split vertically (stacked)
                for i, room in enumerate(rooms_to_place):
                    room_y = zone_y + (i * zone_height / 2)
                    room_height = zone_height / 2
                    self._place_single_room(room, zone_x, room_y, zone_width * 0.95, room_height * 0.95, corridor)

        else:
            # Multiple rooms - use LINEAR layout along corridor to ensure ALL rooms are adjacent
            # This ensures every room can have a door to the corridor
            self._place_rooms_linear_along_corridor(rooms_to_place, zone, corridor)

    def _place_rooms_linear_along_corridor(self, rooms_to_place: List[Dict], zone: Dict, corridor: Corridor):
        """
        Place rooms in a linear strip along the corridor edge to ensure ALL rooms are adjacent.

        This ensures every room can have a door directly to the corridor.

        Args:
            rooms_to_place: Rooms to place in this zone
            zone: Zone boundaries
            corridor: Main corridor
        """
        zone_x = zone['x']
        zone_y = zone['y']
        zone_width = zone['width']
        zone_height = zone['height']
        num_rooms = len(rooms_to_place)

        # Determine which edge of zone is adjacent to corridor
        # and place rooms in a strip along that edge

        # Calculate zone and corridor boundaries
        zone_bottom = zone_y + zone_height
        zone_right = zone_x + zone_width
        corridor_bottom = corridor.y + corridor.height
        corridor_right = corridor.x + corridor.width

        # Check all four possible adjacency positions
        if abs(zone_bottom - corridor.y) < 0.5:
            # Zone is ABOVE corridor - place rooms in horizontal strip at bottom of zone
            strip_height = zone_height  # Use full height
            room_width = zone_width / num_rooms

            for i, room in enumerate(rooms_to_place):
                room_x = zone_x + (i * room_width)
                # Position room to touch corridor (bottom edge of room = top edge of corridor)
                room_y = corridor.y - strip_height
                self._place_single_room(
                    room, room_x, room_y,
                    room_width * 0.95, strip_height * 0.95,
                    corridor
                )

        elif abs(zone_y - corridor_bottom) < 0.5:
            # Zone is BELOW corridor - place rooms in horizontal strip at top of zone
            strip_height = zone_height  # Use full height
            room_width = zone_width / num_rooms

            for i, room in enumerate(rooms_to_place):
                room_x = zone_x + (i * room_width)
                # Position room to touch corridor (top edge of room = bottom edge of corridor)
                room_y = corridor_bottom
                self._place_single_room(
                    room, room_x, room_y,
                    room_width * 0.95, strip_height * 0.95,
                    corridor
                )

        elif abs(zone_right - corridor.x) < 0.5:
            # Zone is LEFT of corridor - place rooms in vertical strip at right edge of zone
            strip_width = zone_width  # Use full width
            room_height = zone_height / num_rooms

            for i, room in enumerate(rooms_to_place):
                room_y = zone_y + (i * room_height)
                # Position room to touch corridor (right edge of room = left edge of corridor)
                room_x = corridor.x - strip_width
                self._place_single_room(
                    room, room_x, room_y,
                    strip_width * 0.95, room_height * 0.95,
                    corridor
                )

        elif abs(zone_x - corridor_right) < 0.5:
            # Zone is RIGHT of corridor - place rooms in vertical strip at left edge of zone
            strip_width = zone_width  # Use full width
            room_height = zone_height / num_rooms

            for i, room in enumerate(rooms_to_place):
                room_y = zone_y + (i * room_height)
                # Position room to touch corridor (left edge of room = right edge of corridor)
                room_x = corridor_right
                self._place_single_room(
                    room, room_x, room_y,
                    strip_width * 0.95, room_height * 0.95,
                    corridor
                )

        else:
            # Zone not adjacent to corridor - use grid layout as fallback
            logger.warning(f"Zone not adjacent to corridor, using grid fallback")
            grid_cols = int(np.ceil(np.sqrt(num_rooms)))
            grid_rows = int(np.ceil(num_rooms / grid_cols))

            cell_width = zone_width / grid_cols
            cell_height = zone_height / grid_rows

            for idx, room in enumerate(rooms_to_place):
                row = idx // grid_cols
                col = idx % grid_cols

                cell_x = zone_x + (col * cell_width)
                cell_y = zone_y + (row * cell_height)

                self._place_single_room(
                    room, cell_x, cell_y,
                    cell_width * 0.9, cell_height * 0.9,
                    corridor
                )

    def _place_single_room(
        self, room_def: Dict, zone_x: float, zone_y: float,
        max_width: float, max_height: float, corridor: Corridor
    ):
        """
        Place a single room within given boundaries.

        Args:
            room_def: Room definition with type and min_area
            zone_x, zone_y: Zone origin
            max_width, max_height: Maximum dimensions available
            corridor: Main corridor
        """
        min_area = room_def['min_area']

        # Calculate room dimensions
        # Try to fit minimum area while respecting max dimensions
        aspect_ratio = 1.3  # Slightly rectangular (width/height)

        # Start with ideal dimensions based on min_area
        ideal_height = np.sqrt(min_area / aspect_ratio)
        ideal_width = min_area / ideal_height

        # Constrain to available space
        room_width = min(ideal_width, max_width)
        room_height = min(ideal_height, max_height)

        # Ensure minimum area is still met
        actual_area = room_width * room_height
        if actual_area < min_area:
            # Scale up proportionally while staying within bounds
            scale = np.sqrt(min_area / actual_area)
            room_width = min(room_width * scale, max_width)
            room_height = min(room_height * scale, max_height)

        # Center room in available space
        room_x = zone_x + (max_width - room_width) / 2
        room_y = zone_y + (max_height - room_height) / 2

        # Create room
        room = RoomSchema(
            type=room_def['type'],
            x=room_x,
            y=room_y,
            width=room_width,
            height=room_height,
            area=room_width * room_height
        )

        self.rooms.append(room)
        logger.debug(f"Placed {room.type}: {room.width:.1f}m × {room.height:.1f}m at ({room.x:.1f}, {room.y:.1f})")

    def _generate_interior_walls(self):
        """
        Generate interior walls between ALL rooms - creating complete floor plan.
        Every room boundary gets a wall!
        """
        logger.debug("Generating interior walls...")

        # Clear existing interior walls (keep exterior)
        exterior_walls = [w for w in self.walls if w.is_exterior]
        self.walls = exterior_walls

        # Generate walls for EACH ROOM'S boundaries
        for room in self.rooms:
            # Create walls around this room
            # Top wall
            self.walls.append(Wall(
                x1=room.x,
                y1=room.y,
                x2=room.x + room.width,
                y2=room.y,
                thickness=self.WALL_THICKNESS,
                is_exterior=False
            ))

            # Bottom wall
            self.walls.append(Wall(
                x1=room.x,
                y1=room.y + room.height,
                x2=room.x + room.width,
                y2=room.y + room.height,
                thickness=self.WALL_THICKNESS,
                is_exterior=False
            ))

            # Left wall
            self.walls.append(Wall(
                x1=room.x,
                y1=room.y,
                x2=room.x,
                y2=room.y + room.height,
                thickness=self.WALL_THICKNESS,
                is_exterior=False
            ))

            # Right wall
            self.walls.append(Wall(
                x1=room.x + room.width,
                y1=room.y,
                x2=room.x + room.width,
                y2=room.y + room.height,
                thickness=self.WALL_THICKNESS,
                is_exterior=False
            ))

        logger.info(f"Generated {len(self.walls)} walls total ({len(exterior_walls)} exterior, {len(self.walls) - len(exterior_walls)} interior)")

    def _create_wall_between_rooms(self, room1: RoomSchema, room2: RoomSchema):
        """
        Create a wall between two adjacent rooms if they share a boundary.

        Args:
            room1: First room
            room2: Second room
        """
        tolerance = 0.1  # meters

        # Check if rooms are adjacent horizontally (share vertical edge)
        # Room1 is to the left of room2
        if abs((room1.x + room1.width) - room2.x) < tolerance:
            # Find overlapping y-range
            y_start = max(room1.y, room2.y)
            y_end = min(room1.y + room1.height, room2.y + room2.height)

            if y_end > y_start:  # There is overlap
                wall_x = (room1.x + room1.width + room2.x) / 2
                self.walls.append(Wall(
                    x1=wall_x,
                    y1=y_start,
                    x2=wall_x,
                    y2=y_end,
                    thickness=self.WALL_THICKNESS,
                    is_exterior=False
                ))

        # Room2 is to the left of room1
        elif abs((room2.x + room2.width) - room1.x) < tolerance:
            y_start = max(room1.y, room2.y)
            y_end = min(room1.y + room1.height, room2.y + room2.height)

            if y_end > y_start:
                wall_x = (room2.x + room2.width + room1.x) / 2
                self.walls.append(Wall(
                    x1=wall_x,
                    y1=y_start,
                    x2=wall_x,
                    y2=y_end,
                    thickness=self.WALL_THICKNESS,
                    is_exterior=False
                ))

        # Check if rooms are adjacent vertically (share horizontal edge)
        # Room1 is above room2
        if abs((room1.y + room1.height) - room2.y) < tolerance:
            x_start = max(room1.x, room2.x)
            x_end = min(room1.x + room1.width, room2.x + room2.width)

            if x_end > x_start:
                wall_y = (room1.y + room1.height + room2.y) / 2
                self.walls.append(Wall(
                    x1=x_start,
                    y1=wall_y,
                    x2=x_end,
                    y2=wall_y,
                    thickness=self.WALL_THICKNESS,
                    is_exterior=False
                ))

        # Room2 is above room1
        elif abs((room2.y + room2.height) - room1.y) < tolerance:
            x_start = max(room1.x, room2.x)
            x_end = min(room1.x + room1.width, room2.x + room2.width)

            if x_end > x_start:
                wall_y = (room2.y + room2.height + room1.y) / 2
                self.walls.append(Wall(
                    x1=x_start,
                    y1=wall_y,
                    x2=x_end,
                    y2=wall_y,
                    thickness=self.WALL_THICKNESS,
                    is_exterior=False
                ))

    def _place_doors(self):
        """
        Place doors for room access from corridors.

        Each room should have at least one door connecting to the corridor.
        If a room can't connect directly, try to connect via adjacent rooms.
        """
        logger.debug("Placing doors...")

        if not self.corridors:
            logger.warning("No corridors available for door placement")
            return

        main_corridor = self.corridors[0]

        # Track which rooms don't have corridor doors
        rooms_without_doors = []

        # Place corridor doors for each room
        for room in self.rooms:
            door = self._find_door_position(room, main_corridor)
            if door:
                self.doors.append(door)
            else:
                rooms_without_doors.append(room)
                logger.debug(f"Room {room.type} not adjacent to corridor, will try room-to-room door")

        # For rooms without corridor access, try to place room-to-room doors
        for room in rooms_without_doors:
            door = self._find_room_to_room_door(room)
            if door:
                self.doors.append(door)
                logger.info(f"Placed room-to-room door for {room.type}")
            else:
                logger.warning(f"Could not place any door for {room.type}")

        logger.info(f"Placed {len(self.doors)} doors total")

    def _find_door_position(self, room: RoomSchema, corridor: Corridor) -> Optional[Door]:
        """
        Find optimal door position between room and corridor.

        Args:
            room: Room to connect
            corridor: Corridor to connect to

        Returns:
            Door object or None if no valid position found
        """
        door_width = 0.9  # Standard door width in meters

        # Check if room is adjacent to corridor horizontally
        # Room is above corridor
        if abs((room.y + room.height) - corridor.y) < 0.1:
            # Door on bottom wall of room / top wall of corridor
            door_x = room.x + room.width / 2 - door_width / 2
            door_y = corridor.y

            return Door(
                x=door_x,
                y=door_y,
                width=door_width,
                orientation="horizontal",
                swing_direction="up"
            )

        # Room is below corridor
        elif abs(room.y - (corridor.y + corridor.height)) < 0.1:
            # Door on top wall of room / bottom wall of corridor
            door_x = room.x + room.width / 2 - door_width / 2
            door_y = room.y

            return Door(
                x=door_x,
                y=door_y,
                width=door_width,
                orientation="horizontal",
                swing_direction="down"
            )

        # Check if room is adjacent to corridor vertically
        # Room is to the left of corridor
        elif abs((room.x + room.width) - corridor.x) < 0.1:
            # Door on right wall of room / left wall of corridor
            door_x = corridor.x
            door_y = room.y + room.height / 2 - door_width / 2

            return Door(
                x=door_x,
                y=door_y,
                width=door_width,
                orientation="vertical",
                swing_direction="left"
            )

        # Room is to the right of corridor
        elif abs(room.x - (corridor.x + corridor.width)) < 0.1:
            # Door on left wall of room / right wall of corridor
            door_x = room.x
            door_y = room.y + room.height / 2 - door_width / 2

            return Door(
                x=door_x,
                y=door_y,
                width=door_width,
                orientation="vertical",
                swing_direction="right"
            )

        # Room not adjacent to corridor - this is a problem
        logger.warning(f"Room {room.type} at ({room.x:.1f}, {room.y:.1f}) not adjacent to corridor")
        return None

    def _find_room_to_room_door(self, room: RoomSchema) -> Optional[Door]:
        """
        Find a door position between this room and an adjacent room.

        This is a fallback when a room can't connect directly to the corridor.

        Args:
            room: Room that needs a door

        Returns:
            Door object or None if no adjacent room found
        """
        door_width = 0.9
        tolerance = 0.1

        # Find an adjacent room
        for other_room in self.rooms:
            if other_room == room:
                continue

            # Check horizontal adjacency (rooms side by side)
            # Room is to the left of other_room
            if abs((room.x + room.width) - other_room.x) < tolerance:
                y_start = max(room.y, other_room.y)
                y_end = min(room.y + room.height, other_room.y + other_room.height)

                if y_end > y_start and (y_end - y_start) >= door_width:
                    # There's overlap - place door
                    door_x = other_room.x
                    door_y = y_start + (y_end - y_start) / 2 - door_width / 2

                    return Door(
                        x=door_x,
                        y=door_y,
                        width=door_width,
                        orientation="vertical",
                        swing_direction="left"
                    )

            # Room is to the right of other_room
            elif abs(room.x - (other_room.x + other_room.width)) < tolerance:
                y_start = max(room.y, other_room.y)
                y_end = min(room.y + room.height, other_room.y + other_room.height)

                if y_end > y_start and (y_end - y_start) >= door_width:
                    door_x = room.x
                    door_y = y_start + (y_end - y_start) / 2 - door_width / 2

                    return Door(
                        x=door_x,
                        y=door_y,
                        width=door_width,
                        orientation="vertical",
                        swing_direction="right"
                    )

            # Check vertical adjacency (rooms stacked)
            # Room is above other_room
            if abs((room.y + room.height) - other_room.y) < tolerance:
                x_start = max(room.x, other_room.x)
                x_end = min(room.x + room.width, other_room.x + other_room.width)

                if x_end > x_start and (x_end - x_start) >= door_width:
                    door_x = x_start + (x_end - x_start) / 2 - door_width / 2
                    door_y = other_room.y

                    return Door(
                        x=door_x,
                        y=door_y,
                        width=door_width,
                        orientation="horizontal",
                        swing_direction="up"
                    )

            # Room is below other_room
            elif abs(room.y - (other_room.y + other_room.height)) < tolerance:
                x_start = max(room.x, other_room.x)
                x_end = min(room.x + room.width, other_room.x + other_room.width)

                if x_end > x_start and (x_end - x_start) >= door_width:
                    door_x = x_start + (x_end - x_start) / 2 - door_width / 2
                    door_y = room.y

                    return Door(
                        x=door_x,
                        y=door_y,
                        width=door_width,
                        orientation="horizontal",
                        swing_direction="down"
                    )

        # No adjacent room found
        logger.warning(f"No adjacent room found for {room.type}")
        return None

    def _add_fixtures(self):
        """
        Add fixtures like toilet, sink, stove to appropriate rooms.

        Places fixtures in optimal positions within each room based on room type.
        """
        logger.debug("Adding fixtures...")

        for room in self.rooms:
            if 'kitchen' in room.type.lower():
                self._add_kitchen_fixtures(room)
            elif 'toilet' in room.type.lower() or 'bathroom' in room.type.lower():
                self._add_bathroom_fixtures(room)
            # Add more fixture types as needed

        logger.info(f"Added {len(self.fixtures)} fixtures")

    def _add_kitchen_fixtures(self, room: RoomSchema):
        """
        Add kitchen fixtures (stove, sink, refrigerator).

        Args:
            room: Kitchen room
        """
        # Place stove in corner
        self.fixtures.append(Fixture(
            x=room.x + 0.3,
            y=room.y + 0.3,
            type="stove",
            width=0.6,
            height=0.6
        ))

        # Place sink next to stove
        self.fixtures.append(Fixture(
            x=room.x + 1.2,
            y=room.y + 0.3,
            type="sink",
            width=0.6,
            height=0.6
        ))

        # Place refrigerator on opposite wall
        self.fixtures.append(Fixture(
            x=room.x + room.width - 0.9,
            y=room.y + 0.3,
            type="refrigerator",
            width=0.7,
            height=0.7
        ))

    def _add_bathroom_fixtures(self, room: RoomSchema):
        """
        Add bathroom fixtures (toilet, sink).

        Args:
            room: Bathroom/toilet room
        """
        # Place toilet in corner
        self.fixtures.append(Fixture(
            x=room.x + 0.3,
            y=room.y + 0.3,
            type="toilet",
            width=0.5,
            height=0.7
        ))

        # Place sink on adjacent wall
        self.fixtures.append(Fixture(
            x=room.x + room.width - 0.8,
            y=room.y + 0.3,
            type="sink",
            width=0.6,
            height=0.5
        ))
