"""
Smart Room Placer - Generates non-overlapping initial room layouts.
Uses grid-based packing algorithm to ensure rooms don't overlap.
"""

import random
from typing import List, Tuple, Dict, Any
import numpy as np
from loguru import logger

from ..models.schemas import LandInputSchema, RoomSchema


class SmartRoomPlacer:
    """
    Generates non-overlapping room layouts using intelligent placement algorithms.

    This solves the problem where random GA initialization creates ALL overlapping
    layouts, giving the genetic algorithm no gradient to evolve from.
    """

    def __init__(self, buildable: Dict[str, float], required_rooms: List[Dict[str, Any]]):
        """
        Initialize smart room placer.

        Args:
            buildable: Buildable area dictionary with width, length, offsets
            required_rooms: List of room definitions
        """
        self.buildable = buildable
        self.required_rooms = required_rooms

    def generate_non_overlapping_layout(
        self,
        method: str = "grid"
    ) -> List[RoomSchema]:
        """
        Generate a non-overlapping room layout.

        Args:
            method: Placement method ("grid", "sequential", "random_fit")

        Returns:
            List of non-overlapping rooms
        """
        if method == "grid":
            return self._grid_based_placement()
        elif method == "sequential":
            return self._sequential_placement()
        else:
            return self._random_fit_placement()

    def _grid_based_placement(self) -> List[RoomSchema]:
        """
        Place rooms on a grid to ensure no overlaps.

        Divides buildable area into a grid and places rooms in cells.
        """
        buildable_width = self.buildable['width']
        buildable_length = self.buildable['length']
        offset_x = self.buildable['offset_x']
        offset_y = self.buildable['offset_y']

        num_rooms = len(self.required_rooms)

        # Calculate grid dimensions (try to make roughly square)
        grid_cols = int(np.ceil(np.sqrt(num_rooms)))
        grid_rows = int(np.ceil(num_rooms / grid_cols))

        cell_width = buildable_width / grid_cols
        cell_length = buildable_length / grid_rows

        rooms = []
        room_idx = 0

        for row in range(grid_rows):
            for col in range(grid_cols):
                if room_idx >= num_rooms:
                    break

                room_def = self.required_rooms[room_idx]

                # Calculate cell boundaries
                cell_x = offset_x + (col * cell_width)
                cell_y = offset_y + (row * cell_length)

                # Room size (fit within cell with 10% margin)
                room_width = cell_width * 0.9
                room_height = cell_length * 0.9

                # Ensure minimum area
                min_area = room_def['min_area']
                current_area = room_width * room_height
                if current_area < min_area:
                    # Scale up proportionally
                    scale = np.sqrt(min_area / current_area)
                    room_width = min(room_width * scale, cell_width * 0.95)
                    room_height = min(room_height * scale, cell_length * 0.95)

                # Center room in cell
                room_x = cell_x + (cell_width - room_width) / 2
                room_y = cell_y + (cell_length - room_height) / 2

                room = RoomSchema(
                    type=room_def['type'],
                    x=room_x,
                    y=room_y,
                    width=room_width,
                    height=room_height,
                    area=room_width * room_height
                )
                rooms.append(room)
                room_idx += 1

        logger.debug(f"Grid placement: {len(rooms)} rooms placed in {grid_rows}x{grid_cols} grid")
        return rooms

    def _sequential_placement(self) -> List[RoomSchema]:
        """
        Place rooms sequentially, avoiding overlaps.

        Places rooms one by one, trying different positions until
        finding one that doesn't overlap with existing rooms.
        """
        rooms = []
        buildable_width = self.buildable['width']
        buildable_length = self.buildable['length']
        offset_x = self.buildable['offset_x']
        offset_y = self.buildable['offset_y']

        for room_def in self.required_rooms:
            # Calculate room dimensions based on minimum area
            min_area = room_def['min_area']
            aspect_ratio = 1.2  # Slightly rectangular (width/height)

            room_height = np.sqrt(min_area / aspect_ratio)
            room_width = min_area / room_height

            # Try to find non-overlapping position
            max_attempts = 100
            placed = False

            for attempt in range(max_attempts):
                # Random position within buildable area
                max_x = max(offset_x, buildable_width - room_width + offset_x)
                max_y = max(offset_y, buildable_length - room_height + offset_y)

                if max_x <= offset_x or max_y <= offset_y:
                    # Room too big for buildable area
                    # Scale down
                    scale = 0.8
                    room_width *= scale
                    room_height *= scale
                    continue

                room_x = random.uniform(offset_x, max_x)
                room_y = random.uniform(offset_y, max_y)

                # Check for overlaps with existing rooms
                test_room = RoomSchema(
                    type=room_def['type'],
                    x=room_x,
                    y=room_y,
                    width=room_width,
                    height=room_height,
                    area=room_width * room_height
                )

                if not self._has_overlap(test_room, rooms):
                    rooms.append(test_room)
                    placed = True
                    break

            if not placed:
                # Couldn't place room - use fallback grid position
                logger.warning(f"Couldn't place {room_def['type']} sequentially, using grid fallback")
                # Just place it somewhere even if it overlaps slightly
                room_x = offset_x + random.random() * (buildable_width - room_width)
                room_y = offset_y + random.random() * (buildable_length - room_height)

                room = RoomSchema(
                    type=room_def['type'],
                    x=room_x,
                    y=room_y,
                    width=room_width,
                    height=room_height,
                    area=room_width * room_height
                )
                rooms.append(room)

        logger.debug(f"Sequential placement: {len(rooms)} rooms placed")
        return rooms

    def _random_fit_placement(self) -> List[RoomSchema]:
        """
        Random placement with multiple attempts to find non-overlapping configuration.
        """
        best_rooms = None
        best_overlap_count = float('inf')

        # Try multiple random configurations
        for attempt in range(20):
            rooms = self._sequential_placement()
            overlap_count = self._count_overlaps(rooms)

            if overlap_count == 0:
                return rooms  # Found non-overlapping layout!

            if overlap_count < best_overlap_count:
                best_overlap_count = overlap_count
                best_rooms = rooms

        logger.warning(f"Random fit: Best layout has {best_overlap_count} overlaps")
        return best_rooms

    def _has_overlap(self, room: RoomSchema, existing_rooms: List[RoomSchema]) -> bool:
        """Check if room overlaps with any existing rooms."""
        for existing in existing_rooms:
            if self._rooms_overlap(room, existing):
                return True
        return False

    def _count_overlaps(self, rooms: List[RoomSchema]) -> int:
        """Count number of overlapping room pairs."""
        count = 0
        for i, room1 in enumerate(rooms):
            for room2 in rooms[i+1:]:
                if self._rooms_overlap(room1, room2):
                    count += 1
        return count

    @staticmethod
    def _rooms_overlap(room1: RoomSchema, room2: RoomSchema, tolerance: float = 0.01) -> bool:
        """Check if two rooms overlap."""
        return not (
            room1.x + room1.width - tolerance <= room2.x or
            room2.x + room2.width - tolerance <= room1.x or
            room1.y + room1.height - tolerance <= room2.y or
            room2.y + room2.height - tolerance <= room1.y
        )
